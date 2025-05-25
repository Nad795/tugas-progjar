from socket import *
import socket
import threading
import logging
import time
import sys
from concurrent.futures import ProcessPoolExecutor


from file_protocol import  FileProtocol


def ProcessTheData(data):
    fp = FileProtocol()
    hasil = fp.proses_string(data)
    return hasil+"\r\n\r\n"

def ProcessTheClient(connection, client_address, executor):
    logging.warning(f"connection from {client_address}")
    try:
        while True:
            data = connection.recv(134217728)
            if not data:
                break
            d = data.decode()
            future = executor.submit(ProcessTheData, d)
            hasil = future.result()
            connection.sendall(hasil.encode())
    except ConnectionResetError:
        logging.warning(f"Connection reset by {client_address}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        connection.close()


class Server:
    def __init__(self,ipaddress='0.0.0.0',port=8889):
        self.ipinfo=(ipaddress,port)
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)
        with ProcessPoolExecutor() as executor:
            while True:
                connection, client_address = self.my_socket.accept()
                threading.Thread(
                    target=ProcessTheClient,
                    args=(connection, client_address, executor),
                    daemon=True
                ).start()


def main():
    svr = Server(ipaddress='0.0.0.0',port=7777)
    svr.run()


if __name__ == "__main__":
    main()

