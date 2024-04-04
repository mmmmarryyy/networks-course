import socket
import random
import datetime
import sys

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.settimeout(1)
server_address = ('127.0.0.1', 12345)
server_socket.bind(server_address)

clients = {} 

def update_clients(client_timeout):
    global clients
    new_clients = {}
    for addr in clients:
        if len(clients[addr]) > 0:
            if (datetime.datetime.now() - clients[addr][-1][1]).total_seconds() < client_timeout:
                new_clients[addr] = clients[addr]
            else:
                print(f"Client {addr} stop\n")
        else:
            new_clients[addr] = []

    clients = new_clients

def handler(client_timeout):
    while True:
        try:
            data, addr = server_socket.recvfrom(1024)
            message = data.decode()
            
            if addr not in clients:
                clients[addr] = []

            if random.random() < 0.3:
                continue
            
            seq_num = message.split()[1]
            timestamp = message.split()[2] + ' ' + message.split()[3]
            clients[addr].append((int(seq_num), datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')))

            data = data.decode().upper()
            server_socket.sendto(data.encode(), addr)
            
            if len(clients[addr]) > 1:
                for i in range(clients[addr][-2][0] + 1, clients[addr][-1][0]):
                    print(f'Packet loss: {i} for address {addr}')

            update_clients(client_timeout)

        except socket.timeout:
            update_clients(client_timeout)

if __name__ == "__main__":
    if (len(sys.argv[1:]) != 1):
        print(f"you provide {len(sys.argv[1:])} arguments, 1 expected (client_timeout)")
        sys.exit(1)
    client_timeout = int(sys.argv[1])
    handler(client_timeout)