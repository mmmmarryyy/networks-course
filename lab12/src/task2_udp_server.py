import socket
import time
import tkinter as tk
from tkinter import ttk

def create_udp_socket(host, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, port))
    udp_socket.settimeout(0.1)
    return udp_socket

def create_tcp_socket(host, port):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((host, port))
    tcp_socket.listen(1)
    return tcp_socket

def start_receiving_data():
    global counter, first_packet, number_of_packets

    counter = 0
    first_packet = 0

    try:
        client_socket, _ = tcp_socket.accept()
        number_of_packets = int(client_socket.recv(1024).decode())
    except Exception as e:
        print(f'Receiving the number of messages failed: {e}')
    finally:
        client_socket.close()

    receive_data()

def receive_data():
    global counter, first_packet, last_packet
    for i in range(number_of_packets):
        try:
            packet = udp_socket.recv(1024).decode().split()[0]
            counter += 1
            if first_packet == 0:
                first_packet = int(packet)
        except socket.timeout:
            pass
    last_packet = time.time()
    update_labels()

def update_labels():
    total_time_ms = last_packet - first_packet
    speed = round(1024 * counter / total_time_ms) if total_time_ms > 0 else 0
    speed_label['text'] = f'{speed} B/s'
    messages_label['text'] = f'{counter}/{number_of_packets}'

def update_socket():
    global host, port, udp_socket, tcp_socket
    try:
        new_host = host_entry.get()
        new_port = int(port_entry.get())
        if new_host != host or new_port != port:
            host, port = new_host, new_port
            udp_socket.close()
            tcp_socket.close()
            udp_socket = create_udp_socket(host, port)
            tcp_socket = create_tcp_socket(host, port)
    except:
        pass

host, port = '127.0.0.1', 12345
udp_socket = create_udp_socket(host, port)
tcp_socket = create_tcp_socket(host, port)

number_of_packets = 0
counter = 0
first_packet = 0
last_packet = 1

root = tk.Tk()
root.title("UDP Server")

host_label = ttk.Label(root, text="IP:")
host_label.grid(row=0, column=0, padx=5, pady=5)

host_entry = ttk.Entry(root)
host_entry.insert(0, host)
host_entry.grid(row=0, column=1, padx=5, pady=5)

port_label = ttk.Label(root, text="Port:")
port_label.grid(row=1, column=0, padx=5, pady=5)

port_entry = ttk.Entry(root)
port_entry.insert(0, str(port))
port_entry.grid(row=1, column=1, padx=5, pady=5)

messages_label = ttk.Label(root, text="0/0")
messages_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

speed_label = ttk.Label(root, text="0 B/s")
speed_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

update_button = ttk.Button(root, text="Update Socket", command=update_socket)
update_button.grid(row=0, column=2, padx=5, pady=5)

start_button = ttk.Button(root, text="Start Receiving", command=start_receiving_data)
start_button.grid(row=1, column=2, padx=5, pady=5)

root.mainloop()

udp_socket.close()
tcp_socket.close()