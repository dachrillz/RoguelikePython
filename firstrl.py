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


#Set fonts
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

#Initialize window
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)

#Set FPS limit
libtcod.sys_set_fps(LIMIT_FPS)

#Game main loop
while not libtcod.console_is_window_closed():
    libtcod.console_set_default_foreground(0, libtcod.white)
    