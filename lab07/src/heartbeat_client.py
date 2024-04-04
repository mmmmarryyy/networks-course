import socket
import datetime
import time

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ('127.0.0.1', 12345)
client_socket.settimeout(1.0)

rtt_list = []
lost_packets = 0

for i in range(1, 20):
    message = f'Ping {i} {datetime.datetime.now()}'
    start_time = datetime.datetime.now()
    client_socket.sendto(message.encode(), server_address)

    try:
        response, addr = client_socket.recvfrom(1024)
        end_time = datetime.datetime.now()
        rtt = (end_time - start_time).total_seconds()
        rtt_list.append(rtt)
        print(f'Response from server: {response.decode()}')
        print(f'RTT: {rtt} seconds')
        min_rtt = min(rtt_list)
        max_rtt = max(rtt_list)
        avg_rtt = sum(rtt_list) / len(rtt_list)
        packet_loss_percentage = (lost_packets / 10) * 100

        print(f'STATS: Min RTT: {min_rtt} s, Max RTT: {max_rtt} s, Avg RTT: {avg_rtt} s, loss: {packet_loss_percentage}%\n')

    except socket.timeout:
        lost_packets += 1
        print('Request timed out\n')
    
client_socket.close()

