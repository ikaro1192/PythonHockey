import sys
import json
import math
import socket
import string
import random

import pygame
from pygame.locals import *

import mover

#Please set server IP adress
host = '127.0.0.1'
port = 3794
SCREEN_SIZE = (640, 480)
SCREEN_RECT = Rect(0, 0, 640, 480)




def limit(val, min_, max_):
    lst =[min_, val, max_]
    lst.sort()
    return lst[1]


def update_pack(self):
    self.rect.move_ip(self.vx, self.vy)
    if self.rect.top < 0 or self.rect.bottom > SCREEN_RECT.height:
        self.vy = -self.vy
    self.rect = self.rect.clamp(SCREEN_RECT)

def update_player(self):
    rcvmsg = self.socket.recv(1024)
    try:
        data =json.loads(rcvmsg)
        self.rect.move_ip(0,data["Move"])
    except ValueError:
        print "ValueError" 
        print rcvmsg


def send_position_data(receiver,enemy,Pack):
    JsonData = string.Template('{"MyPositionY":${MyPositionY}, "EnemyPositionY":${EnemyPositionY}, "PackPositionX":${PackPositionX},"PackPositionY":${PackPositionY}}')

    receiver.socket.sendall(
        JsonData.substitute(
                            MyPositionY = receiver.rect.top,
                            EnemyPositionY = enemy.rect.top,
                            PackPositionX = Pack.rect.left,
                            PackPositionY = Pack.rect.top
                           )
                      ) 

def check_gameover(Player1,Player2,Pack):
    if Pack.rect.left <= 0:
        Player1.socket.sendall("lose")
        Player2.socket.sendall("win")
        return True
        
    if Pack.rect.right >= SCREEN_RECT.width:
        Player1.socket.sendall("win")
        Player2.socket.sendall("lose")
        return True
    return False

def check_hit(Player1,Player2,Pack):
    if Pack.rect.colliderect(Player1.rect) or Pack.rect.colliderect(Player2.rect):
        v_range = range(3)
        Pack.vx = math.copysign(abs(Pack.vx)+random.choice(v_range),-Pack.vx)
        Pack.vx = limit(Pack.vx, -5, 5)

        v_range = range(-2,3)
        Pack.vy += random.choice(v_range)
        Pack.vy = limit(Pack.vy, -5, 5)



def main():
    pygame.init()

    #group settings
    group = mover.MoverRectGroup()


    #create Player
    width = 15
    height = 100

    Player1Rect = pygame.Rect(0, (SCREEN_RECT.height - height)/2, width, height)
    Player1 = mover.MoverRect(Player1Rect, update_player, group)

    Player2Rect = pygame.Rect(SCREEN_RECT.width - width, (SCREEN_RECT.height - height)/2, width, height)
    Player2 = mover.MoverRect(Player2Rect, update_player, group)


    #server settings
    serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversock.bind((host,port))
    serversock.listen(2)
    print 'Waiting for connections...'
    Player1.socket, client_address = serversock.accept()
    Player2.socket, client_address2 = serversock.accept()
    print "connected."

    Player1.socket.sendall("Player1") 
    Player2.socket.sendall("Player2") 


    #create Pack
    width = 42
    height = 42
    PackRect = pygame.Rect((SCREEN_RECT.width - width)/2, (SCREEN_RECT.height - height)/2, width, height)
    Pack = mover.MoverRect(PackRect, update_pack, group)

    v_range = filter(lambda x: x!=0, range(-2,3))
    Pack.vx = random.choice(v_range)
    v_range = range(-2,3)
    Pack.vy = random.choice(v_range)


    #main loop
    print "running server."
    while True:
        group.update()

        check_hit(Player1,Player2,Pack)

        if check_gameover(Player1,Player2,Pack):
            break

        send_position_data(Player1,Player2,Pack)
        send_position_data(Player2,Player1,Pack)

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()



if __name__ == "__main__":
    main()


