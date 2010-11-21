#spaceship.py
	
from utils import *
from parts import *
from floaters import *
from pygame.locals import *
import stardog
from adjectives import addAdjective

def starterShip(game, x, y, dx = 0, dy = 0, dir = 270, script = None, \
				color = (255, 255, 255)):
	"""starterShip(x,y) -> default starting ship at x,y."""
	ship = Ship(game, x, y, dx = dx, dy = dy, dir = dir, \
				script = script, color = color)
	gyro = Gyro(game)
	generator = Generator(game)
	battery = Battery(game)
	cockpit = Cockpit(game)
	gun = LeftGun(game)
	gun2 = RightGun(game)
	engine1 = Engine(game)
	engine2 = Engine(game)
	for part in [gyro, generator, battery, cockpit, gun, gun2, engine1, engine2]:
		if rand() > .8:
			addAdjective(part)
			if rand() > .6:
				addAdjective(part)
		part.color = color
	ship.addPart(cockpit)
	cockpit.addPart(engine1, 0)
	cockpit.addPart(gun2, 1)
	cockpit.addPart(gyro, 2)
	cockpit.addPart(gun, 3)
	gyro.addPart(battery, 1)
	battery.addPart(generator, 0)
	generator.addPart(engine2, 0)
	ship.energy = ship.maxEnergy * .8
	ship.partAdded()
	return ship

def playerShip(game, x, y, dx = 0, dy = 0, dir = 270, script = None, \
				color = (255, 255, 255)):
	"""starterShip(x,y) -> default starting ship at x,y."""
	ship = starterShip(game, x, y, dx, dy, dir, script, color)
	script.bind(K_DOWN % 322, ship.reverse)
	script.bind(K_UP % 322, ship.forward)
	script.bind(K_RIGHT % 322, ship.turnRight)
	script.bind(K_LEFT % 322, ship.turnLeft)
	script.bind(K_RCTRL % 322, ship.shoot)
	script.bind(K_s % 322, ship.reverse)
	script.bind(K_w % 322, ship.forward)
	script.bind(K_e % 322, ship.left)
	script.bind(K_q % 322, ship.right)
	script.bind(K_d % 322, ship.turnRight)
	script.bind(K_a % 322, ship.turnLeft)
	script.bind(K_LCTRL % 322, ship.shoot)
	return ship

