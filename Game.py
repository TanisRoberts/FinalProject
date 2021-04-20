import arcade
import neat
import pymunk
from res.constants import *


# -- AI setup --
window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
gen = 0
events = []
play_type = 0

class PlayerSprite(arcade.Sprite):
    
    def __init__(self, x, y, physics_engine):
        
        super().__init__()
        
        self.physics_engine = physics_engine
        self.center_x = x
        self.center_y = y
        
        self.scale = SPRITE_SCALING_PLAYER
        
        self.jump = False
        self.direction = 0
        
        
        self.idle_texture_pair = arcade.load_texture_pair(f"{PLAYER_SPRITE_FILE_PATH}_idle.png")
        self.jump_texture_pair = arcade.load_texture_pair(f"{PLAYER_SPRITE_FILE_PATH}_jump.png")
        self.fall_texture_pair = arcade.load_texture_pair(f"{PLAYER_SPRITE_FILE_PATH}_fall.png")
        
        self.walk_textures = []
        for i in range(2):
            texture = arcade.load_texture_pair(f"{PLAYER_SPRITE_FILE_PATH}_walk{i}.png")
            self.walk_textures.append(texture)
            
            self.texture = self.idle_texture_pair[0]
            self.hit_box = self.texture.hit_box_points
            self.character_face_direction = RIGHT_FACING
            self.cur_texture = 0
            self.x_odometer = 0
            
            
    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        '''
        Changing the animation of the player as it moves.
        '''
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
            
            
    def move(self, direction, jump):
        if jump > 0 and self.physics_engine.is_on_ground(self):
            self.jump = True
            '''impulse = (0, PLAYER_JUMP_IMPULSE)
            self.physics_engine.apply_impulse(self, impulse)'''
        else:
            self.jump = False
            
        '''if direction < 0:
            # force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
            # self.physics_engine.apply_force(self, force)
            # self.physics_engine.set_friction(self, 0)
        elif direction > 0:
            # force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
            # self.physics_engine.apply_force(self, force)
            # self.physics_engine.set_friction(self, 0)
        else:
            # self.physics_engine.set_friction(self, 1.0)'''
            
        self.direction = direction
            
    def update(self):
        if self.direction < 0:
            force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
            self.physics_engine.apply_force(self, force)
            self.physics_engine.set_friction(self, 0)
        elif self.direction > 0:
            force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
            self.physics_engine.apply_force(self, force)
            self.physics_engine.set_friction(self, 0)
        else:
            self.physics_engine.set_friction(self, 1.0)
            
        if self.jump and self.physics_engine.is_on_ground(self):
            self.jump = False
            impulse = (0, PLAYER_JUMP_IMPULSE)
            self.physics_engine.apply_impulse(self, impulse)
        
    
   
class LaserSprite(arcade.Sprite):
    
    def __init__(self):
        super().__init__()
        
        self.scale = SPRITE_SCALING_LASER
  
  
class SplashView(arcade.View):
    
    def __init__(self, Message):
        super().__init__()
        
        if not Message:
            self.message_text = ""
        else:
            self.message_text = Message
    
    def on_show(self):
        arcade.set_background_color(arcade.csscolor.DARK_GOLDENROD)
        
        arcade.set_viewport(0, SCREEN_WIDTH -1, 0, SCREEN_HEIGHT - 1)    
                  
                  
    def on_draw(self):
        arcade.start_render()
        
        arcade.draw_text(text= self.message_text, 
                         start_x= SCREEN_WIDTH / 2,
                         start_y= SCREEN_HEIGHT / 2+75,
                         color= arcade.color.RED,
                         font_size=25, 
                         anchor_x="center")
        
        arcade.draw_text(text= "Tanis Roberts - Final Project",
                         start_x= SCREEN_WIDTH / 2,
                         start_y= SCREEN_HEIGHT / 2,
                         color= SPLASH_FONT_COLOUR,
                         font_size=50,
                         anchor_x="center")
        
        arcade.draw_text(text= "- Applying NEAT AI to a Platformer Game -", 
                         start_x= SCREEN_WIDTH / 2,
                         start_y= SCREEN_HEIGHT / 2-30,
                         color= SPLASH_FONT_COLOUR,
                         font_size=30, 
                         anchor_x="center")
        
        arcade.draw_text(text= "[1] AI Interface  [2] PYMUNK PHYSICS  [3] PLATFORMER PHYSICS", 
                         start_x= SCREEN_WIDTH / 2,
                         start_y= SCREEN_HEIGHT / 2-75,
                         color= SPLASH_FONT_COLOUR,
                         font_size=20, 
                         anchor_x="center")
        
        
    def on_key_press(self, key, modifiers):
        
        if key == arcade.key.KEY_1:
            #STILL UNDER CONSTRUCTION
            play_type = 1
            self.window.show_view(SplashView("Under Construction..."))
        elif key == arcade.key.KEY_2:
            #Pymunk Physics
            play_type = 2
            view = GameView()
            view.setup()
            self.window.show_view(view)
                                  
        elif key == arcade.key.KEY_3:
            #Platformer Physics
            play_type = 3
            self.window.show_view(SplashView("Removed from game..."))    
        
