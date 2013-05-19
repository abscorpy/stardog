#solarSystem.py

from utils import *
from floaters import *
from spaceship import *
from strafebat import *
from tinyFighter import *
from planet import *
from gui import *
from updater import Updater
import stardog

class SolarSystem:
	"""A SolarSystem holds ships and other floaters, music, the background. 
	It calls update() and draw() on its members and handles collisions.."""
	boundries = 150000
	drawEdgeWarning = False
	calmMusic = "res/sound/music simple.ogg"
	alertMusic = "res/sound/music alert.ogg"
	musicDuration = 98716
	musicPos = 0
	sun = None
	def __init__(self, game):
		self.game = game
		self.floaters = Updater(self)
		self.ships = []
		self.planets = []
		self.specialOperations = []
		self.onScreen = []
		self.bg = BG(self.game) # the background layer
		self.playMusic(False)

	def playMusic(self, alert = False):
		self.musicPos = ((self.musicPos + pygame.mixer.music.get_pos())
							% self.musicDuration)
		pygame.mixer.music.stop()
		if alert:
			pygame.mixer.music.load(self.alertMusic)
		else:
			pygame.mixer.music.load(self.calmMusic)
		pygame.mixer.music.play(-1, self.musicPos / 1000.)
		pygame.mixer.music.set_volume(.15)


	def update(self, dt):
		"""Runs the game."""

		#note that self.floaters is an Updater, which provides optimizations.
		#update floaters:
		screen = Rect((self.game.player.x - self.game.width / 2,
				self.game.player.y - self.game.height / 2),
				(self.game.width, self.game.height))
		self.floaters.update(dt, screen)
		
		#check collisions:
		collisions = self.floaters.collisions()
		for f1,f2 in collisions:
			collide(f1,f2)

		#keep ships inside system boundaries for now:
		if self.drawEdgeWarning:
			self.drawEdgeWarning -= 1. * self.game.dt
			if self.drawEdgeWarning <=0:
				self.drawEdgeWarning = False
		for floater in self.floaters.frame:
			if (floater.x ** 2 + floater .y ** 2) > self.boundries ** 2:
				if isinstance(floater, Ship):
					floater.dx, floater.dy = 0, 0
					if floater == self.game.player:
						self.drawEdgeWarning = 1.
				else:
					floater.kill()

		#list floaters that are on screen now:
		self.onScreen = []
		offset = (self.game.player.x - self.game.width / 2,
				self.game.player.y - self.game.height / 2)
		for floater in self.floaters.sprites():
			r = floater.radius
			if (floater.x + r > offset[0]
			and floater.x - r < offset[0] + self.game.width
			and floater.y + r > offset[1]
			and floater.y - r < offset[1] + self.game.height):
					self.onScreen.append(floater)


	def draw(self, surface, offset):
		self.bg.draw(surface, self.game.player)
		for floater in self.onScreen:
				floater.draw(surface, offset)

	def add(self, floater):
		"""adds a floater to this game."""
		floater.system = self
		self.floaters.add(floater)

		if isinstance(floater, Ship):
			self.ships.append(floater)
		if isinstance(floater, Planet):
			self.planets.append(floater)

	def remove(self, floater):
		self.floaters.remove(floater)
		if floater in self.planets:
			self.planets.remove(floater)
		if floater in self.ships:
			self.ships.remove(floater)

	def empty(self):
		self.ships.empty()
		self.floaters.empty()
		self.planets.empty()

