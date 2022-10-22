import pygame
from settings import *
from support import *
from timer import Timer
import json

class Player(pygame.sprite.Sprite):
    def __init__(self):#, pos, groups, toggle_shop):
        super().__init__()

        # General stats
        self.time_played = 0

        # Assets
        self.import_assets()
        self.status = "down_idle"
        self.frame_index = 0

        # General setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.z = LAYERS['main']

        # Movement
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 500

        # Timers
        self.timers = {
            'tool_use': Timer(0.35, self.use_tool),
            'tool_switch': Timer(0.2),
            'seed_use': Timer(0.35, self.use_seed),
            'seed_switch': Timer(0.2)
        }

        # Tools
        self.tools = ['hoe', 'axe', 'water']
        # self.tool_index = 0
        # self.selected_tool = self.tools[self.tool_index]

        # Seeds
        self.seeds = ['corn', 'tomato']
        # self.seed_index = 0
        # self.selected_seed = self.seeds[self.seed_index]

        # Tool index
        self.total_tools = [*self.tools, *self.seeds]
        self.max_index = len(self.total_tools)
        self.index = 0
        self.tool_indices = [pygame.key.key_code(str(x)) for x in range(1, self.max_index + 1)]
        self.selected_tool = self.total_tools[self.index]

        # Inventory
        self.item_inventory = {
            "wood":   0,
            "apple":  0,
            "corn":   0,
            "tomato": 0
        }

        self.seed_inventory = {
            'corn':5,
            'tomato':5
        }
        self.money = 0

        # Sleep
        self.sleep = False

        # Shop
        #self.toggle_shop = toggle_shop

        # Sound
        self.watering = pygame.mixer.Sound("../audio/water.mp3")
        self.watering.set_volume(0.2)

        with open("../data/test.txt", "w") as f:
            f.write("player-item_inventory-")
            json.dump(self.item_inventory, f)

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]

    def import_assets(self):
        self.animations = {}
        for action in ["", "_idle", "_hoe", "_axe", "_water"]:
            for direction in ["up", "down", "left", "right"]:
                animation = direction + action
                full_path = "../graphics/character/" + animation
                self.animations[animation] = import_folder(full_path)

    def input(self, interaction_sprites):
        keys = pygame.key.get_pressed()

        if not self.timers["tool_use"].active and not self.sleep:
            # Direction vertical
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and not (keys[pygame.K_DOWN] or keys[pygame.K_s]):
                self.direction.y = -1
                self.status = "up"
            elif (keys[pygame.K_DOWN] or keys[pygame.K_s]) and not (keys[pygame.K_UP] or keys[pygame.K_w]):
                self.direction.y = 1
                self.status = "down"
            else:
                self.direction.y = 0

            # Direction horizontal
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                self.direction.x = -1
                self.status = "left"
            elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not (keys[pygame.K_LEFT] or keys[pygame.K_a]):
                self.direction.x = 1
                self.status = "right"
            else:
                self.direction.x = 0

            if not self.direction.magnitude() == 0:
                self.direction = self.direction.normalize()

            # Tool use
            if keys[pygame.K_SPACE]:
                self.timers["tool_use"].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # Switch tools
            # if keys[pygame.K_q] and not self.timers["tool_switch"].active:
            #     self.tool_index += 1
            #     if self.tool_index >= len(self.tools):
            #         self.tool_index = 0
            #
            #     self.selected_tool = self.tools[self.tool_index]
            #     self.timers["tool_switch"].activate()

            # Seed use
            # if keys[pygame.K_LCTRL]:
            #     self.timers["seed_use"].activate()
            #     self.direction = pygame.math.Vector2()
            #     self.frame_index = 0

            # # Switch seeds
            # if keys[pygame.K_e] and not self.timers["seed_switch"].active:
            #     self.seed_index += 1
            #     if self.seed_index >= len(self.seeds):
            #         self.seed_index = 0
            #
            #     self.selected_seed = self.seeds[self.seed_index]
            #     self.timers["seed_switch"].activate()

            # Switch tools/seeds
            if keys[pygame.K_q] and not self.timers["tool_switch"].active:
                self.index += 1
                if self.index >= self.max_index:
                    self.index = 0

                self.selected_tool = self.total_tools[self.index]
                self.timers["tool_switch"].activate()

            for tool_index, location in enumerate(self.tool_indices):
                if keys[location]:
                    self.index = tool_index
                    self.selected_tool = self.total_tools[self.index]


            # Bed interaction
            if keys[pygame.K_RETURN]:
                collided_interaction_sprite = pygame.sprite.spritecollide(self, interaction_sprites, False)
                if collided_interaction_sprite:
                    if collided_interaction_sprite[0].name == 'Trader':
                        self.toggle_shop()
                    elif collided_interaction_sprite[0].name == 'Bed' and "left" in self.status:
                        self.sleep = True
                        self.status = "left_idle"

    def get_status(self):

        # Idle
        if self.direction == pygame.math.Vector2((0,0)):
            self.status = self.status.split("_")[0] + "_idle"

        if self.timers["tool_use"].active and self.selected_tool in self.tools:
            self.status = self.status.split("_")[0] + "_" + self.selected_tool

    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split("_")[0]]

    def use_tool(self, tree_sprites, soil_layer):
        self.get_target_pos()

        if self.selected_tool == 'hoe':
            soil_layer.get_hit(self.target_pos)

        if self.selected_tool == 'axe':
            for tree in tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()

        if self.selected_tool == "water":
            self.watering.play()
            soil_layer.water(self.target_pos)

        if self.selected_tool in self.seeds:
            if self.seed_inventory[self.selected_tool] > 0:
                if soil_layer.plant_seed(self.target_pos, self.selected_tool):
                    self.seed_inventory[self.selected_tool] -= 1

    def use_seed(self, soil_layer):
        self.get_target_pos()
        if self.seed_inventory[self.selected_seed] > 0:
            if soil_layer.plant_seed(self.target_pos, self.selected_seed):
                self.seed_inventory[self.selected_seed] -= 1

    def collision(self, collision_sprites, direction):
        for sprite in collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == "horizontal":
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        else:
                            self.hitbox.right =  sprite.hitbox.left
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                    if direction == "vertical":
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        else:
                            self.hitbox.top =  sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self, collision_sprites, dt):
        # Horizontal
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision(collision_sprites, "horizontal")

        # Vertical
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision(collision_sprites, "vertical")

    def update_timers(self, dt):
        for timer in self.timers.values():
            timer.update(dt)

    def update(self, collision_sprites, interaction_sprites, dt):
        self.update_timers(dt)
        self.input(interaction_sprites)
        self.move(collision_sprites, dt)
        self.get_status()
        self.animate(dt)

        self.time_played += dt