class GameView(arcade.View):
    def __init__(self):
        
        super().__init__()
        
        self.player_sprite: Optional[PlayerSprite] = None
        
        self.player_list: Optional[arcade.SpriteList] = None
        self.laser_list: Optional[arcade.SpriteList] = None
        self.wall_list: Optional[arcade.SpriteList] = None
        self.item_list: Optional[arcade.SpriteList] = None
        self.door_list: Optional[arcade.SpriteList] = None
        self.dynamic_list: Optional[arcade.SpriteList] = None
        self.bg_list: Optional[arcade.SpriteList] = None
        self.hazard_list: Optional[arcade.SpriteList] = None
        
        self.left_pressed = False
        self.right_pressed = False
        self.jump = False
        
        self.view_bottom = 0
        self.view_left = 0
        
        self.current_map = DEFAULT_MAP_NUM
        
        self.physics_engine = Optional[arcade.PymunkPhysicsEngine]
        
        self.score = 0
        self.death_count = 0
        
        arcade.set_background_color(BACKGROUND_COLOUR)
    
        
    def setup(self):
        
        damping = DEFAULT_DAMPING
        gravity = (0, -GRAVITY)
        self.physics_engine = arcade.PymunkPhysicsEngine(damping= damping,
                                                         gravity= gravity)
        
        game_map = arcade.tilemap.read_tmx(MAP_FOLDER_PATH + MAP_SWITCHER.get(self.current_map))
        
        self.laser_list = arcade.tilemap.process_layer(game_map, 'Laser', SPRITE_SCALING_LASER)
        
        self.wall_list = arcade.tilemap.process_layer(game_map, 'Walls', SPRITE_SCALING_TILES)
        self.item_list = arcade.tilemap.process_layer(game_map, 'Items', SPRITE_SCALING_TILES)
        self.door_list = arcade.tilemap.process_layer(game_map, 'Door', SPRITE_SCALING_TILES)
        self.dynamic_list = arcade.tilemap.process_layer(game_map, 'Dynamic', SPRITE_SCALING_TILES)
        self.bg_list = arcade.tilemap.process_layer(game_map, 'Background', SPRITE_SCALING_TILES)
        self.hazard_list = arcade.tilemap.process_layer(game_map, 'Hazards', SPRITE_SCALING_TILES)
        self.player_list = arcade.SpriteList()
        
        self.player_sprite = PlayerSprite(PLAYER_START_POSITION_X, PLAYER_START_POSITION_Y, self.physics_engine)
        self.player_list.append(self.player_sprite)
        
        
        
        # -- Player List
        self.physics_engine.add_sprite(self.player_sprite,
                                        friction= PLAYER_FRICTION,
                                        mass= PLAYER_MASS,
                                        moment= arcade.PymunkPhysicsEngine.MOMENT_INF,
                                        collision_type= "player",
                                        radius= 0.1,
                                        max_horizontal_velocity= PLAYER_MAX_HORIZONTAL_SPEED,
                                        max_vertical_velocity= PLAYER_MAX_VERTICAL_SPEED)
        
        # -- Laser List
        self.physics_engine.add_sprite_list(self.laser_list,
                                            friction= 0,
                                            collision_type= "laser",
                                            body_type= arcade.PymunkPhysicsEngine.STATIC)
        
        # -- Wall List
        self.physics_engine.add_sprite_list(self.wall_list,
                                            friction= WALL_FRICTION,
                                            collision_type= "wall",
                                            body_type= arcade.PymunkPhysicsEngine.STATIC)
        
        # -- Dynamic List
        self.physics_engine.add_sprite_list(self.dynamic_list,
                                            friction= DYNAMIC_ITEM_FRICTION,
                                            collision_type= "item")
        
        # -- Hazard List
        self.physics_engine.add_sprite_list(self.hazard_list,
                                            friction= 1,
                                            collision_type= "hazard",
                                            body_type= arcade.PymunkPhysicsEngine.STATIC)
        
        def no_collision(sprite_a, sprite_b, arbiter, space, data):
            bool_ = False
            return bool_ 
        
        self.physics_engine.add_collision_handler(first_type= "player",
                                                  second_type= "player",
                                                  begin_handler= no_collision)
        
        
        
        
    
    def on_key_press(self, key, modifiers):
        
        '''if key == arcade.key.LEFT or key == arcade.key.A:
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
            elif key == arcade.key.F:
                self.window.set_fullscreen(not self.window.fullscreen)

                width, height = self.window.get_size()
                arcade.set_viewport(0, width, 0, height)'''
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        
        if key == arcade.key.UP:
            self.jump = True
        else:
            self.jump = False
            
        if IS_DEBUG:
            if key == arcade.key.G:
                self.setup()
            elif key == arcade.key.M:
                self.current_map += 1
                if self.current_map > len(MAP_SWITCHER)-1:
                    self.current_map = 0
                print("[current_map: %d]" % self.current_map)
                print("[Map Path: %s]" % MAP_FOLDER_PATH + MAP_SWITCHER.get(self.current_map))
                self.setup()
            
        # self.player_sprite.move(direction,jump)
        
    def get_player_move_param(self):
        if self.left_pressed:
            direction = -1
        elif self.right_pressed:
            direction = 1
        else:
            direction = 0
            
        if self.jump:
            self.jump = False
            jump = 1
        else:
            jump = 0
            
        return {'direction': direction, 'jump': jump}
        
    
    def on_key_release(self, key, modifers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
            
        if not self.left_pressed and not self.right_pressed:
            self.player_sprite.move(0,False)
            
        if key == arcade.key.UP:
            self.jump = False
        
    
    def on_update(self, delta_time):

                                
        arcade.set_viewport(self.player_sprite.left - (SCREEN_WIDTH/2),
                            self.player_sprite.left + (VIEWPORT_TEST_X),
                            self.player_sprite.bottom - (SCREEN_HEIGHT / 2),
                            self.player_sprite.bottom + (VIEWPORT_TEST_Y))
        
        move_param = self.get_player_move_param() 
        self.player_sprite.move(move_param['direction'],move_param['jump'])
        
        self.player_sprite.update()
            

        '''if self.left_pressed and not self.right_pressed:
            force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.right_pressed and not self.left_pressed:
            force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        else:
            self.physics_engine.set_friction(self.player_sprite, 1.0)'''
            
        for laser in self.laser_list:
            laser.set_position(laser._get_center_x() + LASER_MOVE_SPEED,laser._get_center_y())
        
        item_hit_list = arcade.check_for_collision_with_list(self.player_sprite,self.item_list)
        
        for item in item_hit_list:
            self.score += 1
            item.remove_from_sprite_lists()
            
        laser_hit_list = arcade.check_for_collision_with_list(self.player_sprite,self.laser_list)
        
        for beam in laser_hit_list:
            self.death_count += 1
            self.setup()
            #beam.remove_from_sprite_lists()
            break
        
        hazard_hit_list = arcade.check_for_collision_with_list(self.player_sprite,self.hazard_list)
        
        for hazard in hazard_hit_list:
            self.death_count += 1
            self.setup()
            break
        
        self.physics_engine.step()
        
    
    def on_draw(self):
        arcade.start_render()
        self.item_list.draw()
        self.dynamic_list.draw()
        self.hazard_list.draw()
        self.bg_list.draw()
        self.wall_list.draw()
        self.door_list.draw()
        self.laser_list.draw()
        self.player_list.draw()
        
        score_text = f"Score: {self.score}"
        deaths_text = f"Deaths: {self.death_count}"
        
        left, right, bottom, top = arcade.get_viewport()
        
        arcade.draw_text(text= score_text,
                         start_x= 10 + left,
                         start_y= top - 40,
                         color= GAME_FONT_COLOUR,
                         font_size= 35)
        
        arcade.draw_text(text= deaths_text,
                         start_x= 10 + left,
                         start_y= top - 70,
                         color= GAME_FONT_COLOUR,
                         font_size= 35)
     
class AIView():
    def __init__(self):
        
        super().__init__()
        
        self.current_sprite: Optional[arcade.SpriteList] = None
        
        self.player_list: Optional[arcade.SpriteList] = None
        self.laser_list: Optional[arcade.SpriteList] = None
        self.wall_list: Optional[arcade.SpriteList] = None
        self.item_list: Optional[arcade.SpriteList] = None
        self.door_list: Optional[arcade.SpriteList] = None
        self.dynamic_list: Optional[arcade.SpriteList] = None
        self.bg_list: Optional[arcade.SpriteList] = None
        self.hazard_list: Optional[arcade.SpriteList] = None
        
        self.left_pressed = False
        self.right_pressed = False
        
        self.view_bottom = 0
        self.view_left = 0
        
        self.current_map = DEFAULT_MAP_NUM
        
        self.physics_engine = Optional[arcade.PymunkPhysicsEngine]
        
        self.score = 0
        self.death_count = 0
        
        arcade.set_background_color(BACKGROUND_COLOUR)
    
        
    def setup(self):
        
        damping = DEFAULT_DAMPING
        gravity = (0, -GRAVITY)
        self.physics_engine = arcade.PymunkPhysicsEngine(damping= damping,
                                                         gravity= gravity)
        
        game_map = arcade.tilemap.read_tmx(MAP_FOLDER_PATH + MAP_SWITCHER.get(self.current_map))
        
        self.laser_list = arcade.tilemap.process_layer(game_map, 'Laser', SPRITE_SCALING_LASER)
        
        self.wall_list = arcade.tilemap.process_layer(game_map, 'Walls', SPRITE_SCALING_TILES)
        self.item_list = arcade.tilemap.process_layer(game_map, 'Items', SPRITE_SCALING_TILES)
        self.door_list = arcade.tilemap.process_layer(game_map, 'Door', SPRITE_SCALING_TILES)
        self.dynamic_list = arcade.tilemap.process_layer(game_map, 'Dynamic', SPRITE_SCALING_TILES)
        self.bg_list = arcade.tilemap.process_layer(game_map, 'Background', SPRITE_SCALING_TILES)
        self.hazard_list = arcade.tilemap.process_layer(game_map, 'Hazards', SPRITE_SCALING_TILES)
        self.player_list = arcade.SpriteList()
        
        self.player_sprite = PlayerSprite(PLAYER_START_POSITION_X, PLAYER_START_POSITION_Y, physics_engine)
        self.player_list.append(self.player_sprite)
        
        
        
        # -- Player List
        '''self.physics_engine.add_sprite(self.player_sprite,
                                        friction= PLAYER_FRICTION,
                                        mass= PLAYER_MASS,
                                        moment= arcade.PymunkPhysicsEngine.MOMENT_INF,
                                        collision_type= "player",
                                        radius= 0.1,
                                        max_horizontal_velocity= PLAYER_MAX_HORIZONTAL_SPEED,
                                        max_vertical_velocity= PLAYER_MAX_VERTICAL_SPEED)'''
        
        # -- Laser List
        self.physics_engine.add_sprite_list(self.laser_list,
                                            friction= 0,
                                            collision_type= "laser",
                                            body_type= arcade.PymunkPhysicsEngine.STATIC)
        
        # -- Wall List
        self.physics_engine.add_sprite_list(self.wall_list,
                                            friction= WALL_FRICTION,
                                            collision_type= "wall",
                                            body_type= arcade.PymunkPhysicsEngine.STATIC)
        
        # -- Dynamic List
        self.physics_engine.add_sprite_list(self.dynamic_list,
                                            friction= DYNAMIC_ITEM_FRICTION,
                                            collision_type= "item")
        
        # -- Hazard List
        self.physics_engine.add_sprite_list(self.hazard_list,
                                            friction= 1,
                                            collision_type= "hazard",
                                            body_type= arcade.PymunkPhysicsEngine.STATIC)
        
        def no_collision(sprite_a, sprite_b, arbiter, space, data):
            bool_ = False
            return bool_ 
        
        self.physics_engine.add_collision_handler(first_type= "player",
                                                  second_type= "player",
                                                  begin_handler= no_collision)
        
        
        
        
    
    '''def on_key_press(self, key, modifiers):
        
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
            elif key == arcade.key.F:
                self.window.set_fullscreen(not self.window.fullscreen)

                width, height = self.window.get_size()
                arcade.set_viewport(0, width, 0, height)

    
    def on_key_release(self, key, modifers):
        
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
    '''
        
    
    def on_update(self, delta_time):

        current_sprite = self.player_list.__getitem__(0)
        
        arcade.set_viewport(current_sprite.left - (SCREEN_WIDTH/2),
                            current_sprite.left + (VIEWPORT_TEST_X),
                            current_sprite.bottom - (SCREEN_HEIGHT / 2),
                            current_sprite.bottom + (VIEWPORT_TEST_Y))
            
            
        for laser in self.laser_list:
            laser.set_position(laser._get_center_x() + LASER_MOVE_SPEED,laser._get_center_y())
        
        item_hit_list = arcade.check_for_collision_with_list(self.player_sprite,self.item_list)
        
        for item in item_hit_list:
            self.score += 1
            item.remove_from_sprite_lists()
            
        laser_hit_list = arcade.check_for_collision_with_list(self.player_sprite,self.laser_list)
        
        for beam in laser_hit_list:
            self.death_count += 1
            #beam.remove_from_sprite_lists()
        
        
        self.physics_engine.step()
        
    
    def on_draw(self):
        arcade.start_render()
        self.item_list.draw()
        self.dynamic_list.draw()
        self.hazard_list.draw()
        self.bg_list.draw()
        self.wall_list.draw()
        self.door_list.draw()
        self.laser_list.draw()
        self.player_list.draw()
        
        score_text = f"Score: {self.score}"
        deaths_text = f"Deaths: {self.death_count}"
        alive_text = f"Alive: {self.player_list.__len__()}"
        
        left, right, bottom, top = arcade.get_viewport()
        
        arcade.draw_text(text= score_text,
                         start_x= 10 + left,
                         start_y= top - 40,
                         color= GAME_FONT_COLOUR,
                         font_size= 35)
        
        arcade.draw_text(text= deaths_text,
                         start_x= 10 + left,
                         start_y= top - 70,
                         color= GAME_FONT_COLOUR,
                         font_size= 35)
        
        arcade.draw_text(text= alive_text,
                         start_x= 10 + left,
                         start_y= top - 100,
                         color= GAME_FONT_COLOUR,
                         font_size= 35)
        
    def create_player(self):
        new_player = PlayerSprite(PLAYER_START_POSITION_X, PLAYER_START_POSITION_Y, self.physics_engine)
        
        self.physics_engine.add_sprite(new_player,
                                        friction= PLAYER_FRICTION,
                                        mass= PLAYER_MASS,
                                        moment= arcade.PymunkPhysicsEngine.MOMENT_INF,
                                        collision_type= "player",
                                        radius= 0.1,
                                        max_horizontal_velocity= PLAYER_MAX_HORIZONTAL_SPEED,
                                        max_vertical_velocity= PLAYER_MAX_VERTICAL_SPEED)
        
        self.player_list.append(new_player)
        
        return new_player
       
def eval_genomes(genomes, config):
    
    global window, gen, events
    win = window
    gen += 1
    
    view = AIView()
    view.setup()
    win.show_view(view)
    
    ge = []
    nets = []
    players = []
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        player = view.create_player()
        players.append(player)
        ge.append(genome)
    
    run = True
    while run and len(players) > 0:
        for event in events:
            if event == "QUIT":
                run = False
                quit()
                break
            
    for i, player in enumerate(players):
        ge[i].fitness += FRAME_FITNESS
        
        output = nets[players.index(player)].activate(())
    

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_file)
    
    p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    winner = p.run(eval_genomes, MAX_GENERATION)
    
    print("\nBest Genome: \n{!s}".format(winner))
    
        
def main():   
    # - Show splash screen before starting
    start_view = SplashView("")
        
    window.show_view(start_view)
    arcade.run()
    
if __name__ == "__main__":
    
    main()