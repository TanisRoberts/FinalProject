import arcade
import pygame
import math
from typing import Optional

# -- General Settings --
IS_DEBUG = True
OPEN_AT_GAME = False
CONFIG_FILE_PATH = "res/NEAT_config.txt"


# -- Splash View Settings --
SPLASH_FONT_COLOUR = arcade.color.LIGHT_GRAY


# -- Sprite Settings --
SPRITE_FOLDER_PATH = "assets/sprites/"

PLAYER_SPRITE_FILE_NAME = "player"
PLAYER_SPRITE_FILE_PATH = SPRITE_FOLDER_PATH + PLAYER_SPRITE_FILE_NAME

#-Not in use-
LASER_SPRITE_FILE_NAME = "laser"
LASER_SPRITE_FILE_PATH = SPRITE_FOLDER_PATH + LASER_SPRITE_FILE_NAME


SPRITE_IMAGE_SIZE = 128
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

SPRITE_SCALING_TILES = 0.5

SPRITE_SCALING_LASER = 0.5



# -- Game View Settings --
SCREEN_TITLE = "Tanis Roberts - Final Project"
SCREEN_GRID_WIDTH = 20
SCREEN_GRID_HEIGHT = 10
SCREEN_WIDTH = SPRITE_SIZE * SCREEN_GRID_WIDTH
SCREEN_HEIGHT = SPRITE_SIZE * SCREEN_GRID_HEIGHT

GAME_FONT_COLOUR = arcade.color.LIGHT_GRAY
BACKGROUND_COLOUR = arcade.color.SKY_BLUE

LEFT_VIEWPORT_MARGIN = SCREEN_WIDTH / 4
RIGHT_VIEWPORT_MARGIN = SCREEN_WIDTH / 4
BOTTOM_VIEWPORT_MARGIN = 20
TOP_VIEWPORT_MARGIN = 20

VIEWPORT_TEST_X = (SCREEN_WIDTH + SPRITE_SIZE) / 2
VIEWPORT_TEST_Y = (SCREEN_HEIGHT + SPRITE_SIZE) / 2


# -- Map settings --
DEFAULT_MAP_NUM = 0

MAP_SWITCHER = {
    0: "testMap.tmx",
    1: "level1.tmx",
    2: "level2.tmx",
}

MAP_FOLDER_PATH = "assets/tilemap/"
#MAP_FILE_PATH = MAP_FOLDER_PATH + MAP_SWITCHER.get(MAP_NUM,"level1.tmx")
GRID_START_X = 4
GRID_START_Y = 20

PLAYER_START_POSITION_X = SPRITE_SIZE * GRID_START_X + SPRITE_SIZE / 2
PLAYER_START_POSITION_Y = SPRITE_SIZE * GRID_START_Y + SPRITE_SIZE / 2


# -- Physics Settings --
# - General
GRAVITY = 1500
DEFAULT_DAMPING = 1.0
WALL_FRICTION = 0.7
DYNAMIC_ITEM_FRICTION = 0.6


# - Player
PLAYER_DAMPING = 0.4
PLAYER_FRICTION = 1.0
PLAYER_MASS = 2.0
PLAYER_JUMP_IMPULSE = 1000

PLAYER_MAX_HORIZONTAL_SPEED = 450
PLAYER_MAX_VERTICAL_SPEED = 1600

PLAYER_MOVE_FORCE_ON_GROUND = 8000
PLAYER_MOVE_FORCE_IN_AIR = 500

# - Laser
LASER_MOVE_SPEED = 1


# -- Animation Settings --
DEAD_ZONE = 0.1
RIGHT_FACING = 0
LEFT_FACING = 1
DISTANCE_TO_CHANGE_TEXTURE = 20


# -- AI Settings --
GEM_FITNESS = 50
DOOR_FITNESS = 250
FRAME_FITNESS = 1 
MAX_GENERATION = 1000