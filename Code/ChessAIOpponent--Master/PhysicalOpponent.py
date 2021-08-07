import board
import neopixel
import PhysicalBoard
from gpiozero import Button
from gpiozero import Buzzer
from signal import pause
from settings import *


from time import sleep 

def LED_Position(currentPos_x, currentPos_y, newPos_x, newPos_y, physicalBoardGrid):
    
    redX = 15 - currentPos_x * 2
    redY = 16 + currentPos_y * 2
    greenX = 14 - newPos_x * 2
    greenY = 17 + newPos_y * 2
    
    print(redX, redY, greenX, greenY)
    
    prevState = PhysicalBoard.takePicture('previousState')
    
    pixels[redX] = (250,0,0)
    pixels[redY] = (250,0,0)
    pixels[greenX] = (0,250,0)
    pixels[greenY] = (0,250,0)
    pixels[32] = (0, 0, 250)
    pixels.show()
    
    buzzer.beep(0.2, 6, None, True)
    
    while True:
        button.wait_for_press()
        pixels[redX] = (0,0,0)
        pixels[redY] = (0,0,0)
        pixels[greenX] = (0,0,0)
        pixels[greenY] = (0,0,0)
        pixels[32] = (0, 0, 0)
        pixels.show()
        if(PhysicalBoard.comparePositions(prevState, [newPos_x, newPos_y], physicalBoardGrid)):
            pixels[32] = (0, 250, 0)
            pixels[33] = (0, 250, 0)
            pixels[34] = (0, 250, 0)
            pixels.show()
            sleep(0.5)
            pixels[32] = (0, 0, 0)
            pixels[33] = (0, 0, 0)
            pixels[34] = (0, 0, 0)
            pixels.show()
            break
        pixels[32] = (250, 0, 0)
        pixels[33] = (250, 0, 0)
        pixels[34] = (250, 0, 0)
        pixels.show()
        sleep(0.25)
        pixels[32] = (0, 0, 0)
        pixels[33] = (0, 0, 0)
        pixels[34] = (0, 0, 0)
        pixels.show()
        pixels[redX] = (250,0,0)        
        pixels[redY] = (250,0,0)
        pixels[greenX] = (0,250,0)
        pixels[greenY] = (0,250,0)
        pixels[32] = (0, 0, 250)
        pixels.show()
