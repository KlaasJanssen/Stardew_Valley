import pygame
from os import walk

def import_folder(path):
    surface_list = []
    for _,__,imgs in walk(path):
        for img in imgs:
            surf = pygame.image.load(path + "/" + img).convert_alpha()
            surface_list.append(surf)
    return(surface_list)

def import_folder_dict(path):
    surface_dict = {}
    for _,__,imgs in walk(path):
        for img in imgs:
            surf = pygame.image.load(path + "/" + img).convert_alpha()
            surface_dict[img.strip(".png")] = surf
    return(surface_dict)
