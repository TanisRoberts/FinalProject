#Imports
from classes.constants import *

import arcade
import math
from typing import Optional
from classes.gameWindow import GameWindow
        
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
    
    