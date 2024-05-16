import socket
import pygame

HOST = '127.0.0.1' 
PORT = 65432 

pygame.init()

width = 600
height = 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Paint client")

drawing = False
last_pos = (-1, -1)
color = (255, 255, 255)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                s.sendall("mousedown".encode('utf-8'))
            if event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                s.sendall("mouseup".encode('utf-8'))
                last_pos = (-1, -1)
            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    pos = pygame.mouse.get_pos()
                    s.sendall(f"{pos[0]},{pos[1]}".encode('utf-8'))
                    if last_pos != (-1, -1):
                        pygame.draw.line(screen, color, last_pos, pos, 2)
                    last_pos = pos
                
        pygame.display.update()