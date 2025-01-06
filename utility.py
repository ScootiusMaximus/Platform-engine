from enum import nonmember

import pygame

mouse = {"left":[False,False],
        "right":[False,False],
         "pos":[0,0]}

def init(screen):
    global SCREEN
    SCREEN = screen

def tick():
    global mouse
    mouse["left"][1] = mouse["left"][0]
    mouse["right"][1] = mouse["right"][0]

    mouse["pos"] = list(pygame.mouse.get_pos())
    presses = pygame.mouse.get_pressed()
    mouse["left"][0] = presses[0]
    mouse["right"][0] = presses[1]

class old_textbox:
    '''A more compact way of making a text box.
    message --> string of some kind
    font --> a valid font name
    textCol --> a tuple, (redval,greenval,blueval)
    backgroundCol --> also a tuple, (redval,greenval,blueval)
    pos  --> a tuple again, (x coord,y coord)'''

    def __init__(self,message,font,pos,textCol=(255,255,255),backgroundCol=(0,0,0),oval=False,tags=[],center=True):
        self.message = message
        self.font = font
        self.textCol = textCol
        self.backgroundCol = backgroundCol
        self.pos = pos
        self.textRect = None
        self.isShowing = True
        self.tags = tags
        self.wasPressed = False
        self.oval = oval
        self.center = center
        self.mouse = {}

        text = self.font.render(str(self.message), True, self.textCol, None)
        self.textRect = text.get_rect()

    def get_presses(self):
        self.mouse = mouse

    def display(self):
        bg = None if self.oval else self.backgroundCol
        text = self.font.render(str(self.message), True, self.textCol,bg)
        self.textRect = text.get_rect()
        if self.center:
            self.textRect.center = self.pos
        else:
            self.textRect.topleft = self.pos
        if self.oval:
            pygame.draw.ellipse(SCREEN,self.backgroundCol,self.textRect)
        SCREEN.blit(text, self.textRect)

    def update_message(self, message='Textbox'):
        self.message = message

    def update_colour(self, textCol=(255,255,255), backgroundCol=(0,0,0)):
        self.textCol = textCol
        self.backgroundCol = backgroundCol

    def isPressed(self):
        pressed = False
        left, right, up, down = False, False, False, False

        try:
            if pygame.mouse.get_pos()[0] > self.textRect[0]:
                left = True
            if pygame.mouse.get_pos()[0] < self.textRect[0] + self.textRect[2]:
                right = True
            if pygame.mouse.get_pos()[1] > self.textRect[1]:
                up = True
            if pygame.mouse.get_pos()[1] < self.textRect[1] + self.textRect[3]:
                down = True
        except NotImplementedError:
            left, right, up, down = False, False, False, False

        if (up and down and left and right and self.isShowing
                and self.mouse["left"][0] and not self.mouse["left"][1]):
            if not self.wasPressed:
                pressed = True

            self.wasPressed = True
        else:
            self.wasPressed = False

        return (pressed)

class Pressable:
    def __init__(self,xpos,ypos,width,height,mode=1):
        '''mode 1 - hover to press
        mode 2 - click to press'''
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.height = height
        self.canBePressed = True
        self.mode = mode

        self.wasPressed = False
        self.rect = [xpos,ypos,width,height]

    def move_to(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.rect = [xpos, ypos, self.width, self.height]

    def pressed(self):
        press = False
        left, right, up, down = False, False, False, False

        try:
            if pygame.mouse.get_pos()[0] > self.rect[0]:
                left = True
            if pygame.mouse.get_pos()[0] < self.rect[0] + self.rect[2]:
                right = True
            if pygame.mouse.get_pos()[1] > self.rect[1]:
                up = True
            if pygame.mouse.get_pos()[1] < self.rect[1] + self.rect[3]:
                down = True
        except NotImplementedError:
            left, right, up, down = False, False, False, False

        if self.mode == 1:
            if up and down and left and right: #and pygame.mouse.get_pressed()[0]:
                if not self.wasPressed:
                    press = True
                self.wasPressed = True
            else:
                self.wasPressed = False
        elif self.mode == 2:
            if up and down and left and right and pygame.mouse.get_pressed()[0]:
                if not self.wasPressed:
                    press = True
                self.wasPressed = True
            else:
                self.wasPressed = False

        return press
    
class rainbow:
    def __init__(self):
        self.r = 255
        self.g = 0
        self.b = 0
        self.inc = [0,1,0]

    def tick(self):
        self.r += self.inc[0]
        self.g += self.inc[1]
        self.b += self.inc[2]

        if self.r == 255 and self.g == 0 and self.b == 0:
            self.inc = [0,1,0]
        if self.g == 255 and self.r == 0 and self.b == 0:
            self.inc = [0,0,1]
        if self.b == 255 and self.r == 0 and self.g == 0:
            self.inc = [1,0,0]

        if self.r == 255 and self.g == 255:
            self.inc[0] = -1
            self.inc[1] = 0

        if self.g == 255 and self.b == 255:
            self.inc[1] = -1
            self.inc[2] = 0

        if self.b == 255 and self.r == 255:
            self.inc[2] = -1
            self.inc[0] = 0

    def get(self):
        return((self.r,self.g,self.b))

class healthBar:
    def __init__(self, xpos, ypos, maxhp=10):
        self.maxhp = maxhp
        self.hp = maxhp
        self.xpos = xpos
        self.ypos = ypos
        self.col = (0, 255, 0)
        self.inc = 255 / self.maxhp
        self.width = 25
        self.height = 10

    def draw(self):
        val = 255 - ((self.maxhp - self.hp) * self.inc)
        if val <= 0: val = 0
        self.col = (255 - val, val, 0)
        size = self.width * (self.hp / self.maxhp)
        pygame.draw.rect(SCREEN, self.col,(self.xpos, self.ypos, size, self.height))
        pygame.draw.rect(SCREEN, (255,255,255), (self.xpos, self.ypos, self.width, self.height),width=3)

class Slider:
    def __init__(self,xpos,ypos,length=100,width=30):
        self.xpos = xpos
        self.ypos = ypos
        self.length = length
        self.width = width
        self.sliderPos = self.xpos + self.length

    def move_to(self,xpos=None,ypos=None):
        xdiff = self.xpos - xpos
        if xpos is not None:
            self.xpos = xpos
            self.sliderPos -= xdiff
        if ypos is not None:
            self.ypos = ypos

    def draw(self):
        pygame.draw.rect(SCREEN,(50,50,50),(self.xpos,self.ypos,self.length,self.width))
        pygame.draw.rect(SCREEN,(150,150,150),(self.sliderPos,self.ypos-10,15,self.width+20))

    def update(self):
        left, right, up, down = False, False, False, False
        if pygame.mouse.get_pos()[0] > self.xpos:
            left = True
        if pygame.mouse.get_pos()[0] < self.xpos+self.length:
            right = True
        if pygame.mouse.get_pos()[1] > self.ypos:
            up = True
        if pygame.mouse.get_pos()[1] < self.ypos+self.width:
            down = True

        if left and right and up and down:
            self.sliderPos = pygame.mouse.get_pos()[0]

    def get(self):
        '''Returns a float between 0 and 1 of the slider's value '''
        relativePos = self.sliderPos-self.xpos
        return relativePos / self.length