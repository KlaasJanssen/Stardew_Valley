import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import random
from menu import Menu
from debug import debug
import json

class Level:
    def __init__(self, player, name):
        self.display_surface = pygame.display.get_surface()
        self.name = name

        # Sprite groups
        self.update_sprites = UpdateGroup()
        self.visible_sprites = CameraGroup(self.name)
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        # Player
        self.player = player
        self.update_sprites.add(self.player)
        self.visible_sprites.add(self.player)
        self.player.toggle_shop = self.toggle_shop

        # Tree
        self.tree_ID = 0

        # Load map
        tmx_data = load_pygame(f'../data/{self.name}.tmx')

        # House
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x,y,surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x*TILE_SIZE,y*TILE_SIZE), surf, [self.visible_sprites], LAYERS['house_bottom'])

        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x,y,surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x*TILE_SIZE,y*TILE_SIZE), surf, [self.visible_sprites])

        # Fence
        for x,y,surf in tmx_data.get_layer_by_name("Fence").tiles():
            Generic((x*TILE_SIZE,y*TILE_SIZE), surf, [self.visible_sprites, self.collision_sprites])

        # Water
        for x, y, surf in tmx_data.get_layer_by_name("Water").tiles():
            water_frames = import_folder("../graphics/water")
            Water((x*TILE_SIZE,y*TILE_SIZE), water_frames, [self.update_sprites, self.visible_sprites])

        # Trees
        for obj in tmx_data.get_layer_by_name("Trees"):
            Tree(
                ID = self.tree_ID,
                pos = (obj.x,obj.y),
                surf = obj.image,
                groups = [self.visible_sprites, self.collision_sprites, self.tree_sprites],
                name = obj.name,
                update_sprites = self.update_sprites,
                visible_sprites = self.visible_sprites,
                player_add = self.player_add)
            self.tree_ID += 1

        # Wild Flower
        for obj in tmx_data.get_layer_by_name("Decoration"):
            WildFlower((obj.x,obj.y), obj.image, [self.visible_sprites, self.collision_sprites])

        # Collision tiles
        for x, y, surf in tmx_data.get_layer_by_name("Collision").tiles():
            Generic((x*TILE_SIZE,y*TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), [self.collision_sprites])

        # Player
        for obj in tmx_data.get_layer_by_name("Player"):
            # if obj.name == "Start":
            #     self.player = Player((obj.x, obj.y), [self.update_sprites, self.visible_sprites], self.toggle_shop)
            if obj.name == "Start":
                #self.player = Player((obj.x, obj.y), [self.update_sprites, self.visible_sprites], self.toggle_shop)
                self.player.pos = pygame.math.Vector2(obj.x, obj.y)
                self.player.hitbox.center = self.player.pos


            if obj.name == "Bed":
                Interaction(
                    pos = (obj.x, obj.y),
                    size = (obj.width, obj.height),
                    groups = [self.interaction_sprites],
                    name = obj.name
                )

            if obj.name == "Trader":
                Interaction(
                    pos = (obj.x, obj.y),
                    size = (obj.width, obj.height),
                    groups = [self.interaction_sprites],
                    name = obj.name
                )

        # Background
        Generic(
            pos = (0,0),
            surf = pygame.image.load(f'../graphics/world/{self.name}/ground.png').convert_alpha(),
            groups = [self.visible_sprites],
            z = LAYERS['ground']
        )

        # Overlay
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)
        self.soil_layer = SoilLayer(self.visible_sprites, self.update_sprites, self.collision_sprites, self.name)

        # Sky
        self.rain = Rain(self.visible_sprites, self.update_sprites, self.name)
        self.raining = False
        self.soil_layer.raining = self.raining
        self.sky = Sky()

        # Shop
        self.shop_active = False
        self.menu = Menu(self.player, self.toggle_shop)

        # Player interaction timers
        self.player.timers['tool_use'].set_args([self.tree_sprites, self.soil_layer])
        self.player.timers['seed_use'].set_args([self.soil_layer])

        # Audio
        self.item_got_sound = pygame.mixer.Sound("../audio/success.wav")
        self.item_got_sound.set_volume(0.3)

    def player_add(self, item, amount = 1):
        self.player.item_inventory[item] += amount
        self.item_got_sound.play()

    def toggle_shop(self):
        self.shop_active = not self.shop_active

    def reset(self):
        # Apples
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

        # Soil
        self.soil_layer.update_plants()
        self.soil_layer.remove_water()

        # Rain
        self.raining = random() < 0.1

        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

        self.sky.start_color = [255,255,255]
        self.sky.time_elapsed = 0

    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type, 1)
                    Particle(plant.rect.topleft, plant.image, [self.visible_sprites, self.update_sprites], LAYERS['main'])
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')
                    plant.kill()

    def load_tree(self, tree_info):
        for tree in self.tree_sprites.sprites():
            if tree.ID == int(tree_info[0]):
                # Kill previous apples
                for apple in tree.apple_sprites.sprites():
                    apple.kill()

                # New apples
                apple_pos = json.loads(tree_info[2])
                for apple in apple_pos:
                    Generic(tuple(apple), tree.apple_surf, [tree.apple_sprites, self.visible_sprites], z = LAYERS['fruit'])

                # Tree health
                tree.health = int(tree_info[1])
                tree.check_death_load()

    def run(self, dt):

        # Draw logic
        self.visible_sprites.custom_draw(self.player)

        # Daytime
        self.sky.display(dt)

        # Tool bar
        self.overlay.display()

        # Shop
        if self.shop_active:
            self.menu.update()
        else:
            # Updates
            self.update_sprites.update(self.collision_sprites, self.interaction_sprites, dt)
            self.plant_collision()

        # Rain
        if self.raining and not self.shop_active:
            self.rain.update()

        if self.player.sleep:
            self.transition.play(dt)


class CameraGroup(pygame.sprite.Group):
    def __init__(self, name):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.map_width, self.map_height = pygame.image.load(f'../graphics/world/{name}/ground.png').get_size()
        self.offset_x_limit = self.map_width - SCREEN_WIDTH
        self.offset_y_limit = self.map_height - SCREEN_HEIGHT

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        if self.offset.x < 0: self.offset.x = 0
        if self.offset.x > self.offset_x_limit: self.offset.x = self.offset_x_limit
        if self.offset.y < 0: self.offset.y = 0
        if self.offset.y > self.offset_y_limit: self.offset.y = self.offset_y_limit

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    self.display_surface.blit(sprite.image, sprite.rect.topleft - self.offset)

class UpdateGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def update(self, collision_sprites, interaction_sprites, dt):
        for sprite in self.sprites():
            if isinstance(sprite, Player):
                sprite.update(collision_sprites, interaction_sprites, dt)
            else:
                sprite.update(dt)