class SolarA1(SolarSystem):
	"""This is intended to be an instance of a solar system, a data file
	It should only contain things that will be unique to a particular solar
	system.  Eventually there will be dozens of these in their own data file."""
	tinyFighters = []
	maxFighters = 15
	respawnTime = 30
	fightersPerMinute = 2
	def __init__(self, game, player):
		SolarSystem.__init__(self, game)
		self.sun = (Sun( game, radius = 4000, mass = 600000.,
					color = (255, 255, 255), image = None)) # the star
		rockyPlanetImage = loadImage('res/planets/Rocky 2.bmp')
		gasPlanetImage = loadImage('res/planets/Gas Giant 1.bmp')
		#place player:
		angle = randint(0,360)
		distanceFromSun = randint(15000, 25000)
		player.x = distanceFromSun * cos(angle)
		player.y = distanceFromSun * sin(angle)
		#add asteroids:
		for i in range(100):
			x = randint(-30000, 30000)
			y = randint(-30000, 30000)
			radius = randint(10, 60)
			angle = atan2(y, x) + 90
			vel = sqrt(self.sun.mass * self.sun.g / dist(x, y, self.sun.x, self.sun.y))
			dx = vel * cos(angle) + randint(-20, 20)
			dy = vel * sin(angle) + randint(-20, 20)
			self.add(Asteroid(game, x, y, dx, dy, radius))

		self.add(self.sun)
		self.fighterTimer = 40
		self.createPlanets(game)
		
	def createPlanets(self, game):
		"""randomly generates some planets for this system."""
		planetname = 'abcdefghijklmnopqrstuvwxyz'
		distance = self.sun.radius * 1.1 + randint(0,1000)
		p = 0
		while distance < self.boundries - 3000:
			distance, planet = planetGenerator(
									game,
									planetname[p], 
									choice((game.race1,game.race2)),
									self.sun,
									distance)
			self.add(planet)
			p += 1

	def update(self, dt):
		SolarSystem.update(self, dt)

		#tiny fighters:
		if self.fighterTimer <= 0 and len(self.tinyFighters) < self.maxFighters:
			numSpawn = randint(1,3)
			for i in range(numSpawn):
				angle = randint(0,360)
				distance = randint(1000, 4000)
				x = distance * cos(angle) + self.game.player.x
				y = distance * sin(angle) + self.game.player.y
				fighter = TinyFighter(self.game, x, y, self.game.player.dx,
									self.game.player.dy)
				self.add(fighter)
				self.tinyFighters.append(fighter)
				self.fighterTimer = 60 / self.fightersPerMinute
		else:
			self.fighterTimer -= 1. * self.game.dt

class SolarF7(SolarSystem):
	def __init__(self, game):
		SolarSystem.__init__(self, game)



def collide(a, b):
	"""test and act on spatial collision of Floaters a and b"""
	#Because this needs to consider the RTTI of two objects,
	#it is an external function.  This is messy and violates
	#good object-orientation, but when a new subclass is added
	#code only needs to be added here, instead of in every other
	#class.
	if a.tangible and b.tangible:
		#planet/?
		if isinstance(b, Planet): a,b = b,a
		if isinstance(a, Planet):
			if (sign(b.x - a.x) == sign(b.dx - a.dx)
			and sign(b.y - a.y) == sign(b.dy - a.dy)):# moving away from planet.
				return False
			# planet/ship:
			if isinstance(b, Ship):
				planet_ship_collision(a, b)
				return True
			#planet/part:
			if isinstance(b, Part) and b.parent == None:
				planet_freePart_collision(a, b)
				return True
			#planet/planet:
			if isinstance(b, Planet):
				planet_planet_collision(a,b)
				return True
		#explosion/floater:
		if isinstance(b, Explosion): a,b = b,a
		if isinstance(a, Explosion):
			explosion_push(a,b)
			#but don't return!
		#shield ship/?:
		if isinstance(b, Ship) and b.hp > 0: a,b = b,a
		if isinstance(a, Ship) and a.hp > 0:
			hit = False
			#shield ship/free part:
			if isinstance(b, Part) and b.parent == None:
				ship_freePart_collision(a, b)
				return True
			#shield/shield or shield/attached part:
			if (b.hp >= 0 and (sign(b.x - a.x) == - sign(b.dx - a.dx)
							or sign(b.y - a.y) == - sign(b.dy - a.dy))):
				# moving into ship, not out of it.
				crash(a,b)
				hit = True
				#if this ship no longer has shields, start over:
				if a.hp <= 0:
					collide(a, b)
					return True
			#shield ship/no shield ship (maybe because shields just died):
			if isinstance(b, Ship) and b.hp <= 0:
				for part in reversed(b.parts[:]):	#reversed so cockpit is last, copied in case damage removes an item from the list.
					if collide(a, part):
						#if that returned true, everything
						#should be done already.
						return True
			return hit

		#ship / ?
		if isinstance(b, Ship): a,b = b,a
		if isinstance(a, Ship):
			#ship/free part
			if isinstance(b, Part) and b.parent == None:
				ship_freePart_collision(a, b)
				return True

			#recurse to ship parts
			hit = False
			for part in reversed(a.parts[:]):	#reversed so cockpit is last, copied in case damage removes an item from the list.
				if collide(b, part):#works for ship/ship, too.
					#if that returned true, everything
					#should be done already.
					hit = True
			return hit

		#free part/free part
		if (isinstance(b, Part) and b.parent == None
		and isinstance(a, Part) and a.parent == None):
			return False #pass through each other, no crash.
		if isinstance(a, Asteroid) and isinstance(b, Asteroid):
			return asteroid_asteroid_collision(a, b)
		#floater/floater (no ship, planet)
		else:
			crash(a, b)
			return True
	return False

