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
        
        self.physics_engine = Optional[arcade.PymunkPhysicsEngine]
        
        self.left_pressed = False
        self.right_pressed = False
        
        arcade.set_background_color(BACKGROUND_COLOUR)
        
    def setup(self):
        damping = DEFAULT_DAMPING
        gravity = (0, GRAVITY)
        
        self.physics_engine = arcade.PymunkPhysicsEngine(damping= damping,
                                                         gravity= gravity)
        
        # -- Player List
        self.physics_engine.add_sprite(self.player_sprite,
                                       friction= PLAYER_FRICTION,
                                       mass= PLAYER_MASS,
                                       moment= arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player",
                                       max_horizontal_velocity= PLAYER_MAX_HORIZONTAL_SPEED,
                                       max_vertical_velocity= PLAYER_MAX_VERTICAL_SPEED)
        
        # -- Wall List
        self.physics_engine.add_sprite_list(self.wall_list,
                                            friction= WALL_FRICTION,
                                            collision_type= "wall",
                                            body_type= arcade.PymunkPhysicsEngine.STATIC)
        
        # -- Item List        
        self.physics_engine.add_sprite_list(self.item_list,
                                            friction= 0,
                                            collision_type= "none",
                                            body_type= arcade.PymunkPhysicsEngine.STATIC)
        
        # -- Dynamic List
        self.physics_engine.add_sprite_list(self.dynamic_list,
                                            friction= DYNAMIC_ITEM_FRICTION,
                                            collision_type= "item")
        
        self.physics_engine.add_sprite_list(self.hazard_list,
                                            friction= 1,
                                            collision_type= "hazard",
                                            body_type= arcade.PymunkPhysicsEngine.STATIC)
        
        
    
    def on_key_press(self, key, modifiers):
        
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP:
            if self.physics_engine.is_on_ground(self.player_sprite):
                impulse = (0, PLAYER_JUMP_IMPULSE)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)
            
    
    def on_key_release(self, key, modifers):
        
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        
    
    def on_update(self, delta_time):

        if self.left_pressed and not self.right_pressed:
            force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.right_pressed and not self.left_pressed:
            force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        else:
            self.physics_engine.set_friction(self.player_sprite, 1.0)
        
        self.physics_engine.step()
    
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