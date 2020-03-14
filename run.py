
import sys
import os
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw

import inky


inky_display_WIDTH = 250
inky_display_HEIGHT = 128

class InkyPHAT(inky.Inky):
    WIDTH = 250
    HEIGHT = 128
    WHITE = 0
    BLACK = 1
    RED = 2
    YELLOW = 2

    def __init__(self, colour):
        inky.Inky.__init__(self, resolution=(self.WIDTH, self.HEIGHT), colour=colour, h_flip=False, v_flip=False) 

inky_display = InkyPHAT('black')
inky_display.drawString('こんにちは世界')
inky_display.show()
