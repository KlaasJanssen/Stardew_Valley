import pygame

class Timer:
    def __init__(self, duration, func = None, args = []):
        self.duration = duration
        self.func = func
        self.args = args
        self.time_elapsed = 0
        self.active = False

    def set_args(self, args):
        self.args = args

    def activate(self):
        self.active = True
        self.time_elapsed = 0

    def deactivate(self):
        self.active = False
        self.time_elapsed = 0

    def update(self, dt):
        if self.active:
            self.time_elapsed += dt
            if self.time_elapsed > self.duration:
                self.deactivate()
                if self.func:
                    self.func(*self.args)
