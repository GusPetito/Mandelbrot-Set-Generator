import pygame
import re

class NumberInputBox():
    def __init__(self, top_left, length, height, color, font, regex_to_match, text = ''):
        self.top_left = top_left
        self.length = length
        self.height = height
        self.color = color
        self.text = text
        self.is_in_focus = False
        self.font = font
        self.regex_to_match = regex_to_match

    #Handles the mouse and keyboard events for a game
    def handle_event(self, event):
        rect = pygame.Rect(self.top_left, (self.length, self.height))
        if(event.type == pygame.MOUSEBUTTONDOWN):
            #If the mouse was clicked within the confines of this input box
            if(rect.collidepoint(event.pos)):
                self.is_in_focus = True
            else:
                self.is_in_focus = False

        elif(event.type == pygame.KEYDOWN):
            #Only type if this is in focus
            if(self.is_in_focus):
                self.try_to_add_text(event.key)

    #Add the key to the text
    def try_to_add_text(self, key):
        temp_text = (self.text + pygame.key.name(key)) if key != pygame.K_BACKSPACE else self.text[:-1]
        #Make sure the new text matches the given regex. If not, do not update text
        if(re.fullmatch(self.regex_to_match, temp_text)):
            self.text = temp_text

    #Returns the surface associated with this text box
    def get_surface(self):
        text_surface = pygame.Surface((self.length, self.height))
        temp_color = (200, 200, 255) if self.is_in_focus else self.color
        text_surface.fill(temp_color)
        text_surface.blit(self.font.render(self.text, True, (0,0,0)), (0,0))
        return text_surface

    #Returns the number version of the text
    def get_factor(self):
        return float(self.text) if len(self.text) else .01