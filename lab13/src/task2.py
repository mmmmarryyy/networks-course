import psutil
import time
import os
import pandas as pd
import socket

UPDATE_DELAY = 1  # in seconds

def get_size(bytes):
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024

io = psutil.net_io_counters(pernic=True)
app_traffic = {}

while True:
    time.sleep(UPDATE_DELAY)
    io_2 = psutil.net_io_counters(pernic=True)

    connections = psutil.net_connections(kind='inet')

    for iface, iface_io in io.items():
        upload_speed, download_speed = (
            io_2[iface].bytes_sent - iface_io.bytes_sent,
            io_2[iface].bytes_recv - iface_io.bytes_recv,
        )

        iface_ip = None
        ifaces = psutil.net_if_addrs()
        if iface in ifaces:
            for addr_info in ifaces[iface]:
                if addr_info.family == socket.AF_INET or addr_info.family == socket.AF_INET6:
                    iface_ip = addr_info.address
                    break

        for conn in connections:
            local_ip = conn.laddr.ip
            local_port = conn.laddr.port
            remote_port = conn.raddr[1] if conn.raddr else None 
            remote_ip = conn.raddr[0] if conn.raddr else None 
            key = f"{local_ip}:{local_port} ({remote_ip}:{remote_port})" if remote_port else str(local_port)

            if key not in app_traffic:
                app_traffic[key] = {
                    "iface": iface,
                    "Download": 0,
                    "Upload": 0,
                    "Download Speed": 0,
                    "Upload Speed": 0,
                }

            if conn.status == psutil.CONN_ESTABLISHED: 
                if conn.laddr.ip == iface_ip:
                    app_traffic[key]["Download"] += download_speed
                    app_traffic[key]["Download Speed"] += download_speed / UPDATE_DELAY
                if conn.raddr.ip == iface:
                    app_traffic[key]["Upload"] += upload_speed
                    app_traffic[key]["Upload Speed"] += upload_speed / UPDATE_DELAY

    data = []
    for app, stats in app_traffic.items():
        if not (get_size(stats["Download"]) == '0.00B' and get_size(stats["Upload"]) == '0.00B' and get_size(stats['Download Speed']) == '0.00B' and get_size(stats['Upload Speed']) == '0.00B'):
            data.append({
                "App": app,
                "Download": stats["Download"],
                "Upload": get_size(stats["Upload"]),
                "Download Speed": f"{get_size(stats['Download Speed'])}/s",
                "Upload Speed": f"{get_size(stats['Upload Speed'])}/s",
            })

    io = io_2
    df = pd.DataFrame(data)
    df.sort_values(by="Download", inplace=True, ascending=False)
    df['Download'] = df['Download'].apply(get_size)

    os.system("cls") if "nt" in os.name else os.system("clear")
    print(df.to_string())