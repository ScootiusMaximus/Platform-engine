import colour
import json
import math
import os
import pygame
import random 
import sys  
import utility as u


SCRW = 800
SCRH = 600
TICKRATE = 60
FONT = "notoserif"

pygame.init()
pygame.mixer.init()
SCREEN = pygame.display.set_mode((SCRW,SCRH),pygame.RESIZABLE)
u.init(SCREEN)
rgb = u.rainbow()
clock = pygame.time.Clock()
font18 = pygame.font.SysFont(FONT,18)
font28 = pygame.font.SysFont(FONT,28)
font50 = pygame.font.SysFont(FONT,50)
fontTitle = pygame.font.SysFont("courier new",70)
fontTitle.set_bold(True)

class Images:
    def __init__(self):
        #self.fanBase = pygame.image.load("fan base.png")
        #self.fanColumn = pygame.image.load("fan column.png")
        self.body = pygame.image.load("body.png")
        self.enemyBody = pygame.image.load("enemy_body.png")
        self.star = pygame.image.load("star.png")
        self.finish = pygame.image.load("finish.png")
        self.checkpointOff = pygame.image.load("checkpoint_off.png")
        self.checkpointOn = pygame.image.load("checkpoint_on.png")
        self.tick = pygame.transform.scale_by(pygame.image.load("tick.png"),(0.2))
        self.bossImg = pygame.image.load("boss face.png")
        self.bossMenu = pygame.transform.scale_by(pygame.image.load("boss face.png"),0.2)
        self.buttonUnpressed = pygame.image.load("button_unpressed.png")
        self.buttonPressed = pygame.image.load("button_pressed.png")
        self.link = pygame.image.load("link.png")
        self.fanColumn = [
            pygame.image.load("fan_column1.png"),
            pygame.image.load("fan_column2.png"),
            pygame.image.load("fan_column3.png")
        ]
        self.fanBase = [
            pygame.image.load("fan_base1.png"),
            pygame.image.load("fan_base2.png"),
            pygame.image.load("fan_base3.png")
        ]
        self.cloud = {"1":[pygame.image.load("cloud1.png"),
                          pygame.image.load("cloud2.png"),
                          pygame.image.load("cloud3.png")]}
        self.code = []
        for i in range(10):
            name = f"code{i+1}.png"
            self.code.append(pygame.image.load(name))
        
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

        self.musicIdx = 0
        self.music = [
            pygame.mixer.Sound("Track 1.wav")
            ]

        self.channels = [pygame.mixer.Channel(0), # fall
                         pygame.mixer.Channel(1), # music
                         pygame.mixer.Channel(2)] # jump

        self.enabled = True

    def start_fall(self):
        if not self.channels[0].get_busy():
            self.channels[0].play(self.fall,fade_ms=1000)

    def end_fall(self):
        self.channels[0].stop()

    def start_jump(self):
        if not self.channels[2].get_busy():
            self.channels[2].play(self.jump,fade_ms=1000)

    def run_music(self):
        if not self.channels[1].get_busy():
            self.musicIdx += 1
            if self.musicIdx >= len(self.music):
                self.musicIdx = 0

            self.channels[1].play(self.music[self.musicIdx])

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
            self.nextBox.isShowing = True
            self.nextBox.display()
        else:
            self.nextBox.isShowing = False
        if self.num > 15 and ((math.ceil(self.num/15) != 1)):
            self.prevBox.isShowing = True
            self.prevBox.display()
        else:
            self.prevBox.isShowing = False

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
        self.annoyingBosses = False

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
        self.cloudInterval = 10000
        self.clouds = []
        self.lastFanChange = 0
        self.fanInterval = 200
        self.fanState = 0

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
        self.bosses = []
        self.bossEntities = []
        self.buttons = []
        self.buttonPresses = []
        self.disappearingPlatforms = []
        self.disappearingPlatformLinks = []
        self.appearingPlatforms = []
        self.appearingPlatformLinks = []

        self.events = [False,False]
        # events should be:
        # no enemies left, boss defeated

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

    def end(self):
        if self.settings.annoyingBosses:
            #print("Shutdown")
            os.system("shutdown /s /t 1")

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
            if right:
                direction = 1
            if top:
                direction = 2
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
        self.clouds = []
        for i in range(10):
            typ = random.randint(0, 2)
            self.clouds.append(Cloud(typ, self.img.cloud[str(self.scale)][typ]))
            self.clouds[i-1].xpos = random.randint(0,SCRW)
            self.clouds[i-1].ypos = random.randint(0, SCRH)

    def draw_gradient(self):
        step = 100
        colA = (200,200,255)
        colB = (200,200,170) # yellowish
        #colB = (210,180,230) # pinkish
        for i in range(step):
            drawCol = [colA[0]+(i*((colB[0]-colA[0])/step)),
                       colA[1]+(i*((colB[1]-colA[1])/step)),
                       colA[2]+(i*(colB[2]-colA[2])/step)]
            pygame.draw.rect(SCREEN,drawCol,(0,i*(SCRH/step),SCRW,step))

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
            self.player.xpos,self.player.ypos = self.spawnPoint[0]+20,self.spawnPoint[1]+20
            self.update_level(next=False) # lazy, only need to change entity positions
            self.player.wallData = [False,False,False,False,False]
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

    def tick_button_platforms(self):
        # correct any links to buttons that dont exist anymore
        for platform in self.disappearingPlatforms:
            idx = self.disappearingPlatforms.index(platform)
            if self.disappearingPlatformLinks[idx] > len(self.buttonPresses)-1:
                self.disappearingPlatformLinks[idx] = -1
        for platform in self.appearingPlatforms:
            idx = self.appearingPlatforms.index(platform)
            if self.appearingPlatformLinks[idx] > len(self.buttonPresses)-1:
                self.appearingPlatformLinks[idx] = -1

    def tick_enemies(self):
        for mob in self.entities:
            mob.fix_center()
            mob.tick()
            mob.update_hitboxes()
            mob.draw()
            mob.update_target((self.player.xpos,self.player.ypos))
            mob.pathfind()

        for mob in self.bossEntities:
            #print(mob.get_dist(mob.target)<mob.maxTargetDist)
            mob.fix_center()
            mob.update_hitbox()
            mob.draw()
            mob.tick_projectiles()
            mob.update_target((self.player.xpos, self.player.ypos))

            if mob.canSeeTarget:
                mob.wepaon_sequence()
            else:
                mob.state = 1
                mob.lastStateChange = now()
                mob.vulnerable = False

            if not mob.vulnerable:
                mob.tick()
                mob.pathfind()

                #print(f"Boss state: {mob.state}")
            if mob.state == 2:
                self.animations.append(Charge_Up(mob.xpos-125, mob.ypos - 350))
            elif mob.state == 3 and mob.firing:
                mob.projectiles.append(Boss_Projectile(mob.xpos-125,mob.ypos-350,mob.target))

            for item in mob.projectiles:
                item.target = mob.target
                if pygame.Rect.colliderect(self.player.hitbox.whole, toRect((item.xpos, item.ypos, 30, 30))):
                    if self.settings.annoyingBosses:
                        self.end()
                    else:
                        self.trigger_death(die=True)
                for plat in self.platforms:
                    if pygame.Rect.colliderect(toRect(plat),toRect((item.xpos,item.ypos,30,30))):
                        item.needsDel = True

    def tick_player(self):
