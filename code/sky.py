import pygame
from settings import *
from support import import_folder
from sprites import Generic
from random import randint, choice

class Sky:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.full_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_color = [255,255,255]
        self.end_color = [38, 101, 189]
        self.day_length = 60
        self.time_elapsed = 0

    def display(self, dt):
        self.time_elapsed += dt
        current_color = self.start_color.copy()
        if self.time_elapsed > self.day_length:
            color_shift_value = self.time_elapsed - self.day_length
            for index, value in enumerate(self.end_color):
                current_color[index] -=  4 * color_shift_value
                if current_color[index] < value:
                    current_color[index] = value


        self.full_surf.fill(current_color)
        self.display_surface.blit(self.full_surf, (0,0), special_flags = pygame.BLEND_RGBA_MULT)

class Drop(Generic):
    def __init__(self, surf, pos, moving, groups, z):
        super().__init__(pos, surf, groups, z)
        self.lifetime = randint(400, 500) / 1000
        self.elapsed_time = 0

        # Moving
        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2,4)
            self.speed = randint(200,250)

    def update(self, dt):
        # Movement
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        self.elapsed_time += dt
        if self.elapsed_time > self.lifetime:
            self.kill()

class Rain:
    def __init__(self, visible_sprites, update_sprites, level_name):
        self.visible_sprites = visible_sprites
        self.update_sprites = update_sprites
        self.rain_drops = import_folder("../graphics/rain/drops")
        self.rain_floor = import_folder("../graphics/rain/floor")
        self.floor_w, self.floor_h = pygame.image.load(f"../graphics/world/{level_name}/ground.png").get_size()

    def create_floor(self):
        Drop(
            surf = choice(self.rain_floor),
            pos = (randint(0, self.floor_w), randint(0, self.floor_h)),
            moving = False,
            groups = [self.visible_sprites, self.update_sprites],
            z = LAYERS["rain_floor"]
        )

    def create_drops(self):
        Drop(
            surf = choice(self.rain_drops),
            pos = (randint(0, self.floor_w), randint(0, self.floor_h)),
            moving = True,
            groups = [self.visible_sprites, self.update_sprites],
            z = LAYERS["rain_drops"]
        )

    def update(self):
        self.create_floor()
        self.create_drops()
