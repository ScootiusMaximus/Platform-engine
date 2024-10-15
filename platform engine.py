import colour
import json
import math
import pygame
import random 
import sys  
import utility as u


SCRW = 800
SCRH = 600
TICKRATE = 60

pygame.init()
pygame.mixer.init()
SCREEN = pygame.display.set_mode((SCRW,SCRH),pygame.RESIZABLE)
u.init(SCREEN)
rgb = u.rainbow()
clock = pygame.time.Clock()
font18 = pygame.font.SysFont("notoserif",18)
font28 = pygame.font.SysFont("notoserif",28)
font50 = pygame.font.SysFont("notoserif",50)
fontTitle = pygame.font.SysFont("courier new",70)
fontTitle.set_bold(True)

class Images:
    def __init__(self):
        self.fanBase = pygame.image.load("fan base.png")
        self.fanColumn = pygame.image.load("fan column.png")
        self.body = pygame.image.load("body.png")
        self.enemyBody = pygame.image.load("enemy_body.png")
        self.star = pygame.image.load("star.png")
        self.finish = pygame.image.load("finish.png")
        self.checkpointOff = pygame.image.load("checkpoint_off.png")
        self.checkpointOn = pygame.image.load("checkpoint_on.png")
        self.tick = pygame.transform.scale_by(pygame.image.load("tick.png"),(0.2))
        self.cloud = {"1":[pygame.image.load("cloud1.png"),
                          pygame.image.load("cloud2.png"),
                          pygame.image.load("cloud3.png")]}
        
        blank = pygame.image.load("enemy_body.png")
        pygame.draw.circle(blank,colour.white,(20,15),10)
        pygame.draw.circle(blank,colour.black,(20,16),7)
        pygame.draw.circle(blank,colour.white,(22,17),2)
        pygame.draw.circle(blank,colour.black,(20,18),1)
        self.enemyForEditor = blank

    def resize_cloud(self,scale):
        self.cloud[str(scale)] = []
        for item in self.cloud["1"]:
            self.cloud[str(scale)].append(pygame.transform.scale_by(item,scale))


class Cloud:
    def __init__(self,which,img):
        self.xpos = -img.get_width()
        self.ypos = random.randint(100,1000)
        self.yvar = 0
        self.which = which
        self.img = img
        self.speed = random.randint(1,5) / 10
        self.needsDel = False

    def tick(self):
        self.xpos += self.speed
        if self.xpos > SCRW:
            self.needsDel = True

        SCREEN.blit(self.img,(self.xpos,self.ypos-self.yvar))

    def get_player_ypos(self,ypos):
        self.yvar = ypos/5

class Soundboard:
    def __init__(self):
        self.jump = pygame.mixer.Sound("jump.wav")
        self.fall = pygame.mixer.Sound("fall.wav")

        self.music = [
            pygame.mixer.Sound("Track 1.wav")
            ]

        self.channels = [pygame.mixer.Channel(0)]
        self.enabled = True

    def start_fall(self):
        self.channels[0].play(self.fall)

    def end_fall(self):
        self.channels[0].stop()


