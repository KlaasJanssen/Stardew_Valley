import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import import_folder_dict, import_folder
from random import choice
import json

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS["soil"]

class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil_water']

class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, frames, groups, soil, check_watered):
        super().__init__(groups)
        self.plant_type = plant_type
        self.frames = frames
        self.soil = soil
        self.check_watered = check_watered

        # Plant growth
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[self.plant_type]
        self.harvestable = False

        # Sprite setup
        self.image = self.frames[int(self.age)]
        self.y_offset = -16 if plant_type == "corn" else -8
        self.rect = self.image.get_rect(midbottom = self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
        self.z = LAYERS['ground_plant']

    def update_plant(self, age):
        self.age = age
        if self.age >= self.max_age:
            self.age = self.max_age
            self.harvestable = True

        if int(self.age) > 0:
            self.z = LAYERS['main']
            self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4)

        self.image = self.frames[int(self.age)]
        self.rect = self.image.get_rect(midbottom = self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))

    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed
            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True


            if int(self.age) > 0:
                self.z = LAYERS['main']
                self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4)


            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom = self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))

class SoilLayer:
    def __init__(self, visible_sprites, update_sprites, collision_sprites, level_name):
        # general
        self.level_name = level_name

        # sprite groups
        self.visible_sprites = visible_sprites
        self.update_sprites = update_sprites
        self.collision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()

        # graphics
        self.soil_surfs = import_folder_dict("../graphics/soil")
        self.water_surfs = import_folder("../graphics/soil_water")

        self.plant_frames = {
            "tomato":import_folder(f'../graphics/fruit/tomato'),
            "corn":import_folder(f'../graphics/fruit/corn')
        }

        self.create_soil_grid()
        self.create_hit_rects()

        # Sounds
        self.hoe_sound = pygame.mixer.Sound("../audio/hoe.wav")
        self.hoe_sound.set_volume(0.2)

        self.plant_sound = pygame.mixer.Sound("../audio/plant.wav")
        self.plant_sound.set_volume(0.2)

    def create_soil_grid(self):
        ground = pygame.image.load(f'../graphics/world/{self.level_name}/ground.png')
        h_tiles = ground.get_width() // TILE_SIZE
        v_tiles = ground.get_height() // TILE_SIZE

        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, _ in load_pygame(f"../data/{self.level_name}.tmx").get_layer_by_name("Farmable").tiles():
            self.grid[y][x].append("F")

    def create_hit_rects(self):
        self.hit_rects = []
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if "F" in cell:
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if 'F' in self.grid[y][x] and not 'X' in self.grid[y][x]:
                    self.hoe_sound.play()
                    self.grid[y][x].append("X")
                    self.create_soil_tile(x, y)
                    if self.raining:
                        self.water_all()

    def water(self, point):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(point):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                if not "W" in self.grid[y][x]:
                    self.grid[y][x].append("W")


                    WaterTile(
                        pos = soil_sprite.rect.topleft,
                        surf = choice(self.water_surfs),
                        groups = [self.visible_sprites, self.water_sprites]
                    )

    def water_all(self):
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if "X" in cell and not "W" in cell:
                    cell.append("W")
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    WaterTile(
                        pos = (x,y),
                        surf = choice(self.water_surfs),
                        groups = [self.visible_sprites, self.water_sprites]
                    )

    def remove_water(self):
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove("W")

    def check_watered(self, pos):
        x = pos[0] // TILE_SIZE
        y = pos[1] // TILE_SIZE
        cell = self.grid[y][x]
        is_watered = 'W' in cell
        return is_watered

    def plant_seed(self, point, seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(point):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE

                if not "P" in self.grid[y][x]:
                    self.plant_sound.play()
                    self.grid[y][x].append("P")
                    Plant(seed, self.plant_frames[seed], [self.visible_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered)
                    return True

        return False

    def create_soil_tile(self, x, y):
        tile_type = self.get_tile_type(x, y)
        SoilTile(
            pos = (x * TILE_SIZE, y * TILE_SIZE),
            surf = self.soil_surfs[tile_type],
            groups = [self.visible_sprites, self.update_sprites, self.soil_sprites])

        for soil in self.soil_sprites.sprites():
            x_soil = soil.rect.left // TILE_SIZE
            y_soil = soil.rect.top // TILE_SIZE
            if abs(x_soil - x) + abs(y_soil - y) == 1:
                tile_type = self.get_tile_type(x_soil, y_soil)
                soil.image = self.soil_surfs[tile_type]

    def get_tile_type(self, x, y):
        tile_type = ""
        if "X" in self.grid[y + 1][x]: tile_type += "t"
        if "X" in self.grid[y - 1][x]: tile_type += "b"
        if "X" in self.grid[y][x - 1]: tile_type += "r"
        if "X" in self.grid[y][x + 1]: tile_type += "l"

        if tile_type == "": tile_type = "o"
        return tile_type

    def load_soil_tiles(self):
        self.soil_sprites.empty()
        # for soil_tile in self.soil_sprites.sprites():
        #     soil_tile.kill()
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if 'X' in cell:
                    tile_type = self.get_tile_type(col_index, row_index)
                    # # tile options
                    # tile_type = ""
                    # if "X" in self.grid[row_index + 1][col_index]: tile_type += "t"
                    # if "X" in self.grid[row_index - 1][col_index]: tile_type += "b"
                    # if "X" in row[col_index - 1]: tile_type += "r"
                    # if "X" in row[col_index + 1]: tile_type += "l"
                    #
                    # if tile_type == "": tile_type = "o"

                    SoilTile(
                        pos = (col_index * TILE_SIZE, row_index * TILE_SIZE),
                        surf = self.soil_surfs[tile_type],
                        groups = [self.visible_sprites, self.update_sprites, self.soil_sprites])

    def create_water_tiles(self):
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if 'W' in cell:
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE

                    WaterTile(
                        pos = (x,y),
                        surf = choice(self.water_surfs),
                        groups = [self.visible_sprites, self.water_sprites]
                    )

    def load_plant(self, load_data):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.topleft == pygame.math.Vector2(json.loads(load_data[2])):
                plant = Plant(
                    plant_type = load_data[0],
                    frames = self.plant_frames[load_data[0]],
                    groups = [self.visible_sprites, self.plant_sprites, self.collision_sprites],
                    soil = soil_sprite,
                    check_watered = self.check_watered
                )
                plant.update_plant(float(load_data[1]))


    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()
