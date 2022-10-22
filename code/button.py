import pygame

class Button:
    def __init__(self, pos, size, text, font_size, func = None, args = []):
        # General setup
        self.display_surface = pygame.display.get_surface()
        self.pos = pos
        self.size = size
        self.text = text
        self.func = func
        self.args = args

        # Surface
        self.unpressed_surf = pygame.Surface(size)
        self.unpressed_surf.fill((233,176,97))
        self.pressed_surf = pygame.Surface(size)
        self.pressed_surf.fill((255,202,130))

        self.image = self.unpressed_surf
        self.rect = self.image.get_rect(center = self.pos)

        # Text
        self.font = pygame.font.Font("../font/Stardew_Valley.ttf", font_size)
        self.text_surf = self.font.render(text, False, "White")
        self.text_rect = self.text_surf.get_rect(center = self.rect.center)

        # Click variables
        self.mouse_over_button = False
        self.clicked = False

    def detect_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over_button = True
            if pygame.mouse.get_pressed()[0]:
                self.clicked = True
            else:
                if self.clicked:
                    self.clicked = False
                    if self.func != None:
                        self.func(*self.args)
                    return True
                self.clicked = False
        else:
            self.clicked = False
            self.mouse_over_button = False
        return False

    def change_position(self, offset):
        self.rect.center += pygame.math.Vector2(offset)
        self.text_rect.center += pygame.math.Vector2(offset)

    def display(self):
        if self.mouse_over_button:
            self.image = self.pressed_surf
        else:
            self.image = self.unpressed_surf

        self.display_surface.blit(self.image, self.rect)
        pygame.draw.rect(self.display_surface, (225,120,62), self.rect, 4)
        self.display_surface.blit(self.text_surf, self.text_rect)

class LoadSaveButton(Button):
    def __init__(self, pos, size, slot, text, font_size, load_save, start_new_game, save_file, locked):
        self.text = text
        self.slot = slot
        self.save_file = f"../data/saves/{save_file}"
        self.start_new_game = start_new_game
        self.load_save = load_save
        self.locked = locked
        #self.args = [slot, text]
        super().__init__(pos, size, text, font_size, self.load_game, [])

        self.locked_surf = pygame.Surface(size)
        self.locked_surf.fill((206,206,206))

        #self.unlocked_font = pygame.font.Font("../font/Stardew_Valley.ttf", 30)
        if not locked:
            self.name_surf = self.font.render(text, False, "white")
            self.name_rect = self.name_surf.get_rect(midleft = self.rect.midleft + pygame.math.Vector2(20,0))
            with open(self.save_file, "r") as f:
                for line in f.readlines():
                    split_line = line.strip("\n").split("-")
                    if split_line[0] == "player":
                        if split_line[1] == "time_played":
                            time = float(split_line[2])

            self.time_surf = self.font.render(self.convert_time(time),False,"white")
            self.time_rect = self.time_surf.get_rect(midright = self.rect.midright + pygame.math.Vector2(-20,0))

    def convert_time(self, time):
        hours = int(time / 3600)
        minutes = int((time / 60) % 60)
        return f"{hours}:{minutes:02d}"

    def load_game(self):
        self.start_new_game(self.slot, self.text, save = False)
        self.load_save(self.save_file)

    def detect_click(self):
        if not self.locked:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.mouse_over_button = True
                if pygame.mouse.get_pressed()[0]:
                    self.clicked = True
                else:
                    if self.clicked:
                        self.clicked = False
                        if self.func != None:
                            self.func(*self.args)
                        return True
                    self.clicked = False
            else:
                self.clicked = False
                self.mouse_over_button = False
            return False

    def display(self):
        if self.locked:
            self.image = self.locked_surf
            self.display_surface.blit(self.image, self.rect)
            pygame.draw.rect(self.display_surface, (150,150,150), self.rect, 4)
            self.display_surface.blit(self.text_surf, self.text_rect)
        else:
            if self.mouse_over_button:
                self.image = self.pressed_surf
            else:
                self.image = self.unpressed_surf

            self.display_surface.blit(self.image, self.rect)
            pygame.draw.rect(self.display_surface, (225,120,62), self.rect, 4)
            self.display_surface.blit(self.name_surf, self.name_rect)
            self.display_surface.blit(self.time_surf, self.time_rect)

class OverwriteButton(Button):
    def __init__(self, pos, size, slot, text, font_size, save_file):
        super().__init__(pos, size, text, font_size)
        self.save_file = f"../data/saves/{save_file}"
        self.slot = slot

        self.name_surf = self.font.render(text, False, "white")
        self.name_rect = self.name_surf.get_rect(midleft = self.rect.midleft + pygame.math.Vector2(20,0))

        with open(self.save_file, "r") as f:
            for line in f.readlines():
                split_line = line.strip("\n").split("-")
                if split_line[0] == "player":
                    if split_line[1] == "time_played":
                        time = float(split_line[2])

        self.time_surf = self.font.render(self.convert_time(time),False,"white")
        self.time_rect = self.time_surf.get_rect(midright = self.rect.midright + pygame.math.Vector2(-20,0))

        self.selected = False

    def update(self):
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if self.detect_click():
            self.selected = True
            return True
        return False

    def convert_time(self, time):
        hours = int(time / 3600)
        minutes = int((time / 60) % 60)
        return f"{hours}:{minutes:02d}"


    def display(self):
        if self.mouse_over_button:
            self.image = self.pressed_surf
        else:
            self.image = self.unpressed_surf

        self.display_surface.blit(self.image, self.rect)
        if self.selected:
            #pygame.draw.rect(self.display_surface, (243,157,109), self.rect, 4)
            pygame.draw.rect(self.display_surface, (255,255,255), self.rect, 4)
        else:
            pygame.draw.rect(self.display_surface, (225,120,62), self.rect, 4)
        self.display_surface.blit(self.name_surf, self.name_rect)
        self.display_surface.blit(self.time_surf, self.time_rect)
