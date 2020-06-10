import pygame
import numpy
import colorsys

#An instance allows the user to click and pick a color
class ColorWheel:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.top_left = None

    #Returns the color box surface associated with this object
    def get_surface(self):
        colors = []
        for i in range(self.width):
            num = i/(self.width-1)
            color = self.decimal_to_rgb(num)
            colors.append([])
            for j in range(self.height):
                colors[i].append(color)

        return pygame.surfarray.make_surface(numpy.array(colors))

    def decimal_to_rgb(self, num):
        rgb = colorsys.hsv_to_rgb(num / 3., 1.0, 1.0)
        return tuple([round(255*x) for x in rgb])

    def get_color_from_point(self, point):
        x = point[0]-self.top_left[0]
        return self.decimal_to_rgb(x/(self.width-1))

    def handle_event(self, event):
        rect = pygame.Rect(self.top_left, (self.width, self.height))
        if(event.type == pygame.MOUSEBUTTONDOWN):
            #If the mouse was clicked within the confines of this box
            if(rect.collidepoint(event.pos)):
                return self.get_color_from_point(event.pos)
            else:
                return None