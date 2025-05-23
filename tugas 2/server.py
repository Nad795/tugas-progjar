from socket import *
import socket
import threading
import logging
from datetime import datetime
import sys

class ProcessTheClient(threading.Thread):
    def __init__(self,connection,address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)
     
    def run(self):
        while True:
            data = self.connection.recv(32)
            if data:
                data = data.decode('utf-8')
                if data.startswith("TIME") and data.endswith("\r\n"):
                    response = "JAM " + datetime.strftime(datetime.now(), "%H:%M:%S") + "\r\n"
                    print(f"Sending response to client {self.address}")
                    self.connection.sendall(response.encode('utf-8'))
                elif data.startswith("QUIT"):
                    print(f"Client from {self.address} has exited")
                    response = "invalid request \r\n"
                    self.connection.sendall(response.encode('utf-8'))
                else:
                    print(f"Invalid request from client {self.address}")
                    self.connection.close()
                    break

class Server(threading.Thread):
	def __init__(self):
		self.the_clients = []
		self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		threading   .Thread.__init__(self)

	def run(self):
		self.my_socket.bind(('0.0.0.0',45000))
		self.my_socket.listen(1)
		while True:
			self.connection, self.client_address = self.my_socket.accept()
			logging.warning(f"connection from {self.client_address}")
			
			clt = ProcessTheClient(self.connection, self.client_address)
			clt.start()
			self.the_clients.append(clt)
	

def main():
	svr = Server()
	svr.start()

if __name__=="__main__":
	main()