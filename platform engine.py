import colour
from copy import deepcopy
import json
import math
import os
import pygame
import random 
import sys  
import utility as u
import webbrowser as w


SCRW = 800
SCRH = 600
TICKRATE = 60
FONT = "mvboli"
FONTSIZEBASE = 18

uptime = 0

pygame.init()
pygame.mixer.init()
SCREEN = pygame.display.set_mode((SCRW,SCRH),pygame.RESIZABLE)
u.init(SCREEN)
clock = pygame.time.Clock()
pygame.display.set_caption("Platform game!")
pygame.display.set_icon(pygame.image.load("platform icon.bmp"))
font10 = pygame.font.SysFont(FONT,FONTSIZEBASE-8)
font18 = pygame.font.SysFont(FONT,FONTSIZEBASE)
font28 = pygame.font.SysFont(FONT,FONTSIZEBASE+10)
font50 = pygame.font.SysFont(FONT,FONTSIZEBASE+32)
fontTitle = pygame.font.SysFont("courier new",70)
fontTitle.set_bold(True)

class Images:
    def __init__(self):
        #self.fanBase = pygame.image.load("fan base.png")
        #self.fanColumn = pygame.image.load("fan column.png")
        self.image = {
        "body":pygame.image.load("body.png"),
        "body_thick":pygame.image.load("body_thick.png"),
        "enemy_body":pygame.image.load("enemy_body.png"),
        "enemy_body_thick" : pygame.image.load("enemy_body_thick.png"),
        "jumping_enemy_body":pygame.image.load("jumping_enemy_body.png"),
        "jumping_enemy_body_air" : pygame.image.load("jumping_enemy_body_air.png"),
        "star" : pygame.image.load("star.png"),
        "finish" : pygame.image.load("finish.png"),
        "checkpoint_off" : pygame.image.load("checkpoint_off.png"),
        "checkpoint_on" : pygame.image.load("checkpoint_on.png"),
        "tick" : pygame.transform.scale_by(pygame.image.load("tick.png"),(0.2)),
        "boss_img" : pygame.image.load("boss_face.png"),
        "boss_img_thick" : pygame.image.load("boss_face_thick.png"),
        "boss_menu" : pygame.transform.scale_by(pygame.image.load("boss_face.png"),0.2),
        "button_unpressed" : pygame.image.load("button_unpressed.png"),
        "button_pressed" : pygame.image.load("button_pressed.png"),
        "link" : pygame.image.load("link.png"),
        "rock" : pygame.image.load("rock.png"),
        "disappearing_rock" : pygame.image.load("disappearing_rock.png"),
        "appearing_rock" : pygame.image.load("appearing_rock.png"),
        "bomb" : pygame.image.load("bomb.png"),
        "bomb_lit": pygame.image.load("bomb_lit.png"),
        "ice": pygame.image.load("ice.png"),
        "fan_column" : [
            pygame.image.load("fan_column1.png"),
            pygame.image.load("fan_column2.png"),
            pygame.image.load("fan_column3.png")
        ],
        "fan_base" : [
            pygame.image.load("fan_base1.png"),
            pygame.image.load("fan_base2.png"),
            pygame.image.load("fan_base3.png")],
        "cloud" : {"1":[pygame.image.load("cloud1.png"),
                          pygame.image.load("cloud2.png"),
                          pygame.image.load("cloud3.png")]},
        "code" : [],
        "hats":[],
        }
        for i in range(10):
            name = f"code{i+1}.png"
            self.image["code"].append(pygame.image.load(name))
        #self.image["body"].fill((0,0,0))
        for i in range(4):
            name = f"hat{i + 1}.png"
            self.image["hats"].append(pygame.image.load(name))

        blank = pygame.image.load("enemy_body.png")
        pygame.draw.circle(blank,colour.white,(20,15),10)
        pygame.draw.circle(blank,colour.black,(20,16),7)
        pygame.draw.circle(blank,colour.white,(22,17),2)
        pygame.draw.circle(blank,colour.black,(20,18),1)
        self.image["enemy_for_editor"] = blank
        blank = pygame.image.load("jumping_enemy_body_air.png")
        pygame.draw.circle(blank, colour.white, (20, 15), 10)
        pygame.draw.circle(blank, colour.black, (20, 16), 7)
        pygame.draw.circle(blank, colour.white, (22, 17), 2)
        pygame.draw.circle(blank, colour.black, (20, 18), 1)
        self.image["jumping_enemy_for_editor"] = blank

    def resize_cloud(self,scale):
        self.image["cloud"][str(scale)] = []
        for item in self.image["cloud"]["1"]:
            self.image["cloud"][str(scale)].append(pygame.transform.scale_by(item,scale))

