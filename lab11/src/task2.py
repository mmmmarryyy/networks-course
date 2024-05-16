import socket
import threading
import time
from collections import defaultdict

global_lock = threading.Lock()

class Node(threading.Thread):
    INF = float('inf')

    def __init__(self, name, host, port, neighbors, weights):
        threading.Thread.__init__(self)
        self.name = name
        self.host = host
        self.port = port
        self.neighbors = neighbors
        self.weights = weights
        self.routing_table = defaultdict(lambda: self.INF)
        self.routing_table[self.name] = 0
        self.next_hop = {self.name: self.name}
        for key, value in weights.items():
            self.routing_table[key] = value
            self.next_hop[key] = key
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(0.1)
        self.running = True
        self.lock = threading.Lock()

    def send_vector(self):
        for neighbor in self.neighbors:
            vector = {dest: cost for dest, cost in self.routing_table.items() if (dest in self.next_hop.keys() and self.next_hop[dest] != neighbor['name']) and dest != self.name }
            message = f"sv|{self.name}|{vector}"
            self.sock.sendto(message.encode(), (neighbor['host'], neighbor['port']))

    def receive_vector(self):
        try:
            data, addr = self.sock.recvfrom(1024)
            message = data.decode()
            type, sender, data = message.split('|', 2)

            self.lock.acquire()
            if type == 'sv':
                if global_lock.locked():
                    self.lock.release()
                    while global_lock.locked():
                        continue
                    self.lock.acquire()

                vector = eval(data)
                updated = False
                for dest, cost in vector.items():

                    if dest == self.name:
                        if cost < self.routing_table[sender]:
                            self.routing_table[sender] = cost
                            updated = True
                    else:
                        new_cost = self.weights[sender] + cost
                        if new_cost < self.routing_table[dest]:
                            self.routing_table[dest] = new_cost
                            self.next_hop[dest] = sender
                            updated = True

                if updated:
                    print(f'[Node {self.name}] routing table is updated: {dict(sorted(dict(self.routing_table).items()))}')
                    self.send_vector()

            elif type == 'weight':
                new_weight = int(data)
                self.weights[sender] = new_weight
                for weight in self.routing_table:
                    if weight in self.weights.keys() and self.next_hop[sender] == sender:
                        self.routing_table[weight] = self.weights[weight]
                    else:
                        self.routing_table[weight] = self.INF
                        self.next_hop[sender] = sender
                self.routing_table[self.name] = 0
                print(f'[Node {self.name}] set new weight of {sender} to {new_weight}')
                print(f'[Node {self.name}] routing table is updated: {dict(sorted(dict(self.routing_table).items()))}')
                if global_lock.locked():
                    self.lock.release()
                    while global_lock.locked():
                        continue
                    self.lock.acquire()
                    self.send_vector()
            self.lock.release()
        except Exception:
            if self.lock.locked():
                self.lock.release()
            pass

    def run(self):
        cycle_iter = 1
        self.send_vector()
        while self.running:
            if cycle_iter == 100:
                self.send_vector()
                cycle_iter = 0
            self.receive_vector()
            cycle_iter += 1

    def stop(self):
        self.running = False
        if self.lock.locked():
            self.lock.release()
        self.sock.close()

if __name__ == "__main__":
    HOST = '127.0.0.1'

    nodes = {
        '0': Node('0', HOST, 12000, [{'name': '1', 'host': HOST, 'port': 12001}, {'name': '2', 'host': HOST, 'port': 12002}, {'name': '3', 'host': HOST, 'port': 12003}], {'1': 1, '2': 3, '3': 7}),
        '1': Node('1', HOST, 12001, [{'name': '0', 'host': HOST, 'port': 12000}, {'name': '2', 'host': HOST, 'port': 12002}], {'0': 1, '2': 1}),
        '2': Node('2', HOST, 12002, [{'name': '0', 'host': HOST, 'port': 12000}, {'name': '1', 'host': HOST, 'port': 12001}, {'name': '3', 'host': HOST, 'port': 12003}], {'0': 3, '1': 1, '3': 2}),
        '3': Node('3', HOST, 12003, [{'name': '0', 'host': HOST, 'port': 12000}, {'name': '2', 'host': HOST, 'port': 12002}], {'0': 7, '2': 2}),
    }

    for node in nodes.values():
        node.start()

    time.sleep(15)

    main_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def set_new_weight(first, second, new_weight):
        print(f'[Main] for nodes {first} and {second} set weight between them to {new_weight}')
        main_socket.sendto(f'weight|{first}|{new_weight}'.encode(), (nodes[second].host, nodes[second].port))
        main_socket.sendto(f'weight|{second}|{new_weight}'.encode(), (nodes[first].host, nodes[first].port))

    global_lock.acquire()
    set_new_weight('1', '2', 7)
    set_new_weight('3', '0', 2)
    global_lock.release()

    time.sleep(35) 

    for node in nodes.values():
        print(f'[Main] final routing of node {node.name}: {dict(sorted(dict(node.routing_table).items()))}')
        node.stop()