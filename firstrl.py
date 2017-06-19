# -*- coding: utf-8 -*-
"""
Created on Sat Jun 17 14:32:46 2017

@author: crule
"""

#Imports
import libtcodpy as libtcod
import math

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
    def __init__(self,x, y, char, name, color, blocks = False, fighter = None, ai = None):
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        
        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self
        self.ai = ai
        if self.ai:
            self.ai.owner = self
        
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

        
    def move_towards(self, target_x, target_y):
        #Vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        
        #normalize to length 1
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx,dy)
        
    def distance_to(self,other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx**2 + dy**2)
        
    def send_to_back(self):
        #make this object be drawn first, so all others appear above it if they're in the same tile.
        global objects
        objects.remove(self)
        objects.insert(0, self)
    
class Fighter:
    def __init__(self, hp, defense, power, death_function=None):
        self.death_function = death_function
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        
        
    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage
            
            #Check for death_function
            if self.hp <= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner)
                    
    def attack(self, target):
        damage = self.power - target.fighter.defense
        
        if damage > 0:
            print self.owner.name.capitalize() + ' atacks ' + target.name + ' for ' + str(damage) + ' hit points!'
            target.fighter.take_damage(damage)
            
        else:
            print self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!'
        
class BasicMonster:
    #Ai for a basic monster
    def take_turn(self):
        #A basic monster takes its turn. if you can see it
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map,monster.x,monster.y):
            
            #move towards player if...
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)
                
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)
        
        
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
                fighter_component = Fighter(hp=10, defense = 0, power = 3, death_function = monster_death)
                ai_component = BasicMonster()
                monster = Object(x,y, 'O','orc', libtcod.desaturated_green, blocks = True, fighter = fighter_component, ai=ai_component)
            else:
                fighter_component = Fighter(hp=16, defense = 1, power = 3,death_function = monster_death)
                ai_component = BasicMonster()
                monster = Object(x,y, 'T','troll', libtcod.darker_green,
                    blocks = True, fighter = fighter_component, ai = ai_component)
                
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
        if object.fighter and object.x == x and object.y == y:
            target = object
            break
           
    if target is not None:
        player.fighter.attack(target)
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
        if object != player:
            object.draw()
    player.draw()
        
        
    #Do some blitting
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
     


        #show the player's stats
    libtcod.console_set_default_foreground(con, libtcod.white)
    libtcod.console_print_ex(con, 1, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.LEFT,
        'HP: ' + str(player.fighter.hp) + '/' + str(player.fighter.max_hp))

        
def player_death(player):
    #the game ended!
    global game_state
    print 'You died!'
    game_state = 'dead'
 
    #for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = libtcod.dark_red
 
def monster_death(monster):
    #transform it into a nasty corpse! it doesn't block, can't be
    #attacked and doesn't move
    print monster.name.capitalize() + ' is dead!'
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()



#############################################
# Initialization & Main Loop
#############################################

#Initialize objects
fighter_component = Fighter(hp=30, defense = 2, power = 5, death_function = player_death)
player = Object(0,0, '@','player', libtcod.white, blocks = True, fighter=fighter_component)
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
            if object.ai:
                object.ai.take_turn()

