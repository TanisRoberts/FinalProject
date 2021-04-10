import arcade
from res.constants import *

class PlayerSprite(arcade.Sprite):
    
    def __init__(self):
        
        super().__init__()
        
        self.scale = SPRITE_SCALING_PLAYER
        
        self.idle_texture_pair = arcade.load_texture_pair(f"{SPRITE_FILE_PATH}_idle.png")
        self.jump_texture_pair = arcade.load_texture_pair(f"{SPRITE_FILE_PATH}_jump.png")
        self.fall_texture_pair = arcade.load_texture_pair(f"{SPRITE_FILE_PATH}_fall.png")
        
        self.walk_textures = []
        for i in range(2):
            texture = arcade.load_texture_pair(f"{SPRITE_FILE_PATH}_walk{i}.png")
            self.walk_textures.append(texture)
            
            self.texture = self.idle_texture_pair[0]
            self.hit_box = self.texture.hit_box_points
            self.character_face_direction = RIGHT_FACING
            self.cur_texture = 0
            self.x_odometer = 0
            
            
    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        if dx < -DEAD_ZONE and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif dx > DEAD_ZONE and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
            
        is_on_ground = physics_engine.is_on_ground(self)
        
        self.x_odometer += dx
        
        if not is_on_ground:
            if dy > DEAD_ZONE:
                self.texture = self.jump_texture_pair[self.character_face_direction]
                return
            elif dy < -DEAD_ZONE:
                self.texture = self.fall_texture_pair[self.character_face_direction]
                return
            
        if abs(dx) <= DEAD_ZONE:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return
        
        if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE:
            self.x_odometer = 0
            self.cur_texture += 1
            
            if self.cur_texture > 1:
                self.cur_texture = 0
            
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]
                

class GameWindow(arcade.Window):
    
    def __init__(self, width, height, title):
        
        super().__init__(width, height, title)
        
        self.player_sprite: Optional[PlayerSprite] = None
        
        self.player_list: Optional[arcade.SpriteList] = None
        self.wall_list: Optional[arcade.SpriteList] = None
        self.item_list: Optional[arcade.SpriteList] = None
        self.dynamic_list: Optional[arcade.SpriteList] = None
        self.bg_list: Optional[arcade.SpriteList] = None
        self.hazard_list: Optional[arcade.SpriteList] = None
        
        self.physics_engine = Optional[arcade.PymunkPhysicsEngine]
        
        self.left_pressed = False
        self.right_pressed = False
        
        self.view_bottom = 0
        self.view_left = 0
        
        self.current_map = DEFAULT_MAP_NUM
        
        arcade.set_background_color(BACKGROUND_COLOUR)
        
    def setup(self):
        
        game_map = arcade.tilemap.read_tmx(MAP_FOLDER_PATH + MAP_SWITCHER.get(self.current_map))
        
        self.wall_list = arcade.tilemap.process_layer(game_map, 'Walls', SPRITE_SCALING_TILES)
        self.item_list = arcade.tilemap.process_layer(game_map, 'Items', SPRITE_SCALING_TILES)
        self.dynamic_list = arcade.tilemap.process_layer(game_map, 'Dynamic', SPRITE_SCALING_TILES)
        self.bg_list = arcade.tilemap.process_layer(game_map, 'Background', SPRITE_SCALING_TILES)
        self.hazard_list = arcade.tilemap.process_layer(game_map, 'Hazards', SPRITE_SCALING_TILES)
        
        self.player_sprite = PlayerSprite()
        self.player_list = arcade.SpriteList()
        
        # - Player Start Co-ordinates
        self.player_sprite.center_x = SPRITE_SIZE * GRID_START_X + SPRITE_SIZE / 2
        self.player_sprite.center_y = SPRITE_SIZE * GRID_START_Y + SPRITE_SIZE / 2
        
        self.player_list.append(self.player_sprite)
        
        damping = DEFAULT_DAMPING
        gravity = (0, -GRAVITY)
        
        self.physics_engine = arcade.PymunkPhysicsEngine(damping= damping,
                                                         gravity= gravity)
        
        # -- Player List
        self.physics_engine.add_sprite(self.player_sprite,
                                       friction= PLAYER_FRICTION,
                                       mass= PLAYER_MASS,
                                       moment= arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player",
                                       radius= 0.1,
                                       max_horizontal_velocity= PLAYER_MAX_HORIZONTAL_SPEED,
                                       max_vertical_velocity= PLAYER_MAX_VERTICAL_SPEED)
        
        # -- Wall List
        self.physics_engine.add_sprite_list(self.wall_list,
                                            friction= WALL_FRICTION,
                                            collision_type= "wall",
                                            body_type= arcade.PymunkPhysicsEngine.STATIC)
        
        # -- Item List        
        '''self.physics_engine.add_sprite_list(self.item_list,
                                            friction= 0,
                                            collision_type=None,
                                            body_type= arcade.PymunkPhysicsEngine.STATIC)
        '''
        
        # -- Dynamic List
        self.physics_engine.add_sprite_list(self.dynamic_list,
                                            friction= DYNAMIC_ITEM_FRICTION,
                                            collision_type= "item")
        
        # -- Hazard List
        self.physics_engine.add_sprite_list(self.hazard_list,
                                            friction= 1,
                                            collision_type= "hazard",
                                            body_type= arcade.PymunkPhysicsEngine.STATIC)
        
        
    
    def on_key_press(self, key, modifiers):
        
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
            print("left")
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
            print("right")
        elif key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.is_on_ground(self.player_sprite):
                impulse = (0, PLAYER_JUMP_IMPULSE)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)
                print("jump")
        elif IS_DEBUG:
            if key == arcade.key.G:
                self.setup()
            elif key == arcade.key.M:
                self.current_map += 1
                if self.current_map > len(MAP_SWITCHER)-1:
                    self.current_map = 0
                print("[current_map: %d]" % self.current_map)
                print("[Map Path: %s]" % MAP_FOLDER_PATH + MAP_SWITCHER.get(self.current_map))
                self.setup()
            
    
    def on_key_release(self, key, modifers):
        
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        
    
    def on_update(self, delta_time):

        """changed = False
        
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True
            
        if self.player_sprite.right > right_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True
            
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True
            
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True
            
        if changed:
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)"""
                                
        arcade.set_viewport(self.player_sprite.left - (SCREEN_WIDTH/2),
                            self.player_sprite.left + (VIEWPORT_TEST_X),
                            self.player_sprite.bottom - (SCREEN_HEIGHT / 2),
                            self.player_sprite.bottom + (VIEWPORT_TEST_Y))
            

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
        self.item_list.draw()
        self.dynamic_list.draw()
        self.bg_list.draw()
        self.hazard_list.draw()
        self.wall_list.draw()
        self.player_list.draw()
    
    
def main():
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()
    
    
if __name__ == "__main__":
    main()