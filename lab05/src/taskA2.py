import socket
import base64
import ssl
import sys

sender_password=''

def send_email(sender_email, receiver_email, subject, message, message_type='text/plain'):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    smtp_server = 'smtp.mail.ru'
    port = 587
    client_socket.connect((smtp_server, port))
    response = client_socket.recv(1024)
    print(response.decode())

    username = sender_email.split('@', maxsplit=1)[0]

    client_socket.sendall(f'EHLO {username}\r\n'.encode())
    response = client_socket.recv(1024)
    print(response.decode())

    client_socket.sendall(b"STARTTLS\r\n")
    response = client_socket.recv(1024)
    print(response.decode())

    with ssl.wrap_socket(client_socket, ssl_version=ssl.PROTOCOL_SSLv23) as ssl_socket:
        ssl_socket.write(b"EHLO example.com\r\n")
        response = ssl_socket.read(1024)
        print(response.decode())
        
        ssl_socket.sendall(b'AUTH LOGIN\r\n')
        response = ssl_socket.recv(1024)
        print(response.decode())

        ssl_socket.sendall(base64.b64encode(sender_email.encode()) + b'\r\n')
        response = ssl_socket.recv(1024)
        print(response.decode())

        ssl_socket.sendall(base64.b64encode(sender_password.encode()) + b'\r\n')
        response = ssl_socket.recv(1024)
        print(response.decode())

        ssl_socket.sendall(f'MAIL FROM: <{sender_email}>\r\n'.encode())
        response = ssl_socket.recv(1024)
        print(response.decode())

        ssl_socket.sendall(f'RCPT TO: <{receiver_email}>\r\n'.encode())
        response = ssl_socket.recv(1024)
        print(response.decode())

        ssl_socket.sendall(b'DATA\r\n')
        response = ssl_socket.recv(1024)
        print(response.decode())

        message = f'From: {sender_email}\r\nTo: {receiver_email}\r\nSubject: {subject}\r\nContent-Type: {message_type}\r\n{message}'
        ssl_socket.sendall(message.encode())
        ssl_socket.sendall(b'\r\n.\r\n')
        response = ssl_socket.recv(1024)
        print(response.decode())

        ssl_socket.sendall(b'QUIT\r\n')
        response = ssl_socket.recv(1024)
        print(response.decode())

    client_socket.close()

    print('Email sent successfully!')

if __name__ == "__main__":
    if (len(sys.argv[1:]) != 2):
        print(f"you provide {len(sys.argv[1:])} arguments, 2 expected (receiver_email, sender_password)")
        sys.exit(1)

    sender_email = 'barkovskaya.maria@mail.ru'
    receiver_email = sys.argv[1]
    sender_password = sys.argv[2] #for mail it should be special password 
    subject = 'Test Email 2'
    message_txt = 'Hello, this is a test email in plain text format from a Python client from task 2.'
    message_html = '<h1>Hello</h1><p>This is a test email in HTML format from a Python client from task 2.</p>'

    send_email(sender_email, receiver_email, subject, message_txt, 'text/plain')
    send_email(sender_email, receiver_email, subject, message_html, 'text/html')
