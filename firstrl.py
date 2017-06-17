# -*- coding: utf-8 -*-
"""
Created on Sat Jun 17 14:32:46 2017

@author: crule
"""

#Imports
import libtcodpy as libtcod

#Finals
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

MAP_WIDTH = 80
MAP_HEIGHT = 45

color_dark_wall = libtcod.Color(0,0,100)
color_dark_ground = libtcod.Color(50,50,150)


#Set fonts
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

#Initialize window
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)

#Create a new console 
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)


#Set FPS limit
libtcod.sys_set_fps(LIMIT_FPS)

#Variables in main loop
playerx = SCREEN_WIDTH/2
playery = SCREEN_HEIGHT/2


#############################################
# Classes
#############################################

"""
A general purpose object that contains functions for: move, draw and clear.
Takes as input (x, y, char, color)
"""
class Object:
    def __init__(self,x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        
    def move(self,dx,dy):
        if not map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy
    
    def draw(self):
        #set the color and then draw the character that represents this object at its position
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
    
    def clear(self):
        libtcod.console_put_char(con,self.x,self.y, ' ', libtcod.BKGND_NONE)


class Tile:
    def __init__(self,blocked,block_sight = None):
        self.blocked = blocked
        
        #If a tile is blocked it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

#############################################
# Functions
#############################################

def make_map():
    global map
    
    #fill map with "unblocked" tiles
    map = [[ Tile(False)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]
            
    map[30][22].blocked = True
    map[30][22].block_sight = True
    map[50][22].blocked = True
    map[50][22].block_sight = True


def handle_keys():
    global playerx,playery
    
    #Handle misc. keys
    key = libtcod.console_check_for_keypress()
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt + enter -> full screen mode
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return True #Exit the game.
    
    #movement keys
    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        player.move(0,-1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        player.move(0,1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        player.move(-1,0)
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        player.move(1,0)
        
        
def render_all():
    global color_light_wall
    global color_light_ground
    
    #go through all tiles, and set their background color
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = map[x][y].block_sight
            if wall:
                libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET )
            else:
                libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET )


    for object in objects:
        object.draw()
        
        
    #Do some blitting
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
        
        

#############################################
# Initialization & Main Loop
#############################################

#Initialize objects
player = Object(SCREEN_HEIGHT/2,SCREEN_WIDTH/2, '@', libtcod.white)
npc = Object(SCREEN_HEIGHT/2 - 5,SCREEN_WIDTH/2 - 5, 'X', libtcod.yellow)
objects = [npc, player]
make_map()



#Game main loop
while not libtcod.console_is_window_closed():
    
    #Draw all objects in the list
    render_all()
    
    
    libtcod.console_flush()
    
    #This flushes the screen
    for object in objects:
        object.clear()
    
    
    exit = handle_keys()
    if exit:
        break
    

