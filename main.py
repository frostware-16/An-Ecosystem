import pygame
import time
import math
import random
import numpy as np
from ai import *
pygame.init()
screen = pygame.display.set_mode((1400, 800))
running = True
fps = 120
plantsSpawnTimer = 60
agents = []
foods = []
#209, 190, 176
s = 12*4
bg = (24,24,24)
font = pygame.font.SysFont("Arial", 40)
ticks = 0

selected = 0
class food:
    def __init__(self,x,y):
        self.x = x
        self.y = y

        self.energy = 70
    def render(self):
        pygame.draw.rect(screen, (151,182,104), (self.x,self.y,5, 5))

class Agent:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.sprite = mousesprite = pygame.image.load("mouse.png")
        self.sprite = mousesprite = pygame.transform.scale(mousesprite, (32,32))
        self.energy = 100
        self.angle = 0
        self.radar = 0
        self.timer = 10
        self.eattingcoldown = 10
        self.color = [255,255,255]
        self.closefood = []
        self.speed = 2
        self.layer1 = Layer_Dense(2,2)
        self.layer2 = Layer_Dense(2,4)
        self.layer3 = Layer_Dense(4,3)
        self.activation1 = Activation_ReLU()
        self.activation2 = Activation_ReLU()
        self.activation3 = Activation_ReLU()
        
        
    def render(self):           
        # self.color[0] = max(self.color[0],0)
        # self.color[1] = max(self.color[1],0)
        # self.color[2] = max(self.color[2],0)
        # self.color[0] = min(self.color[0],255)
        # self.color[1] = min(self.color[1],255)
        # self.color[2] = min(self.color[2],255)
        roted = self.sprite
        roted = rot_center(self.sprite,self.angle*-1+90)
        # pygame.draw.rect(screen, (255,0,0), (self.x,self.y,32, 32))
        screen.blit(roted,(self.x,self.y))
        # pygame.draw.rect(screen, (self.color[0],self.color[1],self.color[2]), (self.x,self.y,10, 10))

    def reproduce(self):
        if self.energy >= 170:
            self.energy -= 50
            a = Agent(self.x,self.y)

            a.layer1.weights = self.layer1.weights.copy()
            a.layer2.weights = self.layer2.weights.copy()
            a.layer3.weights = self.layer3.weights.copy()
            a.layer1.biases = self.layer1.biases.copy()
            a.layer2.biases = self.layer2.biases.copy()
            a.layer3.biases = self.layer3.biases.copy()
            a.color = self.color.copy()
            a.speed = self.speed
            if random.randint(0,10) != 0:
                a.layer1.weights += 0.05 * np.random.randn(2,2)
                a.layer2.weights += 0.05 * np.random.randn(2,4)
                a.layer3.weights += 0.05 * np.random.randn(4,3)
                a.layer1.biases += 0.05 * np.random.randn(1,2)
                a.layer2.biases += 0.05 * np.random.randn(1,4)
                a.layer3.biases += 0.05 * np.random.randn(1,3)
            if random.randint(0,30) == 0:a.speed += random.randint(-1,1)
            # if random.randint(0,3) == 0:a.color[0] += random.randint(-20,20)
            # if random.randint(0,3) == 0:a.color[1] += random.randint(-20,20)
            # if random.randint(0,3) == 0:a.color[2] += random.randint(-20,20)
            agents.append(a)
    def border(self):
        if self.x >= 1200:
            self.x = 10
        if self.x <= 0:
            self.x = 1190
        if self.y >= 800:
            self.y = 10
        if self.y <= 0:
            self.y = 790
    def move(self):
        self.energy -= 0.6
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))

    def rot(self,direction):
        
        self.angle += direction

    
    def eat(self):
        self.energy -= 0.05
        self.eattingcoldown -= 1
        if self.energy <= 0:
            agents.remove(self)
        # print(len(self.closefood))
        if len(self.closefood) != 0:
            self.radar = self.closefood[0]
            for f in self.closefood:
                dist = math.sqrt((self.x+16-f.x)**2+(self.y+16-f.y)**2)
                dist2 = math.sqrt((self.x+16-self.radar.x)**2+(self.y+16-self.radar.y)**2)
                if dist < dist2:
                    self.radar = f
            # pygame.draw.line(screen, (255,0,0), (self.x,self.y),(self.radar.x,self.radar.y))
                if dist <= 16 and self.eattingcoldown <= 0:
                    self.energy += f.energy-self.speed*3
                    self.eattingcoldown = 2
                    if f in self.closefood:self.closefood.remove(f)
                    if f in foods:foods.remove(f)

    def GetcloseFood(self):
        self.timer -= 1
        if self.timer <= 0:
            self.closefood = []
            for f in foods:
                if f != self:
                    dist = math.sqrt((self.x+16-f.x)**2+(self.y+16-f.y)**2)
                    if dist <= 300:
                        self.closefood.append(f)
            self.timer = 5
    def collision(self):
        for a in agents:
            if a != self:
                dist = math.sqrt((self.x-a.x)**2+(self.y-a.y)**2)
                if dist <= 32:
                    self.energy -= 3
                    point1 = [self.x, self.y]
                    point2 = [a.x, a.y]
                    angle = math.atan2(point2[1] - point1[1], point2[0] - point1[0]) * (180/math.pi)
                    self.x -= self.speed * math.cos(math.radians(angle))
                    self.y -= self.speed * math.sin(math.radians(angle))
    
    def forward(self):
        if self.radar != 0:
            point1 = [self.x, self.y]
            point2 = [self.radar.x,self.radar.y]
            angle = math.atan2(point2[1] - point1[1], point2[0] - point1[0]) * (180/math.pi)
            dist = math.sqrt((self.x-self.radar.x)**2+(self.y-self.radar.y)**2)
            inputs = [self.angle-angle,dist]
        else:
            inputs = [0,0]
        self.layer1.forward(inputs)
        self.activation1.forward(self.layer1.output)
        self.layer2.forward(self.activation1.output)
        self.activation2.forward(self.layer2.output)
        self.layer3.forward(self.activation2.output)
        self.activation3.forward(self.layer3.output)
        if self.activation3.output[0][0] >= 1.1:
            self.rot(1)
        if self.activation3.output[0][1] >= 1.1:
            self.rot(-1)
        if self.activation3.output[0][2] >= 1.1:
            self.move()

