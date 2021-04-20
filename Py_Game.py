import pygame
import pymunk
from res.constants import *

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        super().__init__()
        img = pygame.image.load(PLAYER_SPRITE_FILE_PATH + "_idle.png")
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
    def draw(self):
        screen.blit(self.image, self.rect)
        
        
# -- run --

player = Player(200,200,1)
player2 = Player(400,200,0.8)

run = True
while run:
    
    player.draw()
    player2.draw()
    
    for event in pygame.event.get():
        #quit
        if event.type == pygame.QUIT:
            run = False
    
    pygame.display.update()        

pygame.quit()