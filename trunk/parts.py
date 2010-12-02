#parts.py


from utils import *
from scripts import *
from pygame.locals import *
from floaters import *
import spaceship
import stardog

PART_OVERLAP = 4
DETACH_SPACE = 3

class Port:
	def __init__(self, offset, dir, parent):
		self.offset = offset
		self.dir = dir
		self.part = None
		self.parent = parent
		
	def addPart(self, part):
		self.parent.addPart(part, self.parent.ports.index(self))

class Part(Floater):
	"""A part of a ship."""
	baseImage = pygame.image.load("res/default.gif").convert()
	image = None
	height, width = 9, 3
	parent = None
	dir = 270
	mass = 10
	# position in relation to the center of the ship
	#and the center of this part:
	offset = 0, 0
	#whether this should be redrawn each frame:
	color = (150,150,150)
	animated = False
	animatedBaseImage = None
	animatedImage = None
	number = -1
	name = 'part'
	level = 1
	buffer = pygame.Surface((30,30), flags = hardwareFlag | SRCALPHA).convert_alpha()
	buffer.set_colorkey((0,0,0))
	acted = False
	#a list of functions that are called on the ship during ship.update:
	shipEffects = []
	#a list of functions that are called on this part at attach time:
	attachEffects = []

	def __init__(self, game):
		self.functions = []
		self.functionDescriptions = []
		self.adjectives = []
		self.maxhp = 10
		self.hp = 10
		Floater.__init__(self, game, 0, 0, dir = 270, radius = 10)
		self.baseImage.set_colorkey((255,255,255))
		self.image = self.baseImage
		self.image.set_colorkey((255,255,255))
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		#the length of this list is the number of connections.
		 #each element is the part there, (x,y,dir) position of the connection.
		 #the example is at the bottom of the part, pointed down.
		self.ports = [Port((-self.width / 2 + 2, 0), 0, self)]
	
	def stats(self):
		stats = (self.hp, self.maxhp, self.mass)
		statString = """HP: %s/%s \nMass: %s """
		return statString % stats
	
	def shortStats(self):
		stats = (self.hp, self.maxhp)
		statString = """%s/%s"""
		return statString % stats
		
	def addPart(self, part, port, flip = False):
		"""addPart(part, portNum) -> connects part to port portNum
		of this part."""
		#TODO: pygame.transform.flip(Surface, xbool, ybool)
		if len(self.ports) > port:
			#detach old part, if any:
			if self.ports[port].part:
				self.ports[port].part.parent = None
			self.ports[port].part = part
			part.parent = self
			part.ship = self.ship
			part.dir = self.ports[port].dir + self.dir
			#calculate offsets:
			cost = cos(self.dir) #cost is short for cos(theta)
			sint = sin(self.dir)
			part.offset = self.offset[0] + self.ports[port].offset[0] * cost \
				- self.ports[port].offset[1] * sint \
				- cos(part.dir) * (part.width - PART_OVERLAP) / 2, \
				self.offset[1] + self.ports[port].offset[0] * sint \
				+ self.ports[port].offset[1] * cost \
				- sin(part.dir) * (part.width - PART_OVERLAP) / 2
			#rotate takes a ccw angle.
			part.image = colorShift(pygame.transform.rotate(part.baseImage, \
						-part.dir), part.color).convert()
			part.image.set_colorkey((0,0,0))
			#allow the ship to re-adjust:
			self.ship.reset()
			
	def attach(self):
		"""attaches this part to a ship. This includes increases ship mass
		and moment and possibly other stats."""
		#NOTE: this is done recursively to all parts every time a part
		#is added or removed, so it is not neccesary to undo it in detach.
		#It must be recalculated because moment is calculated from the center
		#of the ship.  
		self.ship.mass += self.mass
		self.ship.moment += self.mass \
					* sqrt(self.offset[0] ** 2 + self.offset[1] ** 2)
		#These two can be modified by adjectives:
		self.ship.partEffects.extend(self.shipEffects)
		for effect in self.attachEffects:
			effect(self)

	def detach(self):
		"""removes this part from its parent and ship,
		and recursively detaches its children."""
		#recurse to children:
		for port in self.ports:
			if port.part:
				port.part.detach()
		detachSpeed = 8
		#set physics to drift away from ship (not collide):
		cost = cos(self.ship.dir) #cost is short for cos(theta)
		sint = sin(self.ship.dir)
		self.x = self.ship.x + DETACH_SPACE * self.offset[0] * cost \
				- DETACH_SPACE * self.offset[1] * sint
		self.y = self.ship.y + DETACH_SPACE * self.offset[0] * sint \
				+ DETACH_SPACE * self.offset[1] * cost
		self.dx = self.ship.dx \
				+ rand() * sign(self.offset[0]) * cost * detachSpeed\
				- rand() * sign(self.offset[1]) * sint * detachSpeed
		self.dy = self.ship.dy \
				+ rand() * sign(self.offset[0]) * sint * detachSpeed\
				+ rand() * sign(self.offset[1]) * cost * detachSpeed
		#if this is the root of the ship, kill the ship:
		if self.parent and self.parent == self.ship:
			self.ship.kill()
		#cleanup relations:
		if self.parent and self.parent != self.ship:
			for port in self.parent.ports:
				if port.part == self:
					port.part = None
		self.ship.parts.remove(self)
		self.ship.reset()
		if self.ship == self.game.player:
			self.game.menu.parts.portPanel.reset()
		self.ship = None
		self.parent = None
		#otherwise add this to the game as an independent Floater:
		self.game.curSystem.add(self)
		
	def scatter(self, ship):
		"""Like detach, but for parts that are in an inventory when a 
		ship is destroyed."""
		self.offset = randint(-10,10),randint(-10,10)
		self.ship = ship
		ship.parts.append(self)#TODO: this is sloppy.
		self.detach()
		
	def update(self):
		"""updates this part."""
		#reset so this part can act again this frame:
		self.acted = False
		#if it's attached to a ship, just rotate with the ship:
		if self.parent:
			cost = cos(self.ship.dir) #cost is short for cos(theta)
			sint = sin(self.ship.dir)
			self.x = self.ship.x + self.offset[0] * cost - self.offset[1] * sint
			self.y = self.ship.y + self.offset[0] * sint + self.offset[1] * cost
		#if it's floating in space, act like a floater:
		else:
			Floater.update(self)
		#update children:
		for port in self.ports:
			if port.part:
				port.part.update()

	def draw(self, surface, offset = None):
		"""draws this part onto the surface."""
		if not offset:
			offset =(surface.get_width() \
					- self.image.get_width()) / 2 + self.offset[0], \
					(surface.get_height() \
					- self.image.get_height()) / 2 + self.offset[1]
		if self.ship == None:
			Floater.draw(self, surface, offset)
		else:
			surface.blit(self.image, offset)
		#draw children:
		for port in self.ports:
			if port.part:
				port.part.draw(surface)
		if not self.parent:
			self.redraw(surface, offset)

	def redraw(self, surface, offset):
		"""redraw(surface, offset) -> draws 
		animated elements of this part to surface. 
		This should circumvent the ship surface and draw directly onto space."""
		if self.animated and self.animatedImage and self.ship:
			self.animatedImage = \
					pygame.transform.rotate(self.baseAnimatedImage, \
								- self.dir - self.ship.dir).convert_alpha()
			self.animatedImage.set_colorkey((0,0,0))
			pos = self.x - self.animatedImage.get_width() / 2 - offset[0], \
				  self.y - self.animatedImage.get_height() / 2 - offset[1]
			surface.blit(self.animatedImage, pos)
		#hp rings:
		pos = 	int(self.x - offset[0] - self.radius), \
				int(self.y - offset[1] - self.radius)
		if self.hp / self.maxhp < .9:
			#color fades green to red as hp decreases.
			color = limit(0, int((1 - self.hp * 1. / self.maxhp ) * 255),255), \
					limit(0, int(1. * self.hp / self.maxhp * 255), 255), 0, 100 
			rect = (0,0, self.radius * 2, self.radius * 2)
			#arc from - hp/maxhp*360 to -90:
			pygame.draw.arc(self.buffer, color, rect, \
					math.pi/2 - math.pi * 2 * (1 - 1. * self.hp / self.maxhp),\
					math.pi/2, 2)
			surface.blit(self.buffer, pos)
			self.buffer.fill((0,0,0,0))

	def takeDamage(self, damage, other):
		hitByPlayer = False
		if isinstance(other, Bullet) and other.ship == self.game.player:
			hitByPlayer = True
			self.game.player.xpDamage(self, damage)
		if self.parent \
		and self.parent != self.ship \
		and rand() <  1. * damage / (self.hp + 1):
			self.detach()
		self.hp -= damage
		if self.hp <= 0:
			if hitByPlayer:
				self.game.player.xpDestroy(self)
				if self.ship:
					self.game.player.xpKill(self.ship)
			if self.parent:
				self.detach()
			self.kill()
			#if dead, make an explosion here.
			self.game.curSystem.add(Explosion(self.game, self.x, self.y, \
						self.dx, self.dy, radius = self.radius * 4,\
						time = self.maxhp / 10))

			
