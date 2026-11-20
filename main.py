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

GOALS: turn on the power of the station, buy the tickets, find food, find the right entrance, go down to the train,
enter train before time runs out

RULES: Player fails if they do not enter train before timer runs out, cannot go out of map, must complete all missions before entering

FEEDBACK: a simple inventory that tracks the item player collects, sound played when player interacts with items
train coming in has a sound, announcement plays when timer is almost over (signalling that the train will depart soon)

'''

class Game: #initialize class Game
    def __init__(self):
        pg.init() #initializing pygame
        pg.mixer.init() #initialize pygame sound
        self.screen = pg.display.set_mode((WIDTH, HEIGHT)) #setting the screen size from settings.py
        print("game initialized...")
        self.load_data("level1.txt") #starting level
        pg.display.set_caption(TITLE) #title of window
        self.running = True
        self.playing = True
        self.clock = pg.time.Clock()
        self.high_score = 0
        self.score = 0
        self.level = 1 #starting at levl1
        self.transitioning = False #whether if player is switching floors or not

    def load_data(self,map):
        print("load_data ran", flush=True) #debug
        self.game_dir = path.dirname(path.abspath(__file__)) #adjusted using gpt        
        self.image_dir = path.join(self.game_dir,'images')
        print(path.join(self.image_dir, "sprite_sheet.png")) #test
        print(path.exists(path.join(self.image_dir, "sprite_sheet.png"))) #debugging test
        self.game_Save_file = path.join(self.game_dir, "highscore.txt") 
        #sound handling
        self.snd_dir = path.join(self.game_dir,'audio')
        self.pickup_snd = pg.mixer.Sound(path.join(self.snd_dir, "pickup.mp3"))
        self.map = Map(path.join(self.game_dir, map))

        try:
            with open(self.game_Save_file, 'x', encoding="utf-8") as file: #creates new save fle
                file.write("hello world")
            print("file created successfully") #test
        except FileExistsError: #if it already exists, prevents error from stopping program
            print("File already exists")

        with open(self.game_Save_file, 'r') as file: #opens save file to read
            try:
                self.high_score = int(file.read()) #type casting, converts file content to integer
            except:
                # self.high_score = 0
                print("high score not read")

    def new(self):
        self.map = Map(f"level{self.level}.txt") #will be both 1 and 2
        self.camera = Camera(self.map.width, self.map.height)
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group() #includes walls + benches
        self.all_stairs = pg.sprite.Group()
        self.all_stairs1 = pg.sprite.Group()
        self.all_stairs2 = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()
        self.all_coins = pg.sprite.Group()
        self.all_powerups = pg.sprite.Group()
        self.all_particles = pg.sprite.Group()

        for row, tiles in enumerate(self.map.data): #look into level 1 text
            for col, tile, in enumerate(tiles): #check each of the tiles
                if tile == ('1'): # wall variable
                    Wall(self,col,row) #instantiate at that point
                if tile == 'M': #mob
                    Mob(self,col,row)
                if tile == 'C': #coin
                    Coin(self,col,row)
                if tile == '3': #stairs
                    Stair1(self,col,row)
                if tile == '5':
                    Stair2(self,col,row)
                if tile == 'd':
                    LBench(self,col,row)
                if tile == 'b':
                    RBench(self,col,row)
                if tile == '0':
                    Stair0(self,col,row)
                if tile == '9':
                    Stair9(self,col,row)
        for row, tiles in enumerate(self.map.data): #same thing but for player
            for col, tile, in enumerate(tiles):
                if tile == 'P':
                    self.player = Player(self,col,row)

    def run(self):
        self.playing = True
        while self.playing: #always be True until exits game
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update() #updates sprite
            self.draw() #draws background color

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: #quits
                if self.score > self.high_score: #makes sure it doesn't reset to a lower high score
                    with open(path.join(self.game_dir, self.game_Save_file), 'w') as f: #creates the new file, writes in it
                        f.write(str(self.score)) #writes score file
                if self.playing:
                    self.playing = False
                self.running = False

    def draw_text(self,text,size,color,x,y):
        font_name = pg.font.match_font('arial') #assigns arial font to font_name
        font = pg.font.Font(font_name, size) #sets the font with size and type from line above
        text_surface = font.render(text, True, color) #calculates the text
        text_rect = text_surface.get_rect() 
        text_rect.midtop = (x,y) #position on screen
        self.screen.blit(text_surface, text_rect)

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player) #make it stay centered on the player
        #respawns the mob once there are no mobs left
        # if len(self.all_mobs) < 1:
        #     print("no more mobs")
        #     self.mob = Mob(self,0,0)

    def draw(self):
        #order matters: first things are on the bottom because they are the first to be drawn
        #the last lines in this method are drawn on top or last
        self.screen.fill(BGCOLOR) #background color
        for sprite in self.all_sprites: 
            #adjust position of sprite the pos in the game world using the camera offset
            #used chatgpt to help me solve the issue, the previous line would not work, had to use blit
            self.screen.blit(sprite.image, self.camera.apply(sprite)) #draws each sprite in the screen based on camera (first parameter is image, second is position)
        self.draw_text(f"Frames per second: " + str(floor(1/self.dt)), 24, WHITE, WIDTH/2, HEIGHT/4 - 100)
        # self.draw_text(f"Coins: " + str(self.player.coins), 24, WHITE, WIDTH/2, HEIGHT/7 + 10)
        # self.draw_text(f"Score: " + str(self.score), 24, WHITE, WIDTH/2, HEIGHT/4 + 40)
        # self.draw_text(f"High Score: " + str(self.high_score), 24, WHITE, WIDTH/2, HEIGHT/12)
        pg.display.flip()

    def change_level(self,level): #changes between level1 and level2
        if level == self.level: #checks if game is already on that level
            return #stop
        self.level = level #assigns the new level -> used in new function to load the level
        self.new()

if __name__ == "__main__":
    g = Game()

while g.running: #keeps window opening forever
    g.new()
    g.run()