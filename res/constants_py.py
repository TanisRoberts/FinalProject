import pygame
import math
from typing import Optional

SETTINGS_CSV_PATH = "res/settings.csv"
SETTINGS = {}
#[Debug Settings]

"""
= IS_DEBUG =
Master switch for all debug settings.
Setting this to false will disable all other debug settings.
"""
IS_DEBUG = True


SHOW_COLLISION_BOXES = False if IS_DEBUG else False
COLLISION_BOX_COLOUR = (235,116,52)

HIGHLIGHT_CLOSEST_PLAYER = False if IS_DEBUG else False
HIGHLIGHT_COLOUR = (52,207,235)


SHOW_MARKER_LOGS = False if IS_DEBUG else False
SHOW_ALL_PLAYER_LOGS = False if IS_DEBUG else False
SHOW_CLOSEST_PLAYER_LOGS = True if IS_DEBUG else False
SHOW_ITEM_LOGS = False if IS_DEBUG else False
SHOW_GOAL_LOGS = False if IS_DEBUG else False
SHOW_HAZARD_LOGS = True if IS_DEBUG else False
SHOW_UI_DEBUG = False if IS_DEBUG else False
SHOW_MAKING_PROGRESS = False if IS_DEBUG else False
ONLY_SHOW_CLOSEST_PLAYER = False if IS_DEBUG else False

#[General Settings]
# === Game View Settings ===
SCREEN_TITLE = "Tanis Roberts - Final Project"
SCREEN_GRID_WIDTH = 16
SCREEN_GRID_HEIGHT = 9
SCREEN_BACKGROUND_COLOUR = (160,180,240)
MENU_BACKGROUND_COLOUR = (235, 137, 99)

SCALE = 2
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
ROWS = 50
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // (ROWS / SCALE)
TILE_TYPES = 25

HAZARD_TILE_MIN = 17
HAZARD_TILE_MAX = 19

BG_TILE_MIN = 20
BG_TILE_MAX = 21

ITEM_TILE_NUM = 22

GOAL_TILE_NUM = 23

PLAYER_START_TILE = 24

MAP_CSV_FILE_PATH = "assets/tilemap/csv/py_test.csv"
MAP_TILES_FILE_PATH = "assets/tilemap/tiles/py_test_tiles/{}.png"


MAP_CSV_PATH = "assets/tilemap/csv/{}.csv"
MAP_CSV_FILE_LIST = {
    0: "py_test",
    1: "level_1",
    2: "level_2"
}

TILE_SPRITE_SIZE = 70


GAME_FRAME_RATE = 60

NAME_FILE_PATH = 'res/player_names.csv'

CHARACTER_FONT = "Comic Sans MS"

NAME_FONT_SIZE = 15
NAME_FONT_COLOUR = (0, 0, 0)

UI_FONT_SIZE = 30
UI_FONT_COLOUR = (0, 0, 0)
UI_X_POS = 0

UI_DEFAULT_BUTTON_COLOUR = (255,255,255)
UI_DEFAULT_BUTTON_PRESSED_COLOUR = (0,0,0)


#[Sprite Settings]
# === Player Sprite Settings ==== 
PLAYER_SPRITE_FILE_NAME = "player"
PLAYER_SPRITE_FILE_PATH = "assets/sprites/{}/".format(PLAYER_SPRITE_FILE_NAME)
PLAYER_ANIMATION_COOLDOWN = 120 #Ticks between animation frames
SPRITE_SCALING_PLAYER = 0.5

# -- Dynamic Player Sprite Settings --
USE_DYNAMIC_SPRITES = True

DYNAMIC_SPRITE_FOLDER_LIST = {
    0: "player_black",
    1: "player_blue",
    2: "player_green",
    3: "player_orange",
    4: "player_pink",
    5: "player_red",
    6: "soldier"
}

DYNAMIC_SPRITE_ANIM_FRAME_LIST = {
    0: "walk0",
    1: "walk1"
}

DYNAMIC_SPRITE_STATIC_FRAME_LIST = {
    0: "idle",
    1: "jump",
    2: "land",
    3: "fall"
}