class Dummy(Part):
	"""A dummy part used by the parts menu."""
	def __init__(self, game):
		Part.__init__(self, game)
		self.ports = []
		
	def update(self):
		if self.parent: 
			#a Dummy should never be a base part, so ignore that case.
			for port in self.parent.ports:
				if port.part == self:
					port.part = None
					self.kill()
					self.ship.reset()
	
class Cannon(Part):
	baseImage = pygame.image.load("res/default" + ext).convert()
	image = None
	bulletImage = None
	bulletSpeed = 300
	bulletRadius = 2
	bulletDamage = 2
	bulletRange = 4
	name = "Cannon"
	shootPoint = -30, 0 
	shootDir = 90
	reloadTime = .5 #in seconds
	reload = 0
	energyCost = 3
	
	def __init__(self, game):
		#TODO:use this structure for all parts:
		if self.bulletImage == None:
			self.bulletImage = BULLET_IMAGE.copy()
		Part.__init__(self, game)
		self.functions.append(self.shoot)
		self.functionDescriptions.append("shoot")
		self.ports = []
		
	def stats(self):
		stats = (self.bulletDamage, 60. / self.reloadTime, self.energyCost, \
				self.bulletSpeed, self.bulletRange, self.shootDir)
		statString = """\nDamage: %s \nRate: %s/minute \nCost: %s \
energy/bullet \nBullet Speed: %s \nRange: %s seconds \nFiring angle: %s CW from attach"""
		return Part.stats(self) + statString % stats
		
	def shortStats(self):
		stats = (self.bulletDamage, 60. / self.reloadTime)
		statString = """\n%s damage\n%s/minute"""
		return Part.shortStats(self) + statString % stats
		
	def attach(self):
		self.bulletImage = colorShift(BULLET_IMAGE, self.ship.color)
		Part.attach(self)
	
	def update(self):
		#reload cooldown:
		if self.reload > 0:
			self.reload -= 1. / self.game.fps
		Part.update(self)
	
	def getDPS(self):
		return 1.0 * self.bulletDamage / self.reloadTime
	
	def shoot(self):
		"""fires a bullet."""
		if self.acted: return
		self.acted = True
		s = self.ship
		if self.reload <= 0 and self.ship.energy > self.energyCost:
			self.reload = self.reloadTime / s.efficiency * s.cannonRateBonus
			self.ship.energy -= self.energyCost
			if soundModule:
				setVolume(shootSound.play(), self, self.game.player)
			self.game.curSystem.floaters.add( \
					Bullet(self.game, self, \
					self.bulletDamage * s.efficiency * s.damageBonus * s.cannonBonus, \
					self.bulletSpeed * s.cannonSpeedBonus,\
					self.bulletRange * s.cannonRangeBonus, image = self.bulletImage))

	
