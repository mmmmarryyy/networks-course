import random
import socket
import time
import tkinter as tk
from tkinter import ttk

def send_data():
    try:
        host = host_entry.get()
        port = int(port_entry.get())
        number_of_packets = int(packets_entry.get())
    except Exception as e:
        print(f'Parsing arguments failed: {e}')
        return

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.sendall(bytes(str(number_of_packets), encoding='utf-8'))
        for i in range(number_of_packets):
            now = time.time()
            data = f'{int(now)} '
            data += ''.join(chr(random.randint(16, 64)) for _ in range(1024 - len(data)))
            sock.sendall(data.encode())
    except Exception as e:
        print(f'{time.time()} Sending packets failed: {e}')
    finally:
        sock.close()

root = tk.Tk()
root.title("TCP Client")

host_label = ttk.Label(root, text="Enter IP:")
host_label.grid(row=0, column=0, padx=5, pady=5)
host_entry = ttk.Entry(root)
host_entry.insert(0, '127.0.0.1')
host_entry.grid(row=0, column=1, padx=5, pady=5)

port_label = ttk.Label(root, text="Enter port:")
port_label.grid(row=1, column=0, padx=5, pady=5)
port_entry = ttk.Entry(root)
port_entry.insert(0, '12345')
port_entry.grid(row=1, column=1, padx=5, pady=5)

packets_label = ttk.Label(root, text="Enter number of packets:")
packets_label.grid(row=2, column=0, padx=5, pady=5)
packets_entry = ttk.Entry(root)
packets_entry.insert(0, '10')
packets_entry.grid(row=2, column=1, padx=5, pady=5)

send_button = ttk.Button(root, text="Send packets", command=send_data)
send_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

root.mainloop()