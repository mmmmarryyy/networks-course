import socket
import sys
import time
import threading
from queue import Queue

def handle_request(client_socket):
    request = client_socket.recv(1024).decode()
    filename = request.split()[1][1:]
    
    try:
        with open(filename, 'rb') as file:
            content = file.read()
            response = b'HTTP/1.1 200 OK\n\n' + content
    except FileNotFoundError:
        response = b'HTTP/1.1 404 Not Found\n\nFile Not Found'

    client_socket.sendall(response)
    # time.sleep(10) #uncomment this for testing
    client_socket.close()

def run_server(port, concurrency_level):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', port))
    server_socket.listen(concurrency_level)

    thread_pool = []
    request_queue = Queue(concurrency_level)

    def worker():
        while True:
            client_socket = request_queue.get()
            handle_request(client_socket)
            request_queue.task_done()

    for _ in range(concurrency_level):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        thread_pool.append(t)

    print(f"Server listening on port {server_port} with concurrency level {concurrency_level}")

    while True:
        print('Waiting for connection...')
        client_socket, addr = server_socket.accept()
        print(f'Connection from {addr}')
        request_queue.put(client_socket)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage is: python server.py server_port concurrency_level")
        sys.exit(1)

    server_port = int(sys.argv[1])
    concurrency_level = int(sys.argv[2])

    run_server(server_port, concurrency_level)