class LeftCannon(Cannon):#move to config
	baseImage = pygame.image.load("res/parts/leftgun" + ext).convert()
	shootPoint = 0, - 30
	shootDir = 270
	name = "Left Cannon"

class RightCannon(Cannon):#move to config
	baseImage = pygame.image.load("res/parts/rightgun" + ext).convert()
	shootPoint = 0, 30
	shootDir = 90
	name = "Right Cannon"
		
class StrafebatCannon(Cannon):#move to config
	baseImage = pygame.image.load("res/parts/strafebatgun" + ext).convert()
	shootDir = 180
	shootPoint = -20, 0
	bulletDamage = .5
	energyCost = 1
	name = "fore gun dam=.5"
	image = None
		
class Engine(Part):
	baseImage = pygame.image.load("res/parts/engine" + ext).convert()
	image = None
	name = "Engine"
	force = 24000
	thrusting = False
	energyCost = 1.
	def __init__(self, game):
		if Engine.animatedImage == None:
			Engine.animatedImage = pygame.image.load(\
					"res/parts/engine thrusting" + ext).convert_alpha()
		self.baseAnimatedImage = Engine.animatedImage
		self.baseAnimatedImage.set_colorkey((0,0,0))
		self.animated = True
		Part.__init__(self, game)
		self.width -= 6	#move the engines in 6 pixels.
		self.ports = []
		self.functions.append(self.thrust)
		self.functionDescriptions.append('thrust')
		
	def stats(self):
		stats = (self.force, self.energyCost)
		statString = """\nThrust: %s N\nCost: %s /second thrusting"""
		return Part.stats(self) + statString % stats
		
	def shortStats(self):
		stats = (self.force,)
		statString = """\n%s N"""
		return Part.shortStats(self) + statString % stats

	def update(self):
		""""""
		if self.thrusting:
			self.animated = True
		else:
			self.animated = False
		self.thrusting = False
		Part.update(self)
	
	def thrust(self):
		"""thrust: pushes the ship from the direction this engine points."""
		if self.acted: return
		self.acted = True
		if self.ship and self.ship.energy >= self.energyCost:
			accel = self.ship.efficiency * self.ship.thrustBonus \
					* self.force / self.ship.mass / self.game.fps
			dir = self.dir + self.ship.dir
			self.ship.dx += cos(dir) * accel
			self.ship.dy += sin(dir) * accel
			self.ship.energy -= self.energyCost / self.game.fps
			self.thrusting = True

