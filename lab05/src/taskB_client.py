import socket

HOST = '127.0.0.1'
PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

try:
    while True:
        command = input("Enter the command to execute on the server (or 'exit' to exit): \n")
        if command.lower() == 'exit':
            client_socket.close()
            break
        client_socket.send(command.encode())
        output = client_socket.recv(1024)
        print("COMMAND OUTPUT:")
        while ("END OF COMMAND OUTPUT" in output.decode()) == False:
            print(output.decode(), end='')
            output = client_socket.recv(1024)
        print(output.decode())
except:
    client_socket.close()