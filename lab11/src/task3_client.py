import socket

client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

server_address = ('::1', 12345)
client_socket.connect(server_address)

message = "example message"

try:
    while True:
        client_socket.send(message.encode('utf-8'))
        data = client_socket.recv(1024).decode('utf-8')
        print(f'Server: {data}')

finally:
    client_socket.close()