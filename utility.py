import pygame 

def init(screen):
    global SCREEN
    SCREEN = screen

class old_textbox:
    '''A more compact way of making a text box.
    message --> string of some kind
    font --> a valid font name
    textCol --> a tuple, (redval,greenval,blueval)
    backgroundCol --> also a tuple, (redval,greenval,blueval)
    pos  --> a tuple again, (x coord,y coord)'''

    def __init__(self,message,font,pos,textCol=(255,255,255),backgroundCol=(0,0,0),tags=[]):
        self.message = message
        self.font = font
        self.textCol = textCol
        self.backgroundCol = backgroundCol
        self.pos = pos
        self.textRect = None
        self.isShowing = True
        self.tags = tags
        self.wasPressed = False
        
        self.display()

    def display(self):
        text = self.font.render(str(self.message), True, self.textCol,self.backgroundCol)
        self.textRect = text.get_rect()
        self.textRect.center = self.pos
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

        if up and down and left and right and self.isShowing:
            if not self.wasPressed:
                pressed = True

            self.wasPressed = True
        else:
            self.wasPressed = False

        return (pressed)
    
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
