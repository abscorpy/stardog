#tinyFighter.py

#strafebat.py

from utils import *
from spaceship import *
from parts import *
from scripts import *
import stardog
from adjectives import *

class TinyFighter(Ship):
	strafeRadius = 100
	planet = None
	stage = 0
	level = .5
	def __init__(self, game, x, y, dx = 0, dy = 0, color = (70, 180,0)):
		self.target = game.player
		self.circling = False
		Ship.__init__(self, game, x, y, dx, dy, script = TinyFighterScript(game), color = color)
		self.addPart(Drone(game))
		self.energy = self.maxEnergy
		self.inventory.append(randItem(self.game, self.level))


class TinyFighterScript(AIScript):
	"""a script for tiny fighters."""
	swarmRadius = 280
	retreatRadius = 300
	acceptableError = 3
	shootingRange = 280
	interceptSpeed = 200
	def update(self, ship):
		target = ship.target
		if stardog.debug: print ship.stage
		if ship.stage == 0:
			dx = target.dx - ship.dx
			dy = target.dy - ship.dy
			dir = atan2(dy, dx)
			if self.turn(ship, dir):
				ship.forward()
			if -50 < dx < 50 and -50 < dy < 50:
				ship.stage = 1
		if ship.stage == 1:
			speed = self.relativeSpeed(ship, target)
			accel = ship.forwardThrust / ship.mass
			distance = dist(ship.x, ship.y, target.x, target.y) - self.swarmRadius
			turnTime = ship.moment / ship.torque * 180
			if speed > - self.interceptSpeed:
				if self.turnTowards(ship, target):
					ship.forward()
			# elif speed < - self.interceptSpeed:
				# if self.turnTowards(ship, target, 180):
					# ship.forward()
			if distance <= self.shootingRange:
					ship.shoot()
			if distance <= self.retreatRadius - self.swarmRadius:
				ship.stage = 2
		if ship.stage == 2:
			distance = dist(ship.x, ship.y, target.x, target.y)
			if distance < self.retreatRadius:
				if self.turnTowards(ship, target, 180):
					ship.forward()
			if distance > self.swarmRadius:
				ship.stage = 0
					
		# x = target.x - ship.x
		# y = target.y - ship.y
		# distance = dist(ship.x, ship.y, target.x, target.y) - self.swarmRadius
		# turnTime = ship.moment / ship.torque * 180
		# speed = self.relativeSpeed(ship, target)
		## v/a = time to stop, d/v = time to arrive
		# if distance > 0 and speed / accel + turnTime < distance / speed:
			# self.intercept(ship, target)
		# else: #going too fast!
			# if self.turnTowards(ship, target, 180):
				# ship.forward()
		# if distance < self.shootingRange:
			# angle = angleNorm(atan2(target.y - ship.y, target.x - ship.x)\
				# - ship.dir)
			# if - self.acceptableError < angle < self.acceptableError:
				# ship.shoot()
		
		
		
class Drone(Cockpit, Engine, Gyro, Gun, Generator, Battery):
	mass = 10
	name = "Tiny Fighter Chassis"
	image = None
	energyCost = 1 #this is used as a coefficient everywhere.
	#gun:
	shootDir = 0
	shootPoint = 20, 0
	bulletDamage = .2
	reloadTime = .1
	burstSize = 3
	reloadBurstTime = 2
	shotCost = .3
	shot = False
	#engine:
	force = 20000
	thrustCost = .1
	thrusted = False
	#gyro:
	torque = 600
	turnCost = .1
	turned = False
	#generator:
	rate = 30
	#battery:
	capacity = 40
	
	def __init__(self,  game, parent = None):
		if Drone.image == None:
			Drone.image = pygame.image.load("res/ship" \
												+ ext).convert()
			Drone.image.set_colorkey((0,0,0))
			Drone.animatedImage = pygame.image.load(\
					"res/shipThrusting" + ext).convert_alpha()
		self.baseImage = Drone.image
		self.baseAnimatedImage = Drone.animatedImage
		self.baseAnimatedImage.set_colorkey((0,0,0))
		self.animated = True
		Part.__init__(self,  game, parent)
		self.reload = 0
		self.reloadBurst = 0
		self.burst = self.burstSize
		self.functions = [self.shoot, self.turnLeft, self.turnRight, \
		self.thrust]
		self.functionDescriptions = ['shoot', 'turn left', 'turn right', 'thrust']
	
	def update(self):
		self.animated = self.thrusted
		self.shot = False
		self.thrusted = False
		self.turned = False
		self.reload -= 1. / self.game.fps
		self.reloadBurst -= 1. / self.game.fps
		if self.reloadBurst <= 0 :
			self.burst = self.burstSize
			self.reloadBurst = self.reloadBurstTime
		#generator:
		if self.ship and self.ship.energy < self.ship.maxEnergy:
			self.ship.energy = min(self.ship.maxEnergy, \
								self.ship.energy + self.rate / self.game.fps)
		Part.update(self)
		
	def attach(self):
		#battery:
		self.ship.maxEnergy += self.capacity
		Part.attach(self)
		
	
	def shoot(self):
		"""fires a bullet."""
		if self.shot: return
		self.shot = True
		if self.reload <= 0 and self.ship.energy > self.shotCost * self.energyCost\
		and self.burst > 0:
			self.reload = self.reloadTime
			self.burst -= 1
			self.ship.energy -= self.shotCost * self.energyCost
			if soundModule:
				setVolume(shootSound.play(), self, self.game.player)
			self.game.curSystem.floaters.add(Bullet(self.game, self,\
					self.bulletSpeed, self.bulletRadius, self.bulletDamage, \
					self.bulletRange, image = self.bulletImage))
			if self.burst <= 0:
				self.reloadBurst = self.reloadBurstTime
				
	def thrust(self):
		"""thrust: pushes the ship from the direction this engine points."""
		if self.thrusted: return
		self.thrusted = True
		if self.ship and self.ship.energy >= self.thrustCost * self.energyCost:
			dir = self.ship.dir
			self.ship.dx += cos(dir) * self.force / self.ship.mass / self.game.fps
			self.ship.dy += sin(dir) * self.force / self.ship.mass / self.game.fps
			self.ship.energy -= self.energyCost / self.game.fps * self.energyCost
			self.thrusting = True
			
	def turnLeft(self):
		"""rotates the ship counter-clockwise."""
		if self.turned: return
		self.turned = True
		if self.ship and self.ship.energy >= self.turnCost * self.energyCost:
			self.ship.dir = angleNorm(self.ship.dir - \
						self.torque / self.ship.moment / self.ship.game.fps)
			self.ship.energy -= self.turnCost / self.game.fps * self.energyCost
		
	def turnRight(self):
		"""rotates the ship clockwise."""
		if self.turned: return
		self.turned = True
		if self.ship and self.ship.energy >= self.turnCost * self.energyCost:
			self.ship.dir = angleNorm(self.ship.dir + \
						self.torque / self.ship.moment / self.ship.game.fps)
			self.ship.energy -= self.turnCost / self.game.fps * self.energyCost
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			