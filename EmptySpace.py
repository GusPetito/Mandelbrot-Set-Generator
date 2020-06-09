from pygame import Surface

#A rigid empty space to be used for formatting
class EmptySpace:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def get_surface(self):
        return Surface((self.width, self.height))