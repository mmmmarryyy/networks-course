import socket
import pickle
import random
import sys

client_port = None
address = '127.0.0.1'

def calculate_checksum(data):
    checksum = 0
    for byte in data:
        checksum = (checksum + byte) & 0xFF
    return checksum

def server(port, filename, receive_filename):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('127.0.0.1', port))
    packet_number = 0
    with open(receive_filename, "wb") as file:
        file.write(b"")

    while True:
        try:
            data, addr = server_socket.recvfrom(1024)
            client_port = addr[1]
            if data == b'EOF':
                break
            if data == b'EXCEPTION':
                print("some exception in client")
                break
            packet = pickle.loads(data)

            if random.random() < 0.3: #30% packet loss
                continue

            if packet['packet_num'] == packet_number and packet['checksum'] == calculate_checksum(packet['data']):
                ack_data = {'packet_num': packet['packet_num'], 'data': 'ACK'}
                ack = pickle.dumps(ack_data)
                server_socket.sendto(ack, addr)
                packet_number = 1 - packet_number
                with open(receive_filename, "ab") as file:
                    file.write(packet['data'])
            else:
                print("wrong packet_num or checksum")
        except Exception as e:
            print(f"Exception: {e}")
            break

    print("NOW SEND FILE")
    packet_number = 0
    server_socket.settimeout(5)
    try:
        with open(filename, 'rb') as file:
            file_data = file.read()
            packet_size = 3
            packets = [file_data[i:i+packet_size] for i in range(0, len(file_data), packet_size)]

            for i, packet in enumerate(packets):
                data = {'packet_num': packet_number, 'data': packet, 'checksum': calculate_checksum(packet)}
                server_socket.sendto(pickle.dumps(data), (address, client_port))
                flag = True
                while flag:
                    try:
                        ack, _ = server_socket.recvfrom(1024)
                        ack_data = pickle.loads(ack)
                        if ack_data['packet_num'] == packet_number:
                            packet_number = 1 - packet_number
                            print(f"Packet {i} ACK received")
                            flag = False
                    except socket.timeout:
                        print(f"Timeout for packet {i}, resending...")
                        server_socket.sendto(pickle.dumps(data), (address, client_port))

        server_socket.sendto(b'EOF', (address, client_port))
    except Exception as e:
        server_socket.sendto(b'EXCEPTION', (address, port))
        print(f"Exception: {e}")
    server_socket.close()

if __name__ == '__main__':
    receive_filename = ""
    filename = ""
    if (len(sys.argv[1:]) < 2):
        print(f"you provide {len(sys.argv[1:])} arguments, at least 2 expected (filename, receive_filename)")
        sys.exit(1)
    filename = sys.argv[1] #example_file_server.txt
    receive_filename = sys.argv[2] #receive_example_file_server.txt

    server_port = 12345
    server(server_port, filename, receive_filename)