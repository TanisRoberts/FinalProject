import arcade
from res.constants import *

class GameWindow(arcade.Window):
    
    def __init__(self, width, height, title):
        
        super().__init__(width, height, title)
        
        self.player_sprite: Optional[arcade.Sprite] = None
        
        self.player_list: Optional[arcade.SpriteList] = None
        self.wall_list: Optional[arcade.SpriteList] = None
        self.item_list: Optional[arcade.SpriteList] = None
        self.dynamic_list: Optional[arcade.SpriteList] = None
        self.bg_list: Optional[arcade.SpriteList] = None
        self.hazard_list: Optional[arcade.SpriteList] = None
        
        self.left_pressed = False
        self.right_pressed = False
        
        arcade.set_background_color(BACKGROUND_COLOUR)
        
    def setup(self):
        
        pass
    
    def on_key_press(self, key, modifiers):
        
        pass
    
    def on_key_release(self, key, modifers):
        
        pass
    
    def on_update(self, delta_time):
        
        pass
    
    def on_draw(self):
        arcade.start_render()
        self.player_list.draw()
        self.wall_list.draw()
        self.item_list.draw()
        self.dynamic_list.draw()
        self.bg_list.draw()
        self.hazard_list.draw()
    
    
def main():
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()
    
    
if __name__ == "__main__":
    main()