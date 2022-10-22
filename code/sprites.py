import pygame
from settings import *
from random import random, choice
from timer import Timer

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z = LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.4, -self.rect.height * 0.75)

class Interaction(Generic):
    def __init__(self, pos, size, groups, name):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.name = name

class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration = 0.2):
        super().__init__(pos, surf, groups, z)
        self.duration = duration
        self.time_elapsed = 0

        # White surface
        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey((0,0,0))
        self.image = new_surf

    def update(self, dt):
        self.time_elapsed += dt
        if self.time_elapsed > self.duration:
            self.kill()

class Water(Generic):
    def __init__(self, pos, frames, groups):
        # Animation setup
        self.frames = frames
        self.frame_index = 0

        # Sprite setup
        super().__init__(pos, self.frames[self.frame_index], groups, LAYERS['water'])

    def animate(self, dt):
        self.frame_index += 5*dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)

class WildFlower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20,-self.rect.height * 0.9)

class Tree(Generic):
    def __init__(self, ID, pos, surf, groups, name, update_sprites, visible_sprites, player_add):
        super().__init__(pos, surf, groups)
        # Tree setup
        self.ID = ID

        # Sprite group access
        self.update_sprites = update_sprites
        self.visible_sprites = visible_sprites
        self.player_add = player_add

        # Tree attributes
        self.health = 5
        self.alive = True
        self.stump_surf = pygame.image.load(f'../graphics/stumps/{name.lower()}.png').convert_alpha()
        #self.invul_timer = Timer(0.2)

        # Apples
        self.apple_surf = pygame.image.load('../graphics/fruit/apple.png').convert_alpha()
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

        # Sounds
        self.axe_sound = pygame.mixer.Sound("../audio/axe.mp3")


    def create_fruit(self):
        if self.alive:
            for pos in self.apple_pos:
                if random() < 0.2:
                    x = self.rect.left + pos[0]
                    y = self.rect.top + pos[1]
                    Generic((x,y), self.apple_surf, [self.apple_sprites, self.visible_sprites], z = LAYERS['fruit'])

    def damage(self):
        if self.alive:
            # Damage tree
            self.health -= 1

            # Play sound
            self.axe_sound.play()

            # Remove an apple
            if self.apple_sprites:
                random_apple = choice(self.apple_sprites.sprites())
                Particle(random_apple.rect.topleft, random_apple.image, [self.visible_sprites, self.update_sprites], LAYERS['fruit'])
                random_apple.kill()
                self.player_add('apple', 1)

            self.check_death()

    def check_death(self):
        if self.health <= 0:
            Particle(self.rect.topleft, self.image, [self.visible_sprites, self.update_sprites], LAYERS['fruit'], duration = 0.3)
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
            self.alive = False
            self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.4, -self.rect.height * 0.9)
            self.hitbox.bottom -= 29
            self.player_add('wood', 1)

    def check_death_load(self):
        if self.health <= 0:
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
            self.alive = False
            self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.4, -self.rect.height * 0.9)
            self.hitbox.bottom -= 29
