import concurrent.futures
import multiprocessing
import threading
import time
import base64
import logging
import os
import csv
from file_client_cli import remote_get, remote_post

server_address = ('172.16.16.101', 7777)


def worker_upload(filename):
    success, elapsed = remote_post(filename)
    size = os.path.getsize(filename)
    return {"operation": "upload", "filename": filename, "success": success, "time": elapsed, "size": size}


def worker_download(filename):
    success, elapsed = remote_get(filename)
    size = os.path.getsize(filename) if success else 0
    return {"operation": "download", "filename": filename, "success": success, "time": elapsed, "size": size}

def run_thread_pool(operation, filename, num_threads):
    worker_func = worker_upload if operation == "upload" else worker_download
    results = []
    lock = threading.Lock()

    def thread_task():
        res = worker_func(filename)
        with lock:
            results.append(res)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(thread_task) for _ in range(num_threads)]
        concurrent.futures.wait(futures)

    return results


def run_process_worker(operation, filename, threads_per_process):
    results = run_thread_pool(operation, filename, threads_per_process)
    return results

def run_stress_test(operation, filename, client_workers, server_workers):
    print(f"Run test: Operasi={operation}, File={filename}, Client workers={client_workers}, Server workers={server_workers}")
    
    max_process = min(10, client_workers)
    process_count = max_process
    while client_workers % process_count != 0 and process_count > 1:
        process_count -= 1
    thread_count = client_workers // process_count

    print(f"Using process pool size: {process_count}, threads per process: {thread_count}")

    start_all = time.time()
    results = []

    with multiprocessing.Pool(processes=process_count) as pool:
        multiple_results = [
            pool.apply_async(run_process_worker, args=(operation, filename, thread_count))
            for _ in range(process_count)
        ]

        for res in multiple_results:
            try:
                proc_res = res.get()
                results.extend(proc_res)
            except Exception as e:
                logging.error(f"Process error: {e}")

    end_all = time.time()
    total_time = end_all - start_all

    total_bytes = sum(r['size'] for r in results if r['success'])
    total_success = sum(1 for r in results if r['success'])
    total_fail = client_workers - total_success
    
    if total_success > 0:
        avg_time = sum(r['time'] for r in results if r['success']) / total_success
        throughput_per_client = total_bytes / avg_time if avg_time > 0 else 0
    else:
        avg_time = 0
        throughput_per_client = 0

    server_success = total_success
    server_fail = total_fail

    print(f"Summary: Total time all clients: {total_time:.2f}s, Throughput/client: {throughput_per_client/1024/1024:.2f} MB/s")
    print(f"Workers client success/fail: {total_success}/{total_fail}")
    print(f"Workers server success/fail: {server_success}/{server_fail}")
    print("-" * 60)

    return {
        "operation": operation,
        "volume": os.path.getsize(filename),
        "client_workers": client_workers,
        "server_workers": server_workers,
        "total_time": total_time,
        "throughput_per_client": throughput_per_client,
        "client_success": total_success,
        "client_fail": total_fail,
        "server_success": server_success,
        "server_fail": server_fail,
    }


def main():
    files = ["files/10MB_file.dat", "files/50MB_file.dat", "files/100MB_file.dat"]
    client_worker_pool = [1, 5, 50]
    server_worker_pool = [1, 5, 50]
    operations = ["upload", "download"]

    all_results = []
    nomor = 1
    
    for op in operations:
        for f in files:
            for client_w in client_worker_pool:
                for server_w in server_worker_pool:
                    print(f"=== Test nomor {nomor} ===")
                    print(f"Pastikan server worker pool diset ke {server_w} dan server di-restart!")
                    result = run_stress_test(op, f, client_w, server_w)
                    result["nomor"] = nomor
                    all_results.append(result)
                    nomor += 1
                    
    with open("stress_test_results.csv", "w", newline='') as csvfile:
        fieldnames = ["nomor", "operation", "volume", "client_workers", "server_workers",
                      "total_time", "throughput_per_client", "client_success", "client_fail",
                      "server_success", "server_fail"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_results:
            writer.writerow(row)

    print("Stress test selesai, hasil tersimpan di stress_test_results.csv")


if __name__ == "__main__":
    main()