##        self.player.wallData = self.player.check()
        self.player.lastIsDead = self.player.isDead
        self.player.lastYvel = self.player.yvel

        if self.player.yvel > 5:
            self.sound.start_fall()
        else:
            self.sound.end_fall()
        
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
            if self.player.onFloor:
                if self.player.wallData[0]:
                    self.player.yvel = -20
                    self.player.onFloor = False
                    if self.sound.enabled: self.sound.start_jump()
            if self.player.wallData[1]:
                self.player.yvel = -20
                self.player.xvel = 10
                if self.sound.enabled: self.sound.start_jump()
            if self.player.wallData[2]:
                self.player.yvel = -20
                self.player.xvel = -10
                if self.sound.enabled: self.sound.start_jump()
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
            self.trigger_death(die=False)
            
##        playerBox = get_actual_pos([self.player.xpos,self.player.ypos,50,50])
##        playerRect = pygame.Rect(self.player.xpos-25,self.player.ypos-25,50,50)
        self.player.wallData = [False,False,False,False,False]
        for mob in self.entities:
            mob.wallData = [False,False,False,False,False]
        for mob in self.bossEntities:
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

            for which in [self.bossEntities, self.entities]:
                for mob in which:
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

        for i in range(len(self.disappearingPlatforms)):
            compItem = toRect(get_actual_pos(self.disappearingPlatforms[i]))
            if not self.buttonPresses[self.disappearingPlatformLinks[i]]:
                if pygame.Rect.colliderect(self.player.hitbox.actBottom, compItem):
                    self.player.wallData[0] = True
                if pygame.Rect.colliderect(self.player.hitbox.actLeft, compItem):
                    self.player.wallData[1] = True
                if pygame.Rect.colliderect(self.player.hitbox.actRight, compItem):
                    self.player.wallData[2] = True
                if pygame.Rect.colliderect(self.player.hitbox.actTop, compItem):
                    self.player.wallData[3] = True
                if pygame.Rect.colliderect(self.player.hitbox.actWhole, compItem):
                    self.player.wallData[4] = True

                for which in [self.bossEntities, self.entities]:
                    for mob in which:
                        if pygame.Rect.colliderect(mob.hitbox.actBottom, compItem):
                            mob.wallData[0] = True
                        if pygame.Rect.colliderect(mob.hitbox.actLeft, compItem):
                            mob.wallData[1] = True
                        if pygame.Rect.colliderect(mob.hitbox.actRight, compItem):
                            mob.wallData[2] = True
                        if pygame.Rect.colliderect(mob.hitbox.actTop, compItem):
                            mob.wallData[3] = True
                        if pygame.Rect.colliderect(mob.hitbox.actWhole, compItem):
                            mob.wallData[4] = True

        for i in range(len(self.appearingPlatforms)):
            compItem = toRect(get_actual_pos(self.appearingPlatforms[i]))
            if self.buttonPresses[self.appearingPlatformLinks[i]]:
                if pygame.Rect.colliderect(self.player.hitbox.actBottom, compItem):
                    self.player.wallData[0] = True
                if pygame.Rect.colliderect(self.player.hitbox.actLeft, compItem):
                    self.player.wallData[1] = True
                if pygame.Rect.colliderect(self.player.hitbox.actRight, compItem):
                    self.player.wallData[2] = True
                if pygame.Rect.colliderect(self.player.hitbox.actTop, compItem):
                    self.player.wallData[3] = True
                if pygame.Rect.colliderect(self.player.hitbox.actWhole, compItem):
                    self.player.wallData[4] = True

                for which in [self.bossEntities, self.entities]:
                    for mob in which:
                        if pygame.Rect.colliderect(mob.hitbox.actBottom, compItem):
                            mob.wallData[0] = True
                        if pygame.Rect.colliderect(mob.hitbox.actLeft, compItem):
                            mob.wallData[1] = True
                        if pygame.Rect.colliderect(mob.hitbox.actRight, compItem):
                            mob.wallData[2] = True
                        if pygame.Rect.colliderect(mob.hitbox.actTop, compItem):
                            mob.wallData[3] = True
                        if pygame.Rect.colliderect(mob.hitbox.actWhole, compItem):
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

            for mob in self.bossEntities:
                if pygame.Rect.colliderect(mob.hitbox.actWhole,spike):
                    mob.health -= 1
                    if mob.health <= 0:
                        self.bossEntities.remove(mob)
                        self.stats.enemiesKilled += 1
                    if not self.contains_animation("code particle"):
                        self.animations.append(Code_Particle(mob.xpos - 250 + random.randint(-100, 100), mob.ypos + 14, self.img.code))

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
                    if self.player.wallData[0]:
                        self.player.yvel = -1
