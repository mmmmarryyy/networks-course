import socket
import threading

def handle_echo(client_socket, client_address):
    print(f'Handle client: {client_address}')
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break

            client_socket.send(data.upper().encode('utf-8'))
        except:
            client_socket.close()
            print(f'Client: {client_address} diconnected')
            break


server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

server_address = ('::1', 12345)
server_socket.bind(server_address)

server_socket.listen(1)

while True:
    client_socket, client_address = server_socket.accept()

    client_thread = threading.Thread(target=handle_echo, args=(client_socket, client_address))
    client_thread.start()