class Ship(Floater):
	"""Ship(x, y, dx = 0, dy = 0, dir = 270,
	script = None, color = (255,255,255)) 
	script should have an update method that 
	returns (moveDir, target, action)."""
	mass = 0
	moment = 0
	parts = []
	forwardEngines = []
	maxhp = 0
	hp = 0
	forwardThrust = 0
	reverseThrust = 0
	leftThrust = 0
	rightThrust = 0
	torque = 0
	reverseEngines = []
	leftEngines = []
	rightEngines = []
	guns = []
	missiles = []
	gyros = []
	number = 0
	name = 'Ship'
	def __init__(self, game, x, y, dx = 0, dy = 0, dir = 270, script = None, \
				color = (255, 255, 255)):
		Floater.__init__(self, game, x, y, dx, dy, dir, 1)
		self.inventory = []
		self.reload = 0
		self.energy = 0
		self.maxEnergy = 0
		self.color = color
		self.part = None
		if script: self.script = script
		else: self.script = Script(None, None)
		self.baseImage = pygame.Surface((200, 200), hardwareFlag | SRCALPHA).convert_alpha()
		self.baseImage.set_colorkey((0,0,0))
		self.functions = [self.forward, self.reverse, self.left, self.right, \
				self.turnLeft, self.turnRight, self.shoot, self.launchMissiles]
		self.functionDescriptions = []
		for function in self.functions:
			self.functionDescriptions.append(function.__doc__)

	def addPart(self, part):
		"""ship.addPart(part) -> Sets the main part for this ship.
		Only used for the base part (usually a cockpit), other parts are added to parts."""
		part.parent = self
		part.dir = 0
		part.offset = (0, 0)
		part.ship = self
		part.image = colorShift(part.baseImage, self.color).convert()
		part.image.set_colorkey((255,255,255))
		self.basePart = part
		self.partAdded()

	def partAdded(self):
		self.parts = []
		self.forwardEngines = []
		self.forwardThrust = 0
		self.reverseThrust = 0
		self.leftThrust = 0
		self.rightThrust = 0
		self.torque = 0
		self.reverseEngines = []
		self.leftEngines = []
		self.rightEngines = []
		self.guns = []
		self.missiles = []
		self.gyros = []
		#recalculate stats:
		self.partRollCall(self.basePart)
		minX, minY, maxX, maxY = 0, 0, 0, 0
		#TODO: ? make the center of the ship the center of mass instead of the 
		#center of the radii. 
		for part in self.parts:
			minX = min(part.offset[0] - part.radius, minX)
			minY = min(part.offset[1] - part.radius, minY)
			maxX = max(part.offset[0] + part.radius, maxX)
			maxY = max(part.offset[1] + part.radius, maxY)
		self.radius = max(maxX - minX, maxY - minY) / 2
		#recenter:
		xCorrection = (maxX + minX) / 2
		yCorrection = (maxY + minY) / 2
		self.mass = 1
		self.moment = 1
		self.maxEnergy = 1
		self.maxhp = 0
		partNum = 1
		for part in self.parts:
			part.number = partNum
			partNum += 1
			part.offset = 	part.offset[0] - xCorrection, \
							part.offset[1] - yCorrection
			part.attach()
		self.energy = min(self.energy, self.maxEnergy)
		self.hp = min(self.hp, self.maxhp)
		#redraw base image:
		self.baseImage = pygame.Surface((int(self.radius * 2), \
					int(self.radius * 2)), \
					hardwareFlag | SRCALPHA).convert_alpha()
		self.baseImage.set_colorkey((0,0,0))
		self.basePart.draw(self.baseImage)

	def partRollCall(self, part):
		"""adds parts to self.parts recursively."""
		if part:
			self.parts.append(part)
		if isinstance(part, Engine):
			if part.dir == 180:
				self.reverseEngines.append(part)
				self.reverseThrust += part.force
			if part.dir == 0:
				self.forwardEngines.append(part)
				self.forwardThrust += part.force
			if part.dir == 90:
				self.rightEngines.append(part)
				self.rightThrust += part.force
			if part.dir == 270:
				self.leftEngines.append(part)
				self.leftThrust += part.force
		if isinstance(part, Gyro):
			self.gyros.append(part)
			self.torque += part.torque
		if isinstance(part, Gun):
			self.guns.append(part)
		#if isinstance(part, missileLauncher):
			#self.missiles.append(part)
		for port in part.ports:
			if port.part:
				self.partRollCall(port.part)
				
	def forward(self):
		"""thrust forward using all forward engines"""
		for engine in self.forwardEngines:
			engine.thrust()
	def reverse(self):
		"""thrust backward using all reverse engines"""
		for engine in self.reverseEngines:
			engine.thrust()
	def left(self):
		"""strafes left using all left engines"""
		for engine in self.leftEngines:
			engine.thrust()
	def right(self):
		"""strafes right using all right engines"""
		for engine in self.rightEngines:
			engine.thrust()
	def turnLeft(self):
		"""Turns ccw using all gyros."""
		for gyro in self.gyros:
			gyro.turnLeft()
	def turnRight(self):
		"""Turns cw using all gyros."""
		for gyro in self.gyros:
			gyro.turnRight()
	def shoot(self):
		"""fires all guns."""
		for gun in self.guns:
			gun.shoot()
	def launchMissiles(self):
		for missles in self.missiles:
			missles.shoot()
	
	
	def update(self):
		#check if dead:
		if not self.parts or self.parts[0].hp <= 0:
			self.kill()

		#run script, get choices.
		self.script.update(self)

		# actual updating:
		Floater.update(self)
		#parts updating:
		if self.basePart:
			self.basePart.update()

	def draw(self, surface, offset = None, pos = (0, 0)):
		"""ship.draw(surface, offset) -> Blits this ship onto the surface. 
		 offset is the (x,y) of the topleft of the surface, pos is the
		 position to draw the ship on the surface, where pos=(0,0) is the
		 center of the surface. If offset is none, the ship will be drawn down 
		 and right from pos where pos(0,0) is the topleft of the surface."""
		#image update:
		#note: transform is counter-clockwise, opposite of everything else.
		buffer = pygame.Surface((self.radius * 2, self.radius * 2), \
				flags = hardwareFlag | SRCALPHA).convert_alpha()
		buffer.set_colorkey((0,0,0))
		self.image = pygame.transform.rotate(self.baseImage, \
									-self.dir).convert_alpha()
		self.image.set_colorkey((0,0,0))
		
		#imageOffset compensates for the extra padding from the rotation.
		imageOffset = [- self.image.get_width() / 2,\
					   - self.image.get_height() / 2]
		#offset is where on the input surface to blit the ship.
		if offset:
			pos =[self.x  - offset[0] + pos[0] + imageOffset[0], \
				  self.y  - offset[1] + pos[1] + imageOffset[1]]
				  
		#draw to buffer:
		surface.blit(self.image, pos)
		for part in self.parts:
			part.redraw(surface, offset)
		
		#shield:
		if self.hp > .0002:
			r = int(self.radius)
			shieldColor = (50,100,200, int(255. / 3 * self.hp / self.maxhp) )
			pygame.draw.circle(buffer, shieldColor, \
						(r, r), r, 0)
			pygame.draw.circle(buffer, (50,50,0,50), \
						(r, r), r, 5)
			rect = (0,0, r * 2, r * 2)
			pygame.draw.arc(buffer, (50,50,200,100), rect, + math.pi/2,\
							math.pi * 2 * self.hp / self.maxhp + math.pi/2, 5)
							
		#draw to input surface:
		pos[0] += - imageOffset[0] - self.radius
		pos[1] += - imageOffset[1] - self.radius
		surface.blit(buffer, pos) 
	def takeDamage(self, damage):
		self.hp = max(self.hp - damage, 0)


	def kill(self):
		"""play explosion effect than call Floater.kill(self)"""
		if soundModule:
			setVolume(explodeSound.play(), self, self.game.player)
		Floater.kill(self)
		for part in self.inventory:
			part.scatter(self)
