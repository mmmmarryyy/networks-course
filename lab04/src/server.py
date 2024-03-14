import json
import socket
import requests
import sys
import os
    
def bad_request_response():
    return b'HTTP/1.1 400 Bad Request\r\n\r\n'

def not_found_response():
    return b'HTTP/1.1 404 Not Found\r\n\r\n'

def ok_response(content):
    return bytes(f'HTTP/1.1 200 OK\r\nContent-Length: {len(content)}\r\n\r\n{content}', 'utf-8')

def not_modified_response(last_modified, etag):
    return bytes(f'HTTP/1.1 304 Not Modified\r\nLast-Modified: {last_modified}\r\nETag: {etag}\r\n\r\n', 'utf-8')

enable_cache = False
enable_blacklist = False

blacklist = list()
cache_metadata = {}

def is_banned(url):
    for banned_url in blacklist:
        if url in banned_url or banned_url in url:
            return True
    return False

def is_cached(url):
    return url in cache_metadata

def get_last_modified(url):
    return cache_metadata.get(url, {}).get('last_modified')

def get_etag(url):
    return cache_metadata.get(url, {}).get('etag')

def log(string):
    print(string)
    with open("proxy_log.txt", "a") as log_file:
        log_file.write(string + "\n")

def proxy_server(port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', port))
        server_socket.listen(5)
        log(f"Proxy server is running on port {port}")

        while True:
            log("\n")
            log("waiting for conneciton...")
            client_socket, _ = server_socket.accept()

            try:
                batch_size = 4096
                result = []
                while True:
                    batch = client_socket.recv(batch_size)
                    result.extend(batch)
                    if len(batch) < batch_size:
                        break
                request = bytes(result).decode()
            except Exception as e:
                log(f"Error reading request: {e}")
                client_socket.close()
                continue

            try:
                method = request.split()[0]
                old_url = request.split()[1][1:]

                referer_line = [line for line in request.split('\n') if 'Referer' in line]
                if referer_line:
                    referer_value = referer_line[0].split(': ')[1].split('\n')[0][22:-1]
                    if 'http://' not in referer_value and 'https://' not in referer_value:
                        referer_value = 'http://' + referer_value

                    while (referer_value[-1] == '/'):
                        referer_value = referer_value[:-1]
                    log(f"referer_value: {referer_value}")

                    url = "{}/{}".format(referer_value, old_url)
                else:
                    if 'http://' not in old_url and 'https://' not in old_url:
                        url = 'http://' + old_url
                    else:
                        url = old_url

                log(f"{method} request for url: {url}")

                if is_banned(old_url):
                    log(f"Requested url {old_url} is banned")
                    client_socket.sendall(ok_response('Requested URL is blacklisted'))
                    client_socket.close()
                    continue

                if method == 'GET':
                    if enable_cache and is_cached(url):
                        last_modified = get_last_modified(url)
                        etag = get_etag(url)
                        headers = {'If-Modified-Since': last_modified, 'If-None-Match': etag}
                        response = requests.get(url, headers=headers)
                        if response.status_code == 304:
                            log(f"Get content from cache, cause get 304 request status code")
                            with open(f'cache/{url.replace("/", "_")}', 'r') as file:
                                content = file.read()
                                client_socket.sendall(ok_response(content))
                            client_socket.close()   
                            continue
                        elif response.status_code == 200:
                            cache_metadata[url] = {'last_modified': response.headers.get('Last-Modified'), 'etag': response.headers.get('ETag')}
                            if (response.encoding == None):
                                content = response.content
                                with open(f'cache/{url.replace("/", "_")}', 'b') as file:
                                    file.write(content)
                            else:
                                content = response.content.decode()
                                with open(f'cache/{url.replace("/", "_")}', 'w') as file:
                                    file.write(content)

                    else:
                        response = requests.get(url)
                        if enable_cache and response.status_code == 200:
                            cache_metadata[url] = {'last_modified': response.headers.get('Last-Modified'), 'etag': response.headers.get('ETag')}
                            if (response.encoding == None):
                                content = response.content
                                with open(f'cache/{url.replace("/", "_")}', 'b') as file:
                                    file.write(content)
                            else:
                                content = response.content.decode()
                                with open(f'cache/{url.replace("/", "_")}', 'w') as file:
                                    file.write(content)

                elif method == 'POST':
                    data = request.split('\r\n\r\n', 1)[1]
                    log(f"data for POST method = {data}")
                    response = requests.post(url, data=data)

                log(f"Got response code {response.status_code} for url: {url}")

                if (response.status_code == 404):
                    client_socket.sendall(not_found_response())
                elif (response.encoding == None):
                    client_socket.sendall(ok_response(response.content))
                else:
                    client_socket.sendall(ok_response(response.content.decode()))
                client_socket.close()
            except Exception as e:
                log(f"Bad request ends with error: {e}")
                client_socket.sendall(bad_request_response())
                client_socket.close()
                continue
    except Exception as e:
        log(f"An error occurred: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    log("\n------------------------------------------------------------------------")
    log(f"START SERVER")
    log(f"------------------------------------------------------------------------")
    if (len(sys.argv[1:]) != 3):
        log(f"you provide {len(sys.argv[1:])} arguments, 3 expected (port, enable_cache, enable_blacklist)")
        sys.exit(1)

    port = int(sys.argv[1])
    if sys.argv[2].lower() == 'true':
        enable_cache = True
    if sys.argv[3].lower() == 'true':
        enable_blacklist = True
    log(f"Configuration: enable_cache = {enable_cache}, enable_blacklist = {enable_blacklist}")

    if enable_blacklist:
        with open("blacklist.json", 'r') as file:
            blacklist = json.load(file)['blacklist']
        log(f"BLACKLIST: {blacklist}")

    try:
        proxy_server(port)
    finally:
        print("clear cache folder")
        if os.path.exists('cache/'):
            # Delete all files in the cache folder
            for file_name in os.listdir('cache/'):
                file_path = os.path.join('cache/', file_name)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