DYNAMIC_SPRITE_FILE_PATH = "assets/sprites/{}/{}.png"
ERROR_SPRITE_FILE_PATH = "assets/sprites/error/{}.png" #Used incase the dynamic sprite folder is not available
DYNAMIC_SPRITE_COUNT = len(DYNAMIC_SPRITE_FOLDER_LIST)
DYNAMIC_ANIM_FRAME_COUNT = len(DYNAMIC_SPRITE_ANIM_FRAME_LIST)
DYNAMIC_STATIC_FRAME_COUNT = len(DYNAMIC_SPRITE_STATIC_FRAME_LIST)

# === Misc Sprite Settings ===
MISC_ANIMATION_COOLDOWN = 200

ITEM_SPRITE_FILE_PATH = "assets/sprites/item/{}.png"
ITEM_ANIM_FRAME_COUNT = 4

GOAL_SPRITE_FILE_PATH = "assets/sprites/goal/{}.png"
GOAL_ANIM_FRAME_COUNT = 4

MARKER_SPRITE_FILE_PATH = "assets/sprites/marker/{}.png"
MARKER_SPRITE_FRAME_COUNT = 3

HAZARD_SPRITE_FILE_PATH = "assets/sprites/hazard/{}.png"
HAZARD_TYPE_LIST = {
    0: "spikes",
    1: "saw",
    2: "lava"
}
HAZARD_TYPE_COUNT = len(HAZARD_TYPE_LIST)


#[Gameplay Settings]
# === Keyboard Settings ===
LEFT_KEYS = [pygame.K_a, pygame.K_LEFT]
RIGHT_KEYS = [pygame.K_d, pygame.K_RIGHT]
UP_KEYS = [pygame.K_w, pygame.K_UP]


# === Player Settings ===
GENERATE_PLAYER = False

PLAYER_START_POS_X = 200
PLAYER_START_POS_Y = SCREEN_HEIGHT - 200

PLAYER_GROUND_SPEED = 5
PLAYER_AIR_SPEED = 2
PLAYER_JUMP_IMPULSE = 11
PLAYER_TERMINAL_VELOCITY = 11
PLAYER_PARABOLIC_STILL = 3

GROUND_TOLERANCE = 1

SCROLL_THRESHOLD = (SCREEN_WIDTH / 2) - 50


# === Game Settings ===
GRAVITY_CONSTANT = 0.75


# === 'Cookie' Settings ===
# A cookie is an object that rewards the player in some way
ANIMATE_COOKIES = True

ITEM_SCORE = 5
NUM_ITEMS = 14 #REPLACE LATER

GOAL_SCORE = 500
NUM_GOALS = 1 #REPLACE LATER

NUM_HAZARDS = 1 #REPLACE LATER

# === AI settings ===
# -- Dummies --
GENERATE_DUMMIES = False
USE_SPREAD_START = True #If true, spread the dummies out across the screen
SPREAD_START_VARIANCE = 50
DUMMY_POPULATION = 5
DUMMY_BATCHES = 4
DUMMY_JUMP_BIAS = 90
DUMMY_JUMP_DEVIATION = 100

# -- Smarties --
GENERATE_SMARTIES = True
CONFIG_FILE_PATH = 'res/NEAT_config.txt'
LONG_CONFIG_FILE_PATH = 'res/NEAT_config_long.txt'
GENERATIONS = 10 #Number of generations to run. 'None' allows infinite generations 
FRAME_FITNESS = 0.1
PROGRESS_FITNESS = 0.4
STUCK_PENALTY = 0.2
ITEM_FITNESS = 50
GOAL_FITNESS = 10000
LASER_PENALTY = 25
MOVE_BIAS = 0.5
JUMP_BIAS = 0.9

SCAN_DOT_RADIUS = 4
SCAN_DOT_THICKNESS = 1

LASER_MOVE_SPEED = 4
LASER_COLOUR = (255,0,0)
LASER_WIDTH = 4

WIN_SCORE = (ITEM_SCORE * NUM_ITEMS) + (GOAL_SCORE * NUM_GOALS)



# === [Automatic Calculations] ===
