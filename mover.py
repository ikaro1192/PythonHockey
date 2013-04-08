
import pygame
import types 
from pygame.locals import *

class MoverRect(object):
    """this class is moving rect object.
    
       ex)Pack,Bar on server
    """
    def __init__(self, rect, update_method,group):
        self.rect =  rect
        self.update = types.MethodType(update_method, self, Mover)
        group.append(self)

class MoverRectGroup(object):
    def __init__(self):
        self._MemberList = []

    def append(self, mover):
        self._MemberList.append(mover)

    def update(self):
        for mover in self._MemberList:
            mover.update()


class Mover(pygame.sprite.Sprite):
    """this class is object whitch move on windows.
    
       ex)Pack,Bar 
    """
    def __init__(self, image, rect, update_method):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image
        self.rect =  rect
        self.update = types.MethodType(update_method, self, Mover)


