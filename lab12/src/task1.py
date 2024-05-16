import json
import socket
import threading
from collections import defaultdict

INFINITY = 10 ** 9
HOST = '127.0.0.1'

global_lock = threading.Lock()

def print_routing_tables(routing_tables, next_hops):
    for router, table in routing_tables.items():
        print(f'{"[Source IP]":20} {"[Destination IP]":20} {"[Next Hop]":20} {"Metric":20}')
        for destination, cost in table.items():
            print(f'{router:20} {destination:20} {next_hops[router].get(destination, "-  ")} {cost:20}')
        print()

def get_host_port(ip, all_hosts, flag=False):
    for i in range(len(all_hosts)):
        if all_hosts[i] == ip:
            return 8000 + i + len(all_hosts) * flag
    raise Exception(f"can't find ip {ip}")

def send_routing_table(sock, neighbor, table, all_hosts):
    data = json.dumps(table).encode()
    sock.sendto(data, (HOST, get_host_port(neighbor, all_hosts)))

def receive_routing_table(sock):
    data, addr = sock.recvfrom(1024)
    return json.loads(data.decode()), addr[0]

def send_has_changes_status(sock, neighbor, has_changes, all_hosts):
    data = json.dumps(has_changes).encode()
    sock.sendto(data, (HOST, get_host_port(neighbor, all_hosts, True)))

def receive_has_changes_status(sock):
    data, addr = sock.recvfrom(1024)
    return json.loads(data.decode()), addr[0]

def router_thread(router_ip, neighbors, all_hosts):
    routing_table = defaultdict(lambda: INFINITY)
    next_hops = {}
    routing_table[router_ip] = 0

    for neighbor in neighbors:
        routing_table[neighbor] = 1
        next_hops[neighbor] = neighbor

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((HOST, get_host_port(router_ip, all_hosts)))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as status_sock:
            status_sock.bind((HOST, get_host_port(router_ip, all_hosts, True)))
            step = 0
            has_changes = True
            while has_changes:
                step += 1
                has_changes = False

                for neighbor in neighbors:
                    send_routing_table(sock, neighbor, routing_table, all_hosts)

                for neighbor in neighbors:
                    updated_table, sender = receive_routing_table(sock)

                    for destination, cost in updated_table.items():
                        new_cost = cost + 1
                        if new_cost < routing_table[destination]:
                            routing_table[destination] = new_cost
                            next_hops[destination] = neighbor
                            has_changes = True

                global_lock.acquire()
                print(f"Simulation step {step} of router {router_ip}:")
                print_routing_tables({router_ip: routing_table}, {router_ip: next_hops})
                global_lock.release()

                for host in all_hosts:
                    send_has_changes_status(status_sock, host, has_changes, all_hosts)

                for host in all_hosts:
                    neighbor_has_changes, _ = receive_has_changes_status(status_sock)
                    has_changes = has_changes or neighbor_has_changes 

    global_lock.acquire()
    print(f'Final state of router {router_ip} table:')
    print(f'{"[Source IP]":20} {"[Destination IP]":20} {"[Next Hop]":20} {"Metric":20}')
    for destination, cost in routing_table.items():
        print(f'{router_ip:20} {destination:20} {next_hops.get(destination, "-  ")} {cost:20}')
    print()
    global_lock.release()

if __name__ == '__main__':
    with open('network.json') as f:
        network = json.load(f)
    # run_rip(network)
    threads = []
    all_hosts = []

    for router in network:
        all_hosts.append(router)

    for router, neighbors in network.items():
        t = threading.Thread(target=router_thread, args=(router, neighbors, all_hosts))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()