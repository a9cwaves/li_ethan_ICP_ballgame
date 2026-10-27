import pygame as pg
from pygame.sprite import Sprite
from settings import *
from utils import *

from random import randint

from os import path

vec = pg.math.Vector2

def collide_hit_rect(one,two):
    return one.hit_rect.colliderect(two.rect)

def collide_with_walls(sprite, group, dir):
    #check for x collision
    if dir == 'x':
        #checking to see if we've collided with hitrects
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            #checks to see if we're to the left of the wall
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                #reposition the player (sprite) to the left side of the wall
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            #chekcs to see if we're to the right of the wall
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                #reposition the player to the right of the wall
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        #checking to see if we've collided with hitrects
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            #checks to see if we're above the wall
            if hits[0].rect.centery > sprite.hit_rect.centery:
                #reposition player to the top of the wall
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            #checks to see if we're below the wall
            if hits[0].rect.centery < sprite.hit_rect.centery:
                #reposition player to the bottom of the wall
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y
        



class Player(Sprite):
    def __init__(self, game, x, y): #initializes only once
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.spritesheet = Spritesheet(path.join(self.game.image_dir, "sprite_sheet.png"))
        self.load_images()
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(0,0,TILESIZE,TILESIZE)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT
        self.vel = vec(0,0)
        self.pos = vec(x*TILESIZE,y*TILESIZE)
        self.coins = 0
        #animation stuff
        self.last_update = 0
        self.current_frame = 0

    def get_keys(self):
        self.vel = vec(0,0)
        keys = pg.key.get_pressed() #boolean value returned if keyboard pressed
        if keys[pg.K_LEFT] or keys[pg.K_a]: #if these keys are pressed
            self.vel.x = -PLAYER_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vel.x = PLAYER_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel.y = -PLAYER_SPEED
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel.y = PLAYER_SPEED
        #check to see if player is moving diagonal
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071
    def animate(self):
        # use the time element to get now
        now = pg.time.get_ticks()
        if now - self.last_update > 500: #if the difference of the current frame and last frame > than 500 ms
            self.last_update = now #make the last frame the current frame
            self.current_frame = (self.current_frame + 1) % len(self.idle_frames) #updates to next frame
            bottom = self.rect.bottom 
            self.image = self.idle_frames[self.current_frame] #updates on to image
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
    def load_images(self):
        #coordinates for the spritesheet, 2 ide frames
        self.idle_frames = [self.spritesheet.get_image(0,0,TILESIZE, TILESIZE),
                            self.spritesheet.get_image(TILESIZE,0,TILESIZE, TILESIZE)]
        # self.run_frames = [self.spritesheet.get_image(0,0,TILESIZE, TILESIZE),
        #                     self.spritesheet.get_image(TILESIZE,0,TILESIZE, TILESIZE)]
        
    def update(self):
        self.get_keys() #senses when keys are pressed
        hits = pg.sprite.spritecollide(self,self.game.all_coins, True)
        if hits:
            for i in range(10):
                Particle(self.game, hits[0].pos.x, hits[0].pos.y) #generates particles once coin is hit
            self.coins  += 1
            self.game.pickup_snd.play()
            self.game.score += 1
        self.animate() #calls the function
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt # d = v * t
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x') # x axis collision test
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y') # y axis collision test
        self.rect.center = self.hit_rect.center
        

class Wall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.spritesheet = Spritesheet(path.join(self.game.image_dir, "sprite_sheet.png"))
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(0,TILESIZE*2,TILESIZE,TILESIZE)
        self.rect = self.image.get_rect()
        self.x = x*TILESIZE
        self.y = y*TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y

