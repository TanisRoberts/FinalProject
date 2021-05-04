import pygame
import pymunk
import random
import csv
import pandas
import numpy
import math
import neat
from res.constants_py import *

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)
clock = pygame.time.Clock()
name_font = pygame.font.SysFont(CHARACTER_FONT, NAME_FONT_SIZE)

screen_scroll = 0
total_scroll = 0
goal_position = 0
wall_list = []
marker_list = []
item_group = pygame.sprite.Group()
hazard_group = pygame.sprite.Group()
goal_group = pygame.sprite.Group()
laser_position = 0
name_list = []

game_mode = 0
#Game modes:
# - 1 : Singleplayer
# - 2 : Dummies
# - 3 : Smarties


def draw_bg():
    screen.fill(SCREEN_BACKGROUND_COLOUR)

def get_names():
    print("--- [Retrieving Player Names] ---")
    
    
    with open(NAME_FILE_PATH, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    
    nl = data
    
    print(nl)
    print(" -- {} Player Names Retrieved! --\n".format(len(nl)))   
    return nl

def create_death_marker(player):
    global strongest_dummy
    
    if player.player_type == 'Dummy':
        if len(marker_list) == 0:
            marker_type = 0
            strongest_dummy = player
        else:
            marker_type = 1

            if player.score > strongest_dummy.score:
                strongest_dummy = player
                player.log("Is the strongest dummy!")
                
    elif player.player_type == 'Player':
        marker_type = 2
        
    else:
        marker_type = 1
            
        
    marker = Marker(player.get_center_x(), player.get_center_y(), marker_type, player.player_tag)
    marker_list.append(marker)

def generate_player(goal_position):
    print("--- [Generating Player] ---")
    p_id = 0
    name = name_list[random.randint(0, len(name_list) - 1)][0]
    print("-- [Generating '{}' - PID: {}] --".format(name,p_id))
    if USE_DYNAMIC_SPRITES:
        sprite_id = random.randint(0,DYNAMIC_SPRITE_COUNT-2)
    else:
        sprite_id = 6
    player = Player(p_id, player_start_x, player_start_y, sprite_id, name, 'Player', goal_position)
    player.log("Starts at: X{} Y{}", {player.rect.left, player.rect.top})
    player.log(" -- Player Generated Successfully! --\n")

    print("--- [Player '{}' Successfully Generated] ---\n".format(player.player_tag))
    return player

def generate_dummies_bulk(offset, goal_position):
    first_set = False
    print("--- [Generating {bat} batches of {pop} Dummies] ---".format(pop= DUMMY_POPULATION, bat= DUMMY_BATCHES))

    for b_id in range(DUMMY_BATCHES):
        #Set Batch Sprite
        if USE_DYNAMIC_SPRITES:
            sprite_id = random.randint(0,DYNAMIC_SPRITE_COUNT-2)
        else:
            sprite_id = 0
                
        for n in range(DUMMY_POPULATION):
            
            name = name_list[random.randint(0, len(name_list) - 1)][0]
            d_id = len(dummy_list)
            print("-- [Generating '{name}' in batch {bid} - DID: {did}] --".format(name= name, did= d_id, bid= b_id))

            if USE_SPREAD_START:
                x = offset + random.randint(player_start_x - SPREAD_START_VARIANCE, player_start_x + SPREAD_START_VARIANCE)
                y = random.randint(player_start_y - SPREAD_START_VARIANCE, player_start_y + SPREAD_START_VARIANCE)
            else:    
                x = player_start_x
                y = player_start_y

            dummy = Player(d_id, x, y, sprite_id, name, 'Dummy', goal_position)
            dummy.log("Starts at: X{} Y{}", {dummy.rect.left, dummy.rect.top})
            dummy.moving_right = True
            dummy_list.append(dummy)
            dummy.log(" -- Dummy Generated Successfully! --\n")

    print("--- [{}/{} Dummies Successfully Generated] ---\n".format(len(dummy_list), (DUMMY_POPULATION * DUMMY_BATCHES)))


class World():
    def __init__(self):
        self.player_start_position_x = PLAYER_START_POS_X
        self.player_start_position_y = PLAYER_START_POS_Y
        
        self.goal_position = 0
        
        self.world_list = []
        self.wall_list = []
        self.item_list = []
        self.goal_list = []
        self.hazard_list = []
        self.bg_list = []
        
        self.item_group = pygame.sprite.Group()
        self.hazard_group = pygame.sprite.Group()
        self.goal_group = pygame.sprite.Group()
        self.wall_group = pygame.sprite.Group()
        
        
        self.tile_img_list = []
        for x in range(TILE_TYPES):
            img = pygame.image.load(MAP_TILES_FILE_PATH.format(x))
            img = pygame.transform.scale(img, (int(TILE_SIZE), int(TILE_SIZE)))
            self.tile_img_list.append(img)
        
    def process_data(self, data):
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    x_pos = x * TILE_SIZE
                    y_pos = y * TILE_SIZE
                    
                    img = self.tile_img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x_pos
                    img_rect.y = y_pos
                    tile_data = (img, img_rect)
                    
                    
                    if tile <= 16:
                        #Create Wall Tile
                        self.wall_list.append(tile_data)
                        self.wall_group.add()
                        self.world_list.append(tile_data)
                    elif tile >= HAZARD_TILE_MIN and tile <= HAZARD_TILE_MAX:
                        #Create Hazard Object
                        h_type = tile - HAZARD_TILE_MIN
                        hazard = Hazard(len(self.hazard_list), x_pos, y_pos, h_type)
                        self.hazard_group.add(hazard)
                        self.hazard_list.append(hazard)
                    elif tile >= BG_TILE_MIN and tile <= BG_TILE_MAX:
                        #Create Background Tile
                        self.bg_list.append(tile_data)
                        self.world_list.append(tile_data)
                    elif tile == ITEM_TILE_NUM:
                        #Create Item Object
                        item = Item(len(self.item_list), x_pos, y_pos)
                        self.item_group.add(item)
                        self.item_list.append(item)
                    elif tile == GOAL_TILE_NUM:
                        #Create Goal Object
                        goal = Goal(len(self.goal_list), x_pos, y_pos)
                        self.goal_position = x_pos
                        self.goal_group.add(goal)
                        self.goal_list.append(goal)
                    elif tile == PLAYER_START_TILE:
                        #Store Player Start Coordinates
                        self.player_start_position_x = x_pos
                        self.player_start_position_y = y_pos
                    
    def draw(self):
        for tile in self.world_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Player(pygame.sprite.Sprite):
    def __init__(self, p_id, x = PLAYER_START_POS_X, y = PLAYER_START_POS_Y, sprite_id = 0, p_name = "", p_type = 'Player', goal_position = 0):
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
        
        self.goal_position = goal_position
        self.distance_to_target = 0
        self.prev_distance_to_target = 0
        self.total_scroll = 0
        
        if p_type == 'Player':
            self.followed = True
        else:
            self.followed = False
            
        
        
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
        
        self.name_text_surface = name_font.render(self.player_tag, False, NAME_FONT_COLOUR)
        
        # -- Action
        self.moving_left = False
        self.moving_right = False
        self.speed = PLAYER_GROUND_SPEED
        self.x_direction = 1
        self.flip = False
        self.vel_y = 0
        self.jump = False
        self.is_in_air = True
        
        
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
                
        
    def get_center_x(self): return self.rect.left + (self.rect.width / 2)
    
    def get_center_y(self): return self.rect.top + (self.rect.height / 2) 
          
    def move(self):
        global screen_scroll, total_scroll, w
        dx = 0
        dy = 0
        
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
            self.is_in_air = True
        
        self.vel_y += GRAVITY_CONSTANT
        if self.vel_y > PLAYER_TERMINAL_VELOCITY:
            self.vel_y = PLAYER_TERMINAL_VELOCITY
        dy += self.vel_y
        
        for tile in wall_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                
                if self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom
                    self.is_in_air = False
        
        
        self.rect.x += dx
        self.rect.y += dy
        
        if self.followed:
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESHOLD and total_scroll < (COLS * TILE_SIZE) - SCREEN_WIDTH):
                self.rect.x -= dx
                screen_scroll = -dx 
                self.total_scroll -= -dx
                
            elif (self.rect.left < (SCROLL_THRESHOLD / 4) and total_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
                self.total_scroll -= -dx
                
            else:
                screen_scroll = 0
        else:
            self.rect.x += screen_scroll
                     
    def die(self, msg):
        self.is_alive = False
        create_death_marker(self)
        self.log("died by {}!",{msg})
        
    def check_collisions(self):
        if self.is_alive:
            hazard_hit_list = pygame.sprite.spritecollide(self, hazard_group, False)
            for hazard in hazard_hit_list:
                self.die(hazard.hazard_type)
                return 0
                
            item_hit_list = pygame.sprite.spritecollide(self, item_group, False)
            for item in item_hit_list:
                if not any(item_id == item.item_id for item_id in self.collected_item_list):
                    self.score += ITEM_SCORE
                    self.collected_item_list.append(item.item_id)
                    self.log("Score: {}",{self.score})
                    return 1

            goal_hit_list = pygame.sprite.spritecollide(self, goal_group, False)
            for goal in goal_hit_list:
                if not self.collected_goal:
                    self.score += GOAL_SCORE
                    self.collected_goal = True
                    self.log("Score: {}",{self.score})
                    return 2
            
            if self.score >= WIN_SCORE:
                self.die("winning")
                return 0
            
            #Kill the player if they get caught by the laser
            global laser_position
            if self.rect.x <= laser_position:
                self.die('the laser')
                return 0
                
        else:
            return False
            
    def get_distance_to_target(self):
        if self.is_alive:
            global goal_position
            self.prev_distance_to_target = self.distance_to_target
            return abs(goal_position - self.rect.right)
        else: 
            return 10000  
    
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
        if (ONLY_SHOW_CLOSEST_PLAYER and self.followed) or not ONLY_SHOW_CLOSEST_PLAYER:
            screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

            if SHOW_COLLISION_BOXES:
                for side in range(4):
                    pygame.draw.rect(screen, COLLISION_BOX_COLOUR, (self.rect.left - side, self.rect.top - side, self.image.get_width(), self.image.get_height()), 1)

            if HIGHLIGHT_CLOSEST_PLAYER and self.followed:
                for side in range(4):
                    pygame.draw.rect(screen, HIGHLIGHT_COLOUR, (self.rect.left - side, self.rect.top - side, self.image.get_width(), self.image.get_height()), 1)

            name_tag_x = self.get_center_x() - (self.name_text_surface.get_width() / 2)
            name_tag_y = self.rect.top - (self.name_text_surface.get_height() + 10)
            screen.blit(self.name_text_surface, (name_tag_x , name_tag_y))
 
    def update(self):
        self.move()
        self.distance_to_target = self.get_distance_to_target()
        self.update_animation()
        collide = self.check_collisions()
        self.draw()
        return collide
        
        
class Item(pygame.sprite.Sprite):
    def __init__(self, i_id, x = 0, y = 0):
        super().__init__()
        
        self.item_id = i_id
        
        self.frame_list = []
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        
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
            print("[IID: {}] {}".format(self.item_id,msg))
        
    def draw(self):
        self.rect.x += screen_scroll
        
        if SHOW_COLLISION_BOXES:
            for side in range(4):
                pygame.draw.rect(screen, COLLISION_BOX_COLOUR, (self.rect.left - side, self.rect.top - side, self.image.get_width(), self.image.get_height()), 1)
                
        screen.blit(self.image, self.rect)
        
    
class Goal(pygame.sprite.Sprite):
    def __init__(self, g_id, x = 0, y = 0):
        super().__init__()
        
        self.goal_id = g_id
        
        self.frame_list = []
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        
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
            print("[GID: {}] {}".format(self.goal_id,msg))
        
    def draw(self):
        global goal_position
        
        self.rect.x += screen_scroll
        goal_position = self.rect.x
        
        if SHOW_COLLISION_BOXES:
            for side in range(4):
                pygame.draw.rect(screen, COLLISION_BOX_COLOUR, (self.rect.left - side, self.rect.top - side, self.image.get_width(), self.image.get_height()), 1)
         
        screen.blit(self.image, self.rect)
        
        
class Marker(pygame.sprite.Sprite):
    def __init__(self, x = 0, y = 0, marker_type = 1, p_name = ""):
        super().__init__()

        self.player_name = p_name
        self.marker_id = len(marker_list)
        
        img = pygame.image.load(MARKER_SPRITE_FILE_PATH.format(marker_type))
        self.image = pygame.transform.scale(img, (int(TILE_SIZE), int(TILE_SIZE)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.log("Marker Generated for {}",{self.player_name})
        
    def log(self, text = "", data = {}):
        msg = text.format(*data)
        if SHOW_MARKER_LOGS:
            print("[MID: {}] {}".format(self.marker_id,msg))
        
    def draw(self):
        self.rect.x += screen_scroll
        screen.blit(self.image, self.rect)
        

class Hazard(pygame.sprite.Sprite):
    def __init__(self, h_id, x = 0, y = 0, hazard_type = 0):
        super().__init__()
        
        self.hazard_id = h_id
        self.hazard_type = HAZARD_TYPE_LIST[hazard_type]
        
        img = pygame.image.load(HAZARD_SPRITE_FILE_PATH.format(self.hazard_type))
        self.image = pygame.transform.scale(img, (int(TILE_SIZE), int(TILE_SIZE)))
        self.rect = self.image.get_rect()
        
        if hazard_type == 0:
            self.rect.height = self.image.get_height() / 2
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
                    
                    
    def log(self, text = "", data = {}):
        msg = text.format(*data)
        if SHOW_HAZARD_LOGS:
            print("[HID: {}] {}".format(self.hazard_id,msg))
        
    def draw(self):
        self.rect.x += screen_scroll
        
        if SHOW_COLLISION_BOXES:
            for side in range(4):
                pygame.draw.rect(screen, COLLISION_BOX_COLOUR, (self.rect.left - side, self.rect.top - side, self.image.get_width(), self.image.get_height()), 1)
         
        screen.blit(self.image, self.rect)
    
class Laser():
    def __init__(self):
        self.speed = LASER_MOVE_SPEED
        self.x_pos = 0
        self.width = LASER_WIDTH
        
    def move(self):
        self.x_pos += self.speed 
        
    def draw(self):
        self.x_pos += screen_scroll
        pygame.draw.line(surface= screen,
                         color= LASER_COLOUR,
                         start_pos= (self.x_pos, 0),
                         end_pos= (self.x_pos, SCREEN_HEIGHT),
                         width= self.width)
        
    def update(self):
        self.move()
        self.draw()
        return self.x_pos
        
class UIText():
    def __init__(self, e_id, value= '', text= '{}', position= (0,0), active= True, colour= UI_FONT_COLOUR, font= CHARACTER_FONT, font_size= UI_FONT_SIZE, background= False, bg_colour= (0,0,0), antialias= False):
        self.font = pygame.font.SysFont(font, font_size)
        
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
    

class UIController():
    def __init__(self):
        global game_mode
        self.element_list = {}
        
        if game_mode == 1: #If we are in single player mode.
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
                                text= 'Distance: {}',
                                position= (0,30),
                                active= True)

            self.element_list[key] = ui_object
        
        elif game_mode == 2: # If we are in dummy mode.
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
                                text= 'Distance: {}',
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
            
        elif game_mode == 3: # If we are in smarty mode
            # Name of closest smarty
            key = 'name'
            ui_object = UIText(e_id= key,
                                value= '',
                                text= 'Name: {}',
                                position= (0,0),
                                active= True)

            self.element_list[key] = ui_object
            
            #Score of closest smarty
            key = 'score'
            ui_object = UIText(e_id= key,
                                value= '',
                                text= 'Score: {}',
                                position= (0,100),
                                active= True)

            self.element_list[key] = ui_object
            
            #Distance to target of closest smarty
            key = 'distance'
            ui_object = UIText(e_id= key,
                                value= '',
                                text= 'Distance: {}',
                                position= (0,200),
                                active= True)

            self.element_list[key] = ui_object
            
            #Current generation
            key = 'generation'
            ui_object = UIText(e_id= key,
                                value= '',
                                text= 'Generation: {}',
                                position= (SCREEN_WIDTH - 200,0),
                                active= True)

            self.element_list[key] = ui_object
            
            key = 'alive'
            ui_object = UIText(e_id= key,
                                value= '',
                                text= 'Alive: {}',
                                position= (SCREEN_WIDTH - 200,100),
                                active= True)

            self.element_list[key] = ui_object
        
        
        #Debug mode - Can be used to show debug on screen
        key = 'debug'
        ui_object = UIText(e_id= key,
                            value= '',
                            text= '[Debug Enabled] {}',
                            position= (0, SCREEN_HEIGHT - 50),
                            active= IS_DEBUG)
        
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
                
    def update(self,data):
        self.update_labels(data)
        self.draw()


def run_smarties(genomes, config):
    
    global screen, gen, game_mode, laser_position, name_list
    global wall_list, marker_list
    global item_group, hazard_group, goal_group
    
    gen += 1
    game_mode = 3
    
    networks = []
    smarties = []
    ge = []
    
    world_data = []
    for row in range(ROWS):
        r = [-1] * COLS
        world_data.append(r)

    with open(MAP_CSV_FILE_PATH, newline='') as mapfile:
        reader = csv.reader(mapfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][y] = int(tile)

    world = World()
    world.process_data(world_data)

    item_list = world.item_list
    goal_list = world.goal_list
    hazard_list = world.hazard_list
    wall_list = world.wall_list

    wall_group = world.wall_group
    item_group = world.item_group
    hazard_group = world.hazard_group
    goal_group = world.goal_group

    player_start_x = world.player_start_position_x
    player_start_y = world.player_start_position_y
    goal_position = world.goal_position
    
    ui = UIController()
    ui.update({'generation': gen})
    
    closest_tag = ''
    closest_index = 0
    closest_distance = -1
    closest_score = 0
    
    laser = Laser()
    laser_position = 0
    
    for genome_id, genome in genomes:
        genome.fitness = 0
        
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        networks.append(net)
        
        sprite_id = random.randint(0,DYNAMIC_SPRITE_COUNT-2)
        name = name_list[random.randint(0, len(name_list) - 1)][0]
        
        smarties.append(Player(genome_id, player_start_x, player_start_y, sprite_id, name, 'Smarty', goal_position))
        
        ge.append(genome)
        
    fitness = 0
    
    run = True
    while run and len(smarties) > 0:
        smarties_alive = len(smarties)
        clock.tick(GAME_FRAME_RATE)
        draw_bg()
        
        closest_index = -1
        closest_distance = -1
        closest_score = -1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
            
        
        
        #Generate Inputs to character
        for n, smarty in enumerate(smarties):
            ge[n].fitness += FRAME_FITNESS
            
            smarty_distance = smarty.get_distance_to_target()
            #To move: send distance to goal, if on ground, and if is moving
            output = networks[smarties.index(smarty)].activate((smarty_distance, smarty.get_is_on_ground(), smarty.get_is_moving()))
            
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
                
            #If it's the closest so far, store it's details
            if closest_distance == -1 or smarty_distance < closest_distance:
                closest_tag = smarty.player_tag
                closest_distance = smarty_distance
               
            
        #Process inputs to character
        for n, smarty in enumerate(smarties):
            if smarty.is_alive:
                if smarty.player_tag == closest_tag:
                    smarty.followed = True
                    closest_tag = smarty.player_tag
                    closest_distance = smarty.get_distance_to_target()
                    closest_index = smarties.index(smarty)
                    closest_score = smarty.score
                    total_scroll = smarty.total_scroll
                else:
                    smarty.followed = False
                
                collide = smarty.update()

                if smarty.get_distance_to_target() < smarty.prev_distance_to_target:
                    genome[n].fitness += PROGRESS_FITNESS

                if collide == False or collide == 0: #If smarty is dead, or dies
                    list_index = smarties.index(smarty)
                    ge[list_index].fitness -= 1
                    networks.pop(list_index)
                    ge.pop(list_index)
                    smarties.pop(list_index)
                elif collide == 1: #If smarty hits an item
                    ge[n].fitness += ITEM_FITNESS
                elif collide == 2: #If smarty hits the goal
                    ge[n].fitness += GOAL_FITNESS
                
        #Update everything else
        # -- Update Items
        for item in item_list:
            item.update_animation()
            item.draw()

        # -- Update Goals
        for goal in goal_list:
            goal.update_animation()
            goal.draw()

        # -- Update Hazards
        for hazard in hazard_list:
            hazard.draw()

        # -- Update Markers
        for marker in marker_list:
            marker.draw()
            
        laser_position = laser.update()
            
        world.draw()
        
        if SHOW_UI_DEBUG:
            print("name: {n} | index: {i} | distance: {d} | screen scroll: {ss}".format(n= closest_tag,
                                                                  i= closest_index,
                                                                  d= closest_distance,
                                                                  ss= screen_scroll))
            
        ui.update({'name': closest_tag,
                    'score': closest_score,
                    'distance': closest_distance,
                    'alive': len(smarties)})

        pygame.display.update()  
            
        
    
        
# --- At Run ---
name_list = get_names()

if GENERATE_SMARTIES:
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, CONFIG_FILE_PATH)
    
    gen = 0
    
    population = neat.Population(config)
    
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    fittest = population.run(run_smarties, GENERATIONS)
    
    print("\n== Only the strongest shall survive... ==\n{!s}".format(fittest))
    
else:
    world_data = []
    for row in range(ROWS):
        r = [-1] * COLS
        world_data.append(r)

    with open(MAP_CSV_FILE_PATH, newline='') as mapfile:
        reader = csv.reader(mapfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][y] = int(tile)

    world = World()
    world.process_data(world_data)

    item_list = world.item_list
    goal_list = world.goal_list
    hazard_list = world.hazard_list
    wall_list = world.wall_list

    wall_group = world.wall_group
    item_group = world.item_group
    hazard_group = world.hazard_group
    goal_group = world.goal_group

    player_start_x = world.player_start_position_x
    player_start_y = world.player_start_position_y
    player_active = False
    player = Optional[Player]

    dummy_list = []
    dead_dummy_count = 0

    strongest_dummy = Optional[Player]
    goal_position = world.goal_position
    new_index = 0
    closest_index = -1

    marker_list = []
    name_list = get_names()
    spawn_offset = 0
    interval = 0
    
    closest_distance = -1
    closest_tag = ''

    # -- Generate 'Players'
    if GENERATE_PLAYER:
        player = generate_player(goal_position)
        player_active = True
        game_mode = 1

    # -- Generate 'Dummies' [TEMPORARY UNTIL AI CODED]
    if GENERATE_DUMMIES:
        generate_dummies_bulk(spawn_offset,goal_position)
        game_mode = 2

    # -- Begin Play
    run = True
    
    ui = UIController()
    
    print("\n --- Begin Play ---\n")

    while run:

        # -- Update Game
        clock.tick(GAME_FRAME_RATE)
        draw_bg()       

        # -- Update Items
        for item in item_list:
            item.update_animation()
            item.draw()

        # -- Update Goals
        for goal in goal_list:
            goal.update_animation()
            goal.draw()

        # -- Update Hazards
        for hazard in hazard_list:
            hazard.draw()

        # -- Update Markers
        for marker in marker_list:
            marker.draw()

        # -- Update Players
        # - Events
        for event in pygame.event.get():
            #quit
            if event.type == pygame.QUIT:
                run = False
            if game_mode == 1:
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

        if game_mode == 1:       
            if player.is_alive:
                player.update()
                ui.update({'score': player.score,
                           'distance': player.get_distance_to_target()})
            else:
                screen_scroll = 0
                player_active = False

        # -- Update Dummies
        if GENERATE_DUMMIES:
            dummy_count = 0

            for index, dummy in enumerate(dummy_list):
                
                distance = dummy.get_distance_to_target()
                if closest_distance == -1 or distance < closest_distance:
                    closest_tag = dummy.player_tag
                    closest_distance = distance
                    closest_index = dummy_list.index(dummy)

                if dummy.is_alive:
                    if dummy.is_in_air:
                        dummy.jump = False
                    else:
                        do_jump = random.randint(0,10)
                        jump_tolerance = 10
                        dummy.jump = do_jump >= jump_tolerance

                    dummy.update()
                    dummy_count += 1

            # - Set new closest Dummy
            for dummy in dummy_list:
                if dummy.is_alive:
                    if dummy.player_tag == closest_tag:
                        dummy.followed = True
                    else:
                        dummy.followed = False
            
            
            ui.update({'name': dummy_list[closest_index].player_tag,
                       'score': dummy_list[closest_index].score,
                       'distance': dummy_list[closest_index].get_distance_to_target(),
                       'alive': dummy_count})

            # - Respawn Dummies when they're all dead [Deactivated temporarily]
            if dummy_count <= 0:
                #generate_dummies_bulk(spawn_offset,goal_position)
                strongest_dummy.log("is the current strongest dummy at {}!",{strongest_dummy.score})
                print("=== Strongest Dummy was: {} ===".format(strongest_dummy.player_tag))
                screen_scroll = 0
                run = False

            #FOR DEBUG
            if interval > 20:
                print("Currently following          {}".format(closest_tag))
                print("Their [distance] is         {}".format(dummy_list[closest_index].followed))
                print("The [screen_scroll] is       {}".format(screen_scroll))
                interval = 0
            else:
                interval += 1


        # -- Update World
        world.draw()
        ui.draw()

        pygame.display.update()        

pygame.quit()