import pygame
from settings import *

class Overlay:
    def __init__(self, player):

        # General setup
        self.display_surface = pygame.display.get_surface()
        self.player = player

        # imports
        overlay_path = "../graphics/overlay/"
        self.tools_surf = {tool:pygame.image.load(f"{overlay_path}{tool}.png").convert_alpha() for tool in player.tools}
        self.seeds_surf = {seed:pygame.image.load(f"{overlay_path}{seed}.png").convert_alpha() for seed in player.seeds}
        self.total_surf = {**self.tools_surf, **self.seeds_surf}
        #self.tool_list = list(self.total_surf.keys())
        self.slots = len(self.total_surf)

        self.slot_size = 80
        self.spacing = 5
        self.slot_alpha = 100

        self.font = pygame.font.Font("../font/LycheeSoda.ttf", 25)

        self.setup()

    def setup(self):
        self.bg_surf = pygame.Surface((self.slot_size,self.slot_size))
        self.bg_surf.set_alpha(self.slot_alpha)

        self.total_width = self.slots * self.slot_size + (self.slots - 1) * self.spacing
        self.slots_left = SCREEN_WIDTH // 2 - self.total_width // 2

    def display(self):
        # # Tool
        # tool_surf = self.tools_surf[self.player.selected_tool]
        # tool_rect = tool_surf.get_rect(midbottom = OVERLAY_POSITIONS['tool'])
        # self.display_surface.blit(tool_surf, tool_rect)
        #
        # # Seeds
        # seed_surf = self.seeds_surf[self.player.selected_seed]
        # seed_rect = seed_surf.get_rect(midbottom = OVERLAY_POSITIONS['seed'])
        # self.display_surface.blit(seed_surf, seed_rect)

        for index, items in enumerate(self.total_surf.items()):
            tool = items[0]
            surf = items[1]

            # Display background
            x = self.slots_left + index * (self.slot_size + self.spacing)
            bg_rect = self.bg_surf.get_rect(bottomleft = (x, SCREEN_HEIGHT - 10))
            self.display_surface.blit(self.bg_surf, bg_rect)
            border_color = "grey90" if index == self.player.index == index else "grey60"
            pygame.draw.rect(self.display_surface, border_color, bg_rect, 4)

            # Display tool/seed
            tool_surf = self.total_surf[tool]
            tool_rect = tool_surf.get_rect(center = bg_rect.center)
            self.display_surface.blit(tool_surf, tool_rect)

            # Display seed number
            if tool in self.player.seed_inventory.keys():
                number_surf = self.font.render(str(self.player.seed_inventory[tool]), False, "White")
                number_rect = number_surf.get_rect(bottomright = bg_rect.bottomright + pygame.math.Vector2(-5,-5))
                self.display_surface.blit(number_surf, number_rect)