class Dummy_Images:
    def __init__(self):
        self.image = {
            "body":self.blank(40,40),
            "body_thick":self.blank(120,40),
            "enemy_body": self.blank(40, 40),
            "enemy_body_thick": self.blank(120, 40),
            "star":self.blank(),
            "finish":self.blank(),
            "checkpoint_on":self.blank(),
            "checkpoint_off":self.blank(),
            "tick":self.blank(142,118),
            "boss_img":self.blank(250,250),
            "boss_img_thick":self.blank(250,250),
            "boss_menu":self.blank(250,250),
            "button_unpressed":self.blank(),
            "button_pressed":self.blank()
        }

        self.image["body"].fill((0,141,201))
        self.image["body_thick"].fill((0, 141, 201))
        self.image["enemy_body"].fill((237,28,36))
        self.image["enemy_body_thick"].fill((237,28,36))
        pygame.draw.polygon(self.image["star"], (255, 255, 0),
                [(2, 19), (19, 19), (25, 2), (31, 19), (48, 19), (36, 29), (40, 44), (24, 35), (10, 44), (14, 29)])
        pygame.draw.rect(self.image["finish"], (150, 100, 0), (10, 10, 5, 40))
        pygame.draw.rect(self.image["finish"], (255, 255, 255), (10, 10, 40, 30))
        pygame.draw.rect(self.image["checkpoint_off"], (127, 127, 127), (22, 15, 6, 35))
        pygame.draw.rect(self.image["checkpoint_off"], (50, 50, 50), (20, 10, 10, 10))
        pygame.draw.rect(self.image["checkpoint_off"], (255, 0, 0), (22, 12, 6, 6))
        pygame.draw.rect(self.image["checkpoint_on"], (127, 127, 127), (22, 15, 6, 35))
        pygame.draw.rect(self.image["checkpoint_on"], (50, 50, 50), (20, 10, 10, 10))
        pygame.draw.rect(self.image["checkpoint_on"], (0, 255, 0), (22, 12, 6, 6))
        pygame.draw.polygon(self.image["tick"], (255, 0, 0),
                            [(15, 71), (27, 70), (33, 87), (129, 19), (136, 30), (23, 112)])
        for each in ["boss_img","boss_img_thick","boss_menu"]:
            pygame.draw.polygon(self.image[each], (219, 178, 152), [(16, 0), (28, 164), (47, 206), (84, 250), (250, 250), (250, 0)])
            pygame.draw.circle(self.image[each], (255, 255, 255), (182, 76), 30)
            pygame.draw.circle(self.image[each], (255, 255, 255), (65, 100), 30)
            pygame.draw.circle(self.image[each], (0, 0, 0), (182, 81), 15)
            pygame.draw.circle(self.image[each], (0, 0, 0), (65, 105), 15)
            pygame.draw.polygon(self.image[each], (127, 93, 72), [(82, 92), (100, 95), (154, 164), (70, 177)])
            pygame.draw.polygon(self.image[each], (138, 100, 81), [(84, 214), (217, 210), (182, 250), (116, 250)])
            pygame.draw.polygon(self.image[each], (0, 0, 0), [(100, 220), (210, 215), (175, 245), (120, 245)])
            pygame.draw.polygon(self.image[each], (55, 45, 36), [(22, 59), (205, 17), (222, 34), (23, 76)])
        self.image["boss_img_thick"] = pygame.transform.scale(self.image["boss_img_thick"],(250,150))
        self.image["boss_menu"] = pygame.transform.scale_by(self.image["boss_menu"], 0.2)
        pygame.draw.rect(self.image["button_unpressed"], (0, 0, 0), (5, 36, 40, 14))
        pygame.draw.rect(self.image["button_pressed"], (0, 0, 0), (5, 36, 40, 14))
        pygame.draw.rect(self.image["button_unpressed"], (255, 0, 0), (10, 29, 30, 7))

    def blank(self,x=50,y=50):
        return pygame.surface.Surface((x,y))

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
        self.death = pygame.mixer.Sound("death.wav")
        self.bossfire = pygame.mixer.Sound("boss fire.wav")
        self.bomb = pygame.mixer.Sound("bomb.wav")
        self.fan = pygame.mixer.Sound("fan.wav")

        self.bossfire.set_volume(0.5)

        self.musicIdx = 0
        self.music = [
            pygame.mixer.Sound("Track 1.wav"),
            pygame.mixer.Sound("160_bpm_bassline.wav")
            ]

        for song in self.music:
            song.set_volume(0.5)

        self.channels = []
        for i in range(8):
            self.channels.append(pygame.mixer.Channel(i))
        # 0 - music,
        # 1 - fall,
        # 2 - jump and deaths
        # 3 - bomb
        # 4 - boss fx
        # 5 - fan

        self.enabled = False

    def start_fall(self):
        if not self.channels[1].get_busy() and self.enabled:
            self.channels[1].play(self.fall,fade_ms=3000)

    def end_fall(self):
        self.channels[1].stop()

    def start_jump(self):
        if self.enabled:
            self.channels[2].stop()
            self.channels[2].play(self.jump)

    def start_bomb(self):
        if self.enabled:
            self.channels[3].stop()
            self.channels[3].play(self.bomb)

    def start_death(self):
        if self.enabled:
            self.channels[2].stop()
            self.channels[2].play(self.death)

    def run_music(self):
        if not self.channels[0].get_busy():
            self.musicIdx += 1
            if self.musicIdx >= len(self.music):
                self.musicIdx = 0

            self.channels[0].play(self.music[self.musicIdx])

    def start_fan(self):
        if self.enabled and not self.channels[5].get_busy():
            self.channels[5].play(self.fan)

    def end_fan(self):
        self.channels[5].stop()

    def boss_fire(self):
        if self.enabled:
            self.channels[4].stop()
            self.channels[4].play(self.bossfire)

    def stop(self,idx):
        self.channels[idx].stop()

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
        self.nextBox = u.old_textbox(" > ", font50, (SCRW - 50, SCRH - 50))
        self.prevBox = u.old_textbox(" < ", font50, (50, SCRH - 50))
        self.boxes = []
        for i in range(self.num):
            j = (i%10)
            x = ((j%5)*SCRW//5)+SCRW//10 
            y = ((j//5)*SCRH//2)+SCRH//4
            #print(f"num {i+1} pos ({x}, {y})")
            self.boxes.append(u.old_textbox(" "+str(i+1)+" ",font50,(x,y)))

    def tick(self):
        self.nextBox.get_presses()
        self.prevBox.get_presses()

        for item in self.boxes:
            item.get_presses()
            item.isShowing = False

        for i in range((self.page-1)*10,self.page*10):
            try:
                self.boxes[i].isShowing = True
            except IndexError:
                pass

        if self.num > 10 and ((math.ceil(self.num/10) != self.page)):
            self.nextBox.isShowing = True
            self.nextBox.display()
        else:
            self.nextBox.isShowing = False
        if self.num > 10 and self.page != 1:
            self.prevBox.isShowing = True
            self.prevBox.display()
        else:
            self.prevBox.isShowing = False

        if self.nextBox.isPressed():
            self.page += 1

        if self.prevBox.isPressed():
            self.page -= 1

        idxRange = [(self.page-1)*10,self.page*10]
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
        self.chaosMode = False
        self.highResTextures = True

class Stats:
    def __init__(self):
        self.stars = []
        self.enemiesKilled = 0
        self.startTime = 0
        self.playTime = 0
        self.deaths = 0
        self.hidden1progress = 0
        self.bossesKilled = 0
        self.fallen = False

class MiscData:
    def __init__(self):
        self.lastCloud = 0
        self.cloudInterval = 10000

        self.lastFanChange = 0
        self.fanInterval = 200
        self.fanState = 0

        self.lastFPSUpdate = 0
        self.FPSUpdateInterval = 200

        self.platformCol = colour.darkgrey
        self.bgCol = [(200,200,255),
                      (200,200,170)]

        self.hasTransition = False
        self.wasTransition = False

        self.bombRadius = 150
        self.bombFuse = 1000
        self.bombDamage = 100

        self.timerStart = 0
        self.timerCount = 0
        self.timerRunning = False
        self.showTimer = False

        self.lastMessageChange = 0
        self.messageState = 0
        self.messages = ["Find me on github! https://github.com/ScootiusMaximus/Platform-engine",
                         "Add a suggestion! https://forms.gle/JnM4B8yjJY9bBqJ86",
                         "Report an issue! https://forms.gle/JnM4B8yjJY9bBqJ86"]
        self.links = ["https://github.com/ScootiusMaximus/Platform-engine",
                      "https://forms.gle/JnM4B8yjJY9bBqJ86",
                      "https://forms.gle/7YipdkXidHuV1KzV6"]

class Chaos:
    def __init__(self):
        self.interval = 5 * 1000
        self.displayTime = 5 * 1000
        self.state = 1
        self.lastChange = 0
        self.action = 0
        self.actions = ["spawn enemies","rgb","low gravity","speed","random teleport",
                        "boss fight","thick","invert screen","wonky","bomb strike"]

    def reset(self):
        self.lastChange = now()
        self.state = 1

class Achievements:
    def __init__(self):
        self.achievements = {
            "death1":False,
            "death10":False,
            "death100":False,
            "death1k":False,
            "star1":False,
            "star10":False,
            "star100":False,
            "fall1":False,
            "enemy1":False,
            "enemy10":False,
            "enemy100":False,
            "enemy1k":False,
            "boss1":False,
            "hidden1":False,
            "time1":False,
            "time10":False,
            "time100":False,
            "hidden2":False,
        }
        self.lastAchievements = {}
        self.messages = {
            "death1": ["Ouch","Die for the first time"],
            "death10": ["Big Ouch","Die 10 times"],
            "death100": ["Biggest Ouch","Die 100 times"],
            "death1k": ["Keep Trying","Die 1000 times"],
            "death10k":["Really?","Die 10,000 times"],
            "star1": ["Shiny","Collect a star"],
            "star10": ["Shinier","Collect 10 stars"],
            "star100": ["Collector of Shiny","Collect 100 stars"],
            "fall1": ["Oops","Fall off the map"],
            "enemy1": ["Little Red Square","Defeat an enemy"],
            "enemy10": ["Little Red Squares","Defeat 10 enemies"],
            "enemy100": ["Many Little Red Squares","Defeat 100 enemies"],
            "enemy1k": ["Square Slayer","Defeat 1000 enemies"],
            "boss1": ["Take That!","Defeat a Boss"],
            "hidden1": ["Hidden achievement 1","Why would you do that?"],
            "time1": ["Getting Started","Play for 1 minute"],
            "time10": ["Getting into it","Play for 10 minutes"],
            "time100": ["Addicted","Play for 100 minutes"],
            "hidden2": ["Hidden achievement 2","You must really love this game"]
        }
        self.slots = []

        self.update_slots()

    def update_slots(self):
        self.slots = []
        y = 100
        x = 50
        for key in self.achievements:
            col = (255,0,0) if not self.achievements[key] else (0,255,0)
            self.slots.append(u.old_textbox(
                f"{self.messages[key][0]}: {self.messages[key][1]}",
                pygame.font.SysFont(FONT,FONTSIZEBASE-3),
                (x, y),
                backgroundCol=col,center=False))
            y += 40
            if y > SCRH-40:
                y = 100
                x = SCRW//2

    def show(self):
        for item in self.slots:
            item.isShowing = True
            item.display()
            item.isShowing = False

class Notification:
    def __init__(self,title,body,time=5000,font=FONT,size=FONTSIZEBASE):
        self.width = 200
        self.height = 40
        self.xpos = 0
        self.ypos = SCRH- self.height
        self.title = title
        self.body = body
        self.time = time
        self.font = font
        self.birth = 0
        self.displaying = False
        self.needsDel = False

        if len(self.title) < 10:
            titleSize = size+4
        if len(self.title) < 18:
            titleSize = size
        else:
            titleSize = size-4
        titleFont = pygame.font.SysFont(self.font,titleSize)
        titleFont.set_bold(True)

        if len(self.body) < 10:
            bodySize = size+2
        if len(self.body) < 18:
            bodySize = size-2
        else:
            bodySize = size-5
        bodyFont = pygame.font.SysFont(self.font,bodySize)
        bodyFont.set_bold(True)

        self.titleBox = u.old_textbox(self.title,titleFont,(25,self.ypos),backgroundCol=None,textCol=colour.black,center=False)
        self.bodyBox = u.old_textbox(self.body,bodyFont,(25,self.ypos+20),backgroundCol=None,textCol=colour.black,center=False)

    def tick(self):
        life = now() - self.birth
        if life > self.time:
            self.needsDel = True

        if life < 250:
            self.ypos = SCRH-((life/250)*self.height)

        pygame.draw.rect(SCREEN, colour.darkgrey, (self.xpos-3, self.ypos-3, self.width+6, self.height+6))
        pygame.draw.rect(SCREEN, colour.lightgrey, (self.xpos, self.ypos, self.width, self.height))
        self.titleBox.pos = (25,self.ypos)
        self.bodyBox.pos = (25,self.ypos+20)
        self.titleBox.display()
        self.bodyBox.display()

class Game:
    def __init__(self):
        self.gravity = 0.981
        self.scene = "menu"
        self.restart = False # if the player presses the restart key
        self.scale = 1

        self.editor = Editor()
        self.img = Images()
        self.player = Player(gravity=self.gravity, img=self.img.image["body"])
        self.sound = Soundboard()
        self.settings = Settings()
        self.stats = Stats()
        self.misc = MiscData()
        self.chaos = Chaos()
        self.achievements = Achievements()
        self.rgb = u.rainbow()
        self.hats = Hat_Selector(self.img.image["hats"])

        self.clouds = []
        self.notifications = []

        self.logs = []

        self.UP = [pygame.K_UP,pygame.K_w,pygame.K_SPACE]
        self.LEFT = [pygame.K_a,pygame.K_LEFT]
        self.RIGHT = [pygame.K_d,pygame.K_RIGHT]
        self.DOWN = [pygame.K_s,pygame.K_DOWN]
        self.RESTART = [pygame.K_r]

        self.enableMovement = True

        self.data = {} # the whole json file
        self.levelIDX = 1

        self.platforms = [] # list of item rects in current level
        self.spikes = []
        self.spikeDir = []
        self.fanBases = []
        self.fanColumns = []
        self.enemies = []
        self.enemyEntities = []
        self.jumpingEnemies = []
        self.jumpingEnemyEntities = []
        self.stars = []
        self.bosses = []
        self.bossEntities = []
        self.buttons = []
        self.buttonPresses = []
        self.disappearingPlatforms = []
        self.disappearingPlatformLinks = []
        self.appearingPlatforms = []
        self.appearingPlatformLinks = []
        self.checkpoints = []
        self.bombs = []
        self.bombStates = [] # should be list of [state,time started exploding]
        self.ice = []
        self.iceStates = [] # False = present, True = broken

        self.events = [False,False]
        # events should be:
        # no enemies left, boss defeated
        # UNUSED

        self.animations = []
        self.spawnPoint = []

        self.load()
        self.update_level()
        self.load_stats()
        self.fix_stats_stars()
        self.achievements.update_slots()

    def log(self,message):
        self.logs.append(message)

    def save_log(self):
        with open("log.txt","w") as file:
            for line in self.logs:
                file.write(f"{line}\n")

    def check_achievements(self,announce=False):
        self.achievements.lastAchievements = deepcopy(self.achievements.achievements)
        # since modifying achievements modifies lastAchievements without deepcopy()

        if self.stats.deaths >= 1:
            self.achievements.achievements["death1"] = True
        if self.stats.deaths >= 10:
            self.achievements.achievements["death10"] = True
        if self.stats.deaths >= 100:
            self.achievements.achievements["death100"] = True
        if self.stats.deaths >= 1000:
            self.achievements.achievements["death1k"] = True
        if self.stats.deaths >= 10000:
            self.achievements.achievements["death10k"] = True

        starCount = 0
        for key in self.stats.stars:
            starCount += len(self.stats.stars[key])
        if starCount >= 1:
            self.achievements.achievements["star1"] = True
        if starCount >= 10:
            self.achievements.achievements["star10"] = True
        if starCount >= 100:
            self.achievements.achievements["star100"] = True

        if self.player.ypos >= 5000 and self.scene == "ingame":
            self.stats.fallen = True
        if self.stats.fallen:
            self.achievements.achievements["fall1"] = True

        if self.stats.enemiesKilled >= 1:
            self.achievements.achievements["enemy1"] = True
        if self.stats.enemiesKilled >= 10:
            self.achievements.achievements["enemy10"] = True
        if self.stats.enemiesKilled >= 100:
            self.achievements.achievements["enemy100"] = True
        if self.stats.enemiesKilled >= 1000:
            self.achievements.achievements["enemy1k"] = True

        if self.stats.bossesKilled >= 1:
            self.achievements.achievements["boss1"] = True

        if self.stats.hidden1progress >= 100:
            self.achievements.achievements["hidden1"] = True

        if self.stats.playTime >= 1 * 1000 * 60:
            self.achievements.achievements["time1"] = True
        if self.stats.playTime >= 10 * 1000 * 60:
            self.achievements.achievements["time10"] = True
        if self.stats.playTime >= 100 * 1000 * 60:
            self.achievements.achievements["time100"] = True
        if self.stats.playTime >= 1000 * 1000 * 60:
            self.achievements.achievements["hidden2"] = True

        if ((self.achievements.lastAchievements != self.achievements.achievements)
                and announce):
            # has got an achievement:
            for key in self.achievements.achievements:
                if self.achievements.achievements[key] != self.achievements.lastAchievements[key]:
                    #print("announcing")
                    ##if key == "death100":
                    #    w.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

                    self.notifications.append(
                        Notification(self.achievements.messages[key][0],self.achievements.messages[key][1]))

        if not empty(self.notifications):
            if not self.notifications[0].displaying:
                self.notifications[0].displaying = True
                self.notifications[0].birth = now()
            self.notifications[0].tick()
            for item in self.notifications:
                if item.needsDel:
                    self.notifications.remove(item)

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

                if pygame.Rect.colliderect(points[0],toRect(plat)):
                    bottom = True
                if pygame.Rect.colliderect(points[1],toRect(plat)):
                    right = True
                if pygame.Rect.colliderect(points[2],toRect(plat)):
                    top = True
                if pygame.Rect.colliderect(points[3],toRect(plat)):
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

    def start_chaos(self,what):
        if what == "spawn enemies":
            for _ in range(5):
                posMod = make_position_modifier(3,8)
                self.enemyEntities.append(Enemy(self.player.xpos + posMod[0],
                                                self.player.ypos + posMod[1],
                                                img=self.img.image["enemy_body"]))
        elif what == "rgb":
            pass # does this in the draw_gradient()

        elif what == "invert screen":
            pass # handled in main game loop

        elif what == "wonky":
            pass # handled in main game loop

        elif what == "boss fight":
            posMod = make_position_modifier(5,10)
            self.bossEntities.append(Boss(self.player.xpos + posMod[0],
                                          self.player.ypos + posMod[1],
                                          img=self.img.image["boss_img"],
                                          health=200))

        elif what == "random teleport":
            posMod = make_position_modifier(2,4)
            self.player.xpos += posMod[0]
            self.player.ypos += posMod[1]

        elif what == "speed":
            self.player.maxXvel = 20
            for which in [self.bossEntities, self.enemyEntities]:
                for item in which:
                    item.maxXvel = 10

        elif what == "low gravity":
            self.player.gravity = 0.5
            for which in [self.bossEntities, self.enemyEntities]:
                for item in which:
                    item.gravity = 0.5

        elif what == "thick":
            self.player.update_image(self.img.image["body_thick"])
            for item in self.enemyEntities:
                item.update_image(self.img.image["enemy_body_thick"])
            for item in self.bossEntities:
                item.update_image(self.img.image["boss_img_thick"])

        elif what == "bomb strike":
            for _ in range(5):
                pos = make_position_modifier(1,3)
                self.bombs.append([self.player.xpos + pos[0],
                                   self.player.ypos + pos[1]])
                self.bombStates.append([0,0])

    def end_chaos(self):
        self.chaos.reset()

        self.player.update_image(self.img.image["body"])
        for item in self.enemyEntities:
            item.update_image(self.img.image["enemy_body"])
        for item in self.bossEntities:
            item.update_image(self.img.image["boss_img"])

        self.player.gravity = 0.981
        for which in [self.bossEntities, self.enemyEntities]:
            for item in which:
                item.gravity = 0.981

        self.player.maxXvel = 10
        for which in [self.bossEntities, self.enemyEntities]:
            for item in which:
                item.maxXvel = random.randint(4, 6)

    def fix_stats_stars(self):
        for i in range(len(self.data)):
            if str(i+1) not in self.stats.stars:
                self.stats.stars[str(i+1)] = []

    def generate_cloud(self):
        if now() - self.misc.lastCloud > self.misc.cloudInterval:
            self.misc.lastCloud = now()
            typ = random.randint(0,2)
            self.clouds.append(Cloud(typ,self.img.image["cloud"][str(self.scale)][typ]))

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
            self.clouds.append(Cloud(typ, self.img.image["cloud"][str(self.scale)][typ]))
            self.clouds[i-1].xpos = random.randint(0,SCRW)
            self.clouds[i-1].ypos = random.randint(0, SCRH)

    def draw_gradient(self):
        step = 100
        if self.chaos.actions[self.chaos.action] == "rgb":
            colA = self.rgb.get()
            for _ in range(20):
                self.rgb.tick()
            colB = self.rgb.get()
        else:
            colA = self.misc.bgCol[0]
            colB = self.misc.bgCol[1]


        for i in range(step):
            drawCol = [colA[0]+(i*((colB[0]-colA[0])/step)),
                       colA[1]+(i*((colB[1]-colA[1])/step)),
                       colA[2]+(i*(colB[2]-colA[2])/step)]
            pygame.draw.rect(SCREEN,drawCol,(0,i*(SCRH/step),SCRW,step))

    def trigger_death(self):
        #print("death triggered")
        self.animations.append(Death_Particle(self.player.xpos,self.player.ypos+14,self.player.colour))
        self.enableMovement = False
        self.stats.deaths += 1

        #self.player.xvel = 0
        #self.player.yvel = 0
                
        #if not self.contains_animation("death"):

    def reset_player(self):
        #self.log(f"{now()}\nplayer reset")
        #self.log(f"Before: Player pos {(self.player.xpos,self.player.ypos)}\n"
        #      f"Game spawnpoints {self.spawnPoint}")
        spawn = self.spawnPoint
        self.player.xpos,self.player.ypos = self.spawnPoint[0]+20,self.spawnPoint[1]+20
        self.update_level(next=False) # lazy, only need to change entity positions
        # this line is possibly what causes the nuclear ray glitch
        self.spawnPoint = spawn
        self.player.wallData = [False,False,False,False,False]
        self.player.isDead = False
        self.player.atFinish = False
        self.enableMovement = True
        self.restart = False
        self.player.collideTop = None
        self.player.collideBottom = None
        self.player.collideLeft = None
        self.player.collideRight = None
        self.player.collideWhole = None
        self.player.floorMaterial = None
        #self.log(f"After: Player pos {(self.player.xpos, self.player.ypos)}\n"
        #      f"Game spawnpoints {self.spawnPoint}")

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

    def load_stats(self):
        with open("stats.json","r") as file:
            info = json.load(file)
            for what in ["enemiesKilled","playTime","deaths","hidden1",
                         "bossesKilled"]:
                if what not in info:
                    info[what] = 0

            if "stars" not in info:
                info["stars"] = {}
            if "fallen" not in info:
                info["fallen"] = False

            self.stats.stars = info["stars"]
            self.stats.enemiesKilled = info["enemiesKilled"]
            self.stats.startTime = info["playTime"]
            self.stats.playTime = self.stats.startTime
            self.stats.deaths = info["deaths"]
            self.stats.hidden1progress = info["hidden1"]
            self.stats.bossesKilled = info["bossesKilled"]
            self.stats.fallen = info["fallen"]

        for _ in range(3):
            self.check_achievements(announce=False)
            # get all the achievements from stats
            # file loaded without all the notifications
            # do this twice so self.lastAchievements and
            # self.achievements are the same

    def save_stats(self):
        with open("stats.json", "w") as file:
            info = {}
            info["stars"] = self.stats.stars
            info["enemiesKilled"] = self.stats.enemiesKilled
            info["playTime"] = self.stats.playTime
            info["deaths"] = self.stats.deaths
            info["hidden1"] = self.stats.hidden1progress
            info["bossesKilled"] = self.stats.bossesKilled
            info["fallen"] = self.achievements.achievements["fall1"]
            file.write(json.dumps(info))

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

    def tick_bombs(self):
        for i in range(len(self.bombs)):
            dists = []
            for which in [self.bossEntities, self.enemyEntities, [self.player]]:
                for mob in which:
                    dists.append(self.get_dist(self.bombs[i],(mob.xpos,mob.ypos)))
            #print(f"bomb at {self.bombs[i]} state {self.bombStates[i][0]}")

            if min(dists) < self.misc.bombRadius and self.bombStates[i][0] == 0:
                self.bombStates[i][0] = 1
                self.bombStates[i][1] = now()

            if now() - self.bombStates[i][1] > self.misc.bombFuse and self.bombStates[i][0] == 1:
                # blow up
                self.bombStates[i][0] = 2
                bomb = self.bombs[i]
                self.animations.append(Bomb_Particle(bomb[0],bomb[1]))
                self.sound.start_bomb()
                if self.get_dist(self.bombs[i],(self.player.xpos,self.player.ypos)) < self.misc.bombRadius:
                    self.player.isDead = True
                for mob in self.enemyEntities:
                    #print(f"[{mob.xpos},{mob.ypos}] to {self.bombs[i]} is {self.get_dist(self.bombs[i],(mob.xpos,mob.ypos))}")
                    if self.get_dist(self.bombs[i],(mob.xpos,mob.ypos)) < self.misc.bombRadius:
                        mob.needsDel = True
                        #print(f"tried to kill entity at {mob.center}")
                for mob in self.bossEntities:
                    if self.get_dist(self.bombs[i],(mob.xpos,mob.ypos)) < self.misc.bombRadius:
                        mob.health -= self.misc.bombDamage

                #for item in self.entities:
                    #print(f"entitiy at {item.center}: {item.needsDel}")

    def tick_enemies(self):
        eToDel = []
        for mob in self.enemyEntities:
            if not mob.needsDel:
                mob.fix_center()
                mob.tick()
                mob.update_hitboxes()
                mob.draw()
                mob.update_target((self.player.xpos,self.player.ypos))
                mob.pathfind()
            else:
                eToDel.append(mob)

        jToDel = []
        for mob in self.jumpingEnemyEntities:
            if not mob.needsDel:
                mob.fix_center()
                mob.draw()
                mob.update_target((self.player.xpos,self.player.ypos))
                # mob.check_vision() handled in game.tick()
                mob.pathfind()
                mob.tick()
                mob.update_hitboxes()
            else:
                jToDel.append(mob)

        bToDel = []
        for mob in self.bossEntities:
            #print(mob.get_dist(mob.target)<mob.maxTargetDist)
            if mob.health <= 0:
                mob.needsDel = True
            if mob.needsDel:
                bToDel.append(mob)
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
                self.animations.append(Charge_Up(mob.xpos-(mob.width//2), mob.ypos - (mob.height+100)))
            elif mob.state == 3 and mob.firing:
                mob.projectiles.append(Boss_Projectile(mob.xpos-(mob.width//2),mob.ypos-(mob.height+100),mob.target))
                self.sound.boss_fire()

            for item in mob.projectiles:
                item.target = mob.target
                if pygame.Rect.colliderect(self.player.hitbox.whole, toRect((item.xpos, item.ypos, 30, 30))):
                    if self.settings.annoyingBosses:
                        self.end()
                    else:
                        self.player.isDead = True
                        #self.trigger_death(die=True)
                for plat in self.platforms:
                    if pygame.Rect.colliderect(toRect(plat),toRect((item.xpos,item.ypos,30,30))):
                        item.needsDel = True

        if len(eToDel) != 0 or len(bToDel) != 0:
            self.sound.start_death()

        for mob in eToDel:
            self.stats.enemiesKilled += 1
            self.animations.append(Impact_Particle(mob.xpos, mob.ypos + 14, colour.red))
            self.enemyEntities.remove(mob)
        for mob in jToDel:
            self.stats.enemiesKilled += 1
            self.animations.append(Impact_Particle(mob.xpos, mob.ypos + 14, colour.red))
            self.jumpingEnemyEntities.remove(mob)
        for mob in bToDel:
            self.stats.enemiesKilled += 1
            self.stats.bossesKilled += 1
            self.bossEntities.remove(mob)

    def tick_player(self):
##        self.player.wallData = self.player.check()
        self.player.lastIsDead = self.player.isDead
        self.player.lastYvel = self.player.yvel

        if self.player.yvel > 20:
            self.sound.start_fall()
        else:
            pass
            #handled in correct_mobs
        
        if not self.player.wallData[0]:
            if abs(self.player.yvel) > self.player.maxYvel:
                self.player.yvel = self.player.maxYvel
                
            self.player.yvel += self.player.gravity
        else:
            self.player.yvel = 0

        if self.player.floorMaterial == "ice":
            self.player.xInc = 0.2
        else:
            self.player.xInc = 1
            
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
            if self.player.floorMaterial == "ice":
                self.player.xvel = self.player.xvel * 0.95
            else:
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
                    self.sound.start_jump()
            if self.player.wallData[1] and self.player.floorMaterial != "ice":
                self.player.yvel = -20
                self.player.xvel = 10
                self.sound.start_jump()
            if self.player.wallData[2] and self.player.floorMaterial != "ice":
                self.player.yvel = -20
                self.player.xvel = -10
                self.sound.start_jump()
            if self.player.wallData[2] and self.player.wallData[1]:
                self.player.xvel = 0
            if self.player.wallData[3]:
                self.yvel = 0

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
        self.tick_bombs()

        self.misc.wasTransition = self.misc.hasTransition
        self.misc.hasTransition = self.contains_animation("transition")

        if self.restart:
            self.player.isDead = True
            #self.trigger_death(die=False)

        if self.player.isDead and not self.contains_animation("death"):
            if self.enableMovement:
                self.sound.start_death()
                self.trigger_death() # has just died
            else:
                self.reset_player() # has finished animation
                #print("finished death")

        if self.contains_animation("death"):
            self.enableMovement = False
            self.player.move = [False,False,False,False]
            if self.player.ypos < 5000:
                self.player.yvel = -self.player.gravity
        else:
            self.enableMovement = True

        self.player.wallData = [False,False,False,False,False]
        self.player.hitbox.clear()
        for mob in self.enemyEntities:
            mob.wallData = [False,False,False,False,False]
            mob.hitbox.clear()
        for mob in self.bossEntities:
            mob.wallData = [False,False,False,False,False]
            mob.hitbox.clear()
        for mob in self.jumpingEnemyEntities:
            mob.wallData = [False,False,False,False,False]
            mob.hitbox.clear()

        for item in self.platforms:
            compItem = toRect(get_actual_pos(item))
            for which in [self.bossEntities, self.enemyEntities, self.jumpingEnemyEntities, [self.player]]:
                for mob in which:
                    if pygame.Rect.colliderect(mob.hitbox.actBottom,compItem):
                        mob.wallData[0] = True
                        mob.hitbox.collideBottom = item
                        mob.floorMaterial = "platform"
                        #print("yup")
                    if pygame.Rect.colliderect(mob.hitbox.actLeft,compItem):
                        mob.wallData[1] = True
                        mob.hitbox.collideLeft = item
                    if pygame.Rect.colliderect(mob.hitbox.actRight,compItem):
                        mob.wallData[2] = True
                        mob.hitbox.collideRight = item
                    if pygame.Rect.colliderect(mob.hitbox.actTop,compItem):
                        mob.wallData[3] = True
                        mob.hitbox.collideTop = item
                    if pygame.Rect.colliderect(mob.hitbox.actWhole,compItem):
                        mob.wallData[4] = True
                        mob.hitbox.collideWhole = item
                        mob.floorMaterial = "platform"

        for item in self.ice:
            compItem = toRect(get_actual_pos(item))
            for which in [self.bossEntities, self.enemyEntities, [self.player]]:
                for mob in which:
                    if pygame.Rect.colliderect(mob.hitbox.actBottom,compItem):
                        mob.wallData[0] = True
                        mob.hitbox.collideBottom = item
                        mob.floorMaterial = "ice"
                        #print("yup")
                    if pygame.Rect.colliderect(mob.hitbox.actLeft,compItem):
                        mob.wallData[1] = True
                        mob.hitbox.collideLeft = item
                    if pygame.Rect.colliderect(mob.hitbox.actRight,compItem):
                        mob.wallData[2] = True
                        mob.hitbox.collideRight = item
                    if pygame.Rect.colliderect(mob.hitbox.actTop,compItem):
                        mob.wallData[3] = True
                        mob.hitbox.collideTop = item
                    if pygame.Rect.colliderect(mob.hitbox.actWhole,compItem):
                        mob.wallData[4] = True
                        mob.hitbox.collideWhole = item
                        mob.floorMaterial = "ice"

        for i in range(len(self.disappearingPlatforms)):
            plat = self.disappearingPlatforms[i]
            compItem = toRect(get_actual_pos(plat))
            if not self.buttonPresses[self.disappearingPlatformLinks[i]]:
                for which in [self.bossEntities, self.enemyEntities, self.jumpingEnemyEntities,[self.player]]:
                    for mob in which:
                        if pygame.Rect.colliderect(mob.hitbox.actBottom, compItem):
                            mob.wallData[0] = True
                            mob.hitbox.collideBottom = plat
                            # print("yup")
                        if pygame.Rect.colliderect(mob.hitbox.actLeft, compItem):
                            mob.wallData[1] = True
                            mob.hitbox.collideLeft = plat
                        if pygame.Rect.colliderect(mob.hitbox.actRight, compItem):
                            mob.wallData[2] = True
                            mob.hitbox.collideRight = plat
                        if pygame.Rect.colliderect(mob.hitbox.actTop, compItem):
                            mob.wallData[3] = True
                            mob.hitbox.collideTop = plat
                        if pygame.Rect.colliderect(mob.hitbox.actWhole, compItem):
                            mob.wallData[4] = True
                            mob.hitbox.collideWhole = plat

        for i in range(len(self.appearingPlatforms)):
            plat = self.appearingPlatforms[i]
            compItem = toRect(get_actual_pos(plat))
            if self.buttonPresses[self.appearingPlatformLinks[i]]:
                for which in [self.bossEntities, self.enemyEntities, self.jumpingEnemyEntities, [self.player]]:
                    for mob in which:
                        if pygame.Rect.colliderect(mob.hitbox.actBottom, compItem):
                            mob.wallData[0] = True
                            mob.hitbox.collideBottom = plat
                            # print("yup")
                        if pygame.Rect.colliderect(mob.hitbox.actLeft, compItem):
                            mob.wallData[1] = True
                            mob.hitbox.collideLeft = plat
                        if pygame.Rect.colliderect(mob.hitbox.actRight, compItem):
                            mob.wallData[2] = True
                            mob.hitbox.collideRight = plat
                        if pygame.Rect.colliderect(mob.hitbox.actTop, compItem):
                            mob.wallData[3] = True
                            mob.hitbox.collideTop = plat
                        if pygame.Rect.colliderect(mob.hitbox.actWhole, compItem):
                            mob.wallData[4] = True
                            mob.hitbox.collideWhole = plat

        spikeRects = []
        for item in self.spikes:
            orn = self.spikeDir[self.spikes.index(item)]
            actualSpike = spike_convert(item,orn)
            spike = toRect(get_actual_pos(actualSpike))
            spikeRects.append(actualSpike)
            if pygame.Rect.colliderect(self.player.hitbox.actWhole,spike):
                self.player.isDead = True
                #self.trigger_death()
                break

            for which in [self.enemyEntities,self.jumpingEnemyEntities]:
                for mob in which:
                    if pygame.Rect.colliderect(mob.hitbox.actWhole,spike):
                        mob.needsDel = True

            for mob in self.bossEntities:
                if pygame.Rect.colliderect(mob.hitbox.actWhole,spike):
                    mob.health -= 1
                    if not self.contains_animation("code particle"):
                        self.animations.append(Code_Particle(mob.xpos - 250 + random.randint(-100, 100), mob.ypos + 14, self.img.image["code"]))

        for mob in self.jumpingEnemyEntities:
            if not mob.needsDel:
                mob.check_vision(spikeRects)

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

        fan = False
        for item in self.fanColumns:
            newItem = [item[0],item[1],50,50]
            if pygame.Rect.colliderect(self.player.hitbox.actWhole,toRect(get_actual_pos(newItem))):
                self.sound.start_fan()
                if self.player.yvel >= -10:
                    self.player.yvel -= 0.5 + self.player.gravity
                #if self.player.wallData[0]:
                #    self.player.yvel = -1
##                    self.player.ypos -= 10
                fan = True
                break
        if not fan:
            self.sound.end_fan()

        end = self.data[str(self.levelIDX)]["end"]
        if pygame.Rect.colliderect(self.player.hitbox.actWhole,
                    toRect(get_actual_pos([end[0],end[1],50,50]))):
            self.player.atFinish = True

        for which in [self.bossEntities, self.enemyEntities, self.jumpingEnemyEntities]:
            for mob in which:
                if pygame.Rect.colliderect(mob.hitbox.actWhole,self.player.hitbox.actWhole):
                    self.player.isDead = True
                    #self.trigger_death()
                    if which == self.bossEntities and self.settings.annoyingBosses:
                        self.end()

        for item in self.buttons:
            press = []
            for which in [self.bossEntities, self.enemyEntities, [self.player]]:
                for mob in which:
                    press.append(pygame.Rect.colliderect(mob.hitbox.actWhole,get_actual_pos((item[0],item[1],50,50))))

            if (True in press):
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

    def correct_mobs(self):
        #print(self.player.yvel)
        if self.player.wallData[3] and self.player.yvel < 0:# and not self.player.wallData[0]: # top only
            self.player.wallData[1] = False
            self.player.wallData[2] = False # stop wall jumping
            self.player.yvel = 0
            #self.player.ypos = ((self.player.ypos//50)*50) + (self.player.height//2) + 10
            self.player.ypos = (self.player.hitbox.collideTop[1] + self.player.hitbox.collideTop[3] + (self.player.height//2))
            # BEHOLD THE BANE OF MY EXISTENCE ^

        if self.player.wallData[3] and self.player.yvel > 0:  # if clipping through ground
            #self.player.ypos -= 50
            self.player.yvel = 0

        if self.player.wallData[0] and self.player.yvel == 0:
            self.player.ypos = ((self.player.ypos // 50) * 50) + (self.player.height//2) + 11
            if self.player.wallData[3]:
                self.player.ypos -= 50
            #self.player.ypos = self.player.hitbox.collideBottom[1] - self.player.height//2 +1
            # the top of the platform it is colliding with
            self.player.onFloor = True
            if self.player.lastYvel != 0: # if just landed
                self.animations.append(Impact_Particle(self.player.xpos,self.player.ypos+14,colour.darkgrey))
                self.sound.end_fall()

        for which in [self.enemyEntities, self.jumpingEnemyEntities]:
            for enemy in which:
                if enemy.wallData[0] and enemy.yvel == 0:
                    enemy.onFloor = True
                    enemy.ypos = enemy.hitbox.collideBottom[1] - enemy.height//2 -9
                    if enemy.lastYvel != 0:
                        self.animations.append(Impact_Particle(enemy.xpos,enemy.ypos+14,colour.darkgrey))

        for enemy in self.bossEntities:
            if enemy.wallData[0]:# and enemy.yvel == 0:
                enemy.ypos = enemy.hitbox.collideBottom[1] +1
                if enemy.lastYvel != 0:
                    self.animations.append(Impact_Particle(enemy.xpos,enemy.ypos+10,colour.darkgrey))

        #print(f"player ypos: {self.player.ypos}, yvel: {self.player.yvel}")

    def update_level(self,next=False):
        #print("level updated")
        if next:
            self.levelIDX += 1

        self.platforms = []    
        self.spikes = []
        self.fanBases = []
        self.fanColumns = []
        self.stars = []
        self.enemies = []
        self.enemyEntities = []
        self.jumpingEnemies = []
        self.jumpingEnemyEntities = []
        self.checkpoints = []
        self.bosses = []
        self.bossEntities = []
        self.buttons = []
        self.buttonPresses = []
        self.disappearingPlatforms = []
        self.disappearingPlatformLinks = []
        self.appearingPlatforms = []
        self.appearingPlatformLinks = []
        self.bombs = []
        self.bombStates = []
        self.ice = []
        self.iceStates = []

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
            if "jumping mobs" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["jumping mobs"] = []
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
            if "bombs" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["bombs"] = []
            if "ice" not in self.data[str(self.levelIDX)]:
                self.data[str(self.levelIDX)]["ice"] = []

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
                "jumping mobs":[],
                "checkpoints":[],
                "bosses":[],
                "buttons":[],
                "disappearing platforms":[],
                "disappearing platform links": [],
                "appearing platforms": [],
                "appearing platform links":[],
                "bombs":[],
                "ice":[]}

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
            self.enemies.append([item[0], item[1]])
            self.enemyEntities.append(Enemy(item[0] + 20, item[1], img=self.img.image["enemy_body"], maxXvel=random.randint(4, 6)))
        for item in self.data[str(self.levelIDX)]["jumping mobs"]:
            self.jumpingEnemies.append([item[0], item[1]])
            self.jumpingEnemyEntities.append(
                Jumping_Enemy(item[0] + 20, item[1], img=[self.img.image["jumping_enemy_body"],self.img.image["jumping_enemy_body_air"]], maxXvel=random.randint(4, 6)))
        for item in self.data[str(self.levelIDX)]["checkpoints"]:
            self.checkpoints.append([item[0],item[1]])
        for item in self.data[str(self.levelIDX)]["bosses"]:
            self.bosses.append([item[0]+50,item[1]+50])
            health = 600 if not self.settings.annoyingBosses else 6000
            self.bossEntities.append(Boss(item[0]+50,item[1]+50,img=self.img.image["boss_img"],health=health))
        for item in self.data[str(self.levelIDX)]["buttons"]:
            self.buttons.append([item[0],item[1]])
            self.buttonPresses.append(False)
        for item in self.data[str(self.levelIDX)]["bombs"]:
            self.bombs.append(item)
            self.bombStates.append([0,0])
        for item in self.data[str(self.levelIDX)]["ice"]:
            self.ice.append(item)
            self.iceStates.append(False)
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
        if now() - self.misc.lastFanChange > self.misc.fanInterval:
            self.misc.fanState += 1
            if self.misc.fanState >= len(self.img.image["fan_column"]):
                self.misc.fanState = 0
            self.misc.lastFanChange = now()

        # why tf am I getting everything from the json I have them stored in lists whyyyy
        blitToCam(self.img.image["finish"], self.data[str(self.levelIDX)]["end"])  # VERY INEFFICIENT FIX ME
        for item in self.data[str(self.levelIDX)]["platforms"]:
            sendPlatformToCam(item,self.settings.highResTextures,col=self.misc.platformCol,platType="normal")
        for i in range(len(self.data[str(self.levelIDX)]["spikes"])):
            #print(f"len of spikes {len(self.data[str(self.levelIDX)]["spikes"])}\nlen of spikeDir {len(self.spikeDir)}")
            sendSpikeToCam(self.data[str(self.levelIDX)]["spikes"][i-1],orn=self.spikeDir[i-1])
        #for item in self.spikes:
        #    orn = self.spikeDir[self.spikes.index(item)]
        #    sendToCam(spike_convert(item,orn),"hitbox")
        for item in self.data[str(self.levelIDX)]["fan bases"]:
            blitToCam(self.img.image["fan_base"][self.misc.fanState],item)
        for item in self.data[str(self.levelIDX)]["fan columns"]:
            blitToCam(self.img.image["fan_column"][self.misc.fanState],item)
        for item in self.data[str(self.levelIDX)]["stars"]:
            if self.scene == "editor":
                blitToCam(self.img.image["star"],item)
            if item not in self.stats.stars[str(self.levelIDX)]:
                blitToCam(self.img.image["star"],item)
        for item in self.data[str(self.levelIDX)]["checkpoints"]:
            if item == self.spawnPoint:
                blitToCam(self.img.image["checkpoint_on"],item)
            else:
                blitToCam(self.img.image["checkpoint_off"],item)
        for i in range(len(self.ice)):
            if not self.iceStates[i]:
                sendPlatformToCam(self.ice[i],self.settings.highResTextures,col=self.misc.platformCol,platType="ice")


        if self.scene == "ingame":
            for item in self.data[str(self.levelIDX)]["buttons"]:
                if self.buttonPresses[self.data[str(self.levelIDX)]["buttons"].index(item)]:
                    blitToCam(self.img.image["button_pressed"], item)
                else:
                    blitToCam(self.img.image["button_unpressed"], item)

            for item in self.data[str(self.levelIDX)]["disappearing platforms"]:
                plat = self.data[str(self.levelIDX)]["disappearing platforms"].index(item) #index of platform
                idx = self.disappearingPlatformLinks[plat] # get which button it is linked to
                #print(f"idx {idx}")
                if idx != -1:
                    if not self.buttonPresses[idx]:
                        sendPlatformToCam(item,self.settings.highResTextures,col=(0,25,80),platType="disappearing")

            for item in self.data[str(self.levelIDX)]["appearing platforms"]:
                plat = self.data[str(self.levelIDX)]["appearing platforms"].index(item)
                idx = self.appearingPlatformLinks[plat]
                if idx != -1:
                    if self.buttonPresses[idx]:
                        sendPlatformToCam(item,self.settings.highResTextures,col=(100,150,221),platType="appearing")

            for i in range(len(self.bombs)):
                if self.bombStates[i][0] == 0:
                    blitToCam(self.img.image["bomb"],self.bombs[i])
                elif self.bombStates[i][0] == 1:
                    pos = [self.bombs[i][0]+random.randint(-5,5),self.bombs[i][1]+random.randint(-5,5)]
                    blitToCam(self.img.image["bomb_lit"],pos)
            
        if self.scene == "editor":
            for item in self.data[str(self.levelIDX)]["mobs"]:
                blitToCam(self.img.image["enemy_for_editor"],(item[0]+5,item[1]+5))

            for item in self.data[str(self.levelIDX)]["jumping mobs"]:
                blitToCam(self.img.image["jumping_enemy_for_editor"],(item[0]+5,item[1]+5))

            for item in self.data[str(self.levelIDX)]["bosses"]:
                blitToCam(self.img.image["boss_img"],(item[0]-200,item[1]-200))

            for item in self.data[str(self.levelIDX)]["buttons"]:
                blitToCam(self.img.image["button_unpressed"], item)

            for item in self.data[str(self.levelIDX)]["disappearing platforms"]:
                sendPlatformToCam(item,self.settings.highResTextures,platType="disappearing")#, col=[80,80,100])

            for item in self.data[str(self.levelIDX)]["appearing platforms"]:
                sendPlatformToCam(item,self.settings.highResTextures,platType="appearing")#, col=[180,180,200])

            for item in self.bombs:
                blitToCam(self.img.image["bomb"],item)

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

        SCREEN.blit(self.img.image["link"],(SCRW-100,SCRH-100))
        # link image
        pygame.draw.rect(SCREEN,colour.darkgrey,(10,30+scr,50,10))
        # platform icon
        pygame.draw.polygon(SCREEN,colour.red,((30,110+scr),(40,110+scr),(35,80+scr)))
        # spike icon
        SCREEN.blit(self.img.image["finish"],(3,125+scr))
        # finish
        SCREEN.blit(self.img.image["fan_base"][1],(10,180+scr))
        # fan base image
        SCREEN.blit(self.img.image["fan_column"][0],(10,245+scr))
        # fan column
        SCREEN.blit(self.img.image["star"],(10,305+scr))
        # fan column
        SCREEN.blit(self.img.image["enemy_for_editor"],(15,370+scr))
        # enemy
        SCREEN.blit(self.img.image["jumping_enemy_for_editor"],(15,430+scr))
        # enemy
        SCREEN.blit(self.img.image["checkpoint_on"],(10,485+scr))
        # checkpoint
        SCREEN.blit(self.img.image["boss_menu"],(10,545+scr))
        # boss
        SCREEN.blit(self.img.image["button_unpressed"], (10, 600+scr))
        # button
        pygame.draw.rect(SCREEN, colour.darkgrey, (10, 685 + scr, 50, 10))
        # platform icon
        pygame.draw.rect(SCREEN, colour.darkgrey, (10, 745 + scr, 50, 10))
        # platform icon
        SCREEN.blit(self.img.image["bomb_lit"],(10,785+scr))
        #bomb
        SCREEN.blit(self.img.image["ice"],(10,845+scr))
        # ice

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
            #self.trigger_death(die=False)
            self.player.xpos,self.player.ypos = 0,0
            self.restart = False

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
            self.run_button_boxes()
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
            if self.editor.selected in ["platform","disappearing platform","appearing platform","ice"]:
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
                        elif self.editor.selected == "ice":
                            self.data[str(self.levelIDX)]["ice"].append(self.editor.pendingRect)

                    self.editor.pendingRect = [0,0,0,0]
                    self.update_level(next=False)

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
                    elif self.editor.selected == "ice":
                        which = "ice"

                    for item in self.data[str(self.levelIDX)][which]:
                        if pygame.Rect.colliderect(toRect(newMouseRect),toRect(item)):
                            try:
                                self.data[str(self.levelIDX)][which].remove(item)
                                idx = self.data[str(self.levelIDX)][which].index(item)
                                infoList.pop(idx)
                            except:
                                pass
                    self.update_level(next=False)
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

                    elif self.editor.selected == "jumping enemy":
                        self.data[str(self.levelIDX)]["jumping mobs"].append(truncPos)

                    elif self.editor.selected == "checkpoint":
                        self.data[str(self.levelIDX)]["checkpoints"].append(truncPos)

                    elif self.editor.selected == "boss":
                        self.data[str(self.levelIDX)]["bosses"].append(truncPos)

                    elif self.editor.selected == "button":
                        self.data[str(self.levelIDX)]["buttons"].append(truncPos)

                    elif self.editor.selected == "bomb":
                        self.data[str(self.levelIDX)]["bombs"].append(truncPos)

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

                    for item in self.enemies:
                        if pygame.Rect.colliderect(toRect(newMouseRect),toRect([item[0],item[1],50,50])):
                            self.data[str(self.levelIDX)]["mobs"].remove(item)
                            self.enemies.remove(item)

                    for item in self.jumpingEnemies:
                        if pygame.Rect.colliderect(toRect(newMouseRect),toRect([item[0],item[1],50,50])):
                            self.data[str(self.levelIDX)]["jumping mobs"].remove(item)
                            self.jumpingEnemies.remove(item)

                    for item in self.checkpoints:
                        if pygame.Rect.colliderect(toRect(newMouseRect),toRect([item[0],item[1],50,50])):
                            self.data[str(self.levelIDX)]["checkpoints"].remove(item)
                            self.checkpoints.remove(item)

                    for item in self.bosses:
                        if pygame.Rect.colliderect(toRect(newMouseRect),toRect([item[0]-50,item[1]-50,50,50])):
                            self.data[str(self.levelIDX)]["bosses"].remove([item[0]-50,item[1]-50])
                            self.bosses.remove(item)

                    for item in self.buttons:
                        if pygame.Rect.colliderect(toRect(newMouseRect),toRect([item[0],item[1],50,50])):
                            self.data[str(self.levelIDX)]["buttons"].remove(item)
                            self.buttons.remove(item)

                    for item in self.bombs:
                        if pygame.Rect.colliderect(toRect(newMouseRect),toRect([item[0],item[1],50,50])):
                            self.data[str(self.levelIDX)]["bombs"].remove(item)

                    self.update_level(next=False)

    def run_button_boxes(self):
        if len(self.buttons) != 0 and len(self.editor.buttonIndexBoxes) == 0:
            # need to make the boxes
            self.editor.buttonIndexBoxes = []
            for i in range(len(self.buttons)):
                pos = (self.buttons[i][0],self.buttons[i][1])
                newBox = u.old_textbox(f" {i+1} ",font18,pos)
                #print(f"tried {pos} {type(pos)}")
                #newBox.pos = pos
                self.editor.buttonIndexBoxes.append(newBox)

        for box in self.editor.buttonIndexBoxes:
            rawPos = get_screen_pos(toRect(box.pos))
            pos = (rawPos[0]+25,rawPos[1]+10)
            boxCopy = u.old_textbox(box.message,font18,pos)
            boxCopy.display()

    def get_dist(self,pos1,pos2):
        return math.sqrt((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)

    def save_asthetics(self,col,hatIDX=-1):
        #self.player.hat = hatIDX
        self.player.colour = col
        if self.player.img is not None:
            self.player.img.lock()
            oldCol = self.player.img.get_at((20,20))
            for x in range(self.player.img.get_width()):
                for y in range(self.player.img.get_height()):
                    if self.player.img.get_at((x,y)) == oldCol:
                        self.player.img.set_at((x,y),col)

            self.player.img.unlock()

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
        self.buttonIndexBoxes = [] # a QOL feature to show the index of
        # a button when in link mode in editor

        self.linkRect = u.Pressable(SCRW-100,SCRH-100,70,70)
        self.originalItemRects = []
        self.itemRects = []
        self.ref = ["platform","spike","end","fan base",
                    "fan column","star","enemy", "jumping enemy",
                    "checkpoint","boss","button","disappearing platform",
                    "appearing platform","bomb","ice"]

        for i in range(50):
            y = i*60
            self.originalItemRects.append((10,y+5,50,50))
            self.itemRects.append((10, y + 5, 50, 50))

class Mob_Hitbox:
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

        self.collideWhole = None
        self.collideTop = None
        self.collideBottom = None
        self.collideLeft = None
        self.collideRight = None

    def clear(self):
        self.collideWhole = None
        self.collideTop = None
        self.collideBottom = None
        self.collideLeft = None
        self.collideRight = None
        self.floorMaterial = "air"

class Physics_Object:
    def __init__(self,xpos,ypos,gravity=0.981,maxXvel=10,maxYvel=30):
        self.xpos = xpos
        self.ypos = ypos
        self.gravity = gravity
        self.maxXvel = maxXvel
        self.maxYvel = maxYvel
        self.xvel = 0
        self.yvel = 0
        self.floorMaterial = None
        self.onFloor = False

class Player(Physics_Object):
    def __init__(self,gravity,maxXvel=10,maxYvel=30,img=None):
        super().__init__(0,0,gravity,maxXvel,maxYvel)
        #self.xpos = 0
        #self.ypos = 0
        #self.xvel = 0
        #self.yvel = 0
        self.lastYvel = 0
        #self.maxYvel = maxYvel
        #self.maxXvel = maxXvel
        self.img = img
        self.xInc = 1
        #self.gravity = gravity
        self.isDead = False
        self.lastIsDead = False
        self.atFinish = False
        self.width = 0
        self.height = 0
        self.lastBlink = 0
        self.isBlinking = False
        self.blinkWait = random.randint(3,6) * 1000
        self.move = [False,False,False,False]
        self.wallData = [False,False,False,False,False]
        self.hat = -1
        self.hitbox = Mob_Hitbox()
        try:
            self.update_image(self.img)
        except:
            self.width = 20
            self.height = 20

        if self.img == None:
            self.colour = (0,141,201)
        else:
            self.colour = self.img.get_at((20,20))
        #self.update_hitboxes()
        #self.rect = pygame.Rect(self.player.xpos-25,self.player.ypos-25,50,50)

    def draw(self):
##        self.colour = rgb.get()
##        rgb.tick()
        if self.img == None:
            pygame.draw.rect(SCREEN,self.colour,((SCRW//2)-20,(SCRH//2)-20,40,40))
        else:
            SCREEN.blit(self.img,((SCRW-self.width)//2,(SCRH-self.height)//2))
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

    def update_image(self,surf):
        self.img = surf
        self.width = self.img.get_width()
        self.height = self.img.get_height()

class Enemy(Physics_Object):
    def __init__(self,xpos,ypos,maxXvel=5,maxYvel=30,gravity=0.981,img=None):
        super().__init__(xpos,ypos,gravity,maxXvel,maxYvel)
        #self.xpos = xpos
        #self.ypos = ypos
        self.center = [self.xpos,self.ypos]
        #self.xvel = 0
        #self.yvel = 0
        self.lastYvel = 0
        self.xInc = 1
        #self.maxXvel = maxXvel
        #self.maxYvel = maxYvel
        #self.gravity = gravity
        self.target = [0,0]
        self.maxTargetDist = 500
        self.canSeeTarget = False
        self.img = img
        self.needsDel = False
        self.wallData = [False,False,False,False,False]
        self.hitbox = Mob_Hitbox()
        self.width = 0
        self.height = 0

        try:
            self.update_image(self.img)
        except:
            self.width = 20
            self.height = 20

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
        blitToCam(self.img,(self.xpos-self.width//2,self.ypos-(self.height//2)+10))
        pygame.draw.circle(SCREEN,colour.white,((SCRW//2)-game.player.xpos+self.xpos,(SCRH//2)+5-game.player.ypos+self.ypos),10)
        if self.xvel == 0:        
                pygame.draw.circle(SCREEN,colour.black,(SCRW//2-game.player.xpos+self.xpos,(SCRH//2)+5-game.player.ypos+self.ypos),7)
                pygame.draw.circle(SCREEN,colour.white,((SCRW//2)+2-game.player.xpos+self.xpos,(SCRH//2)+6-game.player.ypos+self.ypos),2)
                pygame.draw.circle(SCREEN,colour.white,((SCRW//2)-game.player.xpos+self.xpos,(SCRH//2)+7-game.player.ypos+self.ypos),1)

        else:
            if self.xvel < 0:
                pygame.draw.circle(SCREEN,colour.black,((SCRW//2)-3-game.player.xpos+self.xpos,(SCRH//2)+5-game.player.ypos+self.ypos),7)
                pygame.draw.circle(SCREEN,colour.white,((SCRW//2)-1-game.player.xpos+self.xpos,(SCRH//2)+6-game.player.ypos+self.ypos),2)
                pygame.draw.circle(SCREEN,colour.white,((SCRW//2)-3-game.player.xpos+self.xpos,(SCRH//2)+7-game.player.ypos+self.ypos),1)
            elif self.xvel > 0:
                pygame.draw.circle(SCREEN,colour.black,((SCRW//2)+3-game.player.xpos+self.xpos,(SCRH//2)+5-game.player.ypos+self.ypos),7)
                pygame.draw.circle(SCREEN,colour.white,((SCRW//2)+5-game.player.xpos+self.xpos,(SCRH//2)+6-game.player.ypos+self.ypos),2)
                pygame.draw.circle(SCREEN,colour.white,((SCRW//2)+3-game.player.xpos+self.xpos,(SCRH//2)+7-game.player.ypos+self.ypos),1)

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
        if not (False in self.wallData):
            self.needsDel = True

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

    def update_image(self,surf):
        self.img = surf
        self.width = self.img.get_width()
        self.height = self.img.get_height()

class Jumping_Enemy(Enemy):
    def __init__(self,xpos,ypos,maxXvel=5,maxYvel=30,gravity=0.981,img=None):
        super().__init__(xpos,ypos,maxXvel,maxYvel,gravity,img)
        self.vision = [
            toRect(),
            toRect(),
            toRect(),
            toRect(),
            toRect()
        ]
        self.visionResults = [False,False,False,False,False]
        self.state = 0
        try:
            self.update_image(self.img)
        except:
            self.width = 20
            self.height = 20

    def fix_center(self):
        self.center = [self.xpos-self.width, self.ypos-self.height]

    def pathfind(self):
        self.state = 0 if self.onFloor else 1
        self.canSeeTarget = self.get_dist(self.target) < self.maxTargetDist
        if self.canSeeTarget:
            if self.target[0] > self.xpos:
                if self.visionResults[4]:  # left edge
                    self.xvel = 2
                    # if self.visionResults[1]:
                    #    self.xvel = 0
                else:
                    if self.visionResults[3] and self.onFloor:
                        self.yvel = -15
                        self.ypos -= 1
                        self.onFloor = False
                        #self.hitbox.collideBottom = False
                        self.hitbox.clear()
                        self.wallData[0] = False
                    else:
                        self.xvel += self.xInc

            elif self.target[0] < self.xpos:
                if self.visionResults[0]:  # left edge
                    self.xvel = -2
                    #if self.visionResults[1]:
                    #    self.xvel = 0
                else:
                    if self.visionResults[1] and self.onFloor:
                        self.yvel = -15
                        self.ypos -= 1
                        self.onFloor = False
                        #self.hitbox.collideBottom = False
                        self.hitbox.clear()
                        self.wallData[0] = False
                    else:
                        self.xvel -= self.xInc
        else:
            self.xvel = self.xvel * 0.8

    def check_vision(self,spikeList):
        for i in range(5):
            self.vision[i] = toRect([(self.center[0] + (50 * (i-2))), self.center[1] - 5, 40,40])

        self.visionResults = [False,False,False,False,False]
        for i in range(5):
            for spike in spikeList:
                if pygame.Rect.colliderect(self.vision[i],spike):
                    self.visionResults[i] = True
                    break

        #for i in range(5):
        #    col = colour.green if self.visionResults[i] else colour.red
        #    sendToCam(self.vision[i], "hitbox", col)

    def draw(self):
        blitToCam(self.img[self.state], self.center)
        xcorrect = self.center[0] + self.width
        ycorrect = self.center[1] + self.height - 4 - (self.state * 8)

        pygame.draw.circle(SCREEN, colour.white,
                           ((SCRW // 2) - game.player.xpos + xcorrect, (SCRH // 2) + 5 - game.player.ypos + ycorrect),
                           10)
        if self.xvel == 0:
            pygame.draw.circle(SCREEN, colour.black, (
            SCRW // 2 - game.player.xpos + xcorrect , (SCRH // 2) + 5 - game.player.ypos + ycorrect), 7)
            pygame.draw.circle(SCREEN, colour.white, (
            (SCRW // 2) + 2 - game.player.xpos + xcorrect, (SCRH // 2) + 6 - game.player.ypos + ycorrect), 2)
            pygame.draw.circle(SCREEN, colour.white, (
            (SCRW // 2) - game.player.xpos + xcorrect, (SCRH // 2) + 7 - game.player.ypos + ycorrect), 1)

        else:
            if self.xvel < 0:
                pygame.draw.circle(SCREEN, colour.black, (
                (SCRW // 2) - 3 - game.player.xpos + xcorrect, (SCRH // 2) + 5 - game.player.ypos + ycorrect), 7)
                pygame.draw.circle(SCREEN, colour.white, (
                (SCRW // 2) - 1 - game.player.xpos + xcorrect, (SCRH // 2) + 6 - game.player.ypos + ycorrect), 2)
                pygame.draw.circle(SCREEN, colour.white, (
                (SCRW // 2) - 3 - game.player.xpos + xcorrect, (SCRH // 2) + 7 - game.player.ypos + ycorrect), 1)
            elif self.xvel > 0:
                pygame.draw.circle(SCREEN, colour.black, (
                (SCRW // 2) + 3 - game.player.xpos + xcorrect, (SCRH // 2) + 5 - game.player.ypos + ycorrect), 7)
                pygame.draw.circle(SCREEN, colour.white, (
                (SCRW // 2) + 5 - game.player.xpos + xcorrect, (SCRH // 2) + 6 - game.player.ypos + ycorrect), 2)
                pygame.draw.circle(SCREEN, colour.white, (
                (SCRW // 2) + 3 - game.player.xpos + xcorrect, (SCRH // 2) + 7 - game.player.ypos + ycorrect), 1)

class Boss(Enemy):
    def __init__(self,xpos,ypos,img,maxXvel=6,maxYvel=50,health=600,gravity=0.981):
        super().__init__(xpos,ypos,maxXvel=maxXvel,maxYvel=maxYvel,gravity=0.981,img=img)
        self.maxHealth = health
        self.health = self.maxHealth
        self.hb = u.healthBar(0,0,self.maxHealth)
        self.hb.width = 150
        self.hb.height = 30
        self.maxTargetDist = 1000
        self.projectiles = []
        self.width = 0
        self.height = 0

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

        self.update_image(self.img)

    def draw(self):
        blitToCam(self.img,(self.xpos-self.width,self.ypos-self.height))
        self.hb.draw()

        #sendToCam(list(self.hitbox.bottom), "hitbox", col=colour.white)
        #sendToCam(list(self.hitbox.left),"hitbox",col=colour.white)
        #sendToCam(list(self.hitbox.right),"hitbox",col=colour.white)
        #sendToCam(list(self.hitbox.top),"hitbox",col=colour.white)
        #sendToCam(list(self.hitbox.whole),"hitbox",col=colour.white)

    def update_hitbox(self):
        pos = get_screen_pos((self.xpos, self.ypos,0,0))
        self.hb.hp = self.health
        self.hb.xpos = pos[0] - self.width + 50
        self.hb.ypos = pos[1] - self.height - 50

        self.hitbox.whole = toRect([self.xpos - self.width, self.ypos - self.height, self.width, self.height])
        self.hitbox.top = toRect([self.xpos - self.width, self.ypos - self.height, self.width, 10])
        self.hitbox.bottom = toRect([self.xpos - self.width, self.ypos, self.width, 10])
        self.hitbox.left = toRect([self.xpos - self.width, self.ypos - self.height, 10, self.height-5])
        self.hitbox.right = toRect([self.xpos - 10, self.ypos - self.height, 10, self.height-5])

        self.hitbox.actWhole = toRect(get_actual_pos([self.xpos - self.width, self.ypos - self.height, self.width, self.height]))
        self.hitbox.actTop = toRect(get_actual_pos([self.xpos - self.width, self.ypos - self.height, self.width, 10]))
        self.hitbox.actBottom = toRect(get_actual_pos([self.xpos - self.width, self.ypos, self.width, 10]))
        self.hitbox.actLeft = toRect(get_actual_pos([self.xpos - self.width, self.ypos - self.height, 10, self.height-5]))
        self.hitbox.actRight = toRect(get_actual_pos([self.xpos - 10, self.ypos - self.height, 10, self.height-5]))

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
        return math.sqrt((pos[0]-self.xpos-self.height//2)**2+(pos[1]-self.ypos)**2)

    def fix_center(self):
        self.center = [self.xpos-self.width//2, self.ypos]

    def tick_projectiles(self):
        toDel = []
        for item in self.projectiles:
            item.tick()
            if item.needsDel:
                toDel.append(item)

        for item in toDel:
            self.projectiles.remove(item)

    def update_image(self,surf):
        self.img = surf
        self.width = self.img.get_width()
        self.height = self.img.get_height()

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

class Bomb_Particle(Animation):
    def __init__(self,xpos,ypos):
        super().__init__(xpos,ypos)
        self.interval = 50
        self.name = "bomb"

    def draw(self):
        center = get_screen_pos((self.xpos+25,self.ypos+25))[:2]
        if self.frame == 1:
            pygame.draw.circle(SCREEN,(255, 255, 255),center,10)
        elif self.frame == 2:
            pygame.draw.circle(SCREEN, (255, 255, 150), center, 20)
        elif self.frame == 3:
            pygame.draw.circle(SCREEN, (255, 255, 50), center, 25)
        elif self.frame == 4:
            pygame.draw.circle(SCREEN, (255, 255, 0), center, 30)
        elif self.frame == 5:
            pygame.draw.circle(SCREEN, (255, 175, 0), center, 32)
        elif self.frame == 6:
            pygame.draw.circle(SCREEN, (255, 0, 0), center, 35)

        if self.frame > 6:
            self.finished = True

class Transition(Animation):
    def __init__(self):
        super().__init__(0,0)
        self.interval = 5
        self.name = "transition"
        self.amount = 20

    def draw(self):
        pygame.draw.rect(SCREEN,colour.black,(0,0,SCRW,self.frame*self.amount))
        if self.frame > SCRH//self.amount:
            self.finished = True

class Hat_Selector:
    def __init__(self,imgs):
        self.hats = []
        self.prices = []
        self.size = 60
        self.gap = 20
        for i in range(len(imgs)):
            maxsize = max(imgs[i].get_size())
            self.hats.append(pygame.transform.scale_by(imgs[i],(self.size/maxsize)))
        self.selected = -1
        self.rects = []
        self.pressables = []

        for i in range(len(self.hats)):
            self.pressables.append(u.Pressable(
                (SCRW * 0.7) - 5,
                (self.size + (i * (self.size + self.gap))) - 5,
                self.size + 10,
                self.size + 10, mode=2))

    def draw(self):
        for i in range(len(self.hats)):
            border = colour.red if i==self.selected else colour.darkgrey
            pygame.draw.rect(SCREEN, border,
                             ((SCRW * 0.7) - 5,
                              (self.size + (i * (self.size + self.gap))) - 5,
                              self.size + 10,
                              self.size + 10))
            pygame.draw.rect(SCREEN, colour.lightgrey,
                             (SCRW * 0.7,
                              (self.size + (i * (self.size + self.gap))),
                              self.size,
                              self.size))
            SCREEN.blit(self.hats[i],(SCRW*0.7,(10+self.size+(i*(self.size+self.gap)))))

    def check(self):
        for i in range(len(self.pressables)):
            if self.pressables[i].pressed():
                self.selected = i

##################################################


titleBox = u.old_textbox("PLATFORM GAME",fontTitle,(SCRW//2,150),backgroundCol=None,tags=["menu"])
startBox = u.old_textbox("PLAY",font28,(SCRW//2,400),oval=True,tags=["menu"])
menuBox = u.old_textbox("MENU",font18,(SCRW-35,20),oval=True,tags=["ingame","editor","levels","settings","achievements","credits","customise"])
editorBox = u.old_textbox("EDITOR",font18,(SCRW//2,500),oval=True,tags=["menu"])
levelsBox = u.old_textbox("LEVELS",font18,(SCRW//2,300),oval=True,tags=["menu"])
selectedBox = u.old_textbox("",font18,(SCRW//2,60),tags=["editor"])
coordBox = u.old_textbox("",font18,(SCRW//3,20),tags=["editor"])
levelIDXBox = u.old_textbox("",font18,(SCRW//2,20),tags=["ingame","editor"])
settingsBox = u.old_textbox("SETTINGS",font18,(SCRW*0.7,500),oval=True,tags=["menu"])
showFPSBox = u.old_textbox("Show FPS",font18,(SCRW*0.4,50),tags=["settings"])
FPSBox = u.old_textbox("FPS: -",font18,(SCRW-50,SCRH-50),tags=["ingame","editor","settings"])
statsTitleBox = u.old_textbox("Statistics",font28,(SCRW//2,300),tags=["settings"])
collectedStarsBox = u.old_textbox("Stars collectd: -",font18,(SCRW//2,400),tags=["settings"])
enemiesDefeatedBox = u.old_textbox("Enemies defeated: -",font18,(SCRW//2,450),tags=["settings"])
deathCountBox = u.old_textbox("Number of deaths: -",font18,(SCRW//2,500),tags=["settings"])
uptimeBox = u.old_textbox("Time Played: -",font18,(SCRW//2,550),tags=["settings"])
resetStatsBox = u.old_textbox("RESET STATISTICS",font18,(SCRW//5,550),tags=["settings"],backgroundCol=colour.red,textCol=colour.black)
annoyingBossesBox = u.old_textbox("Annoyinger bosses",font18,(SCRW//2,150),tags=["settings"])
soundBox = u.old_textbox("Sound",font18,(SCRW//2,100),tags=["settings"])
highResTexturesBox = u.old_textbox("Fancy Textures",font18,(SCRW*0.6,200),tags=["settings"])
chaosModeBox = u.old_textbox("Chaos Mode",font18,(SCRW*0.4,200),tags=["settings"],backgroundCol=[100,0,0])
chaosModifierBox = u.old_textbox("-",font18,(SCRW*0.5,50),tags=["ingame"],backgroundCol=[0,0,0])
messageBox = u.old_textbox("-",font10,(SCRW*0.5,SCRH-25),tags=["menu"])
achievementBox = u.old_textbox("ACHIEVEMENTS",font18,(SCRW*0.3,500),oval=True,tags=["menu"])
achievementTitleBox = u.old_textbox("ACHIEVEMENTS",fontTitle,(SCRW//2,50),backgroundCol=None,tags=["achievements"])
creditsBox = u.old_textbox("Credits",font18,(SCRW*0.3,400),oval=True,tags=["menu"])
creditsTitleBox = u.old_textbox("CREDITS",fontTitle,(SCRW//2,100),backgroundCol=None,tags=["credits"])
credits1 = u.old_textbox("Developer: Scott Wilson",font18,(SCRW*0.5,200),tags=["credits"],backgroundCol=None)
credits2 = u.old_textbox("Idea by: Freya Ingle",font18,(SCRW*0.5,230),tags=["credits"],backgroundCol=None)
credits3 = u.old_textbox("Level design by: Scott Wilson",font18,(SCRW*0.5,260),tags=["credits"],backgroundCol=None)
credits4 = u.old_textbox("Level 15 design: J Pilphott",font18,(SCRW*0.5,290),tags=["credits"],backgroundCol=None)
credits5 = u.old_textbox("Music by: Scott Wilson",font18,(SCRW*0.5,320),tags=["credits"],backgroundCol=None)
credits6 = u.old_textbox("Artwork by: Scott Wilson",font18,(SCRW*0.5,350),tags=["credits"],backgroundCol=None)
credits7 = u.old_textbox("Thank you to Game testers: ",font18,(SCRW*0.5,400),tags=["credits"],backgroundCol=None)
credits8 = u.old_textbox("Billy Baldwin, Prithvi, Robert Harvey, Esther Walden :D",font18,(SCRW*0.5,430),tags=["credits"],backgroundCol=None)
credits9 = u.old_textbox("Josephine Baker, Carolyn Kuang, J Pilphott",font18,(SCRW*0.5,450),tags=["credits"],backgroundCol=None)
credits10 = u.old_textbox("Mihran Khachatryan, Upe Severija Tamosauskaite, Andrei Mocanu",font18,(SCRW*0.5,470),tags=["credits"],backgroundCol=None)
credits11 = u.old_textbox("Rose Mitchell",font18,(SCRW*0.5,490),tags=["credits"],backgroundCol=None)
timerBox = u.old_textbox("0:0:0",font18,(20,20),center=False)
startStopBox = u.old_textbox("Start timer",font18,(20,50),center=False)
showTimerBox = u.old_textbox("Show timer",font18,(SCRW*0.6,50),tags=["settings"])
warningTitleBox = u.old_textbox("WARNING",fontTitle,(SCRW//2,150),backgroundCol=None,textCol=colour.red,tags=["warning"])
warningMessageBox1 = u.old_textbox("'Annoyinger Bosses' setting is no joke",font18,(SCRW*0.5,300),tags=["warning"],textCol=colour.black,backgroundCol=colour.red)
warningMessageBox2 = u.old_textbox("Please save unsaved work before proceeding",font18,(SCRW*0.5,350),tags=["warning"],textCol=colour.black,backgroundCol=colour.red)
confirmBox = u.old_textbox("Continue",font28,(SCRW*0.5,430),oval=True,tags=["warning"],textCol=colour.red)
cancelBox = u.old_textbox("Cancel",font28,(SCRW*0.5,490),oval=True,tags=["warning"])
customiseBox = u.old_textbox("Customise player",font18,(SCRW*0.7,400),oval=True,tags=["menu"])
resetColourBox = u.old_textbox("Reset",font18,(SCRW*0.1,SCRH*0.9),tags=["customise"])

linkBox = u.old_textbox("Link mode",font18,(SCRW//2,100),tags=["editor"],backgroundCol=colour.red)

redSlider = u.Slider(SCRW*0.4,SCRH*0.3,length=150,width=50)
greenSlider = u.Slider(SCRW*0.4,SCRH*0.5,length=150,width=50)
blueSlider = u.Slider(SCRW*0.4,SCRH*0.7,length=150,width=50)

boxes = [titleBox,startBox,menuBox,editorBox,selectedBox,coordBox,levelIDXBox,levelsBox,
         settingsBox,showFPSBox,statsTitleBox,collectedStarsBox,enemiesDefeatedBox,
         deathCountBox,uptimeBox,resetStatsBox,annoyingBossesBox,soundBox,
         highResTexturesBox,chaosModeBox,messageBox,achievementBox,achievementTitleBox,
         creditsTitleBox,creditsBox,credits1,credits2,credits3,credits4,credits5,credits6,
         credits7,credits8,credits9,credits10,credits11,timerBox,startStopBox,showTimerBox,
         warningTitleBox,warningMessageBox1,warningMessageBox2,confirmBox,cancelBox,
         customiseBox,resetColourBox]
# hard coded textboxes

##################################################

def bind(minim,val,maxim):
    if val > maxim:
        return maxim
    if val < minim:
        return minim
    else:
        return val

def empty(alist):
    return len(alist)==0

def make_position_modifier(min,max):
    posMod = [random.randint(min, max) * 50,
              random.randint(min, max) * 50]
    if random.randint(1, 2) == 1:
        posMod[0] = -1 * posMod[0]
    if random.randint(1, 2) == 1:
        posMod[1] = -1 * posMod[1]

    return posMod

def sendSpikeToCam(item,orn=0,col=colour.red):
    #print(f"orn {orn} for {item}")
    item = spike_convert(item)
    x = item[0] + (SCRW // 2) - game.player.xpos
    y = item[1] + (SCRH // 2) - game.player.ypos

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

def sendPlatformToCam(item,isHighRes,col=None,platType="normal"):
    if isHighRes:
        if platType == "normal":
            image = img.image["rock"]
        elif platType == "disappearing":
            image = img.image["disappearing_rock"]
        elif platType == "appearing":
            image = img.image["appearing_rock"]
        elif platType == "ice":
            image = img.image["ice"]

        for x in range(int(item[2]//50)):
            for y in range(int(item[3]//50)):
                blitToCam(image,(item[0]+(x*50),item[1]+(y*50)))
    else:
        sendToCam(item,col=col)

def sendToCam(item,name=None,col=None):
    newRect = [item[0]-game.player.xpos+(SCRW//2),
               item[1]-game.player.ypos+(SCRH//2),
               item[2],item[3]]

    if newRect[0] + item[2] < 0 != newRect[0] > SCRW or newRect[1] + item[3] < 0 != newRect[3] > SCRW:
        return None  #off the screen

    if name != "hitbox":
        if col == None: col = colour.darkgrey
        pygame.draw.rect(SCREEN,col,newRect)
    else:
        if col == None: col = colour.white
        #print(f"success for {newRect}")
        pygame.draw.rect(SCREEN,col,newRect,width=2)

def blitToCam(item,pos):
    x = (SCRW//2)-game.player.xpos+pos[0]
    y = (SCRH//2)-game.player.ypos+pos[1]
    w = item.get_height()
    h = item.get_width()
    if (x+h > -50 != x < SCRW+50) and (y+w > -50 != y < SCRW+50):
        SCREEN.blit(item,(x,y))

def get_screen_pos(thing):
    '''Actual position -> Screen position'''
    if len(thing) == 2:
        thing = [thing[0],thing[1],0,0]
    return [thing[0]-game.player.xpos+(SCRW//2),thing[1]-game.player.ypos+(SCRH//2),thing[2],thing[3]]

def get_actual_pos(thing):
    '''Screen position -> Actual position'''
    if len(thing) == 2:
        thing = [thing[0],thing[1],0,0]
    return [thing[0]+game.player.xpos-(SCRW//2),thing[1]+game.player.ypos-(SCRH//2),thing[2],thing[3]]

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
    levelSlots.update()
    game.achievements.update_slots()

    titleBox.pos = (SCRW//2,200)
    startBox.pos = (SCRW//2,400)
    menuBox.pos = (SCRW-35,20)
    editorBox.pos = (SCRW//2,500)
    levelsBox.pos = (SCRW//2,300)
    selectedBox.pos = (SCRW//2,60)
    coordBox.pos = (SCRW//3,20)
    levelIDXBox.pos = (SCRW//2,20)
    settingsBox.pos = (SCRW*0.7,500)
    showFPSBox.pos = (SCRW*0.4,50)
    FPSBox.pos = (SCRW-50,SCRH-50)
    statsTitleBox.pos = (SCRW//2,300)
    collectedStarsBox.pos = (SCRW//2,400)
    enemiesDefeatedBox.pos = (SCRW//2,450)
    deathCountBox.pos = (SCRW//2,500)
    uptimeBox.pos = (SCRW//2,550)
    resetStatsBox.pos = (SCRW//5,550)
    annoyingBossesBox.pos = (SCRW//2,150)
    soundBox.pos = (SCRW//2,100)
    linkBox.pos = (SCRW//2,100)
    highResTexturesBox.pos = (SCRW*0.6,200)
    chaosModeBox.pos = (SCRW*0.4,200)
    chaosModifierBox.pos = (SCRW*0.5,50)
    messageBox.pos = (SCRW*0.5,SCRH-50)
    achievementBox.pos = (SCRW*0.3,500)
    achievementTitleBox.pos = (SCRW//2,50)
    creditsBox.pos = (SCRW * 0.3, 400)
    creditsTitleBox.pos = (SCRW//2,100)
    credits1.pos = (SCRW*0.5,200)
    credits2.pos = (SCRW*0.5,230)
    credits3.pos = (SCRW*0.5,260)
    credits4.pos = (SCRW*0.5,290)
    credits5.pos = (SCRW*0.5,320)
    credits6.pos = (SCRW*0.5,350)
    credits7.pos = (SCRW*0.5,400)
    credits8.pos = (SCRW*0.5,430)
    credits9.pos = (SCRW*0.5,450)
    credits10.pos = (SCRW*0.5,470)
    credits11.pos = (SCRW*0.5,490)
    timerBox.pos = (20,20)
    startStopBox.pos = (20,50)
    showTimerBox.pos = (SCRW*0.6,50)
    customiseBox.pos = (SCRW*0.7,400)
    resetColourBox.pos = (SCRW*0.1,SCRH*0.9)

    redSlider.move_to(SCRW*0.4,None)
    greenSlider.move_to(SCRW*0.4,None)
    blueSlider.move_to(SCRW*0.4,None)

    game.editor.linkRect.move_to(SCRW-100,SCRH-100)

def tick_boxes():
    for item in boxes:
        item.get_presses()
        if game.scene in item.tags:
            item.isShowing = True
            item.display()
        else:
            item.isShowing = False

    if game.settings.showFPS:
        if now() - game.misc.lastFPSUpdate > game.misc.FPSUpdateInterval:
            game.misc.lastFPSUpdate = now()
            fps = str(clock.get_fps()).split(".")
            FPSBox.update_message(f"FPS:{fps[0]}.{fps[1][:2]}")
        FPSBox.isShowing = True
        FPSBox.display()
    else:
        FPSBox.isShowing = False

    if game.settings.chaosMode:
        if game.scene in chaosModifierBox.tags:
            chaosModifierBox.isShowing = True
            chaosModifierBox.display()

            if game.chaos.state == 1:
                time = ((game.chaos.interval+1000) - (now() - game.chaos.lastChange))//1000
                chaosModifierBox.update_message(f"Next modifier in {time}")
                if time <= 0:
                    game.chaos.state = 2
                    game.chaos.lastChange = now()
            if game.chaos.state == 2:
                game.end_chaos()
                game.chaos.action = random.randint(0,len(game.chaos.actions)-1)
                chaosModifierBox.update_message(f"Modifier: {game.chaos.actions[game.chaos.action].capitalize()}")
                game.chaos.state = 3
                game.start_chaos(game.chaos.actions[game.chaos.action])
            if game.chaos.state == 3:
                time = ((game.chaos.displayTime+1000) - (now() - game.chaos.lastChange)) // 1000
                if time <= 0:
                    game.chaos.state = 1
                    game.chaos.lastChange = now()

        else:
            chaosModifierBox.isShowing = False

    if titleBox.isPressed():
        game.stats.hidden1progress += 1

    if startBox.isPressed():
        game.scene = "ingame"
        game.init_clouds()
        game.orient_spikes()
        game.chaos.reset()

    if menuBox.isPressed():
        if game.scene == "editor":
            game.save()
            game.update_level(next=False)
        if game.scene == "customise":
            game.save_asthetics((redSlider.get()*255,greenSlider.get()*255,blueSlider.get()*255))
            
        game.scene = "menu"
        game.reset_player()
        #print("menu pressed")

    if editorBox.isPressed():
        game.scene = "editor"
        game.enableMovement = True
        game.orient_spikes()

    if levelsBox.isPressed():
        game.scene = "levels"
        levelSlots.update()
        game.init_clouds()

    if settingsBox.isPressed():
        game.scene = "settings"

    if showFPSBox.isPressed():
        game.settings.showFPS = not game.settings.showFPS

    if resetStatsBox.isPressed():
        game.stats.stars = {}
        game.stats.enemiesKilled = 0
        game.stats.deaths = 0
        game.stats.hidden1progress = 0
        game.stats.bossesKilled = 0
        #game.stats.playTime = 0
        game.fix_stats_stars()
        for key in game.achievements.achievements:
            game.achievements.achievements[key] = False
        for _ in range(2):
            game.check_achievements(announce=False)

    if annoyingBossesBox.isPressed():
        #game.settings.annoyingBosses = not game.settings.annoyingBosses
        if not game.settings.annoyingBosses:
            game.scene = "warning"
        else:
            game.settings.annoyingBosses = False

    if cancelBox.isPressed():
        game.scene = "menu"

    if confirmBox.isPressed():
        game.settings.annoyingBosses = True
        game.scene = "settings"

    if game.scene == "editor" and game.editor.linkMode:
        linkBox.display()

    if highResTexturesBox.isPressed():
        game.settings.highResTextures = not game.settings.highResTextures

    if soundBox.isPressed():
        game.sound.enabled = not game.sound.enabled
        if not game.sound.enabled:
            pygame.mixer.stop()

    if chaosModeBox.isPressed():
        game.settings.chaosMode = not game.settings.chaosMode
        if not game.settings.chaosMode:
            game.end_chaos()

    if now() - game.misc.lastMessageChange > 6000:
        game.misc.messageState += 1
        if game.misc.messageState > len(game.misc.messages)-1:
            game.misc.messageState = 0
        game.misc.lastMessageChange = now()

    messageBox.update_message(game.misc.messages[game.misc.messageState])

    if messageBox.isPressed():
        w.open(game.misc.links[game.misc.messageState])

    if achievementBox.isPressed():
        game.scene = "achievements"

    if creditsBox.isPressed():
        game.scene = "credits"

    if game.misc.showTimer and game.scene == "ingame":
        timerBox.display()
        startStopBox.display()
        startStopBox.isShowing = True
        if game.misc.timerRunning:
            time = now() - game.misc.timerStart
            ms = (time)  # + now())
            secs = (ms // 1000) % 60
            mins = (ms // (1000 * 60)) % 60
            timerBox.update_message(f"{mins}:{secs}:{ms}")

    if startStopBox.isPressed():
        game.misc.timerRunning = not game.misc.timerRunning
        if game.misc.timerRunning:
            game.misc.timerStart = now()
            startStopBox.update_message("Stop timer")
        else:
            startStopBox.update_message("Start timer")
    startStopBox.isShowing = False

    if showTimerBox.isPressed():
        game.misc.showTimer = not game.misc.showTimer

    if customiseBox.isPressed():
        game.scene = "customise"

    if resetColourBox.isPressed():
        redSlider.sliderPos = redSlider.xpos + ((r / 255) * redSlider.length)
        greenSlider.sliderPos = greenSlider.xpos + ((g / 255) * greenSlider.length)
        blueSlider.sliderPos = blueSlider.xpos + ((b / 255) * blueSlider.length)
        game.player.hat = -1
        game.hats.selected = -1

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
    #game.save_log()
    game.save_stats()
    pygame.mixer.quit()
    pygame.quit()
    sys.exit()

def now():
    return uptime#pygame.time.get_ticks()

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
                if game.scene == "menu":
                    go_quit()
                else:
                    if game.scene == "editor":
                        game.save()
                        game.update_level(next=False)
                    if game.scene == "customise":
                        game.save_asthetics((redSlider.get()*255,greenSlider.get()*255,blueSlider.get()*255))

                    game.scene = "menu"
                    game.reset_player()
            elif event.key in game.RESTART:
                game.restart = True
                
            if move:
                if event.key in game.UP:
                    game.player.move[0] = True
                elif event.key in game.LEFT:
                    game.player.move[1] = True
                elif event.key in game.RIGHT:
                    game.player.move[2] = True
                elif event.key in game.DOWN:
                    game.player.move[3] = True
                
        elif event.type == pygame.KEYUP:
            if event.key in game.UP:
                game.player.move[0] = False
            elif event.key in game.LEFT:
                game.player.move[1] = False
            elif event.key in game.RIGHT:
                game.player.move[2] = False
            elif event.key in game.DOWN:
                game.player.move[3] = False

##################################################

img = Images()
game = Game()
levelSlots = Level_slots(len(game.data))

r,g,b,a = game.player.colour
redSlider.sliderPos = redSlider.xpos + ((r/255) * redSlider.length)
greenSlider.sliderPos = greenSlider.xpos + ((g/255) * greenSlider.length)
blueSlider.sliderPos = blueSlider.xpos + ((b/255) * blueSlider.length)

SCREEN.fill(colour.black)

##################################################


while True:
    uptime = pygame.time.get_ticks()
    u.tick()
    tick_boxes()
    game.check_achievements(announce=True)
    game.stats.playTime = game.stats.startTime + now()

    pygame.display.flip()
    SCREEN.fill((200,200,250))
    clock.tick(TICKRATE)

    handle_events(move=game.enableMovement)

    if game.sound.enabled:
        game.sound.run_music()

    #game.log(f"{now()}: ({game.player.xpos},{game.player.ypos})")

    if game.scene == "ingame":
        game.draw_gradient()
        game.generate_cloud()
        game.draw_bg()
        game.tick_enemies()
        game.tick()
        #game.log(f"after tick: ({game.player.xpos},{game.player.ypos})")
        game.correct_mobs() # this one
        game.tick_player()
        game.player.update_hitboxes()
        if game.enableMovement:
            game.player.draw()
            if game.player.hat != -1:
                hat = game.img.image["hats"][game.player.hat]
                SCREEN.blit(hat,((SCRW-hat.get_width())//2,((SCRH-hat.get_height())//2)-game.player.height+6))
        game.draw_animations()
        
        if game.player.ypos > 5000 or game.player.isDead:
            game.player.isDead = True
            #game.trigger_death()
        if game.player.atFinish:
            if not game.contains_animation("transition"):
                if game.misc.wasTransition:
                    game.update_level(next=True)
                    game.reset_player()
                    #print("finished level")
                else:
                    game.animations.append(Transition())
            #game.trigger_death(die=False)
        levelIDXBox.update_message("Level " + str(game.levelIDX))

#        sendToCam(list(game.player.hitbox.bottom),"hitbox",col=colour.white)
#        sendToCam(list(game.player.hitbox.left),"hitbox",col=colour.white)
#        sendToCam(list(game.player.hitbox.right),"hitbox",col=colour.white)
#        sendToCam(list(game.player.hitbox.top),"hitbox",col=colour.white)
#        sendToCam(list(game.player.hitbox.whole),"hitbox",col=colour.white)

        if game.chaos.actions[game.chaos.action] == "invert screen":
            invt = pygame.transform.flip(SCREEN,flip_x=True,flip_y=True)
            SCREEN.blit(invt,(0,0))

        if game.chaos.actions[game.chaos.action] == "wonky":
            invt = pygame.transform.rotate(SCREEN,-10)
            SCREEN.blit(invt,(-50,-15))

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
            game.chaos.reset()

    elif game.scene == "settings":
        #collectedStarsBox,enemiesDefeatedBox,deathCountBox,uptimeBox
        starCount = 0
        for key in game.stats.stars:
            starCount += len(game.stats.stars[key])

        ms = (game.stats.playTime)# + now())
        secs = (ms // 1000) % 60
        mins = (ms // (1000*60)) % 60
        hours = (ms // (1000*60*60)) % 60
        uptime = f"Time played: {hours}h {mins}m {secs}s"
            
        collectedStarsBox.update_message(f"Stars collected: {starCount}")
        enemiesDefeatedBox.update_message(f"Enemies defeated: {game.stats.enemiesKilled}")
        deathCountBox.update_message(f"Number of deaths: {game.stats.deaths}")
        uptimeBox.update_message(uptime)

        th = img.image["tick"].get_height()/2

        if game.settings.showFPS:
            SCREEN.blit(img.image["tick"],(showFPSBox.pos[0]+showFPSBox.textRect[2]/2,showFPSBox.pos[1]-th))

        if game.sound.enabled:
            SCREEN.blit(img.image["tick"],(soundBox.pos[0]+soundBox.textRect[2]/2,soundBox.pos[1]-th))

        if game.settings.annoyingBosses:
            SCREEN.blit(img.image["tick"],(annoyingBossesBox.pos[0]+annoyingBossesBox.textRect[2]/2,annoyingBossesBox.pos[1]-th))

        if game.settings.highResTextures:
            SCREEN.blit(img.image["tick"],(highResTexturesBox.pos[0]+highResTexturesBox.textRect[2]/2,highResTexturesBox.pos[1]-th))

        if game.settings.chaosMode:
            SCREEN.blit(img.image["tick"],(chaosModeBox.pos[0] + chaosModeBox.textRect[2] / 2, chaosModeBox.pos[1] - th))

        if game.misc.showTimer:
            SCREEN.blit(img.image["tick"],(showTimerBox.pos[0]+showTimerBox.textRect[2]/2,showTimerBox.pos[1]-th))

    elif game.scene == "achievements":
        game.achievements.update_slots()
        game.achievements.show()

    elif game.scene == "customise":
        for slider in [redSlider,greenSlider,blueSlider]:
            slider.draw()
            slider.update()

        col = (redSlider.get()*255,greenSlider.get()*255,blueSlider.get()*255)
        pygame.draw.rect(SCREEN,col,(SCRW*0.2,SCRH*0.4,SCRH*0.2,SCRH*0.2))

        game.hats.draw()
        game.hats.check()
        game.player.hat = game.hats.selected