class Level_slots:
    def __init__(self,num):
        self.num = num
        self.slots = []
        self.boxes = []
        self.page = 1

        self.pressed = False
        self.idx = 0

        self.nextBox = u.old_textbox(" > ",font50,(SCRW-50,SCRH-50))
        self.prevBox = u.old_textbox(" < ",font50,(50,SCRH-50))

        self.update()

    def update(self):
        for i in range(self.num):
            j = (i%15)
            x = ((j%5)*SCRW//5)+SCRW//10 
            y = ((j//5)*SCRH//4)+SCRH//8
            self.boxes.append(u.old_textbox(" "+str(i+1)+" ",font50,(x,y)))

    def tick(self):
        if self.num > 15 and ((math.ceil(self.num/15) != self.page)):
            self.nextBox.display()
        if self.num > 15 and ((math.ceil(self.num/15) != 1)):
            self.prevBox.display()

        if self.nextBox.isPressed():
            self.page += 1

        idxRange = [(self.page-1)*15,self.page*15]
        #print(idxRange)
        for i in range(idxRange[0],idxRange[1]):
            try:
                self.boxes[i].display()
            except IndexError:
                pass

    def check(self):
        for item in self.boxes:
            if item.isPressed():
                self.pressed = True
                self.idx = self.boxes.index(item) + 1


class Settings:
    def __init__(self):
        self.showFPS = False
        self.SCRWEX = 0
        self.SCRHEX = 0

class Stats:
    def __init__(self):
        self.stars = []
        self.enemiesKilled = 0
        self.playTime = 0
        self.deaths = 0

class Game:
    def __init__(self):
        self.gravity = 0.981
        self.scene = "menu"
        self.restart = False # if the player presses the restart key
        self.scale = 1

        self.player = None
        self.editor = Editor()
        self.img = Images()
        self.sound = Soundboard()
        self.settings = Settings()
        self.stats = Stats()

        self.UP = [pygame.K_UP,pygame.K_w,pygame.K_SPACE]
        self.LEFT = [pygame.K_a,pygame.K_LEFT]
        self.RIGHT = [pygame.K_d,pygame.K_RIGHT]
        self.DOWN = [pygame.K_s,pygame.K_DOWN]
        self.RESTART = [pygame.K_r]

        self.enableMovement = True

        self.lastCloud = 0
        self.cloudInterval = 5000
        self.clouds = []

        self.data = {} # the whole json file
        self.levelIDX = 1

        self.platformCol = []
        self.bgCol = []

        self.platforms = [] # list of item rects in current level
        self.spikes = []
        self.spikeDir = []
        self.fanBases = []
        self.fanColumns = []
        self.mobs = []
        self.entities = []

        self.animations = []
        self.spawnPoint = []

        self.load()
        self.update_level()

        with open("stats.json","r") as file:
            info = json.load(file)
            self.stats.stars = info["stars"]
            self.stats.enemiesKilled = info["enemiesKilled"]#
            self.stats.playTime = info["playTime"]
            self.stats.deaths = info["deaths"]

        self.fix_stats_stars()

    def orient_spikes(self):
        self.spikeDir = []
        for spike in self.spikes:
            bottom = False
            right = False
            top = False
            left = False
            direction = 0
            points = [pygame.Rect(spike[0], spike[1], 10, 10),
                    pygame.Rect(spike[0] + 50, spike[1] - 50, 10, 10),
                    pygame.Rect(spike[0], spike[1] - 100, 10, 10),
                    pygame.Rect(spike[0] - 50, spike[1] - 50, 10, 10)]
            for plat in self.platforms:
                #for point in points:
                #    sendToCam(list(point), name="hitbox", col=colour.green)

                if pygame.Rect.colliderect(toRect(points[0]),toRect(plat)):
                    bottom = True
                if pygame.Rect.colliderect(toRect(points[1]),toRect(plat)):
                    right = True
                if pygame.Rect.colliderect(toRect(points[2]),toRect(plat)):
                    top = True
                if pygame.Rect.colliderect(toRect(points[3]),toRect(plat)):
                    left = True

            if left:
                direction = 3
            if top:
                direction = 2
            if right:
                direction = 1
            if bottom:
                direction = 0

            self.spikeDir.append(direction)


    def fix_stats_stars(self):
        for i in range(len(self.data)):
            if str(i+1) not in self.stats.stars:
                self.stats.stars[str(i+1)] = []

    def generate_cloud(self):
        if now() - self.lastCloud > self.cloudInterval:
            self.lastCloud = now()
            typ = random.randint(0,2)
            self.clouds.append(Cloud(typ,self.img.cloud[str(self.scale)][typ]))

        toDel = []

        for item in self.clouds:
            item.tick()
            item.get_player_ypos(self.player.ypos)
            if item.needsDel:
                toDel.append(item)

        for item in toDel:
            self.clouds.remove(item)

    def init_clouds(self):
        for i in range(10):
            typ = random.randint(0, 2)
            self.clouds.append(Cloud(typ, self.img.cloud[str(self.scale)][typ]))
            self.clouds[i-1].xpos = random.randint(0,SCRW)
            self.clouds[i-1].ypos = random.randint(0, SCRH)


    def trigger_death(self,die=True):
        if die:
            if not self.player.isDead:
                self.player.isDead = True
                self.animations.append(Death_Particle(self.player.xpos,self.player.ypos+14,self.player.colour))
                self.enableMovement = False
                self.stats.deaths += 1

        self.player.xvel = 0
        self.player.yvel = 0
                
        if not self.contains_animation("death"):
            self.player.xpos,self.player.ypos = self.spawnPoint[0],self.spawnPoint[1]
            self.update_level(next=False) # lazy, only need to change entity positions
            self.player.isDead = False
            self.player.atFinish = False
            self.enableMovement = True
            self.restart = False

    def contains_animation(self,name):
        found = False
        for item in self.animations:
            if item.name == name:
                found = True
                break
        return found        

    def load(self):
        with open("levels.json","r") as file:
            self.data = json.load(file)

    def save(self):
        with open("levels.json","w") as file:
            file.write(json.dumps(self.data))

    def tick_enemies(self):
        for mob in self.entities:
            mob.tick()
            mob.update_hitboxes()
            mob.draw()
            mob.update_target((self.player.xpos,self.player.ypos))
            mob.pathfind()
            
    def tick_player(self):
##        self.player.wallData = self.player.check()
        self.player.lastIsDead = self.player.isDead
        self.player.lastYvel = self.player.yvel
        
        if not self.player.wallData[0]:
            if abs(self.player.yvel) > self.player.maxYvel:
                self.player.yvel = self.player.maxYvel
                
            self.player.yvel += self.player.gravity
        else:
            self.player.yvel = 0
            
        if self.player.move[2]: # move faster
                    self.player.xvel += self.player.xInc   
        if self.player.move[1]:
                    self.player.xvel -= self.player.xInc
        if abs(self.player.xvel)>self.player.maxXvel:
            if self.player.xvel > 0:
                self.player.xvel = self.player.maxXvel
            elif self.player.xvel < 0:
                self.player.xvel = -self.player.maxXvel

            
        if (not self.player.move[1]) and (not self.player.move[2]): # if not pressing l or r
            self.player.xvel = self.player.xvel * 0.8
            if abs(self.player.xvel) < 0.1: self.player.xvel = 0

        if self.player.xvel > 0 and self.player.wallData[2]: # check for walls l and r
            self.player.xvel = 0
        if self.player.xvel < 0 and self.player.wallData[1]:
            self.player.xvel = 0

        if self.player.move[0]: # wall jump 
            if self.player.wallData[0]:
                self.player.yvel = -20
                if self.sound.enabled: self.sound.jump.play()
            if self.player.wallData[1]:
                self.player.yvel = -20
                self.player.xvel = 10
                if self.sound.enabled: self.sound.jump.play()
            if self.player.wallData[2]:
                self.player.yvel = -20
                self.player.xvel = -10
                if self.sound.enabled: self.sound.jump.play()
            if self.player.wallData[2] and self.player.wallData[1]:
                self.player.xvel = 0

        self.player.xpos += self.player.xvel
        self.player.ypos += self.player.yvel


        #self.player.wallData = [False,False,False]

##        self.player.rect = pygame.Rect(self.player.xpos-25,self.player.ypos-25,50,50)

        if now() - self.player.lastBlink > self.player.blinkWait:
            self.player.lastBlink = now()
            if self.player.isBlinking:
                self.player.isBlinking = False
                self.player.blinkWait = random.randint(3,6) * 1000
            else:
                self.player.isBlinking = True
                self.player.blinkWait = 100

    def tick(self):
        if self.restart:
            self.trigger_death()
            
##        playerBox = get_actual_pos([self.player.xpos,self.player.ypos,50,50])
##        playerRect = pygame.Rect(self.player.xpos-25,self.player.ypos-25,50,50)
        self.player.wallData = [False,False,False,False,False]
        for mob in self.entities:
            mob.wallData = [False,False,False,False,False]

        for item in self.platforms:
            compItem = toRect(get_actual_pos(item))
            if pygame.Rect.colliderect(self.player.hitbox.actBottom,compItem):
                self.player.wallData[0] = True
            if pygame.Rect.colliderect(self.player.hitbox.actLeft,compItem):
                self.player.wallData[1] = True
            if pygame.Rect.colliderect(self.player.hitbox.actRight,compItem):
                self.player.wallData[2] = True
            if pygame.Rect.colliderect(self.player.hitbox.actTop,compItem):
                self.player.wallData[3] = True
            if pygame.Rect.colliderect(self.player.hitbox.actWhole,compItem):
                self.player.wallData[4] = True

            for mob in self.entities:
                if pygame.Rect.colliderect(mob.hitbox.actBottom,compItem):
                    mob.wallData[0] = True
                if pygame.Rect.colliderect(mob.hitbox.actLeft,compItem):
                    mob.wallData[1] = True
                if pygame.Rect.colliderect(mob.hitbox.actRight,compItem):
                    mob.wallData[2] = True
                if pygame.Rect.colliderect(mob.hitbox.actTop,compItem):
                    mob.wallData[3] = True
                if pygame.Rect.colliderect(mob.hitbox.actWhole,compItem):
                    mob.wallData[4] = True
                
        
        for item in self.spikes:
            orn = self.spikeDir[self.spikes.index(item)]
            spike = toRect(get_actual_pos(spike_convert(item,orn)))
            if pygame.Rect.colliderect(self.player.hitbox.actWhole,spike):
                self.trigger_death()
                break
            for mob in self.entities:
                if pygame.Rect.colliderect(mob.hitbox.actWhole,spike):
                    self.entities.remove(mob)
                    self.stats.enemiesKilled += 1
                    self.animations.append(Impact_Particle(mob.xpos,mob.ypos+14,colour.red))

        for item in self.checkpoints:
            if pygame.Rect.colliderect(self.player.hitbox.actWhole,get_actual_pos((item[0],item[1],50,50))):
                self.spawnPoint = item
##                print(self.spawnPoint)
                break

        for item in self.stars:
            if pygame.Rect.colliderect(self.player.hitbox.actWhole,get_actual_pos((item[0],item[1],50,50))):
                if item not in self.stats.stars[str(self.levelIDX)]:
                    self.stats.stars[str(self.levelIDX)].append(item)
                    self.animations.append(Star_Particle(item[0],item[1],colour.yellow))

        for which in [self.fanBases,self.fanColumns]:
            for item in which:
                newItem = [item[0],item[1],50,50]
                if pygame.Rect.colliderect(self.player.hitbox.actWhole,toRect(get_actual_pos(newItem))):
                    if self.player.yvel > -10:
                        self.player.yvel -= 0.5 + self.player.gravity
##                    self.player.ypos -= 10
                    break

        end = self.data[str(self.levelIDX)]["end"]
        if pygame.Rect.colliderect(self.player.hitbox.actWhole,
                    toRect(get_actual_pos([end[0],end[1],50,50]))):
            self.player.atFinish = True

        for mob in self.entities:
            if pygame.Rect.colliderect(mob.hitbox.actWhole,self.player.hitbox.actWhole):
                self.trigger_death()

    def draw_animations(self):
        toDel = []
        for item in self.animations:
            if item.finished:
                toDel.append(item)

        for item in toDel:
            self.animations.remove(item)

        for item in self.animations:
            item.tick()
            item.draw()
            

    def correct_player(self):     
        if self.player.wallData[4] and self.player.yvel == 0:
            if self.player.wallData[3]:
                self.player.ypos -= 85
            self.player.ypos = ((self.player.ypos//50)*50)+31
            if self.player.lastYvel != 0:
                self.animations.append(Impact_Particle(self.player.xpos,self.player.ypos+14,colour.darkgrey))

        for enemy in self.entities:
            if enemy.wallData[0] and enemy.yvel == 0:
                enemy.ypos = ((enemy.ypos//50)*50)+21
                if enemy.lastYvel != 0:
                    self.animations.append(Impact_Particle(enemy.xpos,enemy.ypos+14,colour.darkgrey))
                    #print(f"last:{enemy.lastYvel} now {enemy.yvel}")
            
        if self.player.wallData[3]: # top
            self.player.yvel = 0
            self.player.ypos += 25            

    def update_level(self,next=False):
        if next:
            self.levelIDX += 1

        self.platforms = []    
        self.spikes = []
        self.fanBases = []
        self.fanColumns = []
        self.stars = []
        self.mobs = []
        self.entities = []
        self.checkpoints = []

        self.animations = []
        self.spawnPoint = []

        try:
            if "start" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["start"] = [0,0]
            if "end" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["end"] = [300,0]
            if "platforms" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["platforms"] = [[-100,50,500,50]]
            if "spikes" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["spikes"] = []
            if "fan bases" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["fan bases"] = []
            if "fan columns" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["fan columns"] = []
            if "stars" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["stars"] = []
            if "mobs" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["mobs"] = []
            if "checkpoints" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["checkpoints"] = []
            
        except KeyError:
            self.data[str(self.levelIDX)] = {
                "start":[0,0],
                "end":[300,0],
                "platforms":[[-100,50,500,50]],
                "spikes":[],
                "fan bases":[],
                "fan columns":[],
                "stars":[],
                "mobs":[],
                "checkpoints":[]}

        try:
            self.platformCol = self.data[str(self.levelIDX)]["platform colour"]
        except KeyError:
            self.platformCol = colour.darkgrey
        try:
            self.bgCol = self.data[str(self.levelIDX)]["background colour"]
        except KeyError:
            self.bgCol = [200,200,250]
        
        self.spawnPoint = self.data[str(self.levelIDX)]["start"]
        for item in self.data[str(self.levelIDX)]["platforms"]:
            self.platforms.append(item)
        for item in self.data[str(self.levelIDX)]["spikes"]:
            self.spikes.append([item[0],item[1]])
        for item in self.data[str(self.levelIDX)]["fan bases"]:
            self.fanBases.append([item[0],item[1]])
        for item in self.data[str(self.levelIDX)]["fan columns"]:
            self.fanColumns.append([item[0],item[1]])
        for item in self.data[str(self.levelIDX)]["stars"]:
            self.stars.append([item[0],item[1]])
        for item in self.data[str(self.levelIDX)]["mobs"]:
            self.mobs.append([item[0],item[1]])
            self.entities.append(Enemy(item[0],item[1],img=self.img.enemyBody,maxXvel=random.randint(4,6)))
        for item in self.data[str(self.levelIDX)]["checkpoints"]:
            self.checkpoints.append([item[0],item[1]])

        self.orient_spikes()

    def draw_bg(self):
        for item in self.data[str(self.levelIDX)]["platforms"]:
            sendToCam(item,col=self.platformCol)
        for i in range(len(self.data[str(self.levelIDX)]["spikes"])):
            #print(f"len of spikes {len(self.data[str(self.levelIDX)]["spikes"])}\nlen of spikeDir {len(self.spikeDir)}")
            sendSpikeToCam(self.data[str(self.levelIDX)]["spikes"][i-1],orn=self.spikeDir[i-1])
        #for item in self.spikes:
        #    orn = self.spikeDir[self.spikes.index(item)]
        #    sendToCam(spike_convert(item,orn),"hitbox")
        blitToCam(self.img.finish,self.data[str(self.levelIDX)]["end"]) # VERY INEFFICIENT FIX ME
        for item in self.data[str(self.levelIDX)]["fan bases"]:
            sendToCam(item,"fan base")
        for item in self.data[str(self.levelIDX)]["fan columns"]:
            sendToCam(item,"fan column")
        for item in self.data[str(self.levelIDX)]["stars"]:
            if self.scene == "editor":
                sendToCam(item,"star")
            if item not in self.stats.stars[str(self.levelIDX)]:
                sendToCam(item,"star")
        for item in self.data[str(self.levelIDX)]["checkpoints"]:
            if item == self.spawnPoint:
                blitToCam(self.img.checkpointOn,item)
            else:
                blitToCam(self.img.checkpointOff,item)
            
        if self.scene == "editor":
            for item in self.data[str(self.levelIDX)]["mobs"]:
                blitToCam(self.img.enemyForEditor,(item[0]+5,item[1]+5))
                

    def draw_grid(self):
        for i in range((SCRW//50)+2):
            x = (i*50) - (self.player.xpos%50) + (self.settings.SCRWEX//2)
            pygame.draw.line(SCREEN,(220,220,255),(x,0),(x,SCRH))
            
        for j in range((SCRH//50)+2):
            y = (j*50) - (self.player.ypos%50) + (self.settings.SCRHEX//2)
            pygame.draw.line(SCREEN,(220,220,255),(0,y),(SCRW,y))

    def draw_menu(self):
        pygame.draw.rect(SCREEN,colour.lightgrey,(0,0,70,SCRH))
        pygame.draw.rect(SCREEN,colour.darkgrey,(0,0,70,SCRH),width=2)
        # frame
        for item in self.editor.itemRects:
            pygame.draw.rect(SCREEN,(180,180,180),item)
        
        pygame.draw.rect(SCREEN,colour.darkgrey,(10,30,50,10))
        # platform icon
        pygame.draw.polygon(SCREEN,colour.red,((30,110),(40,110),(35,80)))
        # spike icon
        SCREEN.blit(self.img.finish,(3,125))
        # finish
        SCREEN.blit(self.img.fanBase,(10,180))
        # fan base image
        SCREEN.blit(self.img.fanColumn,(10,245))
        # fan column
        SCREEN.blit(self.img.star,(10,305))
        # fan column
        SCREEN.blit(self.img.enemyForEditor,(15,370))
        # enemy
        SCREEN.blit(self.img.checkpointOn,(10,425))
        # checkpoint



    def check_selected(self):
        mouseRect = toRect(self.editor.mouseRect)
        for item in self.editor.itemRects:
            compRect = toRect(item)
            if pygame.Rect.colliderect(compRect,mouseRect): # if mouse is over an item box
                try:
                    self.editor.selected = self.editor.ref[self.editor.itemRects.index(item)]
                except IndexError:
                    self.editor.selected = "Huh, not added yet"
                # select that item
                break # cannot select two items at once

    def run_editor(self):
        self.editor.mouseRect[0],self.editor.mouseRect[1] = pygame.mouse.get_pos()
        pygame.draw.rect(SCREEN,colour.red,self.editor.mouseRect)

        mouseData = pygame.mouse.get_pressed()

        self.editor.clicks[1] = self.editor.clicks[0]
        self.editor.clicks[0] = mouseData[0]
        self.editor.clicksR[1] = self.editor.clicksR[0]
        self.editor.clicksR[0] = mouseData[2]

        newMouseRect = get_actual_pos(self.editor.mouseRect)
        
        if self.restart:
            self.trigger_death(die=False)

        for which in ["platform","spike","fan base","fan column","star","mob","checkpoint"]:
            for item in self.data[str(self.levelIDX)][which+"s"]:
                if pygame.Rect.colliderect(toRect(newMouseRect),toRect(item)):
                    sendToCam(item,col=colour.white,name="hitbox")

        if self.editor.selected == "platform":
            if self.editor.clicks == [True,False]:
                #add start coords
                realx,realy = pygame.mouse.get_pos()
                screenCoords = get_actual_pos((realx,realy,0,0))
                self.editor.pendingRect[0] = (screenCoords[0]//50)*50
                self.editor.pendingRect[1] = (screenCoords[1]//50)*50
            elif self.editor.clicks == [True,True]:
                #add finish coords
                realx,realy = pygame.mouse.get_pos()
                screenCoords = get_actual_pos((realx,realy,0,0))
                self.editor.pendingRect[2] = ((screenCoords[0]//50)*50)-self.editor.pendingRect[0]
                self.editor.pendingRect[3] = ((screenCoords[1]//50)*50)-self.editor.pendingRect[1]
                sendToCam(self.editor.pendingRect,col=colour.white)
            elif self.editor.clicks == [False,True]:
                #save the new platform
                if self.editor.pendingRect[2] > 0 and self.editor.pendingRect[3] > 0:
                    self.data[str(self.levelIDX)]["platforms"].append(self.editor.pendingRect)
                self.editor.pendingRect = [0,0,0,0]

            if pygame.mouse.get_pressed()[2]:
                # right click
                for item in self.data[str(self.levelIDX)]["platforms"]:
                    if pygame.Rect.colliderect(toRect(newMouseRect),toRect(item)):
                        try:
                            self.data[str(self.levelIDX)]["platforms"].remove(item)
                        except ValueError:
                            pass
        else:
            if self.editor.clicks == [True,False]: # LMB
                realx,realy = pygame.mouse.get_pos()
                screenCoords = get_actual_pos((realx,realy,0,0))
                truncPos = [(screenCoords[0]//50)*50, (screenCoords[1]//50)*50]                
            
                if self.editor.selected == "spike":
                    newSpike = [truncPos[0],truncPos[1]+50]
                    self.data[str(self.levelIDX)]["spikes"].append(newSpike)
                    self.orient_spikes()

                elif self.editor.selected == "end":
                    self.data[str(self.levelIDX)]["end"] = truncPos

                elif self.editor.selected == "fan base":
                    self.data[str(self.levelIDX)]["fan bases"].append(truncPos)

                elif self.editor.selected == "fan column":
                    self.data[str(self.levelIDX)]["fan columns"].append(truncPos)

                elif self.editor.selected == "star":
                    self.data[str(self.levelIDX)]["stars"].append(truncPos)

                elif self.editor.selected == "enemy":
                    self.data[str(self.levelIDX)]["mobs"].append(truncPos)

                elif self.editor.selected == "checkpoint":
                    self.data[str(self.levelIDX)]["checkpoints"].append(truncPos)

                self.update_level(next=False)
                
                
            if self.editor.clicksR == [True,False]: #RMB
                for item in self.spikes:
                    orn = self.spikeDir[self.spikes.index(item)]
                    if pygame.Rect.colliderect(toRect(newMouseRect),spike_convert(item,orn)):
                        self.data[str(self.levelIDX)]["spikes"].remove(item)
                        self.orient_spikes()
                        
                for item in self.fanBases:
                    if pygame.Rect.colliderect(toRect(newMouseRect),toRect([item[0],item[1],50,50])):
                        self.data[str(self.levelIDX)]["fan bases"].remove(item)
                        self.fanBases.remove(item)

                for item in self.fanColumns:
                    if pygame.Rect.colliderect(toRect(newMouseRect),toRect([item[0],item[1],50,50])):
                        self.data[str(self.levelIDX)]["fan columns"].remove(item)
                        self.fanColumns.remove(item)

                for item in self.stars:
                    if pygame.Rect.colliderect(toRect(newMouseRect),toRect([item[0],item[1],50,50])):
                        self.data[str(self.levelIDX)]["stars"].remove(item)
                        self.stars.remove(item)

                for item in self.mobs:
                    if pygame.Rect.colliderect(toRect(newMouseRect),toRect([item[0],item[1],50,50])):
                        self.data[str(self.levelIDX)]["mobs"].remove(item)
                        self.mobs.remove(item)

                for item in self.checkpoints:
                    if pygame.Rect.colliderect(toRect(newMouseRect),toRect([item[0],item[1],50,50])):
                        self.data[str(self.levelIDX)]["checkpoints"].remove(item)
                        self.checkpoints.remove(item)

                self.update_level(next=False)          

class Editor:
    '''a namespace to hold editor data'''
    def __init__(self):
        self.clicks = [False,False]
        self.clicksR = [False,False]
        self.pendingRect = [0,0,0,0]
        self.endRect = None
        self.mouseRect = [0,0,3,3]
        self.clicks = [False,False] # current and last state of LMB
        self.selected = "platform"

        self.itemRects = []
        self.ref = ["platform","spike","end","fan base","fan column","star","enemy","checkpoint"]

        for i in range(10):
            y = i*60
            self.itemRects.append((10,y+5,50,50))


class Mob_Hitbox():
    def __init__(self):
        self.whole = pygame.Rect([0,0,0,0])
        self.top = pygame.Rect([0,0,0,0])
        self.bottom = pygame.Rect([0,0,0,0])
        self.left = pygame.Rect([0,0,0,0])
        self.right = pygame.Rect([0,0,0,0])
        self.actWhole = pygame.Rect([0,0,0,0])
        self.actTop = pygame.Rect([0,0,0,0])
        self.actBottom = pygame.Rect([0,0,0,0])
        self.actLeft = pygame.Rect([0,0,0,0])
        self.actRight = pygame.Rect([0,0,0,0])
        

class Player:
    def __init__(self,gravity,maxYvel=50,maxXvel=10,img=None):
        self.xpos = 0
        self.ypos = 0
        self.xvel = 0
        self.yvel = 0
        self.lastYvel = 0
        self.maxYvel = maxYvel
        self.maxXvel = maxXvel
        self.img = img
        self.xInc = 1
        self.gravity = gravity
        self.isDead = False
        self.lastIsDead = False
        self.atFinish = False
        self.lastBlink = 0
        self.isBlinking = False
        self.blinkWait = random.randint(3,6) * 1000
        self.move = [False,False,False,False]
        self.wallData = [False,False,False,False,False]
        self.hitbox = Mob_Hitbox()
        if self.img == None:
            self.colour = (0,68,213)
        else:
            self.colour = self.img.get_at((20,20))
        #self.update_hitboxes()
##        self.rect = pygame.Rect(self.player.xpos-25,self.player.ypos-25,50,50)

    def draw(self):
##        self.colour = rgb.get()
##        rgb.tick()
        if self.img == None:
            pygame.draw.rect(SCREEN,self.colour,((SCRW//2)-20,(SCRH//2)-20,40,40))
        else:
            SCREEN.blit(self.img,((SCRW//2)-20,(SCRH//2)-20))
        # everything else in the draw function is not necessary
        if not self.isBlinking:
            pygame.draw.circle(SCREEN,colour.white,(SCRW//2,(SCRH//2)-5),10)

            if not (self.move[1] or self.move[2]):        
                pygame.draw.circle(SCREEN,colour.black,(SCRW//2,(SCRH//2)-4),7)
                pygame.draw.circle(SCREEN,colour.white,((SCRW//2)+2,(SCRH//2)-3),2)
                pygame.draw.circle(SCREEN,colour.white,((SCRW//2),(SCRH//2)-2),1)

            else:
                if self.move[1]:
                    pygame.draw.circle(SCREEN,colour.black,((SCRW//2)-3,(SCRH//2)-4),7)
                    pygame.draw.circle(SCREEN,colour.white,((SCRW//2)-1,(SCRH//2)-3),2)
                    pygame.draw.circle(SCREEN,colour.white,((SCRW//2)-3,(SCRH//2)-2),1)
                elif self.move[2]:
                    pygame.draw.circle(SCREEN,colour.black,((SCRW//2)+3,(SCRH//2)-4),7)
                    pygame.draw.circle(SCREEN,colour.white,((SCRW//2)+5,(SCRH//2)-3),2)
                    pygame.draw.circle(SCREEN,colour.white,((SCRW//2)+3,(SCRH//2)-2),1)

    def update_hitboxes(self):
        self.hitbox.whole = toRect([self.xpos-20,self.ypos-19,40,40])
        self.hitbox.top = toRect([self.xpos-10,self.ypos-19,20,5])
##        self.hitbox.bottom = toRect([self.xpos-12,self.ypos+15,24,15])
        self.hitbox.bottom = toRect([self.xpos-10,self.ypos+5,20,15])
        self.hitbox.left = toRect([self.xpos-20,self.ypos-20,5,30])
        self.hitbox.right = toRect([self.xpos+15,self.ypos-20,5,30])
        
        self.hitbox.actWhole = toRect(get_actual_pos([self.xpos-20,self.ypos-19,40,40]))
        self.hitbox.actTop = toRect(get_actual_pos([self.xpos-10,self.ypos-19,20,5]))
##        self.hitbox.actBottom = toRect(get_actual_pos([self.xpos-12,self.ypos+15,24,15]))
        self.hitbox.actBottom = toRect(get_actual_pos([self.xpos-10,self.ypos+5,20,15]))
        self.hitbox.actLeft = toRect(get_actual_pos([self.xpos-20,self.ypos-20,5,30]))
        self.hitbox.actRight = toRect(get_actual_pos([self.xpos+15,self.ypos-20,5,30]))


    def check(self):
        # unused
        bottom = False
        left = False
        right = False
        
        if SCREEN.get_at((SCRW//2,(SCRH//2)+21)) == colour.darkgrey:
            bottom = True
            
        if SCREEN.get_at(((SCRW//2)-21,(SCRH//2))) == colour.darkgrey:
            left = True
            
        if SCREEN.get_at(((SCRW//2)+21,(SCRH//2))) == colour.darkgrey:
            right = True

        for pos in [((SCRW//2)-20,(SCRH//2)+21),((SCRW//2),(SCRH//2)+21),((SCRW//2)+20,(SCRH//2)+21)]:
            if (SCREEN.get_at(pos) == colour.green):
                self.atFinish = True

        return [bottom,left,right]

    def free_cam(self):
        if self.move[0] and abs(self.yvel) < 20:
            self.yvel -= self.xInc
        elif self.move[3] and abs(self.yvel) < 20:
            self.yvel += self.xInc
        else:
            self.yvel = self.yvel * 0.8

        if self.move[1] and abs(self.xvel) < 20:
            self.xvel -= self.xInc
        elif self.move[2]  and abs(self.xvel) < 20:
            self.xvel += self.xInc
        else:
            self.xvel = self.xvel * 0.8

        self.xpos += self.xvel
        self.ypos += self.yvel


class Enemy:
    def __init__(self,xpos,ypos,maxXvel=5,maxYvel=50,gravity=0.981,img=None):
        self.xpos = xpos
        self.ypos = ypos
        self.xvel = 0
        self.yvel = 0
        self.lastYvel = 0
        self.xInc = 1
        self.maxXvel = maxXvel
        self.maxYvel = maxYvel
        self.gravity = gravity
        self.target = []
        self.maxTargetDist = 500
        self.img = img
        self.needsDel = False
        self.wallData = [False,False,False,False,False]
        self.hitbox = Mob_Hitbox()

    def pathfind(self):
        if self.get_dist(self.target) < self.maxTargetDist:
            if self.target[0] > self.xpos:
                self.xvel += self.xInc
                #print(">")
            elif self.target[0] < self.xpos:
                self.xvel -= self.xInc
                #print("<")
        else:
            self.xvel = self.xvel * 0.8

    def draw(self):
        blitToCam(self.img,(self.xpos-20,self.ypos-10))
        pygame.draw.circle(SCREEN,colour.white,((SCRW//2)-player.xpos+self.xpos,(SCRH//2)+5-player.ypos+self.ypos),10)
        if self.xvel == 0:        
                pygame.draw.circle(SCREEN,colour.black,(SCRW//2-player.xpos+self.xpos,(SCRH//2)+5-player.ypos+self.ypos),7)
                pygame.draw.circle(SCREEN,colour.white,((SCRW//2)+2-player.xpos+self.xpos,(SCRH//2)+6-player.ypos+self.ypos),2)
                pygame.draw.circle(SCREEN,colour.white,((SCRW//2)-player.xpos+self.xpos,(SCRH//2)+7-player.ypos+self.ypos),1)

        else:
            if self.xvel < 0:
                pygame.draw.circle(SCREEN,colour.black,((SCRW//2)-3-player.xpos+self.xpos,(SCRH//2)+5-player.ypos+self.ypos),7)
                pygame.draw.circle(SCREEN,colour.white,((SCRW//2)-1-player.xpos+self.xpos,(SCRH//2)+6-player.ypos+self.ypos),2)
                pygame.draw.circle(SCREEN,colour.white,((SCRW//2)-3-player.xpos+self.xpos,(SCRH//2)+7-player.ypos+self.ypos),1)
            elif self.xvel > 0:
                pygame.draw.circle(SCREEN,colour.black,((SCRW//2)+3-player.xpos+self.xpos,(SCRH//2)+5-player.ypos+self.ypos),7)
                pygame.draw.circle(SCREEN,colour.white,((SCRW//2)+5-player.xpos+self.xpos,(SCRH//2)+6-player.ypos+self.ypos),2)
                pygame.draw.circle(SCREEN,colour.white,((SCRW//2)+3-player.xpos+self.xpos,(SCRH//2)+7-player.ypos+self.ypos),1)

    def update_hitboxes(self):
        self.hitbox.whole = toRect([self.xpos-20,self.ypos-19,40,40])
        self.hitbox.top = toRect([self.xpos-10,self.ypos-19,20,5])
        self.hitbox.bottom = toRect([self.xpos-12,self.ypos+15,24,15])
        self.hitbox.left = toRect([self.xpos-20,self.ypos-20,5,39])
        self.hitbox.right = toRect([self.xpos+15,self.ypos-20,5,39])
        
        self.hitbox.actWhole = toRect(get_actual_pos([self.xpos-20,self.ypos-19,40,40]))
        self.hitbox.actTop = toRect(get_actual_pos([self.xpos-10,self.ypos-19,20,5]))
        self.hitbox.actBottom = toRect(get_actual_pos([self.xpos-12,self.ypos+15,24,15]))
        self.hitbox.actLeft = toRect(get_actual_pos([self.xpos-20,self.ypos-20,5,39]))
        self.hitbox.actRight = toRect(get_actual_pos([self.xpos+15,self.ypos-20,5,39]))

    def tick(self):
        self.lastYvel = self.yvel
        if not self.wallData[0]:
            self.yvel += self.gravity
        else:
            self.yvel = 0

        if self.xvel > self.maxXvel:
            self.xvel = self.maxXvel
        elif self.xvel < -self.maxXvel:
            self.xvel = -self.maxXvel

        if self.wallData[1] and self.xvel < 0:
            self.xvel = 0
        elif self.wallData[2] and self.xvel > 0:
            self.xvel = 0

        self.xpos += self.xvel
        self.ypos += self.yvel
        

    def update_target(self,pos):
        self.target = list(pos)

    def get_dist(self,pos):
        return math.sqrt((pos[0]-self.xpos)**2+(pos[1]-self.ypos)**2)

    def get_angle(self,pos):
        dx = pos[0] - self.xpos
        dy = pos[1] - self.ypos
        return math.atan2(dy,dx)


class Animation:
    def __init__(self,xpos,ypos):
        self.frame = 0
        self.interval = 100
        self.xpos = xpos
        self.ypos = ypos
        self.finished = False
        self.lastChange = pygame.time.get_ticks()

    def tick(self):
        if now() - self.lastChange > self.interval:
            self.frame += 1
            self.lastChange = now()
            

class Impact_Particle(Animation):
    def __init__(self,xpos,ypos,col):
        super().__init__(xpos,ypos)
        self.interval = 50
        self.col = col
        self.name = "impact"
        self.size = 15

    def draw(self):
        rects = []
        if self.frame == 0:
            rects = [[self.xpos,self.ypos,self.size,self.size]]
        elif self.frame == 1:
            rects = [[self.xpos+5,self.ypos-5,self.size,self.size],
                     [self.xpos-6,self.ypos-3,self.size,self.size],
                     [self.xpos+1,self.ypos,self.size,self.size]]
        elif self.frame == 2:
            rects = [[self.xpos+10,self.ypos-7,self.size,self.size],
                     [self.xpos-12,self.ypos-6,self.size,self.size],
                     [self.xpos+2,self.ypos-10,self.size,self.size]]
        elif self.frame == 3:
            rects = [[self.xpos+15,self.ypos-5,self.size,self.size],
                     [self.xpos-18,self.ypos-3,self.size,self.size],
                     [self.xpos+3,self.ypos-4,self.size,self.size]]
        elif self.frame == 4:
            rects = [[self.xpos+18,self.ypos-1,self.size,self.size],
                     [self.xpos-22,self.ypos-1,self.size,self.size],
                     [self.xpos+3,self.ypos-1,self.size,self.size]]
        elif self.frame >= 5:
            rects = [[self.xpos+18,self.ypos-1,self.size,self.size],
                     [self.xpos-22,self.ypos-1,self.size,self.size],
                     [self.xpos+3,self.ypos-1,self.size,self.size]]
            self.finished = True

        for item in rects:
            pygame.draw.rect(SCREEN,self.col,get_screen_pos(item))

class Death_Particle(Animation):
    def __init__(self,xpos,ypos,col):
        super().__init__(xpos,ypos)
        self.interval = 50
        self.col = col
        self.name = "death"
        self.size = 20

    def draw(self):
        rects = []
        if self.frame == 0:
            rects = [[self.xpos-self.size,self.ypos-self.size,self.size*2,self.size*2]]
        elif self.frame == 1:
            rects = [[self.xpos-self.size-10,self.ypos-self.size-20,self.size,self.size],
                    [self.xpos-self.size+8,self.ypos-self.size-24,self.size,self.size],
                    [self.xpos-self.size+2,self.ypos-self.size-2,self.size,self.size]]
        elif self.frame == 2:
            rects = [[self.xpos-self.size-18,self.ypos-self.size-31,self.size,self.size],
                    [self.xpos-self.size+15,self.ypos-self.size-35,self.size,self.size],
                    [self.xpos-self.size+3,self.ypos-self.size-1,self.size,self.size],
                    [self.xpos-self.size,self.ypos-self.size-20,self.size,self.size]]
        elif self.frame == 3:
            rects = [[self.xpos-self.size-24,self.ypos-self.size-24,self.size,self.size],
                    [self.xpos-self.size+20,self.ypos-self.size-28,self.size,self.size],
                    [self.xpos-self.size+3,self.ypos-self.size-1,self.size,self.size],
                    [self.xpos-self.size,self.ypos-self.size-50,self.size,self.size]]
        elif self.frame == 4:
            rects = [[self.xpos-self.size-30,self.ypos-self.size-10,self.size,self.size],
                    [self.xpos-self.size+25,self.ypos-self.size-8,self.size,self.size],
                    [self.xpos-self.size+3,self.ypos-self.size,self.size,self.size],
                    [self.xpos-self.size+1,self.ypos-self.size-30,self.size,self.size]]
        elif self.frame == 5:
            rects = [[self.xpos-self.size-35,self.ypos-self.size-5,self.size,self.size],
                    [self.xpos-self.size+28,self.ypos-self.size-1,self.size,self.size],
                    [self.xpos-self.size+3,self.ypos-self.size-1,self.size,self.size],
                    [self.xpos-self.size+1,self.ypos-self.size-5,self.size,self.size]]
        elif self.frame >= 6:
            rects = [[self.xpos-self.size-40,self.ypos-self.size-1,self.size,self.size],
                    [self.xpos-self.size+31,self.ypos-self.size-1,self.size,self.size],
                    [self.xpos-self.size+3,self.ypos-self.size-1,self.size,self.size],         
                    [self.xpos-self.size+1,self.ypos-self.size-1,self.size,self.size]]
        if self.frame >= 15:
            self.finished = True

        for item in rects:
            pygame.draw.rect(SCREEN,self.col,get_screen_pos(item))


class Star_Particle(Animation):
    def __init__(self,xpos,ypos,col):
        super().__init__(xpos,ypos)
        self.interval = 50
        self.col = col
        self.name = "star"
        self.size = 20
        
    def draw(self):
        if self.frame >= 6:
            self.finished = True

        for i in range(10):
            pygame.draw.rect(SCREEN,self.col,get_screen_pos(
                    [self.xpos+self.size+random.randint(-20,20),
                     self.ypos+self.size+random.randint(-20,20),
                     random.randint(3,5),random.randint(3,5)]))
        
##################################################


titleBox = u.old_textbox("PLATFORM ENGINE",fontTitle,(SCRW//2,150),backgroundCol=None,tags=["menu"])
startBox = u.old_textbox("PLAY",font28,(SCRW//2,400),tags=["menu"])
menuBox = u.old_textbox("MENU",font18,(SCRW-35,20),tags=["ingame","editor","levels","settings"])
editorBox = u.old_textbox("EDITOR",font18,(SCRW//2,500),tags=["menu"])
levelsBox = u.old_textbox("LEVELS",font18,(SCRW//2,300),tags=["menu"])
selectedBox = u.old_textbox("",font18,(SCRW//2,60),tags=["editor"])
coordBox = u.old_textbox("",font18,(SCRW//3,20),tags=["editor"])
levelIDXBox = u.old_textbox("",font18,(SCRW//2,20),tags=["ingame","editor"])
settingsBox = u.old_textbox("SETTINGS",font18,(SCRW//1.3,500),tags=["menu"])
showFPSBox = u.old_textbox("Show FPS",font18,(SCRW//2,150),tags=["settings"])
FPSBox = u.old_textbox("FPS: -",font18,(SCRW-50,SCRH-50),tags=["ingame","editor","settings"])
statsTitleBox = u.old_textbox("Statistics",font28,(SCRW//2,300),tags=["settings"])
collectedStarsBox = u.old_textbox("Stars collectd: -",font18,(SCRW//2,400),tags=["settings"])
enemiesDefeatedBox = u.old_textbox("Enemies defeated: -",font18,(SCRW//2,450),tags=["settings"])
deathCountBox = u.old_textbox("Number of deaths: -",font18,(SCRW//2,500),tags=["settings"])
uptimeBox = u.old_textbox("Time Played: -",font18,(SCRW//2,550),tags=["settings"])
resetStatsBox = u.old_textbox("RESET STATISTICS",font18,(SCRW//5,550),tags=["settings"],backgroundCol=colour.red,textCol=colour.black)

boxes = [titleBox,startBox,menuBox,editorBox,selectedBox,coordBox,levelIDXBox,levelsBox,settingsBox,
         showFPSBox,statsTitleBox,collectedStarsBox,enemiesDefeatedBox,deathCountBox,uptimeBox,
         resetStatsBox]
# hard coded textboxes

##################################################

def sendSpikeToCam(item,orn=0,col=colour.red):
    #print(f"orn {orn} for {item}")
    item = spike_convert(item)
    x = item[0] + (SCRW // 2) - player.xpos
    y = item[1] + (SCRH // 2) - player.ypos

    if orn == 0: # attached to floor
        for i in range(5):
            pygame.draw.polygon(SCREEN, col, (
                (x + (10 * i) - 5, y + 30),
                (x + (10 * i), y - 5),
                (x + (10 * i) + 5, y + 30)))
    elif orn == 1: # attached to right
        for i in range(5):
            pygame.draw.polygon(SCREEN, col, (
                (x + 45, y + (10 * i) - 20),
                (x + 10, y + (10 * i) - 15),
                (x + 45, y + (10 * i) - 10)))

    elif orn == 2: # attached to ceiling
        for i in range(5):
            pygame.draw.polygon(SCREEN, col, (
                (x + (10 * i) - 5, y - 20),
                (x + (10 * i), y + 15),
                (x + (10 * i) + 5, y - 20)))

    elif orn == 3:  #attached to left
        for i in range(5):
            pygame.draw.polygon(SCREEN, col, (
                (x - 5, y + (10 * i) - 20),
                (x + 30, y + (10 * i) - 15),
                (x - 5, y + (10 * i) - 10)))

    return None

def sendToCam(item,name=None,col=None):
    if name == "fan base":
        SCREEN.blit(img.fanBase,(item[0]-player.xpos+(SCRW//2),item[1]-player.ypos+(SCRH//2)))
        return None

    elif name == "fan column":
        SCREEN.blit(img.fanColumn,(item[0]-player.xpos+(SCRW//2),item[1]-player.ypos+(SCRH//2)))
        return None

    elif name == "star":
        SCREEN.blit(img.star,(item[0]-player.xpos+(SCRW//2),item[1]-player.ypos+(SCRH//2)))
        return None

    elif isinstance(item,list):
        newRect = [item[0]-player.xpos+(SCRW//2),
                   item[1]-player.ypos+(SCRH//2),
                   item[2],item[3]]
##        if newRect[0] + item[2] < 0 or newRect[0] > SCRW:
##            pass #off the screen
##        if newRect[1] + item[3] < 0 or newRect[3] > SCRW:
##            pass #off the screen
        
        if name != "hitbox":
            if col == None: col = colour.darkgrey
            pygame.draw.rect(SCREEN,col,newRect)
        else:
            if col == None: col = colour.white
           # print(f"success for {newRect}")
            pygame.draw.rect(SCREEN,col,newRect,width=2)

def blitToCam(item,pos):
    SCREEN.blit(item,((SCRW//2)-player.xpos+pos[0],(SCRH//2)-player.ypos+pos[1]))
                                   

def get_screen_pos(thing):
    '''Actual position -> Screen position'''
    return [thing[0]-player.xpos+(SCRW//2),thing[1]-player.ypos+(SCRH//2),thing[2],thing[3]]

def get_actual_pos(thing):
    '''Screen position -> Actual position'''
    return [thing[0]+player.xpos-(SCRW//2),thing[1]+player.ypos-(SCRH//2),thing[2],thing[3]]


def toRect(alist=[0,0,0,0]):
    if len(alist) == 4:
        rect = pygame.Rect(alist[0],alist[1],alist[2],alist[3])
    else:
        try:
            rect = pygame.Rect(alist[0],alist[1],0,0)
        except:
            rect = pygame.Rect(0,0,0,0)
    return  rect

def repos_boxes():
    titleBox.pos = (SCRW//2,200)
    startBox.pos = (SCRW//2,400)
    menuBox.pos = (SCRW-35,20)
    editorBox.pos = (SCRW//2,500)
    levelsBox.pos = (SCRW//2,300)
    selectedBox.pos = (SCRW//2,60)
    coordBox.pos = (SCRW//3,20)
    levelIDXBox.pos = (SCRW//2,20)
    settingsBox.pos = (SCRW//1.3,500)
    showFPSBox.pos = (SCRW//2,150)
    FPSBox.pos = (SCRW-50,SCRH-50)

def tick_boxes():
    for item in boxes:
        if game.scene in item.tags:
            item.isShowing = True
            item.display()
        else:
            item.isShowing = False

    if game.settings.showFPS:
        fps = str(clock.get_fps()).split(".")
        FPSBox.update_message(f"FPS:{fps[0]}.{fps[1][:3]}")
        FPSBox.isShowing = True
        FPSBox.display()
    else:
        FPSBox.isShowing = False

    if startBox.isPressed():
        game.scene = "ingame"
        game.init_clouds()
        game.orient_spikes()

    if menuBox.isPressed():
        if game.scene == "editor":
            game.save()
            game.update_level(next=False)
            
        game.scene = "menu"
        game.trigger_death(die=False)

    if editorBox.isPressed():
        game.scene = "editor"
        game.enableMovement = True
        game.orient_spikes()


    if levelsBox.isPressed():
        game.scene = "levels"

    if settingsBox.isPressed():
        game.scene = "settings"

    if showFPSBox.isPressed():
        game.settings.showFPS = not game.settings.showFPS

    if resetStatsBox.isPressed():
        game.stats.stars = {}
        game.stats.enemiesKilled = 0
        game.stats.deaths = 0
        game.stats.playTime = 0
        game.fix_stats_stars()
        

def spike_convert(item,orn=0):
    if orn == 0:
        return [item[0] + 5, item[1] - 30, 40, 30]
    elif orn == 1:
        return [item[0] + 20, item[1] - 45, 30, 40]
    elif orn == 2:
        return [item[0] + 5, item[1] - 50, 40, 30]
    elif orn == 3:
        return [item[0], item[1] - 45, 30, 40]
    else:
        raise SyntaxError("Cannot have a spike of that orientation")
    #return [item[0],item[1],40,30]


def go_quit():
    with open("stats.json","w") as file:
        info = {}
        info["stars"] = game.stats.stars
        info["enemiesKilled"] = game.stats.enemiesKilled
        info["playTime"] = game.stats.playTime + now()
        info["deaths"] = game.stats.deaths
        file.write(json.dumps(info))

    pygame.quit()
    sys.exit()

def now():
    return pygame.time.get_ticks()


def handle_events(move):
    global SCRW,SCRH
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            go_quit()

        if event.type == pygame.VIDEORESIZE:
            SCREEN = pygame.display.set_mode((event.w, event.h),pygame.RESIZABLE)
            SCRW,SCRH = pygame.display.get_window_size()
            game.settings.SCRWEX = SCRW%100
            game.settings.SCRHEX = SCRH%100
            repos_boxes()
            game.scale = min(SCRW/800,SCRH/600,)
            game.img.resize_cloud(game.scale)

            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                go_quit()
            elif event.key in game.RESTART:
                game.restart = True
                
            if move:
                if event.key in game.UP:
                    player.move[0] = True
                elif event.key in game.LEFT:
                    player.move[1] = True
                elif event.key in game.RIGHT:
                    player.move[2] = True
                elif event.key in game.DOWN:
                    player.move[3] = True
                
        elif event.type == pygame.KEYUP:
            if event.key in game.UP:
                player.move[0] = False
            elif event.key in game.LEFT:
                player.move[1] = False
            elif event.key in game.RIGHT:
                player.move[2] = False
            elif event.key in game.DOWN:
                player.move[3] = False

##################################################

img = Images()
player = Player(gravity=0.981,img=img.body)#,maxXvel = 1000, maxYvel = 1000) # hehe
game = Game()
game.player = player
levelSlots = Level_slots(len(game.data))

##testEnemy = Enemy(200,0,img=img.enemyBody)
##game.mobs.append(testEnemy)

##################################################


while True:
    tick_boxes()
    pygame.display.flip()
    SCREEN.fill((200,200,250))
    clock.tick(TICKRATE)

    handle_events(move=game.enableMovement)

    if game.scene == "ingame":
        SCREEN.fill(game.bgCol)
        game.generate_cloud()
        game.draw_bg()
        game.tick_enemies()
        game.tick()
        game.tick_player()
        game.correct_player()
        game.player.update_hitboxes()
        if game.enableMovement:
            game.player.draw()
        game.draw_animations()
        
        if game.player.ypos > 5000 or game.player.isDead:
            game.trigger_death()
        if game.player.atFinish:
            game.update_level(next=True)
            game.trigger_death(die=False)
        levelIDXBox.update_message("Level " + str(game.levelIDX))

            
#        sendToCam(list(game.player.hitbox.bottom),"hitbox",col=colour.white)
#        sendToCam(list(game.player.hitbox.left),"hitbox",col=colour.white)
#        sendToCam(list(game.player.hitbox.right),"hitbox",col=colour.white)
#        sendToCam(list(game.player.hitbox.top),"hitbox",col=colour.white)
#        sendToCam(list(game.player.hitbox.whole),"hitbox",col=colour.white)


    elif game.scene == "editor":
        SCREEN.fill(game.bgCol)
        game.generate_cloud()
        selectedBox.update_message(game.editor.selected.capitalize())
        levelIDXBox.update_message("Level " + str(game.levelIDX))
        mpos = game.editor.mouseRect
        mapped = get_actual_pos(mpos)
        acx,acy = ((mapped[0]//50)*50,(mapped[1]//50)*50)
        coordBox.update_message(( str(acx) + "," + str(acy) ))
        
        game.draw_grid()
        game.run_editor() # temp
        game.draw_bg()
        game.check_selected()
        #game.run_editor()
        game.player.free_cam()
        game.draw_menu()

    elif game.scene == "levels":
        levelSlots.tick()
        levelSlots.check()
        if levelSlots.pressed:
            game.levelIDX = levelSlots.idx
            levelSlots.pressed = False
            game.scene = "ingame"
            game.update_level(next=False)


    elif game.scene == "settings":
        #collectedStarsBox,enemiesDefeatedBox,deathCountBox,uptimeBox
        starCount = 0
        for key in game.stats.stars:
            starCount += len(game.stats.stars[key])

        ms = (game.stats.playTime + now())
        secs = (ms // 1000) % 60
        mins = (ms // (1000*60)) % 60
        hours = (ms // (1000*60*60)) % 60
        uptime = f"Time played: {hours}h {mins}m {secs}s"
            
        collectedStarsBox.update_message(f"Stars colelcted: {starCount}")
        enemiesDefeatedBox.update_message(f"Enemies defeated: {game.stats.enemiesKilled}")
        deathCountBox.update_message(f"Number of deaths: {game.stats.deaths}")
        uptimeBox.update_message(uptime)

        if game.settings.showFPS:
            SCREEN.blit(img.tick,((SCRW//2)+50,135))
