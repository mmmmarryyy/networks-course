import tkinter as tk
from tkinter import ttk
import socket
import scapy.all as scapy

NETWORK_IP = '192.168.0.9'
MASK = [255, 255, 255, 0]

def scan_network(ip, progress_bar):
    comps = []
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    
    scanned = scapy.srp(broadcast / arp_request, timeout=1, verbose=False)[0]
    total_ips = len(scanned)
    progress = 0

    for element in scanned:
        comps.append({'ip': element[1].psrc, 'mac': element[1].hwsrc})
        progress += 1
        progress_percent = int((progress / total_ips) * 100)
        progress_bar['value'] = progress_percent
        progress_bar.update()

    return comps

def start_scan():
    print("start_scan")
    scanned_data = scan_network(f'{NETWORK_IP}/24', progress_bar)

    result_text.insert(tk.END, f'{"IP address":30}{"MAC address":30}{"Host name":30}\n')
    result_text.insert(tk.END, 'This computer:\n')
    result_text.insert(tk.END, f'{"192.168.0.9":30}{"1c:91:80:f3:f0:d5":30}{socket.gethostbyaddr("192.168.0.9")[0]:30}\n')
    result_text.insert(tk.END, 'Local network:\n')

    for i, client in enumerate(scanned_data):
        ip, mac = client['ip'], client['mac']
        if ip == '192.168.0.9':
            continue
        try:
            name = socket.gethostbyaddr(ip)[0]
        except Exception:
            name = "Don't find name"
        result_text.insert(tk.END, f'{str(ip):30}{str(mac):30}{str(name):30}\n')

root = tk.Tk()
root.title("Network Scanner")

progress_bar = ttk.Progressbar(root, length=200, mode='determinate')
progress_bar.pack(pady=10)

scan_button = tk.Button(root, text="Start Scan", command=start_scan)
scan_button.pack(pady=10)

result_text = tk.Text(root, height=20, width=100)
result_text.pack(pady=10)

root.mainloop()