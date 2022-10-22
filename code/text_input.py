import pygame
from string import ascii_lowercase as alphabet

class TextInput:
    def __init__(self, pos, size, font_size, max_size = 10):
        self.display_surface = pygame.display.get_surface()
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect(center = pos)

        self.alphabet = {x: pygame.key.key_code(x) for x in alphabet + "0123456789"}
        self.text = ""
        self.font = pygame.font.Font("../font/Stardew_Valley.ttf", font_size)
        self.max_size = max_size
        self.key_pressed = False
        self.create_text_surf()

    def create_text_surf(self):
        self.text_surf = self.font.render(self.text, False, "White")
        self.text_rect = self.text_surf.get_rect(midleft = self.rect.midleft + pygame.math.Vector2(15,0))


    def update(self):
        keys = pygame.key.get_pressed()

        input = False
        for letter, code in self.alphabet.items():
            if keys[code]:
                input = True
                break

        if input or keys[pygame.K_BACKSPACE]:
            if not self.key_pressed:
                self.key_pressed = True
                if keys[pygame.K_BACKSPACE]:
                    if len(self.text) > 0:
                        self.text = self.text[:-1]
                else:
                    for letter, code in self.alphabet.items():
                        if keys[code]:
                            if len(self.text) < self.max_size:
                                if keys[pygame.K_LSHIFT]:
                                    letter = letter.upper()
                                self.text += letter
                self.create_text_surf()
        else:
            self.key_pressed = False

        return self.text


    def draw(self):
        self.display_surface.blit(self.image, self.rect)
        pygame.draw.rect(self.display_surface, "white", self.rect, 2)
        self.display_surface.blit(self.text_surf, self.text_rect)
