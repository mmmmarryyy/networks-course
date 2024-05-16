import socket
import pygame

HOST = '127.0.0.1'
PORT = 65432

pygame.init()

width = 600
height = 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Paint server")

drawing = False
last_pos = (-1, -1)
color = (255, 255, 255)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    
    pygame.display.update()
    conn, addr = s.accept()
    pygame.display.update()
    with conn:
        print(f"Client connected: {addr}")
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                print(data)
                break
            
            try:
                x, y = map(int, data.split(','))
                if drawing and last_pos != (-1, -1):
                    pygame.draw.line(screen, color, last_pos, (x, y), 2)
                last_pos = (x, y)
            except:
                if data == "mousedown":
                    drawing = True
                elif data == "mouseup":
                    drawing = False
                    last_pos = (-1, -1)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
