import socket
import sys

def check_ports(ip_address, start_port, end_port):
    open_ports = []
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)
        result = sock.connect_ex((ip_address, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    return open_ports

if __name__ == "__main__":
    if (len(sys.argv[1:]) < 3):
        print(f"you provide {len(sys.argv[1:])} arguments, at least 3 expected (ip address, start port, end port)")
        sys.exit(1)

    ip = sys.argv[1]
    start_port = int(sys.argv[2])
    end_port = int(sys.argv[3])
    open_ports = check_ports(ip, start_port, end_port)

    if open_ports:
        print("Open ports:", open_ports)
    else:
        print("Can't find open ports")