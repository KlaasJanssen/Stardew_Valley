import pygame
from settings import *

class Transition:
    def __init__(self, reset, player):
        # Setup
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player

        # Overlay image
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -400

    def play(self, dt):
        self.color += self.speed * dt
        if self.color <= 0:
            self.color = 0
            self.speed *= -1
            self.reset()
        if self.color > 255:
            self.color = 255
            self.speed *= -1
            self.player.sleep = False
        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(self.image, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
