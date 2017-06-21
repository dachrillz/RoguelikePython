# -*- coding: utf-8 -*-
"""
Created on Sat Jun 17 14:32:46 2017

@author: crule
"""

'''
Important with components, they need to know their owner!

Example:
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster #tell the component who owns it!
'''

#Imports
import libtcodpy as libtcod
import math
import textwrap

#Finals
LIMIT_FPS = 20

MAP_WIDTH = 80
MAP_HEIGHT = 43

INVENTORY_WIDTH = 50

SCREEN_WIDTH = MAP_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT

ROOM_MAX_SIZE = 20
ROOM_MIN_SIZE = 10
MAX_ROOMS = 100

FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

MAX_ROOM_MONSTER = 3
MAX_ROOM_ITEMS = 2

#### Item stats
HEAL_AMOUNT = 5
LIGHTNING_DAMAGE = 20
LIGHTNING_RANGE = 5
CONFUSE_RANGE = 10
CONFUSE_NUM_TURNS = 20 
FIREBALL_DAMAGE = 20
FIREBALL_RADIUS = 10

#sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

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
# GUI
#############################################

panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

def render_bar(x,y, total_width, name, value, maximum, bar_color, back_color):
    #Render a bar. first calculate the width of the bar
    bar_width = int(float(value)) / maximum * total_width
    
    #Render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
    
    #Render bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #Finally, centered text with values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
        name + ': ' + str(value) + '/' + str(maximum))
        
        
def message(new_msg, color = libtcod.white):
    
    #Split the message if necessary
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
    
    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for new message
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]
            
        game_msgs.append( (line, color) )
        
   
def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
    
    #calcualte heig for the header
    header_height= libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    height = len(options) + header_height
    
    #create off screen console that represents the menu's window
    window = libtcod.console_new(width, height)
    
    #print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
    
    #print all the options.
    y = header_height
    letter_index = ord('a') #this gets ascii value for 'a'
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1
        
        
    #blit the contents of "window" to the root console
    x = SCREEN_WIDTH/2 - width/2
    y = SCREEN_HEIGHT/2 - height/2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
    
    
    #present the root console to the player and wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)
    
    #convert the ASCII code to an index, if it correspondens to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None
    
    
def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inventory]
 
    index = menu(header, options, INVENTORY_WIDTH) 

    #if an item was chosen, return it
    if index is None or len(inventory) == 0: return None
    return inventory[index].item

#############################################
# Cheats for debugging
#############################################

def cheat_item(cheat_item, name):
    if len(inventory) >= 26:
        message('Inventory was full no item created', libtcod.red)
        
    else:
        item_component = Item(use_function=cheat_item)
        item = Object(0, 0, 'O', name, libtcod.violet, item = item_component)   
        inventory.append(item)
       
#############################################
# Classes
#############################################



class Item:
    def __init__(self, use_function=None):
        self.use_function = use_function
        
    def use(self):
        #Just call the "use-function" if it is defined
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner) # destroy after use!
        
    #an item that can be picked up and used
    def pick_up(self):
        #add to the players inventory and remove from the maps
        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.',libtcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', libtcod.green)

            
    def drop(self):
        #add to the map and remove from the players inventory. also place at players location.
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a' + self.owner.name + '.', libtcod.yellow)

class Object:
    """
    A general purpose object that contains functions for: move, draw and clear.
    Takes as input (x, y, char, color)
    """
    def __init__(self,x, y, char, name, color, blocks = False, fighter = None, ai = None, item = None):
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
        self.item = item
        if self.item:
            self.item.owner = self
        
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
        
        
    
    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        
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
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
            target.fighter.take_damage(damage)
            
        else:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
            
            
    def heal(self, amount):
        #heal by the given amount.
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        
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
                
                
                
class ConfusedMonster:
    #AI for confused Ai
    def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns
       
    def take_turn(self):
        if self.num_turns > 0:
            #move in random direction
            self.owner.move(libtcod.random_get_int(0,-1,1), libtcod.random_get_int(0,-1,1))
            self.num_turns -= 1
            
        else:
            #restore to old ai
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)
        
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
# Item functions
#############################################

def cast_heal():
    #heals the player
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health.', libtcod.red)
        return 'cancelled'
    message('Your wound start to feel better!', libtcod.light_violet)
    player.fighter.heal(HEAL_AMOUNT)
    
def cast_lightning():
    #find closet monster.
    monster = closest_monster(LIGHTNING_RANGE)
    if monster is None:
        message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'
    #zap!
    message('A lightning bolt strikes the ' + monster.name + 'with a loud thunder! The damage is'
        + str(LIGHTNING_DAMAGE) + ' hitpoints.', libtcod.light_blue)
    monster.fighter.take_damage(LIGHTNING_DAMAGE)
    
