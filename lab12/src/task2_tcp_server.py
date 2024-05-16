import socket
import time
import tkinter as tk
from tkinter import ttk

def create_tcp_socket(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(1)
    return sock

def start_receiving():
    global number_of_packets, counter, first_packet, last_packet
    counter = 0
    first_packet = 0

    try:
        client_socket, _ = sock.accept()
        number_of_packets = int(client_socket.recv(1024).decode())
        for i in range(number_of_packets):
            try:
                packet = client_socket.recv(1024).decode().split()[0]
                counter += 1
                if first_packet == 0:
                    first_packet = int(packet)
            except socket.timeout:
                pass
        last_packet = time.time()
    except Exception as e:
        print(f'{time.time()}, Receiving messages failed: {e}')
    finally:
        client_socket.close()
    update_labels()

def update_labels():
    global number_of_packets, counter, first_packet, last_packet
    total_time_ms = last_packet - first_packet
    print(total_time_ms)
    speed = round(1024 * counter / total_time_ms) if total_time_ms > 0 else 0
    speed_label.config(text=f'{speed} B/s')
    messages_label.config(text=f'{counter}/{number_of_packets}')

def update_socket():
    global host, port, sock
    try:
        new_host = host_entry.get()
        new_port = int(port_entry.get())
        if new_host != host or new_port != port:
            host, port = new_host, new_port
            sock.close()
            sock = create_tcp_socket(host, port)
    except:
        pass

host, port = '127.0.0.1', 12345
sock = create_tcp_socket(host, port)

number_of_packets = 0
counter = 0
first_packet = 0
last_packet = 1

window = tk.Tk()
window.title("TCP Server")

host_label = ttk.Label(window, text="Enter IP:")
host_label.grid(row=0, column=0, padx=5, pady=5)
host_entry = ttk.Entry(window)
host_entry.insert(0, host)
host_entry.grid(row=0, column=1, padx=5, pady=5)

port_label = ttk.Label(window, text="Enter Port:")
port_label.grid(row=1, column=0, padx=5, pady=5)
port_entry = ttk.Entry(window)
port_entry.insert(0, str(port))
port_entry.grid(row=1, column=1, padx=5, pady=5)

messages_label = ttk.Label(window, text=f'0/{number_of_packets}')
messages_label.grid(row=2, column=1, padx=5, pady=5)

speed_label = ttk.Label(window, text='0 B/s')
speed_label.grid(row=3, column=1, padx=5, pady=5)

update_button = ttk.Button(window, text="Update Socket", command=update_socket)
update_button.grid(row=0, column=2, padx=5, pady=5)

start_button = ttk.Button(window, text="Start Receiving", command=start_receiving)
start_button.grid(row=1, column=2, padx=5, pady=5)

window.mainloop()

sock.close()