def planet_ship_collision(planet, ship):
	if isinstance(planet, Sun):
		ship.kill()
		return
	#get planet velocity to compare with ship's
	orbvel = sqrt(planet.g * planet.game.curSystem.sun.mass * (2/planet.distance-1/planet.SMa))
	smi = planet.SMa * planet.p
	vx = orbvel * -planet.SMa * math.sin(planet.EccAn) / sqrt((smi * math.cos(planet.EccAn)) ** 2 \
	+ (planet.SMa * math.sin(planet.EccAn)) ** 2)
	vy = orbvel * smi * math.cos(planet.EccAn) / sqrt((smi * math.cos(planet.EccAn)) ** 2 \
	 + (planet.SMa * math.sin(planet.EccAn)) ** 2)
	planetvel = rotate(vx, vy, planet.LPe)
	speed = sqrt((planetvel[0] - ship.dx) ** 2 + (planetvel[1] - ship.dy) ** 2)
	if speed > planet.LANDING_SPEED and not ship.landed:
		if planet.damage.has_key(ship):
			damage = planet.damage[ship]
		else:
			if soundModule:
				setVolume(hitSound.play(), planet, planet.game.player)
			#set damage based on incoming speed and mass.
			damage = speed * ship.mass * planet.PLANET_DAMAGE
			if ship.hp > 0:
				#damage shields
				temp = ship.hp
				ship.hp -= damage
				damage -= ship.hp
				if damage <= 0:
					r = ship.radius + planet.radius
					dx, dy = ship.dx - planetvel[0], ship.dy - planetvel[1]
					ship.dx = planet.bounciness * (dx * -(ship.x - planet.x) / r
							+ dy * -(ship.y - planet.y) / r) + planetvel[0]
					ship.dy = planet.bounciness * (dx * (ship.y - planet.y) / r
							+ dy * -(ship.x - planet.x) / r) + planetvel[1]
					if planet.damage.has_key(ship):
						del planet.damage[ship]
					return
		for part in reversed(ship.parts[:]):	#reversed so cockpit is last, copied in case damage removes an item from the list.
			if collisionTest(planet, part):
				temp = part.hp
				part.takeDamage(damage, planet)
				damage -= temp
				if damage <= 0:
					r = ship.radius + planet.radius
					temp = (ship.dx * -(ship.x - planet.x) / r
							+ ship.dy * -(ship.y - planet.y) / r)
					ship.dy = (ship.dx * (ship.y - planet.y) / r
							+ ship.dy * -(ship.x - planet.x) / r)
					ship.dx = temp
					if planet.damage.has_key(ship):
						del planet.damage[ship]
					return
		if damage > 0:
			planet.damage[ship] = damage
	else:
		#landing:
		if not ship.landed:
			ship.landed = planet
			ship.game.menu.parts.reset()
			ship.land = atan2(ship.y - planet.y, ship.x - planet.x)
			if ship == ship.game.player and ship.thrusting == False:
				ship.game.pause = True

def planet_freePart_collision(planet, part):
	part.kill()
	planet.inventory.append(part)

def planet_planet_collision(a, b):
	if a.mass > b.mass:
		b.kill()
	else:
		a.kill()

def ship_freePart_collision(ship, part):
	part.kill()
	ship.inventory.append(part)
	if ship.game.player == ship:
		ship.game.menu.parts.inventoryPanel.reset()

def explosion_push(explosion, floater):
	"""The push of an explosion.  The rest of the effect is handled by the
	collision branching, which continues."""
	force = (explosion.force /
			not0(dist2(explosion, floater) * explosion.radius ** 2))
	dir = atan2(floater.y - explosion.y, floater.x - explosion.x)
	accel = force / not0(floater.mass)
	floater.dx += accel * cos(dir) * explosion.game.dt
	floater.dy += accel * sin(dir) * explosion.game.dt

def asteroid_asteroid_collision(a, b):
	"""merge the two into one new asteroid."""
	x,y = (a.x + b.x) / 2, (a.y + b.y) / 2
	dx = (a.dx * a.mass + b.dx * b.mass) / (a.mass + b.mass)
	dy = (a.dy * a.mass + b.dy * b.mass) / (a.mass + b.mass)
	radius = sqrt((a.radius ** 2 * pi + b.radius ** 2 * pi) / pi) - 1
	if a.radius > b.radius: image = a.image
	else: image = b.image
	a.kill()
	b.kill()
	a.system.add(Asteroid(a.game, x, y, dx, dy, radius, image = image))

def crash(a, b):
	if soundModule:
		setVolume(hitSound.play(), a, b)
	hpA = a.hp
	hpB = b.hp
	if hpB > 0: a.takeDamage(hpB, b)
	if hpA > 0: b.takeDamage(hpA, a)

