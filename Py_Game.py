import pygame
import pymunk
import random
from res.constants_py import *

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)

# -- Time Keeping
clock = pygame.time.Clock()

tfc = (0,0,0)
tfy = SCREEN_HEIGHT - 100

def draw_bg():
    screen.fill(SCREEN_BACKGROUND_COLOUR)
    pygame.draw.line(screen, tfc, (0,tfy), (SCREEN_WIDTH,tfy))

class Player(pygame.sprite.Sprite):
    def __init__(self, p_id, x = PLAYER_START_POS_X, y = PLAYER_START_POS_Y, sprite_id = 0):
        super().__init__()
        
        # -- General
        self.player_id = p_id
        
        
        # -- Visual
        self.frame_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        
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

        
        #self.image = pygame.transform.scale(img, (int(img.get_width() * SPRITE_SCALING_PLAYER), int(img.get_height() * SPRITE_SCALING_PLAYER)))
        self.image = self.frame_list[1][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        
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
            if self.vel_y > 0:
                self.image = self.frame_list[1][1]
                
            elif self.vel_y < 0:
                self.image = self.frame_list[1][2]
                
            elif self.vel_y == 0:
                self.image = self.frame_list[1][3]
                
        elif self.moving_left or self.moving_right:
            #Update frame
            self.image = self.frame_list[0][self.frame_index]

            #Check if enough time has passed since last frame update
            if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.frame_list[0]):
                    self.frame_index = 0
        else:
            self.image = self.frame_list[1][0]
            
        
    def log(self, text = "", data = {}):
        msg = text.format(*data)
        print("[PID: {}] {}".format(self.player_id,msg))
        
        
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
        
        self.vel_y += GRAVITY_CONSTANT
        if self.vel_y > PLAYER_TERMINAL_VELOCITY:
            self.vel_y = PLAYER_TERMINAL_VELOCITY
        dy += self.vel_y
        
        if self.rect.bottom + dy > tfy:
            dy = tfy - self.rect.bottom
            self.vel_y = 0
        
        self.rect.x += dx
        self.rect.y += dy
        
        
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        
        
        
# --- At Run ---
player_list = []

# -- Generate 'Players'
print("--- [Generating {} Players] ---".format(PLAYER_POPULATION))

for p_id in range(PLAYER_POPULATION):
    print("-- [Generating Player - PID: {}] --".format(p_id))
    if USE_DYNAMIC_SPRITES:
        sprite_id = random.randint(0,DYNAMIC_SPRITE_COUNT-1)
    else:
        sprite_id = 0
    
    if USE_SPREAD_START:
        x = random.randint(0, SCREEN_WIDTH/2)
        y = random.randint(0,SCREEN_HEIGHT/2)
    else:    
        x = PLAYER_START_POS_X
        y = PLAYER_START_POS_Y
        
    player = Player(p_id, x, y, sprite_id)
    player.log("Starts at: X{} Y{}", {player.rect.left, player.rect.top})
    player_list.append(player)
    player.log(" -- Player Generated Successfully! --\n")
    
print("--- [{}/{} Players Successfully Generated] ---\n".format(len(player_list), PLAYER_POPULATION))

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
            
            
        # -- Per Player
    for player in player_list:
        player.move()
        player.update_animation()
        player.draw()
    
    pygame.display.update()        

pygame.quit()