import pygame
import math
from typing import Optional

# -- Game View Settings --
SCREEN_TITLE = "Tanis Roberts - Final Project"
SCREEN_GRID_WIDTH = 16
SCREEN_GRID_HEIGHT = 9
SCREEN_BACKGROUND_COLOUR = (144,201,120)

SPRITE_IMAGE_SIZE = 128
SPRITE_SCALING_PLAYER = 1
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

SCREEN_WIDTH = SPRITE_SIZE * SCREEN_GRID_WIDTH
SCREEN_HEIGHT = SPRITE_SIZE * SCREEN_GRID_HEIGHT

GAME_FRAME_RATE = 60


# -- Sprite Settings --
PLAYER_SPRITE_FILE_NAME = "player"
PLAYER_SPRITE_FILE_PATH = "assets/sprites/{}/".format(PLAYER_SPRITE_FILE_NAME)

# Dynamic Sprite Settings
USE_DYNAMIC_SPRITES = True

DYNAMIC_SPRITE_FOLDER_LIST = {
    0: "player_black",
    1: "player_blue",
    2: "player_green",
    3: "player_orange",
    4: "player_pink",
    5: "player_red"
}

DYNAMIC_SPRITE_ANIM_FRAME_LIST = {
    0: "walk0",
    1: "walk1"
}

DYNAMIC_SPRITE_STATIC_FRAME_LIST = {
    0: "idle",
    1: "jump",
    2: "fall",
    3: "land"
}



DYNAMIC_SPRITE_FILE_PATH = "assets/sprites/{}/{}.png"
ERROR_SPRITE_FILE_PATH = "assets/sprites/error/{}.png" #Used incase the dynamic sprite folder is not available
DYNAMIC_SPRITE_COUNT = len(DYNAMIC_SPRITE_FOLDER_LIST)
DYNAMIC_ANIM_FRAME_COUNT = len(DYNAMIC_SPRITE_ANIM_FRAME_LIST)
DYNAMIC_STATIC_FRAME_COUNT = len(DYNAMIC_SPRITE_STATIC_FRAME_LIST)
ANIMATION_COOLDOWN = 120 #Ticks between animation frames


# -- Keyboard Arrays --
LEFT_KEYS = [pygame.K_a, pygame.K_LEFT]
RIGHT_KEYS = [pygame.K_d, pygame.K_RIGHT]
UP_KEYS = [pygame.K_w, pygame.K_UP]


# -- Player Settings --
USE_SPREAD_START = True #If true, spread the players out across the window

PLAYER_START_POS_X = 200
PLAYER_START_POS_Y = 200

PLAYER_GROUND_SPEED = 5
PLAYER_AIR_SPEED = 2
PLAYER_JUMP_IMPULSE = 11
PLAYER_TERMINAL_VELOCITY = 11

# -- Game Settings --
GRAVITY_CONSTANT = 0.75

# -- AI settings --
PLAYER_POPULATION = 10
