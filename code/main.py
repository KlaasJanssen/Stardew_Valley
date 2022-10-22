import pygame, sys
from time import perf_counter
from settings import *
from level import Level
from player import Player
from mainmenu import MainMenu
import json
from debug import debug
from statistics import mean

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PyDew Valley")

        self.background_music = pygame.mixer.Sound("../audio/music.mp3")
        self.background_music.set_volume(0.2)
        self.background_music.play(loops = -1)

        self.state = "main_menu"
        self.main_menu = MainMenu(self.change_state, self.start_new_game, self.load_game, self.save_game)
        self.selected_save = None

        #self.load_game("../data/saves/3-test.txt")

        self.last_time = perf_counter()
        self.FPS = [1] * 120
        self.frame = 0

    def start_new_game(self, slot, name, save = True):
        self.player = Player()
        self.levels = {
            "farm":Level(self.player, "farm")
        }
        self.active_level = "farm"
        self.level = self.levels[self.active_level]

        self.slot = slot
        self.name = name
        self.state = "game"
        if save:
            self.save_game(slot, name)

    def save_game(self, slot, name):
        with open(f"../data/saves/{slot}-{name}.txt", "w") as f:
            # Sky
            f.write("sky-time_elapsed-")
            json.dump(self.levels[self.active_level].sky.time_elapsed, f)
            f.write("\n")

            # Player
            # Pos
            f.write("player-pos-")
            json.dump(tuple(self.player.pos), f)
            f.write(f"-{self.active_level}")
            f.write("\n")

            # Time played
            f.write("player-time_played-")
            json.dump(self.player.time_played, f)
            f.write("\n")

            #Inventories
            for inv in ["item_inventory", "seed_inventory", "money"]:
                f.write(f"player-{inv}-")
                json.dump(getattr(self.player, inv), f)
                f.write("\n")

            # Levels
            for level_name, level_data in self.levels.items():
                # Soil
                f.write(f"level-{level_name}-soil-grid-")
                json.dump(level_data.soil_layer.grid, f)
                f.write("\n")

                # Plants
                for plant in level_data.soil_layer.plant_sprites.sprites():
                    f.write(f"level-{level_name}-plant-{plant.plant_type}-{plant.age}-{list(plant.soil.rect.topleft)}\n")

                # Trees
                for tree in level_data.tree_sprites.sprites():
                    apple_pos = [list(apple.rect.topleft) for apple in tree.apple_sprites.sprites()]
                    f.write(f"level-{level_name}-tree-{tree.ID}-{tree.health}-{apple_pos}\n")

    def change_state(self, new_state):
        self.state = new_state

    def load_game(self, path):
        save = path.split("/")[-1].split(".txt")[0]
        self.slot = save.split("-")[0]
        self.name = save.split("-")[1]

        with open(path, "r") as f:
            lines = f.readlines()
            for line in lines:
                #print(line.strip("\n"))
                line_split = line.strip("\n").split("-")

                # Player
                if line_split[0] == "player":
                    if line_split[1] == "pos":
                        self.player.pos = pygame.math.Vector2(json.loads(line_split[2]))
                        self.level = self.levels[line_split[3]]
                    else:
                        setattr(self.player, line_split[1], json.loads(line_split[2]))

                # Sky
                elif line_split[0] == "sky":
                    self.level.sky.time_elapsed = json.loads(line_split[2])

                # Soil
                elif line_split[0] == "level":
                    if not line_split[1] in self.levels.keys():
                        self.levels[line_split[1]] = Level(self.player, line_split[1])
                    level = self.levels[line_split[1]]

                    # Soil
                    if line_split[2] == "soil":
                        if line_split[3] == "grid":
                            level.soil_layer.grid = json.loads(line_split[4])
                            level.soil_layer.load_soil_tiles()
                            level.soil_layer.create_water_tiles()

                    # Plants
                    elif line_split[2] == "plant":
                        level.soil_layer.load_plant(line_split[3:])

                    # Trees
                    elif line_split[2] == "tree":
                        level.load_tree(line_split[3:])

            self.selected_save = path

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    #self.save_game("2", "test2")
                    if self.state == "game":
                        self.main_menu.prompt_save(self.slot, self.name)
                    pygame.quit()
                    sys.exit()

            current_time = perf_counter()
            dt = current_time - self.last_time
            if dt > 0.1:
                dt = 0.1
            self.last_time = current_time
            self.FPS[self.frame % 120] = dt
            self.frame += 1

            self.screen.fill("black")
            if self.state == "main_menu":
                self.main_menu.update(dt)
                self.main_menu.display()

            elif self.state == "game":
                self.screen.fill("black")
                self.level.run(dt)

            debug(round(1 / mean(self.FPS)))
            pygame.display.update()

if __name__ == "__main__":
    game = Game()
    game.run()
