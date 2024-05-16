import socket
import struct
import time
import select
import sys

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0
ICMP_TIME_EXCEEDED = 11

def checksum(data):
    if len(data) % 2:
        data += b'\x00'
    res = sum(struct.unpack('!H', data[i:i+2])[0] for i in range(0, len(data), 2))
    while res >> 16:
        res = (res & 0xFFFF) + (res >> 16)
    return ~res & 0xFFFF

def receive_icmp_packet(sock, timeout=1):
    try:
        ready = select.select([sock], [], [], timeout)
        if ready[0] == []:
            return None, None
        recv_packet, addr = sock.recvfrom(1024)
        icmp_header = recv_packet[20:28]
        type, code, checksum, packet_id, sequence = struct.unpack( #TODO: change to _
            '!BBHHH', icmp_header
        )

        if type == ICMP_TIME_EXCEEDED:
            return addr[0], time.time()
        elif type == ICMP_ECHO_REPLY:
            return addr[0], time.time()
        return None, None
    except socket.timeout:
        return None, None


def traceroute(host, max_hops=30, packet_count=3, timeout=1):
    try:
        dest_addr = socket.gethostbyname(host)
    except socket.gaierror:
        print("Can't get host by name: ", host)
        return

    print(f"TRaceroute to {host} [{dest_addr}] with max hops = {max_hops}:")

    ttl = 1
    while ttl <= max_hops:
        ttl_flag = False
        for i in range(packet_count):
            try:
                sock = socket.socket(
                    socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp")
                )
            except socket.error as err:
                print(f"Can't create socket: {err}")
                return

            header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, 0, 1, ttl)
            data = struct.pack('d', time.time())
            checksum_data = checksum(header + data)
            header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, checksum_data, 1, ttl)
            packet = header + data

            sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            start_time = time.time()
            sock.sendto(packet, (dest_addr, 0))
            ip, end_time = receive_icmp_packet(sock, timeout)

            if ip:
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except socket.herror:
                    hostname = "Unknown host"
                if end_time:
                    rtt = round((end_time - start_time) * 1000, 2)
                    if i == 0 or not ttl_flag:
                        ttl_flag = True
                        print(f"{ttl}  {ip} ({hostname})  {rtt} ms", end='', flush=True)
                    else:
                        print(f"  {rtt} ms", end='', flush=True)
                else:
                    if i == 0 or not ttl_flag:
                        ttl_flag = True
                        print(f"{ttl}  {ip} ({hostname})  timeout", end='', flush=True)
                    else:
                        print(f"  timeout", end='', flush=True)
            else:
                if i == 0 or not ttl_flag:
                    ttl_flag = True
                    print(f"{ttl}  *", end='', flush=True)
                else:
                    print(f"  *", end='', flush=True)

            if i == packet_count - 1:
                print()

            sock.close()

        ttl += 1

        if ip == dest_addr:
            break


if __name__ == "__main__":
    if (len(sys.argv[1:]) < 1):
        print(f"you provide {len(sys.argv[1:])} arguments, at least 1 expected (hostname, max_hops, packet_count, timeout)")
        sys.exit(1)

    hostname = sys.argv[1]
    if (len(sys.argv[1:]) > 1):
        max_hops = int(sys.argv[2])
        if (len(sys.argv[1:]) > 2):
            packet_count = int(sys.argv[3])
            if (len(sys.argv[1:]) > 3):
                timeout = int(sys.argv[4])
                traceroute(hostname, max_hops, packet_count, timeout)
            else:
                traceroute(hostname, max_hops, packet_count)
        else:
            traceroute(hostname, max_hops)
    else:
        traceroute(hostname)