class Cockpit(Part):
	baseImage = pygame.image.load("res/parts/cockpit" + ext).convert()
	image = None
	name = "Cockpit"
	def __init__(self, game):
		Part.__init__(self, game)
		self.ports = [Port((self.width / 2 - 2, 0), 180, self), \
					Port((0, self.height / 2 - 2), 270, self), \
					Port((-self.width / 2 + 2, 0), 0, self), \
					Port((0, -self.height / 2 + 2), 90, self)]

class Gyro(Part):
	baseImage = pygame.image.load("res/parts/gyro" + ext).convert()
	image = None
	name = "Gyro"
	torque = 180000 #N m degrees== m m kg degrees /s /s
	energyCost = .8
	def __init__(self, game):
		Part.__init__(self, game)
		self.ports = [Port((0, self.height / 2 - 2), 270, self), \
				Port((-self.width / 2 + 2, 0), 0, self), \
				Port((0, -self.height / 2 + 2), 90, self)]
		self.functions.extend([self.turnLeft,self.turnRight])
		self.functionDescriptions.extend(\
				[self.turnLeft.__doc__,self.turnRight.__doc__])
				
	def stats(self):
		stats = (self.torque, self.energyCost)
		statString = """\nTorque: %s N*m\nCost: %s \
energy/second of turning"""
		return Part.stats(self) + statString % stats
		
	def shortStats(self):
		stats = (self.torque,)
		statString = """\n%s N*m"""
		return Part.shortStats(self) + statString % stats
		
	def turnLeft(self, angle = None):
		"""rotates the ship counter-clockwise."""
		if self.acted: return
		self.acted = True
		if angle:
			angle = max(- self.torque / self.ship.moment / self.ship.game.fps \
					* self.ship.efficiency * self.ship.torqueBonus, -abs(angle) )
		else:
			angle = - self.torque / self.ship.moment / self.ship.game.fps \
					* self.ship.efficiency * self.ship.torqueBonus
		if self.ship and self.ship.energy >= self.energyCost:
			self.ship.dir = angleNorm(self.ship.dir + angle)
			self.ship.energy -= self.energyCost / self.game.fps
		
	def turnRight(self, angle = None):
		"""rotates the ship clockwise."""
		if self.acted: return
		self.acted = True
		if angle:
			angle = min(self.torque / self.ship.moment / self.ship.game.fps \
					* self.ship.efficiency * self.ship.torqueBonus, abs(angle) )
		else:
			angle = self.torque / self.ship.moment / self.ship.game.fps \
					* self.ship.efficiency * self.ship.torqueBonus
		if self.ship and self.ship.energy >= self.energyCost:
			self.ship.dir = angleNorm(self.ship.dir + angle)
			self.ship.energy -= self.energyCost / self.game.fps
	
class Generator(Part):
	baseImage = pygame.image.load("res/parts/generator" + ext).convert()
	image = None
	name = "Generator"
	rate = 6.
		
	def stats(self):
		stats = (self.rate,)
		statString = """\nEnergy Produced: %s/second"""
		return Part.stats(self) + statString % stats
		
	def shortStats(self):
		stats = (self.rate,)
		statString = """\n%s E/s"""
		return Part.shortStats(self) + statString % stats
		
	def update(self):
		if self.ship and self.ship.energy < self.ship.maxEnergy:
			self.ship.energy = min(self.ship.maxEnergy, \
					self.ship.energy + self.rate * self.ship.efficiency \
					* self.ship.generatorBonus / self.game.fps)
		Part.update(self)
	