##                    self.player.ypos -= 10
                    break

        end = self.data[str(self.levelIDX)]["end"]
        if pygame.Rect.colliderect(self.player.hitbox.actWhole,
                    toRect(get_actual_pos([end[0],end[1],50,50]))):
            self.player.atFinish = True

        for which in [self.bossEntities, self.entities]:
            for mob in which:
                if pygame.Rect.colliderect(mob.hitbox.actWhole,self.player.hitbox.actWhole):
                    self.trigger_death()
                    if which == self.bossEntities and self.settings.annoyingBosses:
                        self.end()

        for item in self.buttons:
            if pygame.Rect.colliderect(self.player.hitbox.actWhole,get_actual_pos((item[0],item[1],50,50))):
                self.buttonPresses[self.buttons.index(item)] = True

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
        if self.player.wallData[3] and self.player.yvel > 0:  # if clipping through ground
            self.player.ypos -= 50
            self.player.yvel = 0

        if self.player.wallData[4] and self.player.yvel == 0:
            self.player.ypos = ((self.player.ypos // 50) * 50) + 31
            self.player.onFloor = True
            #self.player.ypos
            if self.player.lastYvel != 0: # if just landed
                self.animations.append(Impact_Particle(self.player.xpos,self.player.ypos+14,colour.darkgrey))

        for enemy in self.entities:
            if enemy.wallData[0] and enemy.yvel == 0:
                enemy.ypos = ((enemy.ypos // 50) * 50) + 21
                if enemy.lastYvel != 0:
                    self.animations.append(Impact_Particle(enemy.xpos,enemy.ypos+14,colour.darkgrey))
                    #print(f"last:{enemy.lastYvel} now {enemy.yvel}")

        for enemy in self.bossEntities:
            if enemy.wallData[0] and enemy.yvel == 0:
                enemy.ypos = ((enemy.ypos // 50) * 50)
                if enemy.lastYvel != 0:
                    self.animations.append(Impact_Particle(enemy.xpos,enemy.ypos+14,colour.darkgrey))

        if self.player.wallData[3] and self.player.yvel < 0:# and not self.player.wallData[0]: # top only
            self.player.wallData[1] = False
            self.player.wallData[2] = False # stop wall jumping
            self.player.yvel = -1
            self.player.ypos += 21

        #print(f"player ypos: {self.player.ypos}, yvel: {self.player.yvel}")

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
        self.bosses = []
        self.bossEntities = []
        self.buttons = []
        self.buttonPresses = []
        self.disappearingPlatforms = []
        self.disappearingPlatformLinks = []
        self.appearingPlatforms = []
        self.appearingPlatformLinks = []

        self.spawnPoint = []

        self.animations = []
        self.events = [False,False]
        # for all enemies defeated and bosses defeated

        try: # correct outdated levels
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
            if "bosses" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["bosses"] = []
            if "buttons" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["buttons"] = []
            if "disappearing platforms" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["disappearing platforms"] = []
            if "disappearing platform links" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["disappearing platform links"] = []
            if "appearing platforms" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["appearing platforms"] = []
            if "appearing platform links" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["appearing platform links"] = []
            
        except KeyError: # should only happen if missing the enitre level number
            self.data[str(self.levelIDX)] = {
                "start":[0,0],
                "end":[300,0],
                "platforms":[[-100,50,500,50]],
                "spikes":[],
                "fan bases":[],
                "fan columns":[],
                "stars":[],
                "mobs":[],
                "checkpoints":[],
                "bosses":[],
                "buttons":[],
                "disappearing platforms":[],
                "disappearing platform links": [],
                "appearing platforms": [],
                "appearing platform links":[]}

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
        for item in self.data[str(self.levelIDX)]["bosses"]:
            self.bosses.append([item[0],item[1]])
            health = 600 if not self.settings.annoyingBosses else 6000
            self.bossEntities.append(Boss(item[0],item[1],img=self.img.bossImg,health=health))
        for item in self.data[str(self.levelIDX)]["buttons"]:
            self.buttons.append([item[0],item[1]])
            self.buttonPresses.append(False)

        for item in self.data[str(self.levelIDX)]["disappearing platforms"]:
            self.disappearingPlatforms.append(item)
            self.disappearingPlatformLinks.append(-1)
        for i in range(len(self.data[str(self.levelIDX)]["disappearing platform links"])):
            try:
                self.disappearingPlatformLinks[i] = self.data[str(self.levelIDX)]["disappearing platform links"][i]
            except IndexError:
                pass

        for item in self.data[str(self.levelIDX)]["appearing platforms"]:
            self.appearingPlatforms.append(item)
            self.appearingPlatformLinks.append(-1)
        for i in range(len(self.data[str(self.levelIDX)]["appearing platform links"])):
            try:
                self.appearingPlatformLinks[i] = self.data[str(self.levelIDX)]["appearing platform links"][i]
            except IndexError:
                pass

        self.orient_spikes()

    def draw_bg(self):
        if now() - self.lastFanChange > self.fanInterval:
            self.fanState += 1
            if self.fanState >= len(self.img.fanColumn):
                self.fanState = 0
            self.lastFanChange = now()

        # why tf am I getting everything from the json file I have them stored in lists whyyyy
        blitToCam(self.img.finish, self.data[str(self.levelIDX)]["end"])  # VERY INEFFICIENT FIX ME
        for item in self.data[str(self.levelIDX)]["platforms"]:
            sendToCam(item,col=self.platformCol)
        for i in range(len(self.data[str(self.levelIDX)]["spikes"])):
            #print(f"len of spikes {len(self.data[str(self.levelIDX)]["spikes"])}\nlen of spikeDir {len(self.spikeDir)}")
            sendSpikeToCam(self.data[str(self.levelIDX)]["spikes"][i-1],orn=self.spikeDir[i-1])
        #for item in self.spikes:
        #    orn = self.spikeDir[self.spikes.index(item)]
        #    sendToCam(spike_convert(item,orn),"hitbox")
        for item in self.data[str(self.levelIDX)]["fan bases"]:
            blitToCam(self.img.fanBase[self.fanState],item)
        for item in self.data[str(self.levelIDX)]["fan columns"]:
            blitToCam(self.img.fanColumn[self.fanState],item)
        for item in self.data[str(self.levelIDX)]["stars"]:
            if self.scene == "editor":
                blitToCam(self.img.star,item)
            if item not in self.stats.stars[str(self.levelIDX)]:
                blitToCam(self.img.star,item)
        for item in self.data[str(self.levelIDX)]["checkpoints"]:
            if item == self.spawnPoint:
                blitToCam(self.img.checkpointOn,item)
            else:
                blitToCam(self.img.checkpointOff,item)

        if self.scene == "ingame":
            for item in self.data[str(self.levelIDX)]["buttons"]:
                if self.buttonPresses[self.data[str(self.levelIDX)]["buttons"].index(item)]:
                    blitToCam(self.img.buttonPressed, item)
                else:
                    blitToCam(self.img.buttonUnpressed, item)

            for item in self.data[str(self.levelIDX)]["disappearing platforms"]:
                plat = self.data[str(self.levelIDX)]["disappearing platforms"].index(item) #index of platform
                idx = self.disappearingPlatformLinks[plat] # get which button it is linked to
                #print(f"idx {idx}")
                if idx != -1:
                    if not self.buttonPresses[idx]:
                        sendToCam(item, col=[80,80,100])

            for item in self.data[str(self.levelIDX)]["appearing platforms"]:
                plat = self.data[str(self.levelIDX)]["appearing platforms"].index(item)
                idx = self.appearingPlatformLinks[plat]
                if idx != -1:
                    if self.buttonPresses[idx]:
                        sendToCam(item, col=[180,180,200])
            
        if self.scene == "editor":
            for item in self.data[str(self.levelIDX)]["mobs"]:
                blitToCam(self.img.enemyForEditor,(item[0]+5,item[1]+5))

            for item in self.data[str(self.levelIDX)]["bosses"]:
                blitToCam(self.img.bossImg,(item[0]-200,item[1]-200))

            for item in self.data[str(self.levelIDX)]["buttons"]:
                blitToCam(self.img.buttonUnpressed, item)

            for item in self.data[str(self.levelIDX)]["disappearing platforms"]:
                sendToCam(item, col=[80,80,100])

            for item in self.data[str(self.levelIDX)]["appearing platforms"]:
                sendToCam(item, col=[180,180,200])

    def draw_grid(self):
        for i in range((SCRW//50)+2):
            x = (i*50) - (self.player.xpos%50) + (self.settings.SCRWEX//2)
            pygame.draw.line(SCREEN,(220,220,255),(x,0),(x,SCRH))
            
        for j in range((SCRH//50)+2):
            y = (j*50) - (self.player.ypos%50) + (self.settings.SCRHEX//2)
            pygame.draw.line(SCREEN,(220,220,255),(0,y),(SCRW,y))

    def draw_menu(self):
        scr = self.editor.scroll#bind(-1000,self.editor.scroll,0)
        pygame.draw.rect(SCREEN,colour.lightgrey,(0,0,70,SCRH))
        pygame.draw.rect(SCREEN,colour.darkgrey,(0,0,70,SCRH),width=2)
        # frame
        for item in self.editor.originalItemRects:
            drawPos = [item[0],item[1]+scr,item[2],item[3]]
            #print(drawPos)
            pygame.draw.rect(SCREEN,(180,180,180),drawPos)

        SCREEN.blit(self.img.link,(SCRW-100,SCRH-100))
        # link image
        pygame.draw.rect(SCREEN,colour.darkgrey,(10,30+scr,50,10))
        # platform icon
        pygame.draw.polygon(SCREEN,colour.red,((30,110+scr),(40,110+scr),(35,80+scr)))
        # spike icon
        SCREEN.blit(self.img.finish,(3,125+scr))
        # finish
        SCREEN.blit(self.img.fanBase,(10,180+scr))
        # fan base image
        SCREEN.blit(self.img.fanColumn,(10,245+scr))
        # fan column
        SCREEN.blit(self.img.star,(10,305+scr))
        # fan column
        SCREEN.blit(self.img.enemyForEditor,(15,370+scr))
        # enemy
        SCREEN.blit(self.img.checkpointOn,(10,425+scr))
        # checkpoint
        SCREEN.blit(self.img.bossMenu,(10,485+scr))
        # boss
        SCREEN.blit(self.img.buttonUnpressed, (10, 540+scr))
        # button
        pygame.draw.rect(SCREEN, colour.darkgrey, (10, 625 + scr, 50, 10))
        # platform icon
        pygame.draw.rect(SCREEN, colour.darkgrey, (10, 685 + scr, 50, 10))
        # platform icon

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
        e = bind(-1000,self.editor.scroll,0) # short for extra
        self.editor.scroll = e
        for i in range(len(self.editor.itemRects)): # account for scrolling
            r = self.editor.originalItemRects[i]
            self.editor.itemRects[i] = [r[0],r[1]+e,r[2],r[3]]

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

        if self.editor.linkRect.pressed():
            self.editor.linkMode = not self.editor.linkMode
            if self.editor.linkMode:
                self.editor.selected = "Hover over highlighted platform to link to event"
            else:
                self.editor.selected = "platform"

        # does not work
        #for which in ["platform","spike","fan base","fan column","star","mob","checkpoint"]:
        #    print(which)
        #    for item in self.data[str(self.levelIDX)][which+"s"]:
        #        print(item)
        #        sendToCam(item,col=colour.white,name="hitbox")
        ###
        if self.editor.linkMode:
            for which in [self.disappearingPlatforms,self.appearingPlatforms]:
                for item in which:
                    sendToCam(item,col=colour.white,name="hitbox")
                    if pygame.Rect.colliderect(toRect(item),newMouseRect):
                        idx = which.index(item)
                        if which == self.disappearingPlatforms:
                            val = bind(0,self.disappearingPlatformLinks[idx]+self.editor.relativeScroll,len(self.buttons)-1)
                            self.disappearingPlatformLinks[idx] = val
                            #print(f"{self.data[str(self.levelIDX)]["disappearing platform links"]}")
                            self.data[str(self.levelIDX)]["disappearing platform links"][idx] = val
                            self.editor.selected = f"Linked to button {self.disappearingPlatformLinks[idx]+1}"
                        elif which == self.appearingPlatforms:
                            val = bind(0,self.appearingPlatformLinks[idx]+self.editor.relativeScroll,len(self.buttons)-1)
                            self.appearingPlatformLinks[idx] = val
                            self.data[str(self.levelIDX)]["appearing platform links"][idx] = val
                            self.editor.selected = f"Linked to button {self.appearingPlatformLinks[idx]+1}"

                        self.data[str(self.levelIDX)]["disappearing platform links"] = self.disappearingPlatformLinks
                        self.data[str(self.levelIDX)]["appearing platform links"] = self.appearingPlatformLinks
        else:
            if self.editor.selected in ["platform","disappearing platform","appearing platform"]:
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
                        if self.editor.selected == "platform":
                            self.data[str(self.levelIDX)]["platforms"].append(self.editor.pendingRect)
                        elif self.editor.selected == "disappearing platform":
                            self.data[str(self.levelIDX)]["disappearing platforms"].append(self.editor.pendingRect)
                            self.data[str(self.levelIDX)]["disappearing platform links"].append(-1)
                        elif self.editor.selected == "appearing platform":
                            self.data[str(self.levelIDX)]["appearing platforms"].append(self.editor.pendingRect)
                            self.data[str(self.levelIDX)]["appearing platform links"].append(-1)
                    self.editor.pendingRect = [0,0,0,0]

                if self.editor.clicksR == [True,False]:
                    # right click
                    which = ""
                    infoList = []
                    if self.editor.selected == "platform":
                        which = "platforms"
                    elif self.editor.selected == "disappearing platform":
                        which = "disappearing platforms"
                        infoList = self.disappearingPlatformLinks
                    elif self.editor.selected == "appearing platform":
                        which = "appearing platforms"
                        infoList = self.appearingPlatformLinks

                    for item in self.data[str(self.levelIDX)][which]:
                        if pygame.Rect.colliderect(toRect(newMouseRect),toRect(item)):
                            try:
                                self.data[str(self.levelIDX)][which].remove(item)
                                idx = self.data[str(self.levelIDX)][which].index(item)
                                infoList.pop(idx)
                            except:
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

                    elif self.editor.selected == "boss":
                        self.data[str(self.levelIDX)]["bosses"].append(truncPos)

                    elif self.editor.selected == "button":
                        self.data[str(self.levelIDX)]["buttons"].append(truncPos)

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

                    for item in self.bosses:
                        if pygame.Rect.colliderect(toRect(newMouseRect),toRect([item[0],item[1],50,50])):
                            self.data[str(self.levelIDX)]["bosses"].remove(item)
                            self.bosses.remove(item)

                    for item in self.buttons:
                        if pygame.Rect.colliderect(toRect(newMouseRect),toRect([item[0],item[1],50,50])):
                            self.data[str(self.levelIDX)]["buttons"].remove(item)
                            self.buttons.remove(item)

                self.update_level(next=False)          

class Editor:
    '''a namespace to hold editor data'''
    def __init__(self):
        self.clicks = [False,False]
        self.clicksR = [False,False]
        self.scroll = 0
        self.relativeScroll = 0
        self.pendingRect = [0,0,0,0]
        self.endRect = None
        self.mouseRect = [0,0,3,3]
        self.clicks = [False,False] # current and last state of LMB
        self.selected = "platform"
        self.linkMode = False

        self.linkRect = u.Pressable(SCRW-100,SCRH-100,70,70)
        self.originalItemRects = []
        self.itemRects = []
        self.ref = ["platform","spike","end","fan base",
                    "fan column","star","enemy","checkpoint",
                    "boss","button","disappearing platform",
                    "appearing platform"]

        for i in range(50):
            y = i*60
            self.originalItemRects.append((10,y+5,50,50))
            self.itemRects.append((10, y + 5, 50, 50))

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
        self.onFloor = False
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
        self.hitbox.top = toRect([self.xpos-10,self.ypos-19,20,20])
##        self.hitbox.bottom = toRect([self.xpos-12,self.ypos+15,24,15])
        self.hitbox.bottom = toRect([self.xpos-10,self.ypos+2,20,18])
        self.hitbox.left = toRect([self.xpos-20,self.ypos-20,5,30])
        self.hitbox.right = toRect([self.xpos+15,self.ypos-20,5,30])
        
        self.hitbox.actWhole = toRect(get_actual_pos([self.xpos-20,self.ypos-19,40,40]))
        self.hitbox.actTop = toRect(get_actual_pos([self.xpos-10,self.ypos-19,20,20]))
##        self.hitbox.actBottom = toRect(get_actual_pos([self.xpos-12,self.ypos+15,24,15]))
        self.hitbox.actBottom = toRect(get_actual_pos([self.xpos-10,self.ypos+2,20,18]))
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
    def __init__(self,xpos,ypos,maxXvel=5,maxYvel=30,gravity=0.981,img=None):
        self.xpos = xpos
        self.ypos = ypos
        self.center = [self.xpos,self.ypos]
        self.xvel = 0
        self.yvel = 0
        self.lastYvel = 0
        self.xInc = 1
        self.maxXvel = maxXvel
        self.maxYvel = maxYvel
        self.gravity = gravity
        self.target = [0,0]
        self.maxTargetDist = 500
        self.canSeeTarget = False
        self.img = img
        self.needsDel = False
        self.wallData = [False,False,False,False,False]
        self.hitbox = Mob_Hitbox()

    def pathfind(self):
        self.canSeeTarget = self.get_dist(self.target) < self.maxTargetDist
        if self.canSeeTarget:
            if self.target[0] > self.center[0]:
                self.xvel += self.xInc
                #print(">")
            elif self.target[0] < self.center[0]:
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

        if self.yvel > self.maxYvel:
            self.yvel = self.maxYvel

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

    def get_angle(self, pos):
        dx = self.xpos - pos[0]
        dy = self.ypos - pos[1]
        return math.degrees(math.atan2(dy, dx)) + 180

    def fix_center(self):
        self.center = [self.xpos, self.ypos]

class Boss(Enemy):
    def __init__(self,xpos,ypos,img,maxXvel=6,maxYvel=50,health=600,gravity=0.981):
        super().__init__(xpos,ypos,maxXvel=maxXvel,maxYvel=maxYvel,gravity=0.981,img=img)
        self.maxHealth = health
        self.health = self.maxHealth
        self.xcen = self.img.get_width()
        self.ycen = self.img.get_height()-50
        self.hb = u.healthBar(0,0,self.maxHealth)
        self.hb.width = 150
        self.hb.height = 30
        self.maxTargetDist = 1000
        self.projectiles = []

        self.vulnerable = False
        self.charge = 0
        self.chargeInterval = 500
        self.maxCharge = 10
        self.lastCharge = 0  # stores the time of the last charge increment
        self.firing = False
        self.lastFire = 0
        self.fireInterval = 300
        self.state = 1
        self.lastStateChange = 0
        self.stateChangeInterval = 3000

    def draw(self):
        blitToCam(self.img,(self.xpos-self.xcen,self.ypos-self.ycen))
        self.hb.draw()

        #sendToCam(list(self.hitbox.bottom), "hitbox", col=colour.white)
        #sendToCam(list(self.hitbox.left),"hitbox",col=colour.white)
        #sendToCam(list(self.hitbox.right),"hitbox",col=colour.white)
        #sendToCam(list(self.hitbox.top),"hitbox",col=colour.white)
        #sendToCam(list(self.hitbox.whole),"hitbox",col=colour.white)

    def update_hitbox(self):
        pos = get_screen_pos((self.xpos, self.ypos,0,0))
        self.hb.hp = self.health
        self.hb.xpos = pos[0] - 200
        self.hb.ypos = pos[1] - 250

        self.hitbox.whole = toRect([self.xpos - self.xcen, self.ypos - self.ycen, self.xcen, self.ycen+50])
        self.hitbox.top = toRect([self.xpos - self.xcen, self.ypos - self.ycen, self.xcen, 10])
        self.hitbox.bottom = toRect([self.xpos - self.xcen, self.ypos + self.ycen//2 - 60, self.xcen, 10])
        self.hitbox.left = toRect([self.xpos - self.xcen, self.ypos - self.ycen, 10, self.ycen-5])
        self.hitbox.right = toRect([self.xpos - 10, self.ypos - self.ycen, 10, self.ycen-5])

        self.hitbox.actWhole = toRect(get_actual_pos([self.xpos - self.xcen, self.ypos - self.ycen, self.xcen, self.ycen+50]))
        self.hitbox.actTop = toRect(get_actual_pos([self.xpos - self.xcen, self.ypos - self.ycen, self.xcen, 10]))
        self.hitbox.actBottom = toRect(get_actual_pos([self.xpos - self.xcen, self.ypos + self.ycen//2 - 60, self.xcen, 10]))
        self.hitbox.actLeft = toRect(get_actual_pos([self.xpos - self.xcen, self.ypos - self.ycen, 10, self.ycen-5]))
        self.hitbox.actRight = toRect(get_actual_pos([self.xpos - 10, self.ypos - self.ycen, 10, self.ycen-5]))

    def wepaon_sequence(self):
        if self.state == 1: # passive
            if now() - self.lastStateChange > self.stateChangeInterval:
                self.lastStateChange = now()
                self.state += 1

        elif self.state == 2: #charging
            self.vulnerable = True
            if now() - self.lastCharge > self.chargeInterval:
                self.lastCharge = now()
                self.charge += 1
            if self.charge >= self.maxCharge:
                self.state += 1

        elif self.state == 3:
            self.firing = False
            if now() - self.lastFire > self.fireInterval:
                self.lastFire = now()
                if self.charge > 0:
                    self.charge -= 1
                    self.firing = True
                else:
                    self.state = 1
                    self.lastStateChange = now()
                    self.vulnerable = False

    def get_dist(self,pos):
        return math.sqrt((pos[0]-self.xpos-self.xcen//2)**2+(pos[1]-self.ypos)**2)

    def fix_center(self):
        self.center = [self.xpos-self.xcen//2, self.ypos]

    def tick_projectiles(self):
        toDel = []
        for item in self.projectiles:
            item.tick()
            if item.needsDel:
                toDel.append(item)

        for item in toDel:
            self.projectiles.remove(item)

class Boss_Projectile:
    def __init__(self,xpos,ypos,target):
        self.xpos = xpos
        self.ypos = ypos
        self.target = [target[0],target[1]-10]
        self.col = [50,0,0] if random.randint(1,2) == 1 else [75,20,0]
        self.speed = 6
        startAngle = random.randint(0, 359)
        self.initalXmove = (self.speed * math.cos(math.radians(startAngle)))
        self.initialYmove = (self.speed * math.sin(math.radians(startAngle)))
        self.birth = now()
        self.life = 0 # how long it has existed for
        self.needsDel = False
        self.history = []

    def tick(self):
        self.life = now() - self.birth
        if self.life < 500: # move outward
            self.xpos += self.initalXmove
            self.ypos += self.initialYmove
        else: # find player
            playerBearing =  self.get_angle(self.target) % 360
            self.xpos += (self.speed * math.cos(math.radians(playerBearing)))
            self.ypos += (self.speed * math.sin(math.radians(playerBearing)))


        if self.life > 8000:
            self.needsDel = True


        self.history.insert(0,(self.xpos,self.ypos))
        while len(self.history) > 20:
            self.history.pop(-1)

        for position in self.history:
            pos = get_screen_pos((position[0], position[1], 0, 0))
            idx = self.history.index(position)
            size = 30-idx
            if size<10: size = 10
            pygame.draw.rect(SCREEN, self.col, (pos[0], pos[1],size,size))
        #for _ in range(3):
        #    pygame.draw.circle(SCREEN, self.col, (pos[0]+random.randint(-60,60), pos[1]+random.randint(-60,60)), 5)

    def get_angle(self,pos):
        dx = self.xpos - pos[0]
        dy = self.ypos - pos[1]
        return math.degrees(math.atan2(dy,dx))+180

class Animation:
    def __init__(self,xpos,ypos):
        self.frame = 0
        self.interval = 100
        self.name = "none"
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

class Code_Particle(Animation):
    def __init__(self,xpos,ypos,imgs):
        super().__init__(xpos,ypos)
        self.interval = 200
        self.imgs = imgs
        self.name = "code particle"

    def draw(self):
        blitToCam(self.imgs[random.randint(0,len(self.imgs)-1)],(self.xpos,self.ypos))
        if self.frame >= 5:
            self.finished = True

class Charge_Up(Animation):
    def __init__(self,xpos,ypos):
        super().__init__(xpos,ypos)
        self.interval = 50
        self.col = [50,0,0] if random.randint(1,2) == 1 else [75,20,0]
        self.xpos = xpos
        self.ypos = ypos
        self.name = "charge up"
        startAngle = random.randint(0,359)
        self.xInt = (150*math.cos(math.radians(startAngle))) /10
        self.yInt = (150*math.sin(math.radians(startAngle)))/10

    def draw(self):
        s = (10-self.frame)
        rect = [self.xpos + (self.xInt * s),
                self.ypos + (self.yInt * s),
                self.frame*5, self.frame*5]
        pygame.draw.rect(SCREEN,self.col,get_screen_pos(rect))
        if self.frame >= 10:
            self.frame = 10
            self.finished = True

class Here(Animation):
    def __init__(self,xpos,ypos):
        super().__init__(xpos,ypos)

    def draw(self):
        if self.frame > 20:
            self.finished = True
        pygame.draw.rect(SCREEN,colour.white,get_screen_pos([self.xpos-20,self.ypos-20,40,40]),width=3)

##################################################


titleBox = u.old_textbox("PLATFORM ENGINE",fontTitle,(SCRW//2,150),backgroundCol=None,tags=["menu"])
startBox = u.old_textbox("PLAY",font28,(SCRW//2,400),tags=["menu"])
menuBox = u.old_textbox("MENU",font18,(SCRW-35,20),tags=["ingame","editor","levels","settings","achievements"])
editorBox = u.old_textbox("EDITOR",font18,(SCRW//2,500),tags=["menu"])
levelsBox = u.old_textbox("LEVELS",font18,(SCRW//2,300),tags=["menu"])
selectedBox = u.old_textbox("",font18,(SCRW//2,60),tags=["editor"])
coordBox = u.old_textbox("",font18,(SCRW//3,20),tags=["editor"])
levelIDXBox = u.old_textbox("",font18,(SCRW//2,20),tags=["ingame","editor"])
settingsBox = u.old_textbox("SETTINGS",font18,(SCRW//1.3,500),tags=["menu"])
showFPSBox = u.old_textbox("Show FPS",font18,(SCRW//2,50),tags=["settings"])
FPSBox = u.old_textbox("FPS: -",font18,(SCRW-50,SCRH-50),tags=["ingame","editor","settings"])
statsTitleBox = u.old_textbox("Statistics",font28,(SCRW//2,300),tags=["settings"])
collectedStarsBox = u.old_textbox("Stars collectd: -",font18,(SCRW//2,400),tags=["settings"])
enemiesDefeatedBox = u.old_textbox("Enemies defeated: -",font18,(SCRW//2,450),tags=["settings"])
deathCountBox = u.old_textbox("Number of deaths: -",font18,(SCRW//2,500),tags=["settings"])
uptimeBox = u.old_textbox("Time Played: -",font18,(SCRW//2,550),tags=["settings"])
resetStatsBox = u.old_textbox("RESET STATISTICS",font18,(SCRW//5,550),tags=["settings"],backgroundCol=colour.red,textCol=colour.black)
annoyingBossesBox = u.old_textbox("Annoyinger bosses",font18,(SCRW//2,150),tags=["settings"])
soundBox = u.old_textbox("Sound",font18,(SCRW//2,100),tags=["settings"])
achievementBox = u.old_textbox("Achievements",font18,(SCRW-(SCRW//1.33),500),tags=["menu"])
achievementTitleBox = u.old_textbox("ACHIEVEMENTS",fontTitle,(SCRW//2,100),tags=["achievements"],backgroundCol=None)

linkBox = u.old_textbox("Link mode",font18,(SCRW//2,100),tags=["editor"],backgroundCol=colour.red)

boxes = [titleBox,startBox,menuBox,editorBox,selectedBox,coordBox,levelIDXBox,levelsBox,settingsBox,
         showFPSBox,statsTitleBox,collectedStarsBox,enemiesDefeatedBox,deathCountBox,uptimeBox,
         resetStatsBox,annoyingBossesBox,soundBox,achievementBox,achievementTitleBox]
# hard coded textboxes

##################################################

def bind(minim,val,maxim):
    if val > maxim:
        return maxim
    if val < minim:
        return minim
    else:
        return val

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
        #print(f"success for {newRect}")
        pygame.draw.rect(SCREEN,col,newRect,width=2)

def blitToCam(item,pos):
    SCREEN.blit(item,((SCRW//2)-player.xpos+pos[0],(SCRH//2)-player.ypos+pos[1]))

def get_screen_pos(thing):
    '''Actual position -> Screen position'''
    if len(thing) == 2:
        thing = [thing[0],thing[1],0,0]
    return [thing[0]-player.xpos+(SCRW//2),thing[1]-player.ypos+(SCRH//2),thing[2],thing[3]]

def get_actual_pos(thing):
    '''Screen position -> Actual position'''
    if len(thing) == 2:
        thing = [thing[0],thing[1],0,0]
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

def reposition_boxes():
    titleBox.pos = (SCRW//2,200)
    startBox.pos = (SCRW//2,400)
    menuBox.pos = (SCRW-35,20)
    editorBox.pos = (SCRW//2,500)
    levelsBox.pos = (SCRW//2,300)
    selectedBox.pos = (SCRW//2,60)
    coordBox.pos = (SCRW//3,20)
    levelIDXBox.pos = (SCRW//2,20)
    settingsBox.pos = (SCRW//1.3,500)
    showFPSBox.pos = (SCRW//2,50)
    FPSBox.pos = (SCRW-50,SCRH-50)
    statsTitleBox.pos = (SCRW//2,300)
    collectedStarsBox.pos = (SCRW//2,400)
    enemiesDefeatedBox.pos = (SCRW//2,450)
    deathCountBox.pos = (SCRW//2,500)
    uptimeBox.pos = (SCRW//2,550)
    resetStatsBox.pos = (SCRW//5,550)
    annoyingBossesBox.pos = (SCRW//2,150)
    soundBox.pos = (SCRW//2,100)
    achievementBox.pos = (SCRW-(SCRW//1.33),500)
    linkBox.pos = (SCRW//2,100)
    achievementTitleBox.pos = (SCRW//2,150)

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
        game.init_clouds()

    if settingsBox.isPressed():
        game.scene = "settings"

    if showFPSBox.isPressed():
        game.settings.showFPS = not game.settings.showFPS

    if resetStatsBox.isPressed():
        game.stats.stars = {}
        game.stats.enemiesKilled = 0
        game.stats.deaths = 0
        #game.stats.playTime = 0
        game.fix_stats_stars()

    if annoyingBossesBox.isPressed():
        game.settings.annoyingBosses = not game.settings.annoyingBosses

    if game.scene == "editor" and game.editor.linkMode:
        linkBox.display()

    if achievementBox.isPressed():
        game.scene = "achievements"

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

    pygame.mixer.quit()
    pygame.quit()
    sys.exit()

def now():
    return pygame.time.get_ticks()

def handle_events(move):
    global SCRW,SCRH
    game.editor.relativeScroll = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            go_quit()

        if event.type == pygame.VIDEORESIZE:
            SCREEN = pygame.display.set_mode((event.w, event.h),pygame.RESIZABLE)
            SCRW,SCRH = pygame.display.get_window_size()
            game.settings.SCRWEX = SCRW%100
            game.settings.SCRHEX = SCRH%100
            reposition_boxes()
            game.scale = min(SCRW/800,SCRH/600,)
            game.img.resize_cloud(game.scale)

        elif event.type == pygame.MOUSEWHEEL:
            #print(f"{event.y}")
            game.editor.relativeScroll = event.y
            if not game.editor.linkMode:
                game.editor.scroll += (event.y*20)

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
player = Player(gravity=0.981,img=img.body,maxXvel = 10, maxYvel = 30)
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

    if game.sound.enabled:
        game.sound.run_music()

    if game.scene == "ingame":
        game.draw_gradient()
        game.generate_cloud()
        game.draw_bg()
        game.tick_enemies()
        game.tick()
        game.correct_player() # temp
        game.tick_player()
        #game.correct_player()
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
        game.draw_gradient()
        game.generate_cloud()
        selectedBox.update_message(game.editor.selected.capitalize())
        levelIDXBox.update_message("Level " + str(game.levelIDX))
        mpos = game.editor.mouseRect
        mapped = get_actual_pos(mpos)
        acx,acy = ((mapped[0]//50)*50,(mapped[1]//50)*50)
        coordBox.update_message(( str(acx) + "," + str(acy) ))
        
        game.draw_grid()
        #game.run_editor() # temp
        game.tick_button_platforms()
        game.draw_bg()
        game.check_selected()
        game.run_editor()
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
            SCREEN.blit(img.tick,((SCRW//2)+50,35))

        if game.settings.annoyingBosses:
            SCREEN.blit(img.tick,((SCRW//2)+100,135))