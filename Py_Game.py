import pygame
import pymunk
import random
import csv
import pandas
import numpy
import math
import neat
import pickle
import time
from os import walk
from concurrent.futures import ThreadPoolExecutor
from res.constants_py import *

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)
clock = pygame.time.Clock()

global_counter = 0
cur_timescore = 0.0
cur_score = 0


pygame.display.update()

#Game modes:
# - 1 : Singleplayer
# - 2 : Dummies
# - 3 : Smarties

class World():
    def __init__(self, game_mode= 0):
        global global_counter
        self.level = 0
        self.world_data = []
        self.map_file_path = ""
        self.name_list = []
        self.game_mode = game_mode
        self.only_show_closest_player = ONLY_SHOW_CLOSEST_PLAYER
        
        self.player_start_position_x = PLAYER_START_POS_X
        self.player_start_position_y = PLAYER_START_POS_Y
        self.goal_position = 0
        self.generation = global_counter
        
        self.ui = Optional[UIController]
        self.game_mode = 0
        
        self.still_list = []
        self.world_list = []
        self.wall_list = []
        self.bg_list = []
        self.marker_list = []
        
        self.screen_scroll = 0
        self.total_scroll = 0
        
        self.relative_scroll = 0
        
        self.object_group = pygame.sprite.Group()
        self.wall_group = pygame.sprite.Group()
        
        self.tile_img_list = []
        self.laser = Laser()
        self.laser_position = 0
        self.num_items = 0
        
        self.left_boundary = (SCREEN_WIDTH // 2) - 100
        self.right_boundary = (SCREEN_WIDTH // 2) + 100
        
        self.map_width = COLS * TILE_SIZE
        self.scroll_cap = self.map_width - (self.right_boundary + (SCREEN_WIDTH // 2))
        
    def load_world(self, level_num= 0):
        self.level = level_num
        self.map_file_path = MAP_CSV_PATH.format(MAP_CSV_FILE_LIST[level_num])
        
        self.load_tiles()
        self.generate_world_data()
        self.generate_ui_controller()    
        
    def load_name_list(self):
        print("--- [Retrieving Player Names] ---")

        with open(NAME_FILE_PATH, newline='') as f:
            reader = csv.reader(f)
            data = list(reader)

        nl = data

        print(nl)
        print(" -- {} Player Names Retrieved! --\n".format(len(nl)))   
        self.name_list = nl
        
        
    def get_name(self):
        return self.name_list[random.randint(0, len(self.name_list) - 1)][0]
        
        
    def create_death_marker(self, player):
    
        if player.player_type == 'Dummy':
            if len(self.marker_list) == 0:
                marker_type = 0
            else:
                marker_type = 1
        elif player.player_type == 'Player':
            marker_type = 2
        else:
            marker_type = 1   

        marker = Marker(player.const_x, player.rect.y, marker_type, player.player_tag)
        self.marker_list.append(marker)
        
    def set_game_mode(self,game_mode):
        global global_counter
        self.game_mode = game_mode
        self.ui = Optional[UIController]
        self.world_list = []
        self.wall_list = []
        self.const_world_list = []
        self.bg_list = []
        self.marker_list = []
        
        self.screen_scroll = 0
        self.total_scroll = 0
        self.relative_scroll = 0
        
        self.object_group = pygame.sprite.Group()
        self.wall_group = pygame.sprite.Group()
        
        self.tile_img_list = []
        self.laser = Laser()
        self.laser_position = 0
        
        self.generation = global_counter
        
    def load_tiles(self):    
        for x in range(TILE_TYPES):
            img = pygame.image.load(MAP_TILES_FILE_PATH.format(x))
            img = pygame.transform.scale(img, (int(TILE_SIZE), int(TILE_SIZE)))
            self.tile_img_list.append(img)
              
    def generate_ui_controller(self):
        self.ui = UIController()
        self.ui.set_screen_ui(self.game_mode)
    
    def generate_world_data(self):
        self.world_data = []
        self.still_list = []
        tile_id = 0
        self.num_items = 0
        for row in range(ROWS):
            r = [-1] * COLS
            self.world_data.append(r)

        with open(self.map_file_path, newline='') as mapfile:
            reader = csv.reader(mapfile, delimiter=',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    self.world_data[x][y] = int(tile)
        
        for y, row in enumerate(self.world_data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    x_pos = x * TILE_SIZE
                    y_pos = y * TILE_SIZE
                    
                    img = self.tile_img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x_pos
                    img_rect.y = y_pos
                    tile_data = (img, img_rect, x_pos)
                    
                    self.still_list.append(tile_data)
                    
                    if tile <= 15:
                        #Create Wall Tile
                        self.wall_list.append(tile_data)
                        self.world_list.append(tile_data)
                        self.const_world_list.append(tile_data)
                    if tile == 16:
                        self.world_list.append(tile_data)
                        self.const_world_list.append(tile_data)    
                    elif tile >= HAZARD_TILE_MIN and tile <= HAZARD_TILE_MAX:
                        #Create Hazard Object
                        h_type = tile - HAZARD_TILE_MIN
                        hazard = Hazard(tile_id, x_pos, y_pos, h_type)
                        self.object_group.add(hazard)
                    elif tile >= BG_TILE_MIN and tile <= BG_TILE_MAX:
                        #Create Background Tile
                        self.bg_list.append(tile_data)
                        self.world_list.append(tile_data)
                        self.const_world_list.append(tile_data)
                    elif tile == ITEM_TILE_NUM:
                        #Create Item Object
                        item = Item(tile_id, x_pos, y_pos)
                        self.object_group.add(item)
                        self.num_items += 1
                    elif tile == GOAL_TILE_NUM:
                        #Create Goal Object
                        goal = Goal(tile_id, x_pos, y_pos)
                        self.goal_position = x_pos
                        self.object_group.add(goal)
                    elif tile == PLAYER_START_TILE:
                        #Store Player Start Coordinates
                        self.player_start_position_x = x_pos
                        self.player_start_position_y = y_pos

                    tile_id += 1
                   
                    
    def generate_player(self, p_id, sprite_id= 0, p_name= -1, p_type= 'Player'):
        if p_name == -1:
            p_name = self.get_name()
            
        player = Player(p_id= p_id,
                             x= self.player_start_position_x,
                             y= self.player_start_position_y,
                             sprite_id= sprite_id,
                             p_name= p_name,
                             p_type= p_type,
                             goal_position= self.goal_position)
        
        return player
                    

    def update_markers(self):
        # -- Update Markers
        for marker in self.marker_list:
            marker.draw()
                    
    
    def update_laser(self):
        self.laser_position = self.laser.update()
    
    def update_ui(self,data):
        self.ui.update_labels(data)
                    
    def draw_background(self):
        screen.fill(SCREEN_BACKGROUND_COLOUR)
                    
                    
    def draw_world(self):
        self.draw_background()
        for n, tile in enumerate(self.world_list):
            tile[1][0] = tile[2] + self.relative_scroll
            if (0 - TILE_SIZE) < tile[1][0] < (SCREEN_WIDTH + TILE_SIZE) and (0 - TILE_SIZE) < tile[1][1] < (SCREEN_HEIGHT):
                screen.blit(tile[0], tile[1])
                
    def draw_still(self):
        self.draw_background()
        for n, tile in enumerate(self.still_list):
            tile[1][0] = tile[2] + self.relative_scroll
            screen.blit(tile[0], tile[1])
            
        self.ui.draw()
        return self.ui.update()
                
    
    def update(self):
        self.draw_world()
        self.object_group.update()
        self.update_markers()
        if self.game_mode == 3 or self.game_mode == 5:
            self.update_laser()
            
        self.ui.draw()
        return self.ui.update()
    
    def update_hidden(self):
        self.laser_position = self.laser.update_hidden()


class Player(pygame.sprite.Sprite):
    def __init__(self, p_id, x = PLAYER_START_POS_X, y = PLAYER_START_POS_Y, sprite_id = 0, p_name = "", p_type = 'Player', goal_position = 0, hidden = False):
        super().__init__()
        
        # -- General
        self.player_id = p_id
        self.player_tag = "{} {}".format(p_name,p_id)
        self.player_type = p_type
        self.is_alive = True
        self.score = 0
        self.fitness = 0
        self.collected_item_list = []
        self.collected_goal = False
        self.distance_travelled = 0
        self.prev_distance_travelled = 0
        self.time_score = 0.0
        
        self.goal_position = goal_position
        self.distance_to_target = 0
        self.prev_distance_to_target = 0
        self.total_scroll = 0
        self.p_type = p_type
        
        if self.p_type == 'Player':
            self.followed = True
            self.name_tag_active = False
        else:
            self.followed = False
            self.name_tag_active = True
            
        if self.p_type == 'Smarty':
            self.scan_active = True
        else:
            self.scan_active = False
            
            
        # -- Visual
        self.frame_list = []
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        
        self.log("Creating Sprite From Frames...")
        try:
            temp_list = []
            
            for i in range(DYNAMIC_ANIM_FRAME_COUNT):
                sprite_file_path = DYNAMIC_SPRITE_FILE_PATH.format(DYNAMIC_SPRITE_FOLDER_LIST[sprite_id],DYNAMIC_SPRITE_ANIM_FRAME_LIST[i])
                self.log("Loading Animation Frame: {}", {sprite_file_path})
                
                img = pygame.image.load(sprite_file_path)
                img = pygame.transform.scale(img, (int(img.get_width() * SPRITE_SCALING_PLAYER), int(img.get_height() * SPRITE_SCALING_PLAYER)))
                temp_list.append(img)
            
            self.frame_list.append(temp_list)
            temp_list = []
            
            for i in range(DYNAMIC_STATIC_FRAME_COUNT):
                sprite_file_path = DYNAMIC_SPRITE_FILE_PATH.format(DYNAMIC_SPRITE_FOLDER_LIST[sprite_id],DYNAMIC_SPRITE_STATIC_FRAME_LIST[i])
                self.log("Loading Static Frame: {}", {sprite_file_path})
                
                img = pygame.image.load(sprite_file_path)
                img = pygame.transform.scale(img, (int(img.get_width() * SPRITE_SCALING_PLAYER), int(img.get_height() * SPRITE_SCALING_PLAYER)))
                temp_list.append(img)
            
            self.frame_list.append(temp_list)
            self.log("Sprite Created Successfully!")
            
        except FileNotFoundError:
            self.frame_list = []
            temp_list = []
            
            for i in range(DYNAMIC_ANIM_FRAME_COUNT):
                img = pygame.image.load(ERROR_SPRITE_FILE_PATH.format(DYNAMIC_SPRITE_ANIM_FRAME_LIST[i]))
                img = pygame.transform.scale(img, (int(img.get_width() * SPRITE_SCALING_PLAYER), int(img.get_height() * SPRITE_SCALING_PLAYER)))
                temp_list.append(img)
            
            self.frame_list.append(temp_list)
            temp_list = []
            
            for i in range(DYNAMIC_STATIC_FRAME_COUNT):
                img = pygame.image.load(ERROR_SPRITE_FILE_PATH.format(DYNAMIC_SPRITE_STATIC_FRAME_LIST[i]))
                img = pygame.transform.scale(img, (int(img.get_width() * SPRITE_SCALING_PLAYER), int(img.get_height() * SPRITE_SCALING_PLAYER)))
                temp_list.append(img)
            
            self.frame_list.append(temp_list)
            self.log("!!! Error Creating Sprite, Zombie created !!!")

        self.image = self.frame_list[1][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.hit_rect = self.rect.inflate(-self.width / 2, 0)
        self.rect.center = (x,y)
        
        # -- Action
        self.moving_left = False
        self.moving_right = False
        self.speed = PLAYER_GROUND_SPEED
        self.x_direction = 1
        self.flip = False
        self.vel_y = 0
        self.jump = False
        self.is_in_air = True
        
        # -- Name Tag
        self.name_tag = UINametag(e_id= self.player_id,
                                    text= self.player_tag,
                                    position= (0,0),
                                    active= self.name_tag_active)
        
        # -- Scanning
        self.scan_active = True
        
        self.scan_top_f = False
        self.scan_mid_f = False
        self.scan_bot_f = False
        self.scan_mid_r = False
        self.scan_x_f = 0
        self.scan_x_r = 0
        self.scan_y = 0
        self.scan_dot_radius = SCAN_DOT_RADIUS
        self.scan_dot_thickness = SCAN_DOT_THICKNESS
        
        self.scan_ground = False
        self.scan_ground_tolerance = GROUND_TOLERANCE
        self.scan_ground_rect = (0, 0, 0, 0)
        
        
        self.const_x = x
        self.relative_scroll = 0
        
        self.hidden = hidden
        self.output_j = 0
        self.output_w = 0
        
    def update_animation(self):
        if self.is_in_air:
            if self.vel_y < -PLAYER_PARABOLIC_STILL:
                #Jumping
                self.image = self.frame_list[1][1]
            elif self.vel_y > PLAYER_PARABOLIC_STILL:
                #Falling
                self.image = self.frame_list[1][2]
            else:
                #Parabolic Still
                self.image = self.frame_list[1][3]
                
        elif self.moving_left or self.moving_right:
            #Update frame
            self.image = self.frame_list[0][self.frame_index]

            #Check if enough time has passed since last frame update
            if pygame.time.get_ticks() - self.last_frame_update > PLAYER_ANIMATION_COOLDOWN:
                self.last_frame_update = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.frame_list[0]):
                    self.frame_index = 0
        else:
            self.image = self.frame_list[1][0]        
        
    def log(self, text = "", data = {}):
        msg = text.format(*data)
        
        if SHOW_ALL_PLAYER_LOGS:
            print("[P: {tag}] {msg}".format(tag= self.player_tag, msg= msg))
        
        if SHOW_CLOSEST_PLAYER_LOGS and self.followed:
            print("[Closest is {tag}] {msg}".format(tag= self.player_tag, msg= msg))
                
    def get_name_tag_pos(self): return ((self.get_center_x() - (self.name_tag.width // 2)),(self.rect.top - (self.name_tag.height + 10)))
    
    def get_center_x(self): return self.rect.left + (self.rect.width / 2)
    
    def get_center_y(self): return self.rect.top + (self.rect.height / 2) 
    
    def scan(self):
        if self.scan_active:
            if self.x_direction == 1:
                self.scan_x_f = self.rect.right + (TILE_SIZE // 2)
                self.scan_x_r = self.rect.left - (TILE_SIZE // 2)
            else:
                self.scan_x_f = self.rect.left - (TILE_SIZE // 2)
                self.scan_x_r = self.rect.right + (TILE_SIZE // 2)
                
            self.scan_y = self.rect.bottom - (TILE_SIZE // 2)
            
            self.scan_top_f = 0
            self.scan_mid_f = 0
            self.scan_bot_f = 0
            self.scan_mid_r = 0
            self.scan_ground = False
            
            for obj in world.wall_list:
                if self.rect.x + 100 > obj[1].x > self.rect.x - 100:
                    if obj[1].collidepoint((self.scan_x_f, self.scan_y - TILE_SIZE)):
                        self.scan_top_f = 1

                    if obj[1].collidepoint((self.scan_x_f, self.scan_y)):
                        self.scan_mid_f = 1

                    if obj[1].collidepoint((self.scan_x_f, self.scan_y + TILE_SIZE)):
                        self.scan_bot_f = 1

                    #REAR VIEW
                    if obj[1].collidepoint((self.scan_x_r, self.scan_y)):
                        self.scan_mid_r = 1

                    if obj[1].colliderect(self.scan_ground_rect):
                        self.scan_ground = True
                
            for obj in world.object_group.sprites():
                #check if top dot is active, and set scan_top to object_type
                if self.rect.x + 100 > obj.rect.x > self.rect.x - 100:
                    if obj.rect.collidepoint((self.scan_x_f, self.scan_y - TILE_SIZE)):
                        if obj.type == 'hazard':
                            self.scan_top_f = -1
                        
                    #check if middle dot is active, and set scan_mid to object_type
                    if obj.rect.collidepoint((self.scan_x_f, self.scan_y)):
                        if obj.type == 'hazard':
                            self.scan_mid_f = -1
                        
                    #check if bottom dot is active, and set scan_bot to object_type
                    if obj.rect.collidepoint((self.scan_x_f, self.scan_y + TILE_SIZE)):
                        if obj.type == 'hazard':
                            self.scan_bot_f = -1
                        
                    #check if rear dot is active, and set scan_mid_r to object_type
                    if obj.rect.collidepoint((self.scan_x_r, self.scan_y)):
                        if obj.type == 'hazard':
                            self.scan_mid_r = -1
                        
            
            
        else:
            return False
            
    def draw_scan_dots(self):

        radius = 5
        thickness = 2
         
        #top dot
        if self.scan_top_f == -1: # scanned a hazard
            pygame.draw.circle(screen, (255,0,0), (self.scan_x_f, self.scan_y - TILE_SIZE), radius, 0)
        elif self.scan_top_f == 1: # scanned the ground
            pygame.draw.circle(screen, (255,255,255), (self.scan_x_f, self.scan_y - TILE_SIZE), radius, 0)
        else:
            pygame.draw.circle(screen, (255,255,255), (self.scan_x_f, self.scan_y - TILE_SIZE), radius, thickness)
            
        
        #middle dot
        if self.scan_mid_f == -1: # scanned a hazard
            pygame.draw.circle(screen, (255,0,0), (self.scan_x_f, self.scan_y), radius, 0)
        elif self.scan_mid_f == 1: # scanned the ground
            pygame.draw.circle(screen, (255,255,255), (self.scan_x_f, self.scan_y), radius, 0)
        else:
            pygame.draw.circle(screen, (255,255,255), (self.scan_x_f, self.scan_y), radius, thickness)
        
        #bottom dot
        if self.scan_bot_f == -1: # scanned a hazard
            pygame.draw.circle(screen, (255,0,0), (self.scan_x_f, self.scan_y + TILE_SIZE), radius, 0)
        elif self.scan_bot_f == 1: # scanned the ground
            pygame.draw.circle(screen, (255,255,255), (self.scan_x_f, self.scan_y + TILE_SIZE), radius, 0)
        else:
            pygame.draw.circle(screen, (255,255,255), (self.scan_x_f, self.scan_y + TILE_SIZE), radius, thickness)
            
        # rear view
        if self.scan_mid_r == -1: # scanned a hazard
            pygame.draw.circle(screen, (255,0,0), (self.scan_x_r, self.scan_y), radius, 0)
        elif self.scan_mid_r == 1: # scanned the ground
            pygame.draw.circle(screen, (255,255,255), (self.scan_x_r, self.scan_y), radius, 0)
        else:
            pygame.draw.circle(screen, (255,255,255), (self.scan_x_r, self.scan_y), radius, thickness)
    
            
        #ground dot
        if self.scan_ground: # did not scan the ground
            pygame.draw.rect(screen, (255,255,255), self.scan_ground_rect)
        else: # scanned the ground
            pygame.draw.rect(screen, (255,255,255), self.scan_ground_rect, width= 1)
          
    def move(self):
        if self.is_alive:
            global world
            dx = 0
            dy = 0
            self.prev_distance = self.distance_travelled

            if self.moving_left:
                dx = -self.speed
                self.x_direction = -1
                self.flip = True

            if self.moving_right:
                dx = self.speed
                self.x_direction = 1
                self.flip = False

            if self.jump and not self.is_in_air:
                self.vel_y = -PLAYER_JUMP_IMPULSE
                self.jump = False
                #self.is_in_air = True
            elif self.jump and self.is_in_air:
                self.jump = False

            self.vel_y += GRAVITY_CONSTANT
            if self.vel_y > PLAYER_TERMINAL_VELOCITY:
                self.vel_y = PLAYER_TERMINAL_VELOCITY
            dy += self.vel_y


            if self.scan_ground:
                self.is_in_air = False
            else: 
                self.is_in_air = True
                
            for tile in world.wall_list:
                if self.rect.x + 100 > tile[1].x > self.rect.x - 100:
                    if tile[1].colliderect(self.hit_rect.x + dx, self.hit_rect.y, self.width // 2, self.height):
                        dx = 0

                    if tile[1].colliderect(self.hit_rect.x, self.hit_rect.y + dy, self.width // 2, self.height):
                        if self.vel_y < 0:
                            self.vel_y = 0
                            dy = tile[1].bottom - self.rect.top

                        elif self.vel_y >= 0:
                            self.vel_y = 0
                            dy = tile[1].top - self.rect.bottom
                            #self.is_in_air = False
            
            if not self.is_in_air:
                self.distance_travelled += abs(dx)
            
            if not self.hidden:
                self.const_x += dx
                self.rect.y += dy
                #self.distance_travelled += abs(dx)

                if 0 < self.rect.x < world.right_boundary:
                    if self.relative_scroll - dx >= 0:
                        self.relative_scroll = 0
                    else:
                        if not dx >= 0:
                            self.relative_scroll -= dx
                elif world.left_boundary < self.rect.x < SCREEN_WIDTH:
                    if self.relative_scroll - dx <= -world.scroll_cap:
                        self.relative_scroll = -world.scroll_cap
                    elif self.relative_scroll - dx >= 0:
                        self.relative_scroll = 0
                    else:
                        if not dx <= 0:
                            self.relative_scroll -= dx

                if self.followed:
                    if self.p_type == 'Player':
                        world.relative_scroll = self.relative_scroll
                    else:
                        if self.relative_scroll < world.relative_scroll: 
                           world.relative_scroll = self.relative_scroll

                self.rect.x = self.const_x + world.relative_scroll

                self.hit_rect.center = self.rect.center

                self.distance_to_target = abs(world.goal_position - self.rect.x)

                self.scan_ground_rect = (self.rect.left + (self.rect.width // 4), self.rect.bottom + self.scan_ground_tolerance, self.rect.width // 2, 4)

                self.name_tag.update_value(self.get_name_tag_pos())
            
            else:
                self.const_x += dx
                self.rect.y += dy
                self.rect.x = self.const_x
                self.hit_rect.center = self.rect.center
                self.distance_to_target = abs(world.goal_position - self.rect.x)
                self.scan_ground_rect = (self.rect.left + (self.rect.width // 4), self.rect.bottom + self.scan_ground_tolerance, self.rect.width // 2, 4)

    def die(self, msg):
        global world
        if self.is_alive:
            self.is_alive = False
            self.followed = False
            world.create_death_marker(self)
            self.log("died by {}!",{msg})
        
    def check_collisions(self):
        global world
        if self.is_alive:
            
            hit_list = pygame.sprite.spritecollide(self, world.object_group, False)
            for obj in hit_list:
                if obj.rect.colliderect(self.hit_rect):
                    if obj.type == 'hazard':
                        self.die(obj.hazard_type)
                        return -1
                    elif obj.type == 'item':
                        if not any(item_id == obj.object_id for item_id in self.collected_item_list):
                            self.score += ITEM_SCORE
                            self.collected_item_list.append(obj.object_id)
                            self.log("Score: {}",{self.score})
                            return 1
                    elif obj.type == 'goal':
                        if not self.collected_goal:
                            self.score += GOAL_SCORE
                            self.collected_goal = True
                            self.log("Score: {}",{self.score})
                            return 2
            
            if self.score >= ((world.num_items * ITEM_SCORE) + GOAL_SCORE):
                self.die("winning")
                print("died by winning?")
                return -1
            
            #Kill the player if they get caught by the laser
            if self.p_type == 'Smarty':
                if self.rect.x <= world.laser_position:
                    self.die('the laser')
                    return -2
                
            return False
        else:
            return False
            
    def get_progress(self):
        if self.is_alive:
            if self.distance_travelled > self.prev_distance:
                return True
            else:
                return False
        else: 
            return False 
    
    def get_is_moving(self):
        if self.moving_right:
            return 1
        elif self.moving_left:
            return -1
        else:
            return 0
        
    def get_is_on_ground(self):
        if self.is_in_air:
            return 0
        else:
            return 1
                
    def draw(self):
        global world
        if (world.only_show_closest_player and self.followed) or not world.only_show_closest_player:
            screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

            if SHOW_COLLISION_BOXES:
                pygame.draw.rect(screen, COLLISION_BOX_COLOUR, self.hit_rect, width= 2)

            if HIGHLIGHT_CLOSEST_PLAYER and self.followed:
                pygame.draw.rect(screen, HIGHLIGHT_COLOUR, self.rect, width= 2)

            self.name_tag.update()
            
 
    def update(self):
        self.move()
        self.update_animation()
        collide = self.check_collisions()
        self.scan()
        self.draw()
        return collide
    
    def update_hidden(self):
        self.move()
        collide = self.check_collisions()
        self.scan()
        return collide
        
        
class Item(pygame.sprite.Sprite):
    def __init__(self, i_id, x = 0, y = 0):
        super().__init__()
        
        self.object_id = i_id
        
        self.frame_list = []
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.type = 'item'
        
        self.log("Creating Sprite From Frames...")
        for i in range(ITEM_ANIM_FRAME_COUNT):
                sprite_file_path = ITEM_SPRITE_FILE_PATH.format(i)
                self.log("Loading Animation Frame: {}", {sprite_file_path})
                
                img = pygame.image.load(sprite_file_path)
                #img = pygame.transform.scale(img, (int(img.get_width() * SPRITE_SCALING_ITEM), int(img.get_height() * SPRITE_SCALING_ITEM)))
                img = pygame.transform.scale(img, (int(TILE_SIZE), int(TILE_SIZE)))
                self.frame_list.append(img)
        self.log("Sprite Created Successfully!")
        
        self.image = self.frame_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        self.const_x = x
        self.const_y = y        
        
    def update_animation(self):
        if ANIMATE_COOKIES:
            #Update frame
            self.image = self.frame_list[self.frame_index]

            #Check if enough time has passed since last frame update
            if pygame.time.get_ticks() - self.last_frame_update > MISC_ANIMATION_COOLDOWN:
                self.last_frame_update = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.frame_list):
                    self.frame_index = 0
                    
                    
    def log(self, text = "", data = {}):
        msg = text.format(*data)
        if SHOW_ITEM_LOGS:
            print("[IID: {}] {}".format(self.object_id,msg))
        
    def draw(self):
        global world
        self.rect.x = self.const_x + world.relative_scroll
        
        if SHOW_COLLISION_BOXES:
            pygame.draw.rect(screen, COLLISION_BOX_COLOUR, self.rect, width= 2)
                
        screen.blit(self.image, self.rect)
        
    def update(self):
        self.update_animation()
        self.draw()
              
    
class Goal(pygame.sprite.Sprite):
    def __init__(self, g_id, x = 0, y = 0):
        super().__init__()
        
        self.object_id = g_id
        
        self.frame_list = []
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.type = 'goal'
        
        self.log("Creating Sprite From Frames...")
        for i in range(GOAL_ANIM_FRAME_COUNT):
                sprite_file_path = GOAL_SPRITE_FILE_PATH.format(i)
                self.log("Loading Animation Frame: {}", {sprite_file_path})
                
                img = pygame.image.load(sprite_file_path)
                img = pygame.transform.scale(img, (int(TILE_SIZE), int(TILE_SIZE)))
                self.frame_list.append(img)
        self.log("Sprite Created Successfully!")
        
        self.image = self.frame_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        self.const_x = x
        
        
    def update_animation(self):
        if ANIMATE_COOKIES:
            #Update frame
            self.image = self.frame_list[self.frame_index]

            #Check if enough time has passed since last frame update
            if pygame.time.get_ticks() - self.last_frame_update > MISC_ANIMATION_COOLDOWN:
                self.last_frame_update = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.frame_list):
                    self.frame_index = 0
                    
                    
    def log(self, text = "", data = {}):
        msg = text.format(*data)
        if SHOW_GOAL_LOGS:
            print("[GID: {}] {}".format(self.object_id,msg))
        
    def draw(self):
        global world
        
        self.rect.x = self.const_x + world.relative_scroll
        world.goal_position = self.rect.x
        
        if SHOW_COLLISION_BOXES:
            pygame.draw.rect(screen, COLLISION_BOX_COLOUR, self.rect, width= 2)
         
        screen.blit(self.image, self.rect)
        
    def update(self):
        self.update_animation()
        self.draw()
        
        
class Marker(pygame.sprite.Sprite):
    def __init__(self, x = 0, y = 0, marker_type = 1, p_name = ""):
        global world
        super().__init__()
        
        self.player_name = p_name
        self.object_id = len(world.marker_list)
        
        img = pygame.image.load(MARKER_SPRITE_FILE_PATH.format(marker_type))
        self.image = pygame.transform.scale(img, (int(TILE_SIZE), int(TILE_SIZE)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.log("Marker Generated for {}",{self.player_name})
        
        self.const_x = x
        
    def log(self, text = "", data = {}):
        msg = text.format(*data)
        if SHOW_MARKER_LOGS:
            print("[MID: {}] {}".format(self.object_id,msg))
        
    def draw(self):
        global world
        self.rect.x = self.const_x + world.relative_scroll
        screen.blit(self.image, self.rect)
        

class Hazard(pygame.sprite.Sprite):
    def __init__(self, h_id, x = 0, y = 0, hazard_type = 0):
        super().__init__()
        
        self.object_id = h_id
        self.hazard_type = HAZARD_TYPE_LIST[hazard_type]
        self.type = 'hazard'
        
        img = pygame.image.load(HAZARD_SPRITE_FILE_PATH.format(self.hazard_type))
        self.image = pygame.transform.scale(img, (int(TILE_SIZE), int(TILE_SIZE)))
        self.rect = self.image.get_rect()
        
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        
        self.const_x = x
                    
                    
    def log(self, text = "", data = {}):
        msg = text.format(*data)
        if SHOW_HAZARD_LOGS:
            print("[HID: {}] {}".format(self.object_id,msg))
        
    def draw(self):
        global world
        self.rect.x = self.const_x + world.relative_scroll
        
        if SHOW_COLLISION_BOXES:
            pygame.draw.rect(screen, COLLISION_BOX_COLOUR, self.rect, width= 2)
         
        screen.blit(self.image, self.rect)
        
    def update(self):
        self.draw()
    
class Laser():
    def __init__(self):
        self.speed = LASER_MOVE_SPEED
        self.x_pos = 0
        self.const_x = 0
        self.width = LASER_WIDTH
        
    def draw(self):
        global world
        self.const_x += self.speed 
        self.x_pos = self.const_x + world.relative_scroll
        pygame.draw.line(surface= screen,
                         color= LASER_COLOUR,
                         start_pos= (self.x_pos, 0),
                         end_pos= (self.x_pos, SCREEN_HEIGHT),
                         width= self.width)
        return self.x_pos
        
    def update(self):
        return self.draw()
    
    def update_hidden(self):
        self.x_pos += self.speed
        return self.x_pos
 

class UINametag():
    def __init__(self, e_id, text= 'UNNAMED', position= (0,0), active= True, colour= UI_FONT_COLOUR, font= CHARACTER_FONT, font_size= UI_FONT_SIZE, background= False, bg_colour= (0,0,0), antialias= True):
        self.font = pygame.font.SysFont(font, font_size)
        
        self.type = 'nametag'
        self.id = e_id
        self.label = text
        self.position = position
        self.antialias = antialias
        self.colour = colour
        self.active = active
        
        #Work In Progress
        self.bg_colour = bg_colour
        self.background = background
        
        self.surface = self.font.render(self.label, self.antialias, self.colour)
        self.width = self.surface.get_width()
        self.height = self.surface.get_height()
        
    def update_value(self, new_value):
        self.position = new_value
        
    def update(self):
        if self.active:
            self.draw()
        
    def draw(self):
        screen.blit(self.surface, self.position)
        
class UIText():
    def __init__(self, e_id, value= '', text= '{}', position= (0,0), active= True, colour= UI_FONT_COLOUR, font= CHARACTER_FONT, font_size= UI_FONT_SIZE, background= False, bg_colour= (0,0,0), antialias= True):
        self.font = pygame.font.SysFont(font, font_size)
        
        self.type = 'text'
        self.id = e_id
        self.value = value
        self.text = text
        self.label = self.text.format(value)
        self.position = position
        self.active = active
        self.antialias = antialias
        self.colour = colour
        
        #Work In Progress
        self.bg_colour = bg_colour
        self.background = background
        
    def update_value(self, new_value):
        self.value = new_value
        
    def update_label(self):
        self.label = self.text.format(self.value)
        
    def update(self):
        self.update_label()
        
        if self.active:
            self.draw()
        
    def draw(self):
        self.surface = self.font.render(self.label, self.antialias, self.colour)
        screen.blit(self.surface, self.position)
    
class UIButton():
    def __init__(self, e_id= 'button', button_action= 'exit', text= "Example Button", position= (0,0), width= 100, height= 100, colour= UI_DEFAULT_BUTTON_COLOUR, pressed_colour= UI_DEFAULT_BUTTON_PRESSED_COLOUR, font= CHARACTER_FONT, text_colour= UI_FONT_COLOUR, border_colour= UI_DEFAULT_BUTTON_PRESSED_COLOUR):
        self.width = width
        self.height = height
        self.rect = pygame.Rect(position,(width,height))
        self.clicked = False
        self.id = e_id
        self.type = 'button'
        self.font = pygame.font.SysFont(font, self.height//2)
        self.text = text
        w, h = self.font.size(self.text)
        self.text_width = w
        self.text_colour = text_colour
        self.border_colour = border_colour
        
        self.colour = colour
        self.pressed_colour = pressed_colour
        
        self.button_action = button_action
        
    def draw(self):
            
        for side in range(4):
            pygame.draw.rect(screen, self.border_colour, (self.rect.left - side, self.rect.top - side, self.width, self.height), 1)
        
        if self.clicked:
            pygame.draw.rect(screen, self.pressed_colour, self.rect)
        else:
            pygame.draw.rect(screen, self.colour, self.rect)
            
        self.text_surface = self.font.render(self.text, True, self.text_colour)
        self.text_rect = self.text_surface.get_rect(center= self.rect.center)
        screen.blit(self.text_surface, self.text_rect)
            
    
    def update_value(self, new_value):
        self.text = new_value
        
    def get_action(self):
        action = False
        
        pos = pygame.mouse.get_pos()
        
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = self.button_action
                self.clicked = True
                
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
            
        return action
        
    
    def update(self):
        self.draw()

class UIController():
    def __init__(self):
        pygame.font.init()
        self.element_list = {}
        self.game_mode = 0
        
    def set_screen_ui(self, game_mode= 0):
        self.element_list = {}
        self.game_mode = game_mode
        
        if self.game_mode == 1: #If we are in single player mode.
            self.set_singleplayer_ui()
        elif self.game_mode == 2: # If we are in dummy mode.
            self.set_dummy_ui()
        elif self.game_mode == 3: # If we are in smarty mode
            self.set_smarty_ui()
        elif self.game_mode == 4: # If we are in the start menu
            self.set_start_ui()
        elif self.game_mode == 5: # If we are in the start menu
            self.set_smarty_background_ui()
        elif self.game_mode == 6: # If we are in the game start screen
            self.set_game_start_ui()
        elif self.game_mode == 7: # If we are in the game start screen
            self.set_game_end_ui()
        else:
            self.set_start_ui()
            
        
        #Debug mode - Can be used to show debug on screen
        key = 'debug'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= '[Debug Enabled] {}',
                            position= (0, SCREEN_HEIGHT - 50),
                            active= IS_DEBUG)
        
        self.element_list[key] = ui_object
    
    def set_singleplayer_ui(self):
        #Score of player
        key = 'score'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Score: {}',
                            position= (0,2),
                            active= True)
        self.element_list[key] = ui_object
        
        #Distance to target of player
        key = 'distance'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Timescore: {}',
                            position= (0,30),
                            active= True)
        self.element_list[key] = ui_object
        
        key = 'restart_button'
        ui_object = UIButton(e_id= key,
                             button_action= 'restart',
                             text= 'Restart',
                             position= (20, SCREEN_HEIGHT - 300),
                             width= 200,
                             height= 50)
        self.element_list[key] = ui_object
        
        key = 'menu_button'
        ui_object = UIButton(e_id= key,
                             button_action= 'menu',
                             text= 'Return to Menu',
                             position= (20, SCREEN_HEIGHT - 200),
                             width= 200,
                             height= 50)
        self.element_list[key] = ui_object
        
    def set_game_start_ui(self):
        #Score of player
        key = 'text'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= '[Press Space to Start...]',
                            position= ((SCREEN_WIDTH // 2) - 200, (SCREEN_HEIGHT // 2) + 250),
                            active= True)
        self.element_list[key] = ui_object
        
        key = 'menu_button'
        ui_object = UIButton(e_id= key,
                             button_action= 'menu',
                             text= 'Return to Menu',
                             position= (20, SCREEN_HEIGHT - 200),
                             width= 200,
                             height= 50)
        self.element_list[key] = ui_object
        
    def set_game_end_ui(self):
        #Score of player
        global cur_timescore, cur_score
        
        key = 'score'
        ui_object = UIText(e_id= key,
                            value= cur_score,
                            text= 'Score: {}',
                            position= ((SCREEN_WIDTH // 2) - 200, (SCREEN_HEIGHT // 2) + 50),
                            active= True)
        self.element_list[key] = ui_object
        
        key = 'timescore'
        ui_object = UIText(e_id= key,
                            value= cur_timescore,
                            text= 'Timescore: {}',
                            position= ((SCREEN_WIDTH // 2) - 200, (SCREEN_HEIGHT // 2) + 100),
                            active= True)
        self.element_list[key] = ui_object
        
        key = 'text'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Game Over',
                            position= ((SCREEN_WIDTH // 2) - 200, (SCREEN_HEIGHT // 2) - 50),
                            active= True)
        self.element_list[key] = ui_object
        
        key = 'restart_button'
        ui_object = UIButton(e_id= key,
                             button_action= 'restart',
                             text= 'Restart',
                             position= ((SCREEN_WIDTH // 2) - 200, (SCREEN_HEIGHT // 2) + 150),
                             width= 200,
                             height= 50)
        self.element_list[key] = ui_object
        
        key = 'menu_button'
        ui_object = UIButton(e_id= key,
                             button_action= 'menu',
                             text= 'Return to Menu',
                             position= ((SCREEN_WIDTH // 2) - 200, (SCREEN_HEIGHT // 2) + 250),
                             width= 200,
                             height= 50)
        self.element_list[key] = ui_object
            
    def set_dummy_ui(self):
        #Name of closest dummy
        key = 'name'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Name: {}',
                            position= (0,0),
                            active= True)
        self.element_list[key] = ui_object
        
        #Score of closest dummy
        key = 'score'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Score: {}',
                            position= (0,100),
                            active= True)
        self.element_list[key] = ui_object
        
        #Distance to target of closest dummy
        key = 'distance'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Timescore: {}',
                            position= (0,200),
                            active= True)
        self.element_list[key] = ui_object
        
        key = 'alive'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Alive: {}',
                            position= (SCREEN_WIDTH - 200,0),
                            active= True)
        self.element_list[key] = ui_object
        
        key = 'closest_toggle_button'
        ui_object = UIButton(e_id= key,
                             button_action= 'only_show_closest_toggle',
                             text= 'Show / Hide',
                             position= (20, SCREEN_HEIGHT - 200),
                             width= 200,
                             height= 50)
        self.element_list[key] = ui_object
        
        key = 'restart_button'
        ui_object = UIButton(e_id= key,
                             button_action= 'restart',
                             text= 'Restart',
                             position= (20, SCREEN_HEIGHT - 300),
                             width= 200,
                             height= 50)
        self.element_list[key] = ui_object
            
    def set_smarty_ui(self):
        global world
        # Name of closest smarty
        key = 'name'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Name: {}',
                            position= (10,0),
                            active= True)
        self.element_list[key] = ui_object
        
        #Score of closest smarty
        key = 'score'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Fitness: {}',
                            position= (10,50),
                            active= True)
        self.element_list[key] = ui_object
        
        #Distance to target of closest smarty
        key = 'distance'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Timescore: {}',
                            position= (10,100),
                            active= True)
        self.element_list[key] = ui_object
        
        #Current generation
        key = 'generation'
        ui_object = UIText(e_id= key,
                            value= world.generation,
                            text= 'Generation: {}',
                            position= (SCREEN_WIDTH - 300,0),
                            active= True)
        self.element_list[key] = ui_object
        
        key = 'alive'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Alive: {}',
                            position= (SCREEN_WIDTH - 300,50),
                            active= True)
        self.element_list[key] = ui_object    
        
        key = 'menu_button'
        ui_object = UIButton(e_id= key,
                             button_action= 'menu',
                             text= 'Return to Menu',
                             position= (20, SCREEN_HEIGHT - 200),
                             width= 200,
                             height= 50)
        self.element_list[key] = ui_object
        
    def set_smarty_hidden_ui(self):
        global world
        # Name of closest smarty
        key = 'name'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Name: {}',
                            position= (10,0),
                            active= True)
        self.element_list[key] = ui_object
        
        #Score of closest smarty
        key = 'fitness'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Score: {}',
                            position= (10,50),
                            active= True)
        self.element_list[key] = ui_object
        
        #Distance to target of closest smarty
        key = 'distance'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Timescore: {}',
                            position= (10,100),
                            active= True)
        self.element_list[key] = ui_object
        
        #Current generation
        key = 'generation'
        ui_object = UIText(e_id= key,
                            value= world.generation,
                            text= 'Generation: {}',
                            position= (SCREEN_WIDTH - 300,0),
                            active= True)
        self.element_list[key] = ui_object
        
        key = 'alive'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Alive: {}',
                            position= (SCREEN_WIDTH - 300,50),
                            active= True)
        self.element_list[key] = ui_object
        
        key = 'input_j'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Jump {}',
                            position= (SCREEN_WIDTH //2, (SCREEN_HEIGHT // 2) - 100),
                            active= True)
        self.element_list[key] = ui_object
        
        key = 'input_w'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Move {}',
                            position= (SCREEN_WIDTH //2, (SCREEN_HEIGHT // 2) - 150),
                            active= True)
        self.element_list[key] = ui_object
    
    def set_smarty_background_ui(self):
        global global_counter
        key = 'counter'
        ui_object = UIText(e_id= key,
                            value= global_counter,
                            text= 'Generation: {}',
                            position= (20, (SCREEN_HEIGHT // 2) + 100),
                            active= True)
        self.element_list[key] = ui_object
        
        key = 'remaining'
        ui_object = UIText(e_id= key,
                            value= global_counter,
                            text= '{a}/{b}'.format(a= '{}', b= GENERATIONS),
                            position= (20, (SCREEN_HEIGHT // 2) + 150),
                            active= True)
        self.element_list[key] = ui_object
        
        key = 'text'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'Cannot return to menu or exit while running...',
                            position= (20, (SCREEN_HEIGHT // 2) + 250),
                            active= True)
        self.element_list[key] = ui_object
    
    def set_start_ui(self):
        key = 'title'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= 'NeuroEvolution Playground',
                            position= (SCREEN_WIDTH / 2,100),
                            active= True)
        self.element_list[key] = ui_object
        
        key = 'singleplayer_button'
        ui_object = UIButton(e_id= key,
                             button_action= 'singleplayer',
                             text= 'Singleplayer',
                             position= (100, 100),
                             width= 400,
                             height= 100)
        self.element_list[key] = ui_object
        
        key = 'dummy_button'
        ui_object = UIButton(e_id= key,
                             button_action= 'dummy',
                             text= 'Dumb AI',
                             position= (100, 250),
                             width= 400,
                             height= 100)
        self.element_list[key] = ui_object
        
        key = 'smarty_button'
        ui_object = UIButton(e_id= key,
                             button_action= 'smarty',
                             text= 'Smart AI - Quick',
                             position= (100, 400),
                             width= 400,
                             height= 100)
        self.element_list[key] = ui_object
        
        key = 'long_button'
        ui_object = UIButton(e_id= key,
                             button_action= 'long',
                             text= 'Smart AI - Long',
                             position= (100, 550),
                             width= 400,
                             height= 100)
        self.element_list[key] = ui_object
        
        key = 'best_button'
        ui_object = UIButton(e_id= key,
                             button_action= 'best',
                             text= 'Smart AI - Best',
                             position= (600, 550),
                             width= 400,
                             height= 100)
        self.element_list[key] = ui_object
        
    def update_labels(self,data):
        #Updates label values from data
        #@params dictionary of {key:value}
        for d_key in data:
            for e_key in self.element_list:
                if e_key == d_key:
                    self.element_list[e_key].update_value(data[d_key])
        
    def draw(self):
        """
        Draws all UI elements loaded to the UI Controller
        @Param None
        """
        for key in self.element_list:
            self.element_list[key].update()
                             
    def update(self):
        for key in self.element_list:
            if self.element_list[key].type == 'button':
                action = self.element_list[key].get_action()
                if action != False:
                    return action
        
        return False


def run_singleplayer():
    global world, cur_timescore, cur_score
    world.set_game_mode(6)
    level_num = 1
    world.load_world(level_num)
    respawn = True
    timescore = 0.0
    collide = False
    started = False
    
    while not started:
        button = world.draw_still()
        
        for event in pygame.event.get():
            #quit
            if event.type == pygame.QUIT:
                run = False
                respawn = False
                started = True
                action = 'exit'
                break
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    started = True
                
        if button != False:
            if button == 'menu':
                run = False
                action = 'menu'
                return check_action(action)
        
        pygame.display.update()
        
    world.set_game_mode(1)
    world.load_world(level_num)
    
    while respawn:
        world.relative_scroll = 0
        player = world.generate_player(p_id= 1,
                                       sprite_id= 6,
                                       p_name= 'Player',
                                       p_type= 'Player')

        player.time_score = timescore
        
        # -- Begin Play
        run = True
        action = False
        print("\n --- Begin Play ---\n")

        while run:

            # -- Update Game
            clock.tick(GAME_FRAME_RATE)
            player.time_score += 1  
            timescore = player.time_score
            #button = False
            button = world.update()

            if button != False:
                if button == 'restart':
                    run = False
                    respawn = False
                    action = 'singleplayer'
                elif button == 'menu':
                    run = False
                    respawn = False
                    action = 'menu'

            # - Events
            for event in pygame.event.get():
                #quit
                if event.type == pygame.QUIT:
                    run = False
                    respawn = False
                    action = 'exit'

                if player.is_alive:
                    # -- Keyboard Press
                    if event.type == pygame.KEYDOWN:
                        if any(key == event.key for key in LEFT_KEYS):
                            player.moving_left = True
                        if any(key == event.key for key in RIGHT_KEYS):
                            player.moving_right = True
                        if any(key == event.key for key in UP_KEYS):
                            player.jump = True
                        if event.key == pygame.K_ESCAPE:
                            run = False

                    # -- Keyboard Release
                    if event.type == pygame.KEYUP:
                        if any(key == event.key for key in LEFT_KEYS):
                            player.moving_left = False
                        if any(key == event.key for key in RIGHT_KEYS):
                            player.moving_right = False

            if player.is_alive:
                collide = player.update()
                world.update_ui({'score': player.score,
                                'distance': player.time_score})
                if collide != False:
                    if collide < 0:
                        run = False
                    if collide == 2:
                        action = 'win'
                        
                        if timescore < SETTINGS['best_player_time']:
                            print(timescore)
                            SETTINGS['best_player_time'] = timescore
                            save_settings()
                            
                        cur_timescore = timescore
                        cur_score = player.score
                        print('Skill rating: {s}/{t} = {r}%'.format(s= cur_score, t= cur_timescore, r= (cur_score/cur_timescore) * 100))
                        run = False
                        respawn = False
                
            else:
                world.screen_scroll = 0
                run = False

            # -- Update World
            pygame.display.update()
    
    
    if action == 'win':
        run = True
        world.set_game_mode(7)
        world.load_world(level_num)
        button = False
        while run:
            button = world.draw_still()
        
            for event in pygame.event.get():
                #quit
                if event.type == pygame.QUIT:
                    run = False
                    action = 'exit'
                    break
                
            if button != False:
                if button == 'menu':
                    run = False
                    action = 'menu'
                elif button == 'restart':
                    run = False
                    action = 'singleplayer'


            pygame.display.update()
            
    return check_action(action)

def run_smarties(genomes, config):
    
    global world, global_counter
    world.set_game_mode(3)
    world.load_world(1)
    
    networks = []
    smarties = []
    ge = []
    times = []
    scores = []
    
    closest_tag = ''
    closest_index = 0
    closest_distance = -1
    closest_score = 0
    
    action = False
    
    for genome_id, genome in genomes:
        genome.fitness = 0
        
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        networks.append(net)
        
        sprite_id = random.randint(0,DYNAMIC_SPRITE_COUNT-2)
        smarty = world.generate_player(p_id= genome_id,
                                           sprite_id= sprite_id,
                                           p_type= 'Smarty')
        smarties.append(smarty)
        
        ge.append(genome)
    
    run = True
    while run and len(smarties) > 0:
        smarties_alive = len(smarties)
        clock.tick(GAME_FRAME_RATE)
        button = world.update()
        
        if button != False:
                if button == 'restart':
                    run = False
                    action = 'smarty'
                elif button == 'menu':
                    run = False
                    action = 'menu'
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                break
            
        closest_index = 0
        
        for n, smarty in enumerate(smarties):
            if smarty.is_alive:
                if smarty.const_x > smarties[closest_index].const_x:
                    closest_index = smarties.index(smarty)
                
                smarty.followed = False
                    
                    
        closest_smarty = smarties[closest_index]
        closest_smarty.followed = True
        closest_smarty.relative_scroll = world.relative_scroll - (closest_smarty.rect.x - (SCREEN_WIDTH // 2))
        closest_tag = closest_smarty.player_tag
        closest_distance = closest_smarty.distance_to_target
        closest_score = closest_smarty.fitness
        world.total_scroll = closest_smarty.total_scroll
               
        #Generate Inputs to character
        for n, smarty in enumerate(smarties):

            smarty.time_score += 1
            smarty_distance = smarty.distance_to_target
            #To move: send distance to goal, if on ground, if it's moving and it's distance travelled
            output = networks[smarties.index(smarty)].activate((smarty.get_is_on_ground(), smarty.scan_top_f, smarty.scan_mid_f, smarty.scan_bot_f, smarty.scan_mid_r ))
            
            #Activate movements based on NN outputs
            if output[0] > MOVE_BIAS:
                smarty.moving_right = True
                smarty.moving_left = False
            elif output[0] < -MOVE_BIAS:
                smarty.moving_right = False
                smarty.moving_left = True
            else:
                smarty.moving_right = False
                smarty.moving_left = False
                
            if output[1] > JUMP_BIAS:
                smarty.jump = True
            
            #Process inputs to character
            
            collide = smarty.update()
            
            if SHOW_MAKING_PROGRESS:
                smarty.log("[a: {a}] < [b: {b}] = [{c}]".format(a= smarty.distance_to_target, b= smarty.prev_distance_to_target, c= smarty.distance_to_target < smarty.prev_distance_to_target))
            
            #if smarty.get_progress():
                #ge[n].fitness += PROGRESS_FITNESS
                
            if smarty.scan_mid_f == 1 and smarty.scan_bot_f == 1: #If they're stuck against a wall, deduct fitness
                ge[n].fitness -= STUCK_PENALTY
                
            if smarty.scan_mid_r == 1:
                ge[n].fitness -= (STUCK_PENALTY / 2)
                
            if collide == 1: #If smarty hits an item
                ge[n].fitness += ITEM_FITNESS
            elif collide == 2: #If smarty hits the goal
                times.append(smarty.time_score)
                scores.append(smarty.score)
                ge[n].fitness = GOAL_FITNESS
                ge[n].fitness += (GOAL_FITNESS * ((smarty.score / smarty.time_score) * 100)) / 100
                collide = -1
                
            smarty.fitness = ge[n].fitness
                
            if collide < 0: #If smarty is dead, or dies
                if collide == -2: # smart died from the laser :(
                    ge[n].fitness -= LASER_PENALTY
                    
                list_index = smarties.index(smarty)
                ge[list_index].fitness -= 1
                networks.pop(list_index)
                ge.pop(list_index)
                smarties.pop(list_index)

                
        
        if SHOW_UI_DEBUG:
            print("name: {n} | index: {i} | distance: {d} | screen scroll: {ss}".format(n= closest_tag,
                                                                  i= closest_index,
                                                                  d= closest_distance,
                                                                  ss= world.screen_scroll))
            
        world.update_ui({'name': closest_tag,
                            'score': closest_smarty.fitness,
                            'distance': closest_smarty.time_score,
                            'alive': smarties_alive})
        
        closest_smarty.draw_scan_dots()
        
        world.update_ui({'debug': 'now:{a} > prev:{b} = {c}'.format(a= closest_smarty.distance_travelled, b= closest_smarty.prev_distance, c= closest_smarty.get_progress())})

        pygame.display.update()
        
    global_counter += 1
    
    if len(times) > 0:
        print('\n== times ==')
        print(times)
        average_time = sum(times) / len(times)
        print(average_time)
        print('\n== scores ==')
        print(scores)
        average_score = sum(scores) / len(scores)
        print(average_score)
        if average_time >= 0:
            SETTINGS['generation_average_time'] = average_time
            
    if action != False:
        return action

def run_smarties_hidden(genomes, config):
    
    global world, global_counter, global_loop
    world.set_game_mode(5)
    world.load_world(1)
    
    networks = []
    smarties = []
    ge = []
    times = []
    scores = []
    
    action = False
    
    for genome_id, genome in genomes:
        genome.fitness = 0
        
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        networks.append(net)
        
        sprite_id = random.randint(0,DYNAMIC_SPRITE_COUNT-2)
        smarty = world.generate_player(p_id= genome_id,
                                           sprite_id= sprite_id,
                                           p_type= 'Smarty')
        smarty.followed = False
        smarty.hidden = True
        
        smarties.append(smarty)
        
        ge.append(genome)
    
    run = True
    while run and len(smarties) > 0:
        smarties_alive = len(smarties)
        world.update_hidden()
               
        #Generate Inputs to character
        for n, smarty in enumerate(smarties):
            smarty.time_score += 1
            smarty_distance = smarty.distance_to_target
            #To move: send distance to goal, if on ground, if it's moving and it's distance travelled
            output = networks[smarties.index(smarty)].activate((smarty.get_is_on_ground(), smarty.scan_top_f, smarty.scan_mid_f, smarty.scan_bot_f, smarty.scan_mid_r ))
            
            smarty.output_w = output[0]
            smarty.output_j = output[1]
                
            #Activate movements based on NN outputs
            if output[0] > MOVE_BIAS:
                smarty.moving_right = True
                smarty.moving_left = False
            elif output[0] < -MOVE_BIAS:
                smarty.moving_right = False
                smarty.moving_left = True
            else:
                smarty.moving_right = False
                smarty.moving_left = False
                
            if output[1] > JUMP_BIAS:
                smarty.jump = True
            
            #Process inputs to character
            
            collide = smarty.update_hidden()
            
            #if smarty.get_progress():
                #ge[n].fitness += PROGRESS_FITNESS
            
            if smarty.scan_mid_f == 1 and smarty.scan_bot_f == 1: #If they're stuck against a wall, deduct fitness
                ge[n].fitness -= STUCK_PENALTY
                
            if smarty.scan_mid_r == 1:
                ge[n].fitness -= (STUCK_PENALTY / 2)
                
            if smarty.scan_mid_f == -1 or smarty.scan_top_f == -1:
                ge[n].fitness -= (STUCK_PENALTY / 2)
                
            if collide == 1: #If smarty hits an item
                ge[n].fitness += ITEM_FITNESS
            elif collide == 2: #If smarty hits the goal
                times.append(smarty.time_score)
                scores.append(smarty.score)
                ge[n].fitness = GOAL_FITNESS
                ge[n].fitness += (GOAL_FITNESS * ((smarty.score / smarty.time_score) * 100)) / 100
                collide == -1
            
            smarty.fitness = ge[n].fitness
                
            if collide < 0: #If smarty is dead, or dies
                if collide == -2: # smart died from the laser :(
                    ge[n].fitness -= LASER_PENALTY
                    
                list_index = smarties.index(smarty)
                ge[list_index].fitness -= 1
                networks.pop(list_index)
                ge.pop(list_index)
                smarties.pop(list_index)
        
        if len(smarties) > 0 and False:
            closest_smarty = smarties[0]

            world.update_ui({'name': closest_smarty.player_tag,
                            'score': closest_smarty.fitness,
                            'distance': closest_smarty.distance_travelled,
                            'alive': smarties_alive,
                            'input_j': closest_smarty.output_j,
                            'input_w': closest_smarty.output_w})

            world.update_ui({'debug': 'now:{a} > prev:{b} = {c}'.format(a= closest_smarty.distance_travelled, b= closest_smarty.prev_distance, c= closest_smarty.get_progress())})

            pygame.display.update()
            
    global_counter += 1
    global_loop += 1
    
    if len(times) > 0:
        print('\n== times ==')
        print(times)
        average_time = sum(times) / len(times)
        print(average_time)
        print('\n== scores ==')
        print(scores)
        average_score = sum(scores) / len(scores)
        print(average_score)
    
def run_dummy():
    global world, cur_timescore, cur_score
    world.set_game_mode(6)
    level_num = 1
    world.load_world(level_num)
    respawn = True
    timescore = 0.0
    collide = False
    started = False
    
    while not started:
        button = world.draw_still()
        
        for event in pygame.event.get():
            #quit
            if event.type == pygame.QUIT:
                run = False
                respawn = False
                started = True
                action = 'exit'
                break
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    started = True
                
        if button != False:
            if button == 'menu':
                run = False
                action = 'menu'
                return check_action(action)
        
        pygame.display.update()
        
    world.set_game_mode(1)
    world.load_world(level_num)
    
    while respawn:
        world.relative_scroll = 0
        dummy = world.generate_player(p_id= 1,
                                       sprite_id= 0,
                                       p_name= 'Dummy',
                                       p_type= 'Dummy')

        dummy.moving_right = True
        dummy.followed = True
        dummy.time_score = timescore
        
        # -- Begin Play
        run = True
        action = False
        print("\n --- Begin Play ---\n")

        while run:

            # -- Update Game
            clock.tick(GAME_FRAME_RATE)
            dummy.time_score += 1  
            timescore = dummy.time_score
            #button = False
            button = world.update()

            if button != False:
                if button == 'restart':
                    run = False
                    respawn = False
                    action = 'dummy'
                elif button == 'menu':
                    run = False
                    respawn = False
                    action = 'menu'

            # - Events
            for event in pygame.event.get():
                #quit
                if event.type == pygame.QUIT:
                    run = False
                    respawn = False
                    action = 'exit'


            if dummy.scan_top_f == 0 and dummy.scan_mid_f == 0 and dummy.scan_bot_f < 1:
                dummy.jump = True
            
            if dummy.scan_top_f != 0 and dummy.scan_mid_f != 0 and dummy.scan_bot_f != 0:
                if dummy.moving_right:
                    dummy.moving_right = False
                    dummy.moving_left = True
                elif dummy.moving_left:
                    dummy.moving_right = True
                    dummy.moving_left = False
            
            if dummy.scan_top_f == 0 and dummy.scan_mid_f != 0 and dummy.scan_bot_f != 0:
                dummy.jump = True
                
            if dummy.is_alive:
                collide = dummy.update()
                dummy.draw_scan_dots()
                world.update_ui({'score': dummy.score,
                                'distance': dummy.time_score})
                if collide != False:
                    if collide < 0:
                        run = False
                    if collide == 2:
                        action = 'win'
                            
                        cur_timescore = timescore
                        cur_score = dummy.score
                        run = False
                        respawn = False
                
            else:
                world.screen_scroll = 0
                run = False

            # -- Update World
            pygame.display.update()
    
    
    if action == 'win':
        run = True
        world.set_game_mode(7)
        world.load_world(level_num)
        button = False
        while run:
            button = world.draw_still()
        
            for event in pygame.event.get():
                #quit
                if event.type == pygame.QUIT:
                    run = False
                    action = 'exit'
                    break
                
            if button != False:
                if button == 'menu':
                    run = False
                    action = 'menu'
                elif button == 'restart':
                    run = False
                    action = 'dummy'


            pygame.display.update()
            
    return check_action(action)

def run_dummies(population= DUMMY_POPULATION, batches= DUMMY_BATCHES):
    global world
    world.set_game_mode(2)
    world.load_world(1)


    print("--- [Generating {bat} batches of {pop} Dummies] ---".format(pop= population, bat= batches))
    dummies = []

    for b_id in range(batches):
        #Set Batch Sprite
        sprite_id = random.randint(0,DYNAMIC_SPRITE_COUNT-2)
        print("-- [Generating Batch {bid} - Sprite_id: {sid}] --".format(sid= sprite_id, bid= b_id))
        for n in range(population):
            
            d_id = len(dummies)
            print("-- [Generating Dummy - DID: {did}] --".format(did= d_id, bid= b_id))

            dummy = world.generate_player(p_id= d_id,
                                           sprite_id= sprite_id,
                                           p_type= 'Dummy')
            dummy.moving_right = True
            dummies.append(dummy)
            dummy.log(" -- Generated Successfully! --\n")

    print("--- [{}/{} Dummies Successfully Generated] ---\n".format(len(dummies), (population * batches)))

    # -- Begin Play
    print("\n --- Begin Play ---\n")
    closest_distance = -1
    closest_tag = ''
    closest_index = -1
    closest_score = -1
    action = False

    run = True
    while run:
        
        # -- Update Game
        clock.tick(GAME_FRAME_RATE)     
        button = world.update()
        
        if button != False:
            if button == 'only_show_closest_toggle':
                world.only_show_closest_player = False if world.only_show_closest_player else True
            if button == 'restart':
                run = False
                action = 'dummy'
            if button == 'stop':
                run = False
                action = 'menu'
            
        # - Events
        for event in pygame.event.get():
            #quit
            if event.type == pygame.QUIT:
                run = False
                action = 'exit'
                
        
        #Generate Inputs to dummy
        for n, dummy in enumerate(dummies):
            
            dummy_distance = dummy.distance_to_target
            
            #To Jump
            output = random.randint(0,DUMMY_JUMP_DEVIATION)
            
            #Activate movements based on Rand output
            # if output > DUMMY_JUMP_BIAS:
            #     dummy.jump = True
                
            if dummy.scan_top_f == 0 and dummy.scan_mid_f == 0 and dummy.scan_bot_f < 1:
                dummy.jump = True
            
            if dummy.scan_top_f != 0 and dummy.scan_mid_f != 0 and dummy.scan_bot_f != 0:
                if dummy.moving_right:
                    dummy.moving_right = False
                    dummy.moving_left = True
                elif dummy.moving_left:
                    dummy.moving_right = True
                    dummy.moving_left = False
            
            if dummy.scan_top_f == 0 and dummy.scan_mid_f != 0 and dummy.scan_bot_f != 0:
                dummy.jump = True
                
                
            #If it's the closest so far, store it's details
            if closest_distance == -1 or dummy_distance < closest_distance:
                closest_tag = dummy.player_tag
                closest_distance = dummy_distance     

        alive_dummies = 0
        
        #Process inputs to character
        for n, dummy in enumerate(dummies):
            if dummy.is_alive:
                if dummy.player_tag == closest_tag:
                    dummy.followed = True
                    closest_tag = dummy.player_tag
                    closest_distance = dummy.distance_to_target
                    closest_index = dummies.index(dummy)
                    closest_score = dummy.score
                    world.total_scroll = dummy.total_scroll
                    dummy.draw_scan_dots()
                else:
                    dummy.followed = False

                alive_dummies += 1
                
                collide = dummy.update()
                
                if collide == 2:
                    action = 'win'
                    cur_timescore = dummy.timescore
                    cur_score = dummy.score
                    run = False
                    break
        
        
        world.update_ui({'name': dummies[closest_index].player_tag,
                   'score': dummies[closest_index].score,
                   'distance': dummies[closest_index].distance_to_target,
                   'alive': alive_dummies})
        
        # - Respawn Dummies when they're all dead [Deactivated temporarily]

        if alive_dummies == 0:
            run = False
            action = 'dummy'
        
        
        # -- Update World
        pygame.display.update() 
        
        
    if action == 'win':
        run = True
        world.set_game_mode(7)
        #world.load_world(level_num)
        button = False
        while run:
            button = world.draw_still()
        
            for event in pygame.event.get():
                #quit
                if event.type == pygame.QUIT:
                    run = False
                    action = 'exit'
                    break
                
            if button != False:
                if button == 'menu':
                    run = False
                    action = 'menu'
                elif button == 'restart':
                    run = False
                    action = 'singleplayer'


            pygame.display.update()
            
    return check_action(action)
    
def run_menu():
    clock = pygame.time.Clock()
    run = True
    next_screen = -1
    ui = UIController()
    ui.set_screen_ui(4)
    
    
    while run: 
        clock.tick(GAME_FRAME_RATE)
        
        screen.fill(MENU_BACKGROUND_COLOUR)
        
        action = ui.update()
        ui.draw()
        
        if action != False:
            if action == 'exit':
                next_screen = -1
                run = False
            elif action == 'singleplayer':
                next_screen = 1
                run = False
            elif action == 'dummy':
                next_screen = 2
                run = False
            elif action == 'smarty':
                next_screen = 3
                run = False
            elif action == 'long':
                next_screen = 4
                run = False
            elif action == 'best':
                next_screen = 5
                run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                next_screen = -1
                run = False
            
        pygame.display.update()
        
    return next_screen
        
def check_action(action):
    if action == False:
        return 0
    else:
        if action == 'exit':
            return -1
            
        elif action == 'singleplayer':
            return 1
            
        elif action == 'dummy':
            return 2
            
        elif action == 'smarty':
            return 3
        
        elif action == 'long':
            return 4
        
        elif action == 'best':
            return 5
        
        elif action == 'menu':
            return 0
        
        else:
            return 0

def read_settings():
    with open(SETTINGS_CSV_PATH) as settings_file:
        settings_reader = csv.reader(settings_file,
                                delimiter= ':')
        
        line_count = 0
        for row in settings_reader:
            if row[1] == 'b':
                SETTINGS[row[0]] = (row[2] == 'True')
            elif row[1] == 'i':
                SETTINGS[row[0]] = int(row[2])
            elif row[1] == 'f':
                SETTINGS[row[0]] = float(row[2])
            elif row[1] == 's':
                SETTINGS[row[0]] = row[2]
            else:
                SETTINGS[row[0]] = int(row[2])
                    
            line_count += 1
            
        print('read {n} lines from {p}\n'.format(n= line_count, p= SETTINGS_CSV_PATH))
        
        for key, value,  in SETTINGS.items():
            print('[{k}] \t{v}'.format(k= key, v= value))
            
        SETTINGS['reads'] += 1            

def save_settings():
    with open(SETTINGS_CSV_PATH, mode= 'w', newline= '') as settings_file:
        settings_writer = csv.writer(settings_file,
                                     delimiter= ':',
                                     quotechar='"',
                                     quoting= csv.QUOTE_MINIMAL)

        print(' === Saving... ===')
        for key, value in SETTINGS.items():
            if type(value) is int:
                t = 'i'
            elif type(value) is float:
                t = 'f'
            elif type(value) is str:
                t = 's'
            elif type(value) is bool:
                t = 'b'
            else:
                t = 's'

            print('Saving [{k}:{t}:{v}] to file...'.format(k= key, t= t, v= value))
            settings_writer.writerow([key, t, value])   
 
def scan_genome_directory():
    d_list = []
    for (dirpath, dirnames, filenames) in walk('genomes/'):
        d_list.extend(filenames)
        break
    
    return d_list
    
  
  
# --- At Run ---
read_settings()
scan_genome_directory()
current_screen = 0
world = World(0)
world.load_name_list()
checkpointer = False
global_counter = 0

run = True
while run:
    start_time = time.time()
    
    if current_screen == 0:
        #Main Menu
        current_screen = run_menu()
    
    elif current_screen == 1:
        #Singleplayer
        current_screen = run_singleplayer()
    
    elif current_screen == 2:
        #Dumb Ai
        current_screen = run_dummy()
    
    elif current_screen == 3:
        #Smart AI (Quick)
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, CONFIG_FILE_PATH)

        population = neat.Population(config)

        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)

        fittest = population.run(run_smarties, GENERATIONS)

        print("\n== Only the strongest shall survive... ==\n{!s}".format(fittest))
        
        current_screen == 0
        
    elif current_screen == 4:
        #Smart AI (Long)
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, LONG_CONFIG_FILE_PATH)    
        
        if SETTINGS['long_started']:
            print('Restoring checkpoint...')
            genome_file = '{a}{b}'.format(a= SETTINGS['filename_prefix'], b= SETTINGS['long_generation'])
            population = neat.Checkpointer.restore_checkpoint(genome_file)
            global_counter = SETTINGS['long_generation']
        else:
            print('Creating new population...')   
            population = neat.Population(config)
            SETTINGS['long_generation'] = -1
            global_counter = 0

        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        
        population.add_reporter(stats)
        population.add_reporter(neat.Checkpointer(generation_interval= GENERATIONS,
                                                  time_interval_seconds=None,
                                                  filename_prefix= SETTINGS['filename_prefix']))
            
        ui = UIController() 
        smart_run = True
        while smart_run:
            fittest = population.run(run_smarties, GENERATIONS)
            print("\n== Only the strongest shall survive... ==\n{!s}".format(fittest))
            SETTINGS['long_started'] = True
            SETTINGS['long_generation'] += GENERATIONS
            SETTINGS['test_genome_file'] = '{a}{b}'.format(a= SETTINGS['filename_prefix'], b= SETTINGS['long_generation'])
            save_settings()
        
        
    elif current_screen == 5:
        #Long but only show best
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, LONG_CONFIG_FILE_PATH)    
        
        if SETTINGS['long_started']:
            print('Restoring checkpoint...')
            genome_file = '{a}{b}'.format(a= SETTINGS['filename_prefix'], b= SETTINGS['long_generation'])
            population = neat.Checkpointer.restore_checkpoint(genome_file)
            global_counter = SETTINGS['long_generation']
        else:
            print('Creating new population...')   
            population = neat.Population(config)
            SETTINGS['long_generation'] = -1
            global_counter = 0

        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        
        population.add_reporter(stats)
        population.add_reporter(neat.Checkpointer(generation_interval= GENERATIONS,
                                                  time_interval_seconds=None,
                                                  filename_prefix= SETTINGS['filename_prefix']))
            
        ui = UIController() 
        smart_run = True
        while smart_run:
            fittest = ''
            finished = True
            running = True
            ui.set_screen_ui(5)
            pool = ThreadPoolExecutor(3)
            global_loop = 0
            while running:
                if finished:
                    future = pool.submit(population.run, run_smarties_hidden, GENERATIONS)
                    SETTINGS['long_generation'] += GENERATIONS
                    finished = False
                else:
                    clock.tick(GAME_FRAME_RATE)
                    screen.fill((175,175,175))
                    ui.update_labels({'counter': global_counter,
                                      'remaining': global_loop})
                    ui.draw()
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pool.shutdown(wait= False)
                            running = False
                            smart_run = False
                            run = False
                            break
                    
                    if future.done():
                        fittest = future.result()
                        print("\n== Only the strongest shall survive... ==\n{!s}".format(fittest))
                        SETTINGS['long_started'] = True
                        SETTINGS['test_genome_file'] = '{a}{b}'.format(a= SETTINGS['filename_prefix'], b= SETTINGS['long_generation'])
                        action = run_smarties([(0,fittest)],config)
                        save_settings()
                        global_counter -= 1
                        running = False
                        if action == 'menu':
                            smart_run = False
                            current_screen = 0
                            break
                        
                    pygame.display.update()
        
    elif current_screen == -1:
        #Quit signal
        run = False
    else:
        print("UNKNOWN SCREEN: {}".format(current_screen))

save_settings()
    
pygame.quit()  