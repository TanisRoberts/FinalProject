#Imports
from constants import *

import arcade
import math
from typing import Optional

#Class for the game window
class GameWindow(arcade.Window):
    
    def __init__(self, width, height, title, backgroundCol):
        
        #Init parent
        super().__init__(width, height, title)
        
        #Player Sprite
        self.player_sprite: Optional[arcade.Sprite] = None
        
        #Sprite lists
        self.player_list: Optional[arcade.SpriteList] = None
        self.wall_list: Optional[arcade.SpriteList] = None
        self.bullet_list: Optional[arcade.SpriteList] = None
        self.item_list: Optional[arcade.SpriteList] = None
        self.obstacle_list: Optional[arcade.SpriteList] = None
        
        #Keypress tracking
        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        
        #GameState
        arcade.set_background_color(backgroundCol)
        
        
    def setup(self):
        
        #Sprite Lists
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        
        #Read in tiled map
        map_name = MAP_PATH + "testmap.tmx"
        my_map = arcade.tilemap.read_tmx(map_name)
        
        #Read in map layers
        self.wall_list = arcade.tilemap.process_layer(my_map, 'Physical', SPRITE_SCALING_TILES)
        self.item_list = arcade.tilemap.process_layer(my_map, 'Dynamic', SPRITE_SCALING_TILES)
        
        #Create player sprite
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", SPRITE_SCALING_PLAYER)
        grid_x = 1
        grid_y = 1
        self.player_sprite.center_x = SPRITE_SIZE_PLAYER * grid_x + SPRITE_SIZE_PLAYER / 2
        self.player_sprite.center_y = SPRITE_SIZE_PLAYER * grid_y + SPRITE_SIZE_PLAYER / 2
        
        self.player_list.append(self.player_sprite)
    
    def on_key_press(self, key, modifiers):
        
        pass
    
    def on_key_release(self, key, modifiers):
        
        pass
    
    def on_update(self, delta_time):
        
        pass
    def on_draw(self):
        
        arcade.start_render()