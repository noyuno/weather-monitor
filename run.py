
import sys
import os
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw

import inky


inky_display_WIDTH = 250
inky_display_HEIGHT = 128
DEFAULT_FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
font22 = ImageFont.truetype(DEFAULT_FONT, 22, encoding='unic')


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
img = Image.new("P", (inky_display_WIDTH, inky_display_HEIGHT))
draw = ImageDraw.Draw(img)
draw.text((0,0),text1,font=font22,fill=1)
inky_display.set_image(img)
inky_display.show()
