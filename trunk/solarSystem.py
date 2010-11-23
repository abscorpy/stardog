#solarSystem.py

from utils import *
from floaters import *
from spaceship import *
from strafebat import *
from tinyFighter import *
from planet import *
from gui import *
import stardog

class SolarSystem:

	"""Game(resolution = None, fullscreen = False) 
	-> new game instance. Multiple game instances
	are probably a bad idea."""
	def __init__(self, game):
		self.game = game
		self.floaters = pygame.sprite.Group()
		self.ships = pygame.sprite.Group()
		self.bg = BG(self.game) # the background layer
		pygame.mixer.music.load("res/space music.ogg")
		pygame.mixer.music.play(-1)
		
	def update(self):
		"""Runs the game."""
		self.floaters.update()
		
		#collision:
		# TODO: sort lists to minimize collision tests.
		floaters = self.floaters.sprites()
		for i in range(len(floaters)):
			for j in range(i + 1, len(floaters)):
				collide(floaters[i], floaters[j])
		
	def draw(self, surface, offset):
		self.bg.draw(surface, self.game.player)
		for floater in self.floaters:
			r = floater.radius
			if (r + floater.x > offset[0] \
				and floater.x - r < offset[0] + self.game.width)\
			and (r + floater.y > offset[1] \
				and floater.y - r < offset[1] + self.game.height):
				floater.draw(surface, offset)
		
	def add(self, floater):
		"""adds a floater to this game."""
		self.floaters.add(floater)
		if isinstance(floater, Ship):
			self.ships.add(floater)
		
	def empty(self):
		self.ships.empty()
		self.floaters.empty()

class SolarA1(SolarSystem):
	respawnTime = 30
	fightersPerMinute = 5
	def __init__(self, game, player, numPlanets = 10):
		SolarSystem.__init__(self, game)
		self.sun = (Planet( game, 0, 0, radius = 4000, mass = 1000000, \
					color = (255, 255, 255), image = None)) # the star
		#place player:
		angle = randint(0,360)
		distanceFromSun = randint(10000, 40000)
		player.x = distanceFromSun * cos(angle)
		player.y = distanceFromSun * sin(angle)
		self.add(self.sun)
		self.planets = []
		#add planets:
		d = 10000
		for i in range(numPlanets):
			angle = randint(0,360)
			distanceFromSun = randint(d, d+5000)
			color = randint(40,255),randint(40,255),randint(40,255)
			radius = randint(100,500)
			mass = randnorm(radius * 10, 800)
			self.planets.append(Planet(game, distanceFromSun * cos(angle), \
				distanceFromSun * sin(angle), radius = radius, mass = mass, \
				color = color))
			self.add(self.planets[i])
			d+= 5000
				
		for planet in self.planets:
			planet.numShips = 0
			planet.ships = pygame.sprite.Group()
			planet.respawn = 0
			self.add(planet)
		self.fighterTimer = 2
			
	def update(self):
		SolarSystem.update(self)
		#enemy respawning:
		for planet in self.planets:
			if not planet.ships.sprites():
				if planet.respawn > 0:#countdown the timer
					planet.respawn -= 1. / self.game.fps
					continue
				elif planet.respawn < -100: #reset respawn timer
					planet.respawn = self.respawnTime
					continue
				else:
					#respawn now!
					planet.respawn = - 200#sentinal value
					planet.numShips += 1
					for i in range(planet.numShips):
						angle = randint(0, 360)
						x = planet.x + cos(angle) * (planet.radius + 300)
						y = planet.y + sin(angle) * (planet.radius + 300)
						ship = Strafebat(self.game, x, y, color = planet.color)
						planet.ships.add(ship)
						self.add(ship)
						ship.planet = planet
		if self.fighterTimer <= 0:
			angle = randint(0,360)
			distance = randint(1000, 4000)
			x = distance * cos(angle) + self.game.player.x
			y = distance * sin(angle) + self.game.player.y
			self.add(TinyFighter(self.game, x, y, self.game.player.dx, self.game.player.dy))
			self.fighterTimer = 60 / self.fightersPerMinute
		else:
			self.fighterTimer -= 1. / self.game.fps
		
	
