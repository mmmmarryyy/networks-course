import socket
import struct
import time
import sys

def checksum(data):
    if len(data) % 2:
        data += b'\x00'
    res = sum(struct.unpack('!H', data[i:i+2])[0] for i in range(0, len(data), 2))
    while res >> 16:
        res = (res & 0xFFFF) + (res >> 16)
    return ~res & 0xFFFF

def get_icmp_error_message(code):
    error_messages = {
        0: 'Network Unreachable',
        1: 'Host Unreachable',
    }
    return error_messages.get(code, 'Unknown Error')

def ping(host, count=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
    
    ID = 12345
    seq_num = 1
    rtt_list = []
    dest_addr = socket.gethostbyname(host)
    
    for i in range (count):
        header = struct.pack('!BBHHH', 8, 0, 0, ID, seq_num)
        data = struct.pack('d', time.time())
        checksum_val = checksum(header + data)
        header = struct.pack('!BBHHH', 8, 0, checksum_val, ID, seq_num)
        packet = header + data
        
        sock.sendto(packet, (host, 0))
        
        sock.settimeout(1)
        
        try:
            start_time = time.time()
            data, addr = sock.recvfrom(1024)
            end_time = time.time()
            rtt = (end_time - start_time) * 1000
            rtt_list.append(rtt)

            icmp_header = data[20:28]
            icmp_type, icmp_code, _, _, _ = struct.unpack('!BBHHH', icmp_header)

            if icmp_type == 0:
                print(f'{len(data)} bytes from {dest_addr}: icmp_seq={i} time={rtt:.1f} ms')
            elif icmp_type == 3:
                error_message = get_icmp_error_message(icmp_code)
                print(f'{len(data)} bytes from {dest_addr}: {error_message}')
            else:
                print("UNEXPECTED ICMP TYPE: ", icmp_type)
        except socket.timeout:
            print(f'Request timeout for icmp_seq {i}')
            continue
        
        seq_num += 1
        time.sleep(1)

    sock.close()
    if len(rtt_list) > 0:
        min_rtt = min(rtt_list)
        max_rtt = max(rtt_list)
        avg_rtt = sum(rtt_list) / len(rtt_list)
        loss_rate = (count - len(rtt_list)) / seq_num * 100
        print(f'--- {host} ping statistics ---')
        print(f'{count} packets transmitted, {len(rtt_list)} packets received, {loss_rate:.2f}% packet loss')
        print(f'RTT min/avg/max = {min_rtt:.1f}/{avg_rtt:.1f}/{max_rtt:.1f} ms')

if __name__ == '__main__':
    if (len(sys.argv[1:]) < 1):
        print(f"you provide {len(sys.argv[1:])} arguments, 1 expected (target_host)")
        sys.exit(1)

    target_host = sys.argv[1]
    ping(target_host, count=10)