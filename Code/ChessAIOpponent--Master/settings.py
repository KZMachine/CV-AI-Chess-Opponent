import pygame

from gpiozero import Button
from gpiozero import Buzzer
import board
import neopixel
from time import sleep

button = Button(2)
buzzer = Buzzer(23)


pixels = neopixel.NeoPixel(board.D18, 60, auto_write=False)


# Screen components
TILE_SIZE = 64
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOARD_SIZE = TILE_SIZE * 8
BOARD_X = (SCREEN_WIDTH-BOARD_SIZE)//2
BOARD_Y = int((SCREEN_HEIGHT / 2) - (BOARD_SIZE / 2))
IMG_SCALE = (TILE_SIZE, TILE_SIZE)



# Basic colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game colors
SMALL_TEXT_COLOR = (241, 250, 238)
LARGE_TEXT_COLOR = (230, 57, 70)
#BG_COLOR = (29, 53, 87)
BG_COLOR = (250, 250, 250)
BG_COLOR_LIGHT = (70, 70, 70)
TILE_COLOR_LIGHT = (241, 250, 238)
TILE_COLOR_DARK = (80, 80, 80)

# Create screen
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

#Minimax Depth
MINIMAX_DEPTH = 80

# Converts 8x8 grid locations to pixel coordinates
def to_coords(x, y):
    return BOARD_X + x * TILE_SIZE, BOARD_Y + y * TILE_SIZE

def victory():
    for j in range(3):
        for i in range(0, 35):
            pixels[i] = (0, 0 ,0)
            pixels[i+1] = (250, 250 ,0)
            pixels.show()
            sleep(0.075)
