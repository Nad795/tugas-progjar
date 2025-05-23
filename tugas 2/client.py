import socket

server_address = ('172.16.16.101', 45000)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)

try:
    while True:
        message = input()
        
        request = message + "\r\n"
        sock.sendall(message.encode('utf-8'))
        data = sock.recv(1024)
        
        response = data.decode('utf-8')
        print(response.strip())
        if response.strip() == "invalid request":
            break
finally:
    sock.close()