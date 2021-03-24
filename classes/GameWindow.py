#Imports
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
    
        pass
    
    def on_key_press(self, key, modifiers):
        
        pass
    
    def on_key_release(self, key, modifiers):
        
        pass
    
    def on_update(self, delta_time):
        
        pass
    def on_draw(self):
        
        arcade.start_render()