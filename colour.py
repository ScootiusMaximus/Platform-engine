'''A module to quickly get colours'''
from random import randint

red = (255,0,0)
orange = (255,125,0)
yellow = (255,255,0)
green = (0,255,0)
cyan = (0,255,255)
blue = (0,0,255)
purple = (125,0,255)
magenta = (255,0,255)
white = (255,255,255)
lightgrey = (200,200,200)
darkgrey = (100,100,100)
black = (0,0,0)

colours = [red,orange,yellow,green,cyan,blue,purple,magenta,white,lightgrey,darkgrey,black]

def randCol():
    return colours[ranint(0,len(colours)-1)]