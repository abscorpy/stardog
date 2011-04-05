import pygame
from pygame.locals import *
from math import pi, sin, cos, atan2, sqrt
from random import Random

random = Random().random
resolution = 800, 600
player2Human = True
averageCourseChange = 6 #seconds
screen = pygame.display.set_mode(resolution)
clock = pygame.time.Clock()


class Space:
    def __init__(self):
        self.clock = pygame.time.Clock()    #waits between frames.
        self.keys = []  #array of keyboard keys.  1 is pressed, 0 in up.
        for i in range(322):
            self.keys.append(0)
        self.ship1 = Ship(self, 300, 300)
        self.ship1.color = (255,0,0)
        self.ship1.acceleration = 6
        self.ship2 = Ship(self, 600, 400)
        self.ship2.color = (0,0,255)
        self.ship2.heading =(int(random()*resolution[0]), 
                        int(random()*resolution[1]))
        self.running = True
        self.dt = .001
        
    def mainloop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = 0
                # elif event.type == pygame.MOUSEBUTTONDOWN:
                    # self.mouse[event.button] = 1
                    # self.mouse[0] = event.pos
                # elif event.type == pygame.MOUSEBUTTONUP:
                    # self.mouse[event.button] = 0
                    # self.mouse[0] = event.pos
                # elif event.type == pygame.MOUSEMOTION:
                    # self.mouse[0] = event.pos
                elif event.type == pygame.KEYDOWN:
                    self.keys[event.key % 322] = 1
                elif event.type == pygame.KEYUP:
                    self.keys[event.key % 322] = 0
            
            self.debug = False
            if self.keys[K_BACKSPACE % 322]:
                #you can print your debug info at any point by 
                #using "if game.debug: print(...)"
                self.debug = True #print debug information
                self.keys[K_BACKSPACE % 322] = False
                print "Debug:"
            # quit on esc:
            if self.keys[K_ESCAPE % 322]:
                self.running = False
            
            #reset ships when space is pressed:
            if self.keys[K_SPACE % 322]:
                self.ship1.x,self.ship1.y = 300, 300
                self.ship2.x,self.ship2.y = 600, 400
                
            #update ship2 from keyboard input:
            if player2Human:
                if self.keys[K_UP % 322]:
                    self.ship2.accel()
                if self.keys[K_LEFT % 322]:
                    self.ship2.turnLeft()
                if self.keys[K_RIGHT % 322]:
                    self.ship2.turnRight()
            else:
                runnerAI(self.ship2)
            self.ship2.update()
            
            #update ship1 from script:
            ai(self.ship1, self.ship2)
            self.ship1.update()
            
            #frame maintanance:
            screen.fill((0,0,0))
            self.ship1.draw(screen)
            self.ship2.draw(screen)
            pygame.draw.circle(screen, (100,100,200), self.ship2.heading, 3)
            pygame.display.flip()
            self.dt = clock.tick(30) / 1000.
            
class Ship:
    dx,dy = 0,0
    dir = 0
    tri = (3,0), (-2, -2), (-2, 2)
    acceleration = 4
    torque = 2 * pi
    turned = False
    acceled = False
    def __init__(self, game, x, y):
        self.x, self.y = x,y
        self.game = game
    
    def draw(self, surface):
        newTri = []
        sint = sin(self.dir)
        cost = cos(self.dir)
        for point in self.tri:
            newTri.append([point[0] * cost - point[1] * sint + self.x,
                         point[0] * sint + point[1] * cost + self.y])
        pygame.draw.polygon(surface, self.color, newTri)
        
    def update(self):
        self.x += self.dx * self.game.dt
        self.y += self.dy * self.game.dt
        self.acceled = False
        self.turned = False
        #keep them on the screen.
        if self.x < 0: self.x = 0 ; self.dx = 0
        if self.x > resolution[0]: self.x = resolution[0]; self.dx = 0
        if self.y < 0: self.y = 0 ; self.dy = 0
        if self.y > resolution[1]: self.y = resolution[1]; self.dy = 0
        
    def accel(self):
        if self.acceled: return
        self.acceled = True
        self.dx += self.acceleration * cos(self.dir) * self.game.dt
        self.dy += self.acceleration * sin(self.dir) * self.game.dt
        
    def turnRight(self):
        if self.turned: return
        self.turned = True
        self.dir += self.torque * self.game.dt
        self.dir = angleNorm(self.dir)
        
    def turnLeft(self):
        if self.turned: return
        self.turned = True
        self.dir -= self.torque * self.game.dt
        self.dir = angleNorm(self.dir)
            
def runnerAI(ship):
    if random() * averageCourseChange < ship.game.dt:
        ship.heading =(int(random()*resolution[0]), 
                        int(random()*resolution[1]))
    flyTowards(ship, ship.heading)
    
def ai(ship, enemy):
    #ultimate result should be calling ship1.accel(dt) and/or
    #ship1.turnLeft(dt) / ship1.turnRight or none of these.
    
    targetX = enemy.x + (2 * (enemy.dx - ship.dx) + enemy.acceleration * cos(enemy.dir)) / 2
    targetY = enemy.y + (2 * (enemy.dy - ship.dy) + enemy.acceleration * sin(enemy.dir)) / 2
    flyTowards(ship, (targetX, targetY))
    
def flyTowards(ship, point):
    goalDir = atan2(point[1] - ship.y, point[0] - ship.x)
    dirDif=angleNorm(goalDir - ship.dir)
    if dirDif < 0:
        ship.turnLeft()
    elif dirDif > 0:
        ship.turnRight()
    if -30 < dirDif < 30:
        ship.accel()
    if ship.game.debug:
        print("ship heading towards %s, pointed at %s, turning to %s"
                    %(ship.heading, ship.dir, goalDir))
    
                
def distance2(ship1, ship2):
    """skipping the sqrt makes it faster."""
    return ((ship1.x - ship2.x) * (ship1.x - ship2.x) 
          + (ship1.y - ship2.y) * (ship1.y - ship2.y))
    
def distance(ship1, ship2):
    return sqrt((ship1.x - ship2.x) **2 + (ship1.y - ship2.y) ** 2)
    
def relativeDir(ship1, ship2):
    """compare this to ship1.dir to see if you're pointed at him."""
    return atan2(ship2.dy - ship1.dy, ship2.dx - ship1.dx)
    
def angleNorm(angle):
    return (angle + pi) % (2 * pi) - pi
    
if __name__ == "__main__":
    space = Space()
    space.mainloop()            
            
            
            