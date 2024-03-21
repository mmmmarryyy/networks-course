import time
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server.bind(("", 12345))

while True:
    current_time = time.ctime()
    server.sendto(current_time.encode(), ('<broadcast>', 12345))
    time.sleep(1)
