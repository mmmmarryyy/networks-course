import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys

password = ''

def send_email(sender_email, receiver_email, subject, message, message_type='txt'):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    if message_type == 'txt':
        msg.attach(MIMEText(message, 'plain'))
    elif message_type == 'html':
        msg.attach(MIMEText(message, 'html'))

    with smtplib.SMTP('smtp.mail.ru', 587) as server:
        server.ehlo()
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)

if __name__ == "__main__":
    if (len(sys.argv[1:]) != 2):
        print(f"you provide {len(sys.argv[1:])} arguments, 2 expected (receiver_email, sender_password)")
        sys.exit(1)

    sender_email = 'barkovskaya.maria@mail.ru'
    receiver_email = sys.argv[1]
    password = sys.argv[2] #for mail it should be special password
    subject = 'Test Email'
    message_txt = 'Hello, this is a test email in plain text format.'
    message_html = '<h1>Hello</h1><p>This is a test email in HTML format.</p>'

    send_email(sender_email, receiver_email, subject, message_txt, 'txt')
    send_email(sender_email, receiver_email, subject, message_html, 'html')
