import pygame
from settings import *
from button import Button, LoadSaveButton, OverwriteButton
from os import walk
import os
from text_input import TextInput

class MainMenu:
    def __init__(self, change_state, start_new_game, load_game, save_game):
        self.display_surface = pygame.display.get_surface()
        self.change_game_state = change_state
        self.state = "title_screen"
        self.font = pygame.font.Font("../font/LycheeSoda.ttf", 60)
        self.new_slot = None

        # Functions
        self.start_new_game = start_new_game
        self.load_game = load_game
        self.save_game = save_game

        # Title screen
        self.title_background = pygame.image.load("../graphics/menu/title_screen.jpg").convert_alpha()
        self.key_surf = self.font.render("Press any key to start", False, "White")
        self.key_rect = self.key_surf.get_rect(midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 10))
        self.time_elapsed = 0
        self.move_from_menu = False

        # Main menu
        self.menu_background = pygame.image.load("../graphics/menu/menu_background.png").convert_alpha()
        self.main_menu_buttons = []
        self.main_menu_buttons.append(Button((SCREEN_WIDTH // 2,120), (SCREEN_WIDTH * 0.6, 120), "New game", 60, self.change_menu_state, ["name_select"]))
        self.main_menu_buttons.append(Button((SCREEN_WIDTH // 2,280), (SCREEN_WIDTH * 0.6, 120), "Load game", 60, self.change_menu_state, ["load_game"]))
        self.main_menu_buttons.append(Button((SCREEN_WIDTH // 2,440), (SCREEN_WIDTH * 0.6, 120), "Options", 60))
        self.main_menu_buttons.append(Button((SCREEN_WIDTH // 2,600), (SCREEN_WIDTH * 0.6, 120), "Credits", 60))

        # Load menu
        self.load_menu_buttons = []
        save_info = walk("../data/saves")
        for _,__,save_files in save_info:
            self.save_files = save_files
        for save in range(5):
            if save < len(self.save_files):
                self.load_menu_buttons.append(
                    LoadSaveButton(
                        pos = (SCREEN_WIDTH // 2, 100 + (96 + 40) * save),
                        size = (SCREEN_WIDTH * 0.6, 96),
                        slot = save + 1,
                        text = self.save_files[save].split(".txt")[0].split("-")[1],
                        font_size = 60,
                        load_save = self.load_game,
                        start_new_game = self.start_new_game,
                        save_file = self.save_files[save],
                        locked = False
                    )
                )
            else:
                self.load_menu_buttons.append(
                    LoadSaveButton(
                        pos = (SCREEN_WIDTH // 2, 100 + (96 + 40) * save),
                        size = (SCREEN_WIDTH * 0.6, 96),
                        slot = save,
                        text = "No saved data",
                        font_size = 60,
                        load_save = self.load_game,
                        start_new_game = self.start_new_game,
                        save_file = "",
                        locked = True
                    )
                )

        # Save prompt
        self.prompt_background = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.prompt_background.fill((60, 166, 252))
        self.prompt_rect = self.prompt_background.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.prompt_text_top_surf = self.font.render("Do you want to save", False, "White")
        self.prompt_text_bottom_surf = self.font.render("the game?", False, "White")
        self.prompt_text_top_rect = self.prompt_text_top_surf.get_rect(midtop = self.prompt_rect.midtop + pygame.math.Vector2(0, 30))
        self.prompt_text_bottom_rect = self.prompt_text_bottom_surf.get_rect(midtop = self.prompt_text_top_rect.midbottom + pygame.math.Vector2(0, 30))

        self.save_button = Button(
                                pos = self.prompt_rect.midbottom + pygame.math.Vector2(-120, -80),
                                size = (200,100),
                                text = "Yes",
                                font_size = 50,
                                func = save_game
                                )
        self.quit_button = Button(
                                pos = self.prompt_rect.midbottom + pygame.math.Vector2(120, -80),
                                size = (200,100),
                                text = "No",
                                font_size = 50
                                )

        # Name select
        self.name_input = TextInput(
                                    pos = ((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) + pygame.math.Vector2(0,50)),
                                    size = (SCREEN_WIDTH // 2, 100),
                                    font_size = 80,
                                    max_size = 16
                                    )

        self.start_game_button = Button(
                                    pos = ((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) + pygame.math.Vector2(0,200)),
                                    size = (400,100),
                                    text = "Start game",
                                    font_size = 50
        )

        self.name_select_text_surf = self.font.render("Choose a name for your save:", False, "White")
        self.name_select_text_rect = self.name_select_text_surf.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) + pygame.math.Vector2(0,-150))
        self.overwrite_buttons = []

        if len(self.save_files) < 5:
            self.new_slot = len(self.save_files) + 1
            self.display_overwrite = False
        else:
            self.display_overwrite = True
            self.overwrite_text_surf = self.font.render("Choose a file to overwrite:", False, "White")
            self.overwrite_text_rect = self.overwrite_text_surf.get_rect(center = (SCREEN_WIDTH // 2, 65))

            self.name_select_text_rect.center += pygame.math.Vector2(0, 210)
            self.name_input.rect.center += pygame.math.Vector2(0, 110)
            self.start_game_button.change_position((0,90))

            for save in range(5):
                self.overwrite_buttons.append(
                    OverwriteButton(
                        pos = (SCREEN_WIDTH // 2, 150 + (40 + 10) * save),
                        size = (SCREEN_WIDTH * 0.6, 40),
                        slot = save + 1,
                        text = self.save_files[save].split(".txt")[0].split("-")[1],
                        font_size = 30,
                        save_file = self.save_files[save]
                    )
                )


    def change_menu_state(self, new_state):
        self.state = new_state

    def create_new_game(self, slot, name):
        self.start_new_game(slot, name)

    def display(self):
        if self.state == "title_screen":
            self.display_surface.blit(self.title_background, (0,0))
            if int(self.time_elapsed * 1.5) % 2:
                self.display_surface.blit(self.key_surf, self.key_rect)

        elif self.state == "menu":
            #self.display_surface.fill((65, 135, 240))
            self.display_surface.blit(self.menu_background, (0,0))
            for button in self.main_menu_buttons:
                button.display()

        elif self.state == "load_game":
            self.display_surface.blit(self.menu_background, (0,0))
            for button in self.load_menu_buttons:
                button.display()

        elif self.state == "name_select":
            self.display_surface.blit(self.menu_background, (0,0))
            if self.display_overwrite:
                self.display_surface.blit(self.overwrite_text_surf, self.overwrite_text_rect)
                for button in self.overwrite_buttons:
                    button.display()

            self.display_surface.blit(self.name_select_text_surf, self.name_select_text_rect)
            self.name_input.draw()
            self.start_game_button.display()

    def prompt_save(self, slot, name):
        prompt = True
        self.save_button.args = [slot, name]
        while prompt:
            pygame.event.get()
            # Draw prompt
            self.display_surface.blit(self.prompt_background, self.prompt_rect)
            pygame.draw.rect(self.display_surface, (225,120,62), self.prompt_rect, 8)
            self.display_surface.blit(self.prompt_text_top_surf, self.prompt_text_top_rect)
            self.display_surface.blit(self.prompt_text_bottom_surf, self.prompt_text_bottom_rect)

            # Update buttons
            if self.save_button.detect_click() or self.quit_button.detect_click():
                prompt = False

            # Draw buttons
            self.save_button.display()
            self.quit_button.display()
            pygame.display.update()

    def update(self, dt):
        if self.state == "title_screen":
            self.time_elapsed += dt
            keys = pygame.key.get_pressed()
            mouse_pressed = pygame.mouse.get_pressed()
            if any(keys) or any(mouse_pressed):
                self.move_from_menu = True
            elif self.move_from_menu:
                self.state = "menu"

        elif self.state == "menu":
            for button in self.main_menu_buttons:
                button.detect_click()

        elif self.state == "load_game":
            for button in self.load_menu_buttons:
                button.detect_click()

        elif self.state == "name_select":
            self.name = self.name_input.update()

            if self.start_game_button.detect_click():
                if len(self.name) > 0:
                    if self.display_overwrite:
                        for button in self.overwrite_buttons:
                            if button.selected:
                                self.new_slot = button.slot
                                os.remove(f"../data/saves/{self.save_files[self.new_slot - 1]}")
                                self.create_new_game(self.new_slot, self.name)
                                break
                    else:
                        self.create_new_game(self.new_slot, self.name)

            if self.display_overwrite:
                for button in self.overwrite_buttons:
                    if button.update():
                        for button2 in self.overwrite_buttons:
                            if not button2 == button:
                                button2.selected = False
