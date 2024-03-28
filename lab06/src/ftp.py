import socket
import sys
import os

def receive_data(sock):
    data = b""
    while True:
        part = sock.recv(1024)
        data += part
        if len(part) < 1024:
            break
    return data

def list_files(sock, data_sock):
    print("LIST COMMAND")
    sock.sendall(b"LIST\r\n")

    data = receive_data(data_sock)
    print(data.decode())
    print("_____________________________________")
    data = receive_data(sock)
    print(data.decode())
    print("_____________________________________")
    print("LIST COMMAND END")
    print()

def upload_file(sock, data_sock, filename):
    print("STOR COMMAND")
    with open(filename, "rb") as file:
        command = b"STOR " + bytes(filename, "utf-8") + b"\r\n"
        sock.sendall(command)
        file_data = file.read()
        data_sock.sendall(file_data)
        data = receive_data(sock)
        print(data.decode())
        print("_____________________________________")
        print("STOR COMMAND END")
        print()

def download_file(sock, data_sock, filename, response_filename):
    print("RETR COMMAND")
    command = b"RETR " + bytes(filename, "utf-8") + b"\r\n"
    sock.sendall(command)
    data = receive_data(sock)
    print(data)
    print("_____________________________________")
    data = receive_data(data_sock)
    print(data.decode())
    print("_____________________________________")
    with open(response_filename, "wb") as file2:
        file2.write(data)
    print("RETR COMMAND END")
    print()
        

def main(command: str, filename, response_filename):
    server_address = ('ftp.dlptest.com', 21)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(server_address)
        data = receive_data(sock)
        print(data.decode())

        username = "dlpuser"
        password = "rNrKYTX9g7z3RgJRmxWuGHbeu"
        print("USER")
        sock.sendall(b"USER " + bytes(username, "utf-8") + b"\r\n")
        data = receive_data(sock)
        print(data.decode())

        print("Password")
        sock.sendall(b"PASS " + bytes(password, "utf-8") + b"\r\n")

        data = receive_data(sock)
        print(data.decode())

        print("PASV")
        sock.sendall(b"PASV\r\n")
        response = receive_data(sock)
        print(response.decode())

        start = response.decode().find("(") + 1
        end = response.decode().find(")")
        data = response.decode()[start:end].split(",")
        datahost = ".".join(data[:4])
        dataport = int(data[4]) * 256 + int(data[5])

        print(datahost, dataport)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as data_sock:
            data_sock.connect((datahost, dataport))

            if (command == "ls"):
                list_files(sock, data_sock)
            elif (command == "upload"):
                upload_file(sock, data_sock, filename)
            elif (command == "download"):
                download_file(sock, data_sock, filename, response_filename)
            else:
                print("WRONG COMMMAND")
            data_sock.close()
            response = receive_data(sock)
            print(response.decode())
        sock.close()

if __name__ == "__main__":
    # ls: python3 ftp.py ls
    # upload: python3 ftp.py upload example.txt
    # download: python3 ftp.py download example.txt example-response.txt

    receive_filename = ""
    filename = ""
    if (len(sys.argv[1:]) < 1):
        print(f"you provide {len(sys.argv[1:])} arguments, at least 1 expected (command, filename, receive_filename)")
        sys.exit(1)
    else:
        command = sys.argv[1]
        if (command == "download" or command == "upload"):
            if (len(sys.argv[1:]) < 2):
                print(f"you provide {len(sys.argv[1:])} arguments, at least 2 expected (command, filename, receive_filename)")
                sys.exit(1)
            filename = sys.argv[2]
            if (command == "download"):
                if (len(sys.argv[1:]) < 3):
                    print(f"you provide {len(sys.argv[1:])} arguments, at least 2 expected (command, filename, receive_filename)")
                    sys.exit(1)
                receive_filename = sys.argv[3]

    main(command, filename, receive_filename)