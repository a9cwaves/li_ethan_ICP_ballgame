import pygame as pg
from settings import *
from math import floor

class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE
        print("map instantiated")

class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert() #loading an image, converting png to something pygame can use

    def get_image(self,x,y,width,height):
        image = pg.Surface((width,height))
        image.blit(self.spritesheet, (0,0), (x,y,width,height)) #extracts the specific image we want from spritesheet
        new_image = pg.transform.scale(image, (width,height))
        image = new_image
        return image

class Timer:
    def __init__(self):
        #converts ms to s, rounds to nearest whole #
        self.event_time = floor((pg.time.get_ticks())/1000)
    def get_delta(self):
        #returns difference in time (s) from time of instantiation to now
        return floor((pg.time.get_ticks())/1000) - self.event_time

class Camera:
    def __init__(self,width,height):
        self.camera = pg.Rect(0,0,width,height)

    def apply(self,sprite): #changes the pos of where the sprites get drawn on screen
        # take original position of sprite and add the camera offset to make sidescroller effect
        screen_x = sprite.rect.x + self.camera.x
        screen_y = sprite.rect.y + self.camera.y
        return screen_x, screen_y #final screen coords
    
    def update(self,player):
        #subtracts the difference between the distance between the center of player to the side of screen in x & y
        #this moves the camera so that the player will always be at the center of the screen
        x = -player.rect.centerx + WIDTH // 2
        y = -player.rect.centery + HEIGHT // 2

        self.camera.topleft = (x, y)






