#This file was created by Ethan Li
#Code inspired by game dev Chris Brafield who was inspired by Notch

import pygame as pg #makes typing pygame shorter (pg)
from os import path
from settings import * #imports everything form settings.py
from sprites import * #imports everything from sprites.py
from utils import *

'''
Input (events): keyboard, mouse, right click, voice, 
power button, eye tracking, camera, gyroscoping, electrostatic, location, volume,
microphone - zelda game where you blow out a candle with the mic

Process: cursor position, position of player, score, enemy position, velocity,
aim in fps

Output: graphics - things are drawn, sound: jump, power up, footsteps, haptics,

'''

class Game: #initialize class Game
    def __init__(self):
        pg.init() #initializing pygame
        pg.mixer.init() #initialize pygame sound
        self.screen = pg.display.set_mode((WIDTH, HEIGHT)) #setting the screen size from settings.py
        print("game initialized...")
        pg.display.set_caption(TITLE) #title of window
        self.running = True
        self.playing = True
        self.clock = pg.time.Clock()

    def load_data(self,map):
        self.game_dir = path.dirname(__file__)
        self.image_dir = path.join(self.game_dir,'images')
        self.snd_dir = path.join(self.game_dir,'audio')
        self.map = Map(path.join(self.game_dir, map))

    def new(self):
        self.load_data('level1.txt')
        print(self.map.data)
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()

        for row, tiles in enumerate(self.map.data): #look into level 1 text
            for col, tile, in enumerate(tiles): #check each of the tiles
                if tile == '1': # wall variable
                    Wall(self,col,row) #instantiate at that point
                if tile == 'M': #mob
                    Mob(self,col,row)
        for row, tiles in enumerate(self.map.data): #same thing but for player
            for col, tile, in enumerate(tiles):
                if tile == 'P':
                    Player(self,col,row)

    def run(self):
        self.playing = True
        while self.playing: #always be True until exits game
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update() #updates sprite
            self.draw() #draws background color

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: #changes self.running to false, quitting the game when closing window
                if self.playing:
                    self.playing = False
                self.running = False    

    def update(self):
        self.all_sprites.update()
        #respawns the mob once there are not mobs left
        # if len(self.all_mobs) < 1:
        #     print("no more mobs")
        #     self.mob = Mob(self,0,0)

    def draw(self):
        self.screen.fill(BGCOLOR) #fills screen with BGCOLOR from settings
        self.all_sprites.draw(self.screen) #everything will be draw on screen
        pg.display.flip()

if __name__ == "__main__":
    g = Game()

while g.running: #keeps window opening forever
    g.new()
    g.run()