def cast_confuse():
    #ask the player for a target to confuse
    message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
    monster = target_monster(CONFUSE_RANGE)
    if monster is None: return 'cancelled'

    #replace old ai in monster
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster #tell the component who owns it!
    message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)

def cast_fireball():
    #ask the player for a target tile to throw a fireball at
    message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    message('The fireball explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', libtcod.orange)
 
    for obj in objects:  #damage every fighter in range, including the player
        if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
            message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
            obj.fighter.take_damage(FIREBALL_DAMAGE)    
    
def closest_monster(max_range):
    #find closest_enemy
    closest_enemy = None
    closest_dist = max_range + 1
    
    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x,object.y):
            #calculate distance between this object and player.
            dist = player.distance_to(object)
            if dist < closest_dist: 
                closest_enemy = object
                closest_dist = dist
    return closest_enemy
               
               
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
            
            
def get_names_under_mouse():
    global mouse
    
    #retur a string with the names of all objects under mouse
    (x, y) = (mouse.cx, mouse.cy)
    
    #create a list with the names of all objects at the mouse coordinates AND in FOV
    names = [obj.name for obj in objects
        if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]
        
    names = ', '.join(names)
    return names.capitalize()
    
def target_tile(max_range=None):
    #return the position of a tile that is left clicked inplayer's FOV,
    #optionally in a range, or (None,None) if Right click
    global key,mouse
    while True:
        #render the screen this erases the inventroy and showsnameof objects under mouse.
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        render_all()
 
        (x, y) = (mouse.cx, mouse.cy)
 
        #accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and
            (max_range is None or player.distance(x, y) <= max_range)):
            return (x, y)
            
        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  #cancel if the player right-clicked or pressed Escape
 
def target_monster(max_range=None):
    #returns a clicked monster inside FOV up to a range or none if right clicked.
    while(True):
        (x, y) = target_tile(max_range)
        if x is None: #player cancelled,
            return None
        
        #check if monster.
        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != player:
                return obj
 
def handle_keys():
    global key
    global fov_recompute
    global game_state
    
    #Handle misc. keys
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
            #test for other keys:
            key_char = chr(key.c)
            
            if key_char == 'd':
                #show the menu of items and if selected drop it.
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()
            
            if key_char == 'i':
                #show the inventory
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()
            
            if key_char == 'g':
                #pick up item
                for object in objects:
                    if object.x == player.x and object.y == player.y and object.item:
                        object.item.pick_up()
                        break
            
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
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
        
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
            
            
    num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)
    
    for i in range(num_items):
        
        #randomize item:
        dice = libtcod.random_get_int(0,0,100)

        #Choose random spot for items
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
        
        #only place if tiled not blocked
        if not is_blocked(x, y):
            if dice > 95:
                #Create fireball scroll
                item_component = Item(use_function=cast_fireball)
                item = Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)

            elif dice > 70:
                #create healing potion
                item_component = Item(use_function=cast_heal)
                item = Object(x, y, '!', 'healing potion', libtcod.violet, item = item_component)
            
            elif dice > 45:
                #create confue item:
                item_component = Item(use_function=cast_confuse)
                item = Object(x, y, '#', 'scroll of confusion', libtcod.violet, item = item_component)
             
            else:
                item_component = Item(use_function=cast_lightning)
                item = Object(x, y, '#', 'scroll of lightning bolt', libtcod.violet, item = item_component)
        
            objects.append(item)
        
            item.send_to_back()
 
 
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
    global fov_map
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
                        
                        
    #Draw the objects
    for object in objects:
        if object != player:
            object.draw()
    player.draw()
    
    #Do some blitting
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
     
    
    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)
     
    
    #Print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1
        
    
    #render hpbar
    render_bar(1,1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
        libtcod.light_red, libtcod.darker_red)
        
    #display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())
        
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)
    

        
def player_death(player):
    #the game ended!
    global game_state
    message('You died!', libtcod.red)
    game_state = 'dead'
 
    #for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = libtcod.dark_red
 
def monster_death(monster):
    #transform it into a nasty corpse! it doesn't block, can't be
    #attacked and doesn't move
    message(monster.name.capitalize() + ' is dead!', libtcod.orange)
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

#Define inventory
inventory = []

#create the list of game messages and their colors, starts empty
game_msgs = []

#a warm welcoming message!
message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', libtcod.red)

mouse = libtcod.Mouse()
key = libtcod.Key()

#Limit the games speed
libtcod.sys_set_fps(LIMIT_FPS)


#cheats, (cast_heal,cast_lightning, cast_confuse,cast_fireball)
cheat_item(cast_lightning, 'cheated item')
cheat_item(cast_confuse, 'cheated item 1 ')
cheat_item(cast_fireball, 'cheated item 2')

#Game main loop
while not libtcod.console_is_window_closed():
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
    
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

