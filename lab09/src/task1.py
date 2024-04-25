import socket
import psutil

def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def get_netmask(ip_address):
    for _, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == socket.AF_INET and snic.address == ip_address:
                return snic.netmask
    return None

if __name__ == "__main__":
    ip_address = get_ip_address()
    netmask = get_netmask(ip_address)

    if ip_address and netmask:
        print(f"IP-address: {ip_address}")
        print(f"Network mask: {netmask}")
    else:
        print("Can't get information about network")