from socket import *
import socket
import threading
import logging
import time
import sys
from concurrent.futures import ThreadPoolExecutor


from file_protocol import  FileProtocol
fp = FileProtocol()


class ProcessTheClient:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address

    def run(self):
        try:
            while True:
                data = self.connection.recv(33554432)
                if data:
                    d = data.decode()
                    hasil = fp.proses_string(d)
                    hasil=hasil+"\r\n\r\n"
                    self.connection.sendall(hasil.encode())
                else:
                    break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        finally:
            self.connection.close()


class Server(threading.Thread):
    def __init__(self,ipaddress='0.0.0.0',port=8889):
        self.ipinfo=(ipaddress,port)
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self)

    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)
        with ThreadPoolExecutor() as executor:
            while True:
                connection, client_address = self.my_socket.accept()
                logging.warning(f"connection from {client_address}")
                
                clt = ProcessTheClient(connection, client_address)
                executor.submit(clt.run)
                self.the_clients.append(clt)


def main():
    svr = Server(ipaddress='0.0.0.0',port=7777)
    svr.run()


if __name__ == "__main__":
    main()