class Battery(Part):
	baseImage = pygame.image.load("res/parts/battery" + ext).convert()
	image = None
	name = "Battery"
	capacity = 100
	
	def stats(self):
		stats = (self.capacity,)
		statString = """\nCapacity: %s energy"""
		return Part.stats(self) + statString % stats
		
	def shortStats(self):
		stats = (self.capacity,)
		statString = """\n%s E"""
		return Part.shortStats(self) + statString % stats
		
	def attach(self):
		self.ship.maxEnergy += self.capacity * self.ship.batteryBonus
		Part.attach(self)

class Shield(Part):
	baseImage = pygame.image.load("res/parts/shield" + ext).convert()
	image = None
	name = "Shield"
	shieldhp = 10
	shieldRegen = .30
	energyCost = 1.5
	def __init__(self, game): 
		Part.__init__(self, game)
		self.ports = []
	
	def stats(self):
		stats = (self.shieldhp, self.shieldRegen, self.energyCost)
		statString = """\nMax Shield: %s \nRegeneration Rate: %s/second \
		\nCost: %senergy/second of regeneration"""
		return Part.stats(self) + statString % stats
		
	def shortStats(self):
		stats = (self.shieldhp, self.shieldRegen)
		statString = """\n%s max \n% regen"""
		return Part.shortStats(self) + statString % stats
		
	def attach(self):
		self.ship.maxhp += self.shieldhp * self.ship.shieldMaxBonus
		Part.attach(self)
		
	def update(self):
		if self.ship and self.ship.hp <= self.ship.maxhp\
		and self.ship.energy > self.energyCost:
			if self.ship.hp == 0:
				self.ship.hp = .0001
			else:
				self.ship.hp = min(self.ship.maxhp, \
						self.ship.hp + self.shieldRegen \
						* self.ship.shieldRegenBonus/ self.game.fps)
				self.ship.energy -= self.energyCost / self.game.fps
		Part.update(self)


class Drone(Cockpit, Engine, Gyro, Cannon, Generator, Battery):
	baseImage = pygame.image.load("res/ship" + ext).convert()
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
	force = 10000
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
	
	def __init__(self,  game):
		if Drone.animatedImage == None:
			Drone.animatedImage = pygame.image.load("res/shipThrusting" + ext).convert_alpha()
		self.baseAnimatedImage = Drone.animatedImage
		self.baseAnimatedImage.set_colorkey((0,0,0))
		self.animated = True
		Part.__init__(self, game)
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
			s = self.ship
			s.energy -= self.shotCost * self.energyCost
			if soundModule:
				self.game.curSystem.floaters.add( \
					Bullet(self.game, self, \
					self.bulletDamage * s.efficiency * s.damageBonus * s.cannonBonus, \
					self.bulletSpeed * s.cannonSpeedBonus,\
					self.bulletRange * s.cannonRangeBonus, image = self.bulletImage))
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
			
	def turnLeft(self, angle = None):
		"""rotates the ship counter-clockwise."""
		if self.turned: return
		self.turned = True
		if angle:
			angle = max(- self.torque / self.ship.moment / self.ship.game.fps \
					* self.ship.efficiency * self.ship.torqueBonus, -abs(angle) )
		else:
			angle = - self.torque / self.ship.moment / self.ship.game.fps \
					* self.ship.efficiency * self.ship.torqueBonus
		if self.ship and self.ship.energy >= self.turnCost * self.energyCost:
			self.ship.dir = angleNorm(self.ship.dir + angle)
			self.ship.energy -= self.turnCost / self.game.fps * self.energyCost
		
	def turnRight(self, angle = None):
		"""rotates the ship clockwise."""
		if self.turned: return
		self.turned = True
		if angle:
			angle = min(self.torque / self.ship.moment / self.ship.game.fps \
					* self.ship.efficiency * self.ship.torqueBonus, abs(angle) )
		else:
			angle = self.torque / self.ship.moment / self.ship.game.fps \
					* self.ship.efficiency * self.ship.torqueBonus
		if self.ship and self.ship.energy >= self.turnCost * self.energyCost:
			self.ship.dir = angleNorm(self.ship.dir + angle)
			self.ship.energy -= self.turnCost / self.game.fps * self.energyCost