def rot_center(image, angle):
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

for i in range(50):
    a = Agent(random.randint(50,1150),random.randint(50,750))
    agents.append(a)
for i in range(50):
    f = food(random.randint(50,1150),random.randint(50,750))
    foods.append(f)

while running:
        start = time.time()
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        running = False
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    for a in agents:
                        dist = math.sqrt((pos[0]-a.x)**2+(pos[1]-a.y)**2)
                        if dist <= 50:
                            selected = a
        ticks += 1
        theplantsspawnequ = (min(ticks,1000000)/(10000/3))
        if len(agents) == 0:
            for i in range(50):
                a = Agent(random.randint(50,1150),random.randint(50,750))
                agents.append(a)
            foods = []
            for i in range(50):
                f = food(random.randint(50,1150),random.randint(50,750))
                foods.append(f)
            print(ticks)
            ticks = 0
        plantsSpawnTimer -= 1
        if plantsSpawnTimer <= 0:
            plantsSpawnTimer = theplantsspawnequ
            f = food(random.randint(50,1150),random.randint(50,750))
            foods.append(f)
        screen.fill(bg)  
        # for i in range(100):
        #     pygame.draw.line(screen, (80,80,80), (i*s,0), (i*s,800), 5)
        # for i in range(100):
        #     pygame.draw.line(screen, (80,80,80), (0,i*s), (1200,i*s), 5)
        pygame.draw.rect(screen, bg, (1210,0,200,800))
        if selected != 0:
            pygame.draw.rect(screen, (255,0,0), (selected.x,selected.y,32,32))
            speed = font.render(str(selected.speed), True,(255,255,255))
            energy = font.render(str(selected.energy), True,(255,255,255))
            screen.blit(speed,(1380,300))
            screen.blit(energy,(1320,350))
        for a in agents:
            a.border()
            a.render()
            a.collision()
            a.GetcloseFood()
            a.eat()
            a.forward()
            a.reproduce()
        for f in foods:
            f.render()
        
        
        time.sleep(1/fps)
        end = time.time()
        fpstxt = font.render(str(int(1/(end+ - start))), True,(255,255,255))
        tickstxt = font.render(str(ticks), True,(255,255,255))
        spawnTimertxt = font.render(str(theplantsspawnequ), True,(255,255,255))
        plantspop = font.render(str(len(foods)), True,(255,255,255))
        agentspop = font.render(str(len(agents)), True,(255,255,255))
        screen.blit(fpstxt,(1350,0))
        screen.blit(tickstxt,(1370-len(str(ticks))*15,50))
        screen.blit(spawnTimertxt,(1300,100))
        screen.blit(plantspop,(1340,150))
        screen.blit(agentspop,(1340,200))
        
        pygame.display.update()