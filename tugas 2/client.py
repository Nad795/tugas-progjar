import socket
import sys

server_address = ('172.16.16.101', 45000)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)

try:
    while True:
        request = input("Message: ")
        
        if request == "QUIT":
            sock.sendall(request.encode())
            print("Quitting...")
            sock.close()
            exit()
        elif request == "TIME":
            request += "\r\n"
            sock.sendall(request.encode())
            data = sock.recv(14)
            if len(data) == 14:
                print(data.decode('utf-8'))
            else:
                print("Invalid response")
                
except Exception as e:
    print(f"Error: {e}")
    
finally:
    sock.close()