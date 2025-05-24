from socket import *
import socket
import threading
import logging
import time
import sys
from concurrent.futures import ProcessPoolExecutor


from file_protocol import  FileProtocol
fp = FileProtocol()


def ProcessTheClient(data):
    d = data.decode()
    hasil = fp.proses_string(d)
    hasil=hasil+"\r\n\r\n"
    return hasil.encode()


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
                logging.warning(f"connection from {client_address}")
                try:
                    while True:
                        data = connection.recv(33554432)
                        if not data:
                            break
                        clt = executor.submit(ProcessTheClient, data)
                        hasil = clt.result()
                        connection.sendall(hasil)
                except ConnectionResetError:
                    logging.warning(f"Connection reset by {client_address}")
                except Exception as e:
                    logging.error(f"Unexpected error: {e}")
                finally:
                    connection.close()


def main():
    svr = Server(ipaddress='0.0.0.0',port=7777)
    svr.run()


if __name__ == "__main__":
    main()

