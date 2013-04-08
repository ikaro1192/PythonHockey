import re
import sys
import json
import socket

import pygame
from pygame.locals import *

import mover

#Please set server IP adress
host = '127.0.0.1'
port = 3794
SCREEN_SIZE = (640, 480)
SCREEN_RECT = Rect(0, 0, 640, 480)




def update_pack(self):
    if self.PlayerID == 1:
        self.rect = pygame.Rect( self.data["PackPositionX"], self.data["PackPositionY"], self.rect.width, self.rect.height)
    else:
        self.rect = pygame.Rect( SCREEN_RECT.width -(self.rect.width + self.data["PackPositionX"]), self.data["PackPositionY"], self.rect.width, self.rect.height)


def update_player(self):
    self.rect = pygame.Rect( 0, self.data["MyPositionY"], self.rect.width, self.rect.height)
    pass

def update_enemy(self):
    self.rect = pygame.Rect(SCREEN_RECT.width - self.rect.width, self.data["EnemyPositionY"], self.rect.width, self.rect.height)
    pass


JsonData ='{"MyPositionY":100, "EnemyPositionY":300, "PackPositionX":0,"PackPositionY":200}'
mover.Mover.data = json.loads(JsonData)

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("waiting connection...")

    clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsock.connect((host,port))
    rcvmsg = clientsock.recv(1024)
    print rcvmsg 
    p = re.compile("Player\d")
    PlayerName = p.match(rcvmsg).group()
    pygame.display.set_caption("Python hockey "+PlayerName)

    PlayerID = 0
    if PlayerName == "Player1":
        PlayerID = 1
    else:
        PlayerID = 2

    #Load result picture
    LoseImg = pygame.image.load("lose.png").convert()
    WinImg = pygame.image.load("win.png").convert()

    #group settings
    group = pygame.sprite.RenderUpdates()
    mover.Mover.containers = group


    #create Pack
    PackImg = pygame.image.load("python.png").convert_alpha()
    width = PackImg.get_width()
    height = PackImg.get_height()
    PackRect = pygame.Rect((SCREEN_RECT.width - width)/2, (SCREEN_RECT.height - height)/2, width, height)
    Pack = mover.Mover(PackImg, PackRect, update_pack)
    Pack.PlayerID = PlayerID 
    Pack.vx = -1
    Pack.vy = 1


    #create Bar
    BarImg = pygame.image.load("bar.png").convert_alpha()
    width = BarImg.get_width()
    height = BarImg.get_height()

    PlayerRect = pygame.Rect(0, (SCREEN_RECT.height - height)/2, width, height)
    Player = mover.Mover(BarImg, PlayerRect, update_player)

    EnemyRect = pygame.Rect(SCREEN_RECT.width - width, (SCREEN_RECT.height - height)/2, width, height)
    Enemy = mover.Mover(BarImg, EnemyRect, update_enemy)

    fps = pygame.time.Clock()

    WinFlag = False

    while True:
        screen.fill((0, 0, 0))

        pressed_keys = pygame.key.get_pressed() 
        if pressed_keys[K_j]:
            clientsock.sendall('{"Move":3}')
        elif pressed_keys[K_k]:
            clientsock.sendall('{"Move":-3}')
        else:
            clientsock.sendall('{"Move":0}')


        #get data by server
        rcvmsg = clientsock.recv(1024)
        if rcvmsg.find("lose") != -1:
            WinFlag = False
            break
        elif rcvmsg.find("win") != -1:
            WinFlag = True
            break
        
        try:
            mover.Mover.data =json.loads(rcvmsg)
        except ValueError:
            print "ValueError" 
            print rcvmsg

        group.update()
        group.draw(screen)
        pygame.display.update()

        #control FPS
        fps.tick_busy_loop(60)


        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()

    while True:
        screen.fill((0, 0, 0))
        
        if WinFlag:
           screen.blit(WinImg, (120,0))
        else:
           screen.blit(LoseImg, (120,0))


        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()




if __name__ == "__main__":
    main()