class Particle(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_particles
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE/8, TILESIZE/8))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.vel = vec(randint(-180,180),randint(-180,180)) #gives random velocity in x and y direction
        self.pos = vec(x,y) #starting position
        self.speed = randint(1,3) #random speed
        self.countdown = Cooldown() #creates the cooldown object so we can use it
        self.countdown.event_time = floor(pg.time.get_ticks()/1000) #countdown starts as soon as it is created
        # print(self.rect.x)
        # print(self.rect.y)
        # print(str(len(self.game.all_particles)))
        
    def update(self):
        self.countdown.ticking() #once generated, starts ticking

        self.pos += self.vel * self.speed * self.game.dt #updates the position, mutiples to calculate the movement
        # countdowns for two seconds, then makes them disappears
        if self.countdown.delta > 2: 
            self.kill()
        #updates particle position on screen
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y


class Mob(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)
        self.game = game
        self.spritesheet = Spritesheet(path.join(self.game.image_dir, "sprite_sheet.png")) #connects the image to spritesheet
        self.load_images()
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(0,0,TILESIZE,TILESIZE)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.speed = 100
        self.vel = vec(0,0)
        self.pos = vec(x*TILESIZE,y*TILESIZE)
        self.x = x*TILESIZE
        self.y = y*TILESIZE
        self.dir = "none"
        self.rect.x = self.x
        self.rect.y = self.y
        self.hit_rect = MOB_HIT_RECT
        #animation stuff
        self.last_update = 0
        self.current_frame = 0

    
    #copied animation from player
    def animate(self):
            # use the time element to get now
            now = pg.time.get_ticks()
            if now - self.last_update > 500: #if the difference of the current frame and last frame > than 500 ms
                self.last_update = now #make the last frame the current frame
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames) #updates to next frame
                bottom = self.rect.bottom 
                self.image = self.idle_frames[self.current_frame] #updates on to image
                self.image.set_colorkey(BLACK)
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
    def load_images(self):
        #2 ide frames for mob
        self.idle_frames = [self.spritesheet.get_image(0,TILESIZE,TILESIZE, TILESIZE),
                            self.spritesheet.get_image(TILESIZE,TILESIZE,TILESIZE, TILESIZE)]
        # self.run_frames = [self.spritesheet.get_image(0,0,TILESIZE, TILESIZE),
        #                     self.spritesheet.get_image(TILESIZE,0,TILESIZE, TILESIZE)]

    #uses autocomplete by creating a hcase method using pos vectors and obj as a parameter
    def chase(self, obj):
        if self.pos.x < obj.pos.x:
            self.vel.x = self.speed
            self.dir = "right"
        elif self.pos.x > obj.pos.x:
            self.vel.x = -self.speed
            self.dir = "left"
        else:
            self.vel.x = 0

        if self.pos.y < obj.pos.y:
            self.vel.y = self.speed
        elif self.pos.y > obj.pos.y:
            self.vel.y = -self.speed
        else:
            self.vel.y = 0

    def update(self):
        self.animate()
        self.chase(self.game.player)
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt #updates position by mutiplying time and velocity
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x') # x axis collision test
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y') # y axis collision test
        self.rect.center = self.hit_rect.center

class Coin(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_coins
        Sprite.__init__(self, self.groups)
        self.game = game
        self.spritesheet = Spritesheet(path.join(self.game.image_dir, "sprite_sheet.png"))
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(TILESIZE,TILESIZE*2,TILESIZE,TILESIZE)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        # self.x = x*TILESIZE
        # self.y = y*TILESIZE
        self.pos = vec(x*TILESIZE,y*TILESIZE)
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
    def update(self):
        pass

class PowerUp(Sprite):
    def __init__(self, game, x, y):
            self.groups = game.all_sprites, game.all_powerups
            Sprite.__init__(self, self.groups)
            self.game = game
            self.spritesheet = Spritesheet(path.join(self.game.image_dir, "sprite_sheet.png"))
            self.image = pg.Surface((TILESIZE, TILESIZE))
            self.image = self.spritesheet.get_image(0,TILESIZE*3,TILESIZE,TILESIZE)
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.x = x*TILESIZE
            self.y = y*TILESIZE
            self.rect.x = self.x
            self.rect.y = self.y
    def update(self):
        pass