def collide(a, b):
	"""test and act on spatial collision of Floaters a and b"""
	#Because this needs to consider the RTTI of two objects,
	#it is an external function.  This is messy and violates
	#good object-orientation, but when a new subclass is added
	#code only needs to be added here, instead of in every other
	#class.
	#test rect first (faster), then circle:
	if collisionTest(a, b):
		#planet/?
		if isinstance(b, Planet): tmp = a; a = b; b = tmp
		if isinstance(a, Planet):
			if  sign(b.x - a.x) == sign(b.dx - a.dx) \
			and sign(b.y - a.y) == sign(b.dy - a.dy):# moving away from planet.
				return False
			# planet/ship
			if isinstance(b, Ship):
				planet_ship_collision(a, b)
				return True
			if isinstance(b, Part) and b.parent == None:
				planet_freePart_collision(a, b)
				return True
		#shield ship/?
		if isinstance(b, Ship) and b.hp > 0: tmp = a; a = b; b = tmp
		if isinstance(a, Ship) and a.hp > 0:
			#shield ship/free part
			if isinstance(b, Part) and b.parent == None:
				ship_freePart_collision(a, b)
				return True
			#crash against ship's shields, if any:
			hit = False
			if b.hp >= 0 and (sign(b.x - a.x) == - sign(b.dx - a.dx) \
							or sign(b.y - a.y) == - sign(b.dy - a.dy)):
				# moving into ship, not out of it.
				crash(a,b)
				hit = True
				#if this ship no longer has shields:
				if a.hp <= 0:
					collide(a, b)
					return True
			#shield ship/no shield ship (or less shield than this one)
			if isinstance(b, Ship) and b.hp <= 0:
				for part in b.parts:
					if collide(a, part):
						#if that returned true, everything
						#should be done already.
						return True
			return hit

		#ship / ?
		if isinstance(b, Ship): tmp = a; a = b;	b = tmp
		if isinstance(a, Ship):
			#ship/free part
			if isinstance(b, Part) and b.parent == None:
				ship_freePart_collision(a, b)
				return True
							
			#recurse to ship parts
			for part in a.parts:
				if collide(b, part):#works for ship/ship, too.
					#if that returned true, everything
					#should be done already.
					return True
			return False
			
		#free part/free part
		if isinstance(b, Part) and b.parent == None \
		and isinstance(a, Part) and a.parent == None:
			return False #pass through each other, no crash.
		
		#floater/floater (no ship, planet)
		else:
			crash(a, b)
			return True
	return False

def planet_ship_collision(planet, ship):
	angle = atan2(planet.y - ship.y, planet.x - ship.x)
	dx, dy = rotate(ship.dx, ship.dy, angle)
	speed = sqrt(dy ** 2 + dx ** 2)
	if speed > planet.LANDING_SPEED:
		if planet.damage.has_key(ship):
			damage = planet.damage[ship]
		else:
			if soundModule:
				setVolume(hitSound.play(), planet, planet.game.player)
			#set damage based on incoming speed and mass.
			damage = speed * ship.mass * planet.PLANET_DAMAGE
		for part in ship.parts:
			if collisionTest(planet, part):
				temp = part.hp
				part.takeDamage(damage)
				damage -= temp
				if damage <= 0:
					r = ship.radius + planet.radius
					temp = ship.dx * -(ship.x - planet.x) / r \
							+ ship.dy * -(ship.y - planet.y) / r
					ship.dy = ship.dx * (ship.y - planet.y) / r \
							+ ship.dy * -(ship.x - planet.x) / r
					ship.dx = temp
					if planet.damage.has_key(ship):
						del planet.damage[ship]
					return
		if damage > 0:
			planet.damage[ship] = damage
	else:
		#landing:
				# if ship == planet.game.player:
					# planet.game.pause = True
		ship.dx, ship.dy = planet.dx, planet.dy

def planet_freePart_collision(planet, part):
	part.dx, part.dy = planet.dx, planet.dy
		
def ship_freePart_collision(ship, part):
	part.kill()
	ship.inventory.append(part)
	if ship.game.player == ship:
		ship.game.menu.parts.inventoryPanel.reset() #TODO: make not suck
	
def crash(a, b):
	if soundModule:
		setVolume(hitSound.play(), a, b)
	hpA = a.hp
	hpB = b.hp
	a.takeDamage(hpB)
	b.takeDamage(hpA)
	if stardog.debug:
		print a,(a.x,a.y),b,(b.x,b.y)