import pygame
import pymunk
import random
import csv
import pandas
import numpy
from res.constants_py import *

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)
clock = pygame.time.Clock()
name_font = pygame.font.SysFont(CHARACTER_FONT, NAME_FONT_SIZE)
ui_font = pygame.font.SysFont(CHARACTER_FONT, UI_FONT_SIZE)


#Hopefully Temporary
tfc = (0,0,0)
tfy = SCREEN_HEIGHT - 210

def draw_bg():
    screen.fill(SCREEN_BACKGROUND_COLOUR)
    pygame.draw.line(screen, tfc, (0,tfy), (SCREEN_WIDTH,tfy))
    
def get_names():
    print("--- [Retrieving Player Names] ---")
    
    
    with open(NAME_FILE_PATH, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    
    nl = data
    
    print(nl)
    print(" -- {} Player Names Retrieved! --\n".format(len(nl)))   
    return nl

def create_marker(player):
    if not marker_list:
        marker_type = 0
    elif len(marker_list) == (len(player_list) - 1):
        marker_type = 2
    else:
        marker_type = 1
        
    marker = Marker(player.get_center_x(), player.get_center_y(), marker_type, player.player_tag)
    marker_list.append(marker)


class World():
    def __init__(self):
        self.player_start_position = (PLAYER_START_POS_X, PLAYER_START_POS_Y)
        
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
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
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
                    elif tile >= HAZARD_TILE_MIN and tile <= HAZARD_TILE_MAX:
                        #Create Hazard Object
                        h_type = tile - HAZARD_TILE_MIN
                        hazard = Hazard(len(self.hazard_list), x_pos, y_pos, h_type)
                        self.hazard_group.add(hazard)
                        self.hazard_list.append(hazard)
                    elif tile >= BG_TILE_MIN and tile <= BG_TILE_MAX:
                        #Create Background Tile
                        self.bg_list.append(tile_data)
                    elif tile == ITEM_TILE_NUM:
                        #Create Item Object
                        item = Item(len(self.item_list), x_pos, y_pos)
                        self.item_group.add(item)
                        self.item_list.append(item)
                    elif tile == GOAL_TILE_NUM:
                        #Create Goal Object
                        goal = Goal(len(self.goal_list), x_pos, y_pos)
                        self.goal_group.add(goal)
                        self.goal_list.append(goal)
                    elif tile == PLAYER_START_TILE:
                        #Store Player Start Coordinates
                        self.player_start_position = (x_pos, y_pos)
                    
    def draw(self):
        for tile in self.wall_list:
            screen.blit(tile[0], tile[1])
        
        for tile in self.bg_list:
            screen.blit(tile[0], tile[1])

class Player(pygame.sprite.Sprite):
    def __init__(self, p_id, x = PLAYER_START_POS_X, y = PLAYER_START_POS_Y, sprite_id = 0, p_name = ""):
        super().__init__()
        
        # -- General
        self.player_id = p_id
        self.player_tag = "{} {}".format(p_name,p_id)
        self.is_alive = True
        self.score = 0
        self.collected_item_list = []
        self.collected_goal = False
        
        
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
                self.frame_list.append(img)
            
            self.frame_list.append(temp_list)
            temp_list = []
            
            for i in range(DYNAMIC_STATIC_FRAME_COUNT):
                img = pygame.image.load(ERROR_SPRITE_FILE_PATH.format(DYNAMIC_SPRITE_STATIC_FRAME_LIST[i]))
                img = pygame.transform.scale(img, (int(img.get_width() * SPRITE_SCALING_PLAYER), int(img.get_height() * SPRITE_SCALING_PLAYER)))
                self.frame_list.append(img)
            
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
        self.is_in_air = False
        
        
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
        print("[P: {}] {}".format(self.player_tag,msg))
        
    def get_center_x(self): return self.rect.left + (self.rect.width / 2)
    
    def get_center_y(self): return self.rect.top - (self.rect.height / 2) 
        
        
    def move(self):
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
        
        if self.jump:
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
        
        
    def die(self, msg):
        self.is_alive = False
        create_marker(self)
        self.log("died by {}!",{msg})
        
        
    def update(self):
        if self.is_alive:
            hazard_hit_list = pygame.sprite.spritecollide(self, hazard_group, False)
            for hazard in hazard_hit_list:
                self.die(hazard.hazard_type)
                
            item_hit_list = pygame.sprite.spritecollide(self, item_group, False)
            for item in item_hit_list:
                if not any(item_id == item.item_id for item_id in self.collected_item_list):
                    self.score += ITEM_SCORE
                    self.collected_item_list.append(item.item_id)
                    self.log("Score: {}",{self.score})

            goal_hit_list = pygame.sprite.spritecollide(self, goal_group, False)
            for goal in goal_hit_list:
                if not self.collected_goal:
                    self.score += GOAL_SCORE
                    self.collected_goal = True
                    self.log("Score: {}",{self.score})
            
            if self.score >= WIN_SCORE:
                self.die("winning")

        
        
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        if SHOW_COLLISION_BOXES:
            for side in range(4):
                pygame.draw.rect(screen, (255,100,255), (self.rect.left - side, self.rect.top - side, self.width, self.height), 1)
            
        name_tag_x = self.get_center_x() - (self.name_text_surface.get_width() / 2)
        name_tag_y = self.rect.top - (self.name_text_surface.get_height() + 10)
        screen.blit(self.name_text_surface, (name_tag_x , name_tag_y))
 
        
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
                img = pygame.transform.scale(img, (int(img.get_width() * SPRITE_SCALING_ITEM), int(img.get_height() * SPRITE_SCALING_ITEM)))
                self.frame_list.append(img)
        self.log("Sprite Created Successfully!")
        
        self.image = self.frame_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        
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
        print("[IID: {}] {}".format(self.item_id,msg))
        
    def draw(self):
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
                img = pygame.transform.scale(img, (int(img.get_width() * SPRITE_SCALING_GOAL), int(img.get_height() * SPRITE_SCALING_GOAL)))
                self.frame_list.append(img)
        self.log("Sprite Created Successfully!")
        
        self.image = self.frame_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        
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
        print("[GID: {}] {}".format(self.goal_id,msg))
        
    def draw(self):
        screen.blit(self.image, self.rect)
        
        
class Marker(pygame.sprite.Sprite):
    def __init__(self, x = 0, y = 0, marker_type = 1, p_name = ""):
        super().__init__()

        self.player_name = p_name
        self.marker_id = len(marker_list)
        
        img = pygame.image.load(MARKER_SPRITE_FILE_PATH.format(marker_type))
        self.image = pygame.transform.scale(img, (int(img.get_width() * SPRITE_SCALING_MARKER), int(img.get_height() * SPRITE_SCALING_MARKER)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.log("Marker Generated for {}",{self.player_name})
        
    def log(self, text = "", data = {}):
        msg = text.format(*data)
        print("[MID: {}] {}".format(self.marker_id,msg))
        
    def draw(self):
        screen.blit(self.image, self.rect)
        

class Hazard(pygame.sprite.Sprite):
    def __init__(self, h_id, x = 0, y = 0, hazard_type = 0):
        super().__init__()
        
        self.hazard_id = h_id
        self.hazard_type = HAZARD_TYPE_LIST[hazard_type]
        
        img = pygame.image.load(HAZARD_SPRITE_FILE_PATH.format(self.hazard_type))
        self.image = pygame.transform.scale(img, (int(img.get_width() * SPRITE_SCALING_HAZARD), int(img.get_height() * SPRITE_SCALING_HAZARD)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
                    
                    
    def log(self, text = "", data = {}):
        msg = text.format(*data)
        print("[HID: {}] {}".format(self.hazard_id,msg))
        
    def draw(self):
        screen.blit(self.image, self.rect)
        
        
# --- At Run ---

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

player_list = []
marker_list = []
name_list = get_names()
    

# -- Generate 'Players'
print("--- [Generating {} Players] ---".format(PLAYER_POPULATION))

for p_id in range(PLAYER_POPULATION):
    name = name_list[random.randint(0, len(name_list) - 1)][0]
    print("-- [Generating '{}' - PID: {}] --".format(name,p_id))
    if USE_DYNAMIC_SPRITES:
        sprite_id = random.randint(0,DYNAMIC_SPRITE_COUNT-1)
    else:
        sprite_id = 0
    
    if USE_SPREAD_START:
        x = random.randint(50, SCREEN_WIDTH/2)
        y = random.randint(tfy,SCREEN_HEIGHT/2)
    else:    
        x = PLAYER_START_POS_X
        y = PLAYER_START_POS_Y
    
    player = Player(p_id, x, y, sprite_id, name)
    player.log("Starts at: X{} Y{}", {player.rect.left, player.rect.top})
    player_list.append(player)
    player.log(" -- Player Generated Successfully! --\n")
    
print("--- [{}/{} Players Successfully Generated] ---\n".format(len(player_list), PLAYER_POPULATION))

"""
# -- Generate Items
print("--- [Generating {} Items] ---".format(NUM_ITEMS))

for i_id in range(NUM_ITEMS):
    print("-- [Generating Item - IID: {}] --".format(i_id))
    x = (i_id * 300) + 150
    y = tfy - 30
    item = Item(i_id, x, y)
    item.log("Position: X{} Y{}", {item.rect.left, item.rect.top})
    item_list.append(item)
    item_group.add(item)
    item.log(" -- Item Generated Successfully! --\n")
    
print("--- [{}/{} Items Successfully Generated] ---\n".format(len(item_list), NUM_ITEMS))


# -- Generate Goals
print("--- [Generating {} Goals] ---".format(NUM_GOALS))

for g_id in range(NUM_GOALS):
    print("-- [Generating Goal - GID: {}] --".format(g_id))
    x = SCREEN_WIDTH - 200
    y = tfy - 45
    goal = Goal(g_id, x, y)
    goal.log("Position: X{} Y{}", {goal.rect.left, goal.rect.top})
    goal_list.append(goal)
    goal_group.add(goal)
    goal.log(" -- Goal Generated Successfully! --\n")
    
print("--- [{}/{} Goals Successfully Generated] ---\n".format(len(goal_list), NUM_GOALS))


# -- Generate Hazards
print("--- [Generating {} Hazards] ---".format(NUM_HAZARDS))

for h_id in range(NUM_HAZARDS):
    print("-- [Generating Hazard - HID: {}] --".format(h_id))
    
    x = SCREEN_WIDTH - 500
    y = tfy - 30
    
    if USE_RANDOM_HAZARDS:
        hazard_type = random.randint(0, HAZARD_TYPE_COUNT)
    else:
        hazard_type = 0
        
    hazard = Hazard(h_id, x, y, hazard_type)
    hazard.log("Position: X{} Y{}", {hazard.rect.left, hazard.rect.top})
    hazard_list.append(hazard)
    hazard_group.add(hazard)
    hazard.log(" -- Hazard Generated Successfully! --\n")
    
print("--- [{}/{} Hazards Successfully Generated] ---\n".format(len(goal_list), NUM_HAZARDS))
"""



# -- Begin Play
run = True
print("\n --- Begin Play ---\n")

while run:
    
    # -- Update
    clock.tick(GAME_FRAME_RATE)
    draw_bg()
    
    # -- Events
    for event in pygame.event.get():
        #quit
        if event.type == pygame.QUIT:
            run = False
        
        for player in player_list:
            
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
            
            
    # -- Update World
    world.draw()
        
    # -- Update Items
    for item in item_list:
        item.update_animation()
        item.draw()
        #item_group.update()ddddddddd
        #item_group.draw()
        
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
    for player in player_list:
        if player.is_alive:
            player.move()
            player.update_animation()
            player.update()
            player.draw()
            
    
    pygame.display.update()        

pygame.quit()