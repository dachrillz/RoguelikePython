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

ROOM_MAX_SIZE = 20
ROOM_MIN_SIZE = 5
MAX_ROOMS = 100

FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

MAX_ROOM_MONSTER = 3

color_dark_wall = libtcod.Color(0,0,100)
color_light_wall = libtcod.Color(130,110,50)
color_dark_ground = libtcod.Color(50,50,150)
color_light_ground = libtcod.Color(200,180,50)


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
    def __init__(self,x, y, char, name, color, blocks = False):
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        
    def move(self,dx,dy):
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
    
    def draw(self):
    
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            #set the color and then draw the character that represents this object at its position
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
    
    def clear(self):
        libtcod.console_put_char(con,self.x,self.y, ' ', libtcod.BKGND_NONE)


class Tile:
    def __init__(self,blocked,block_sight = None):
        self.blocked = blocked
        
        self.explored = False
        
        #If a tile is blocked it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
        
class Rect:
    #Rectangle used on map to define room
    def __init__(self,x,y,w,h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return(center_x,center_y)
        
        
    def intersect(self, other):
        #returns true if it intersects with other
        return(self.x1 <= other.x2 and self.x2 >= other.x1 and
               self.y1 <= other.y2 and self.y2 >= other.y2)

#############################################
# Functions
#############################################

def make_map():
    global map
    
    #fill map with "unblocked" tiles
    map = [[ Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]
            
    
    rooms = []
    num_rooms = 0
    
    for r in range(MAX_ROOMS):
        #random width and height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE,ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE,ROOM_MAX_SIZE)
        
        #random positions
        x = libtcod.random_get_int(0, 0 , MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0 , MAP_HEIGHT - h - 1)
        
        new_room = Rect(x, y, w, h)
        
        #check if it overlaps with other rooms.
        
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break
                
                
        if not failed:
            create_room(new_room)
            
            (new_x, new_y) = new_room.center()
            
            if num_rooms == 0:
            
                player.x = new_x
                player.y = new_y
                
            else: 
                (prev_x, prev_y) = rooms[num_rooms-1].center()
                
                if libtcod.random_get_int(0, 0, 1) == 1:
                    create_h_tunnel(prev_x,new_x,prev_y)
                    create_v_tunnel(prev_y,new_y,new_x)
                else:
                    create_v_tunnel(prev_y,new_y,prev_x)
                    create_h_tunnel(prev_x,new_x,new_y)
            
            #Create monster in room
            place_objects(new_room)
            
            rooms.append(new_room)
            num_rooms += 1
    
def create_room(room):
    global map
    
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False


def handle_keys():
    global fov_recompute
    global game_state
    
    #Handle misc. keys
    key = libtcod.console_check_for_keypress()
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt + enter -> full screen mode
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit' #Exit the game.
        
        

    
    #movement keys
    
    if game_state == 'playing':
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            player_move_or_attack(0,-1)
        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            player_move_or_attack(0,1)
        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            player_move_or_attack(-1,0)
        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            player_move_or_attack(1,0)
            
        else:
            return 'didnt-take-turn'
 
def create_h_tunnel(x1,x2,y):
    global map
    for x in range(min(x1,x2),max(x1,x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
      
     
def create_v_tunnel(x1,x2,x):
    global map
    for y in range(min(x1,x2),max(x1,x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
        
def place_objects(room):
    #Choose random number of monster
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTER)
    
    for i in range(num_monsters):
        x = libtcod.random_get_int(0, room.x1, room.x2)
        y = libtcod.random_get_int(0, room.y1, room.y2)
        
        if not is_blocked(x,y):
        
            if libtcod.random_get_int(0, 0, 100) < 80:
                monster = Object(x,y, 'O','orc', libtcod.desaturated_green,blocks = True)
            else:
                monster = Object(x,y, 'T','troll', libtcod.darker_green,blocks = True)
                
            objects.append(monster)
 
def is_blocked(x, y):
    #First test the map tile
    if map[x][y].blocked:
        return True
        
    #Check for blocking object
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True
            
            
    return False
    
def player_move_or_attack(dx,dy):
    global fov_recompute
    
    #Coodinates
    x = player.x + dx
    y = player.y + dy
    
    #Find attackable target
    target = None
    for object in objects:
        if object.x == x and object.y == y:
            target = object
            break
           
    if target is not None:
        print 'The ' + target.name + ' laughs at your attack!'
    else:
        player.move(dx,dy)
        fov_recompute = True


 
def render_all():
    global color_light_wall, color_dark_ground
    global color_light_ground, color_dark_ground
    global fov_recompute
    
    if fov_recompute:
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x,player.y,TORCH_RADIUS,FOV_LIGHT_WALLS,FOV_ALGO)
    
    #go through all tiles, and set their background color
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map,x,y)
                wall = map[x][y].block_sight
                
                if not visible:
                    if map[x][y].explored:
                        if wall:
                            libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET )
                        else:
                            libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET )
                    
                else:
                    if wall:
                        libtcod.console_set_char_background(con, x, y, color_light_wall, libtcod.BKGND_SET )
                    else:
                        libtcod.console_set_char_background(con, x, y, color_light_ground, libtcod.BKGND_SET )
                        map[x][y].explored = True


    for object in objects:
        object.draw()
        
        
    #Do some blitting
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
        

#############################################
# Initialization & Main Loop
#############################################

#Initialize objects
player = Object(0,0, '@','player', libtcod.white, blocks = True)
objects = [player]
make_map()

fov_map = libtcod.map_new(MAP_WIDTH,MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)


fov_recompute = True
game_state = 'playing'
player_action = None

#Game main loop
while not libtcod.console_is_window_closed():
    
    #Draw all objects in the list
    render_all()
    
    
    libtcod.console_flush()
    
    #This flushes the screen
    for object in objects:
        object.clear()
    
    
    player_action = handle_keys()
    if player_action == 'exit':
        break
    
    #Let monsters take a turn
    if game_state == 'playing' and player_action != 'didnt-take-turn':
        for object in objects:
            if object != player:
                print 'The' + object.name+ ' growls!'

