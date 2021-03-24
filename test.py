#Imports
import arcade
import math
from typing import Optional
import antigravity
from classes.GameWindow import GameWindow


#Native Sprite Sizes
SPRITE_IMAGE_SIZE = 128

#Sprite Sizing
SPRITE_SCALING_PLAYER   = 0.5
SPRITE_SCALING_TILES    = 0.5
SPRITE_SIZE_PLAYER      = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)
SPRITE_SIZE_TILES       = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_TILES)

#Screen Settings
SCREEN_TITLE        = "Test platformer"
SCREEN_BACK_COLOUR  = arcade.color.ALMOND
SCREEN_GRID_WIDTH   = 25 
SCREEN_GRID_HEIGHT  = 15 
SCREEN_WIDTH        = SPRITE_SIZE_TILES * SCREEN_GRID_WIDTH
SCREEN_HEIGHT       = SPRITE_SIZE_TILES * SCREEN_GRID_HEIGHT



        
def main():
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_BACK_COLOUR)
    window.setup()
    printAll()
    arcade.run()
    
def printAll():
    pSep = " : "
    print("Tanis Roberts - Project Test v1")
    print("-------------------------------")
    print("[SCREEN_WIDTH]", SCREEN_WIDTH, sep=pSep)
    print("[SCREEN_HEIGHT]", SCREEN_HEIGHT, sep=pSep)
    print("[GRID_WIDTH]", SCREEN_GRID_WIDTH, sep=pSep)
    print("[GRID_HEIGHT]", SCREEN_GRID_HEIGHT, sep=pSep)
    print("-------------------------------")
    
    
    
if __name__ == "__main__":
    main()
    
    