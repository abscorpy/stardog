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
	"""A SolarSystem holds ships and other floaters."""
	boundries = ((-30000, 30000), (-30000, 30000))
	drawEdgeWarning = False
	calmMusic = "res/sound/music simple.ogg"
	alertMusic = "res/sound/music alert.ogg"
	musicDuration = 98716
	musicPos = 0
	sun = None
	def __init__(self, game):
		self.game = game
		self.floaters = pygame.sprite.Group()
		self.ships = pygame.sprite.Group()
		self.planets = pygame.sprite.Group()
		self.specialOperations = []
		self.onScreen = []
		self.bg = BG(self.game) # the background layer
		self.playMusic(False)
		#collisionGrid:
		self.collisionGrid = []
		for i in range(100):
			self.collisionGrid.append([])
			for j in range(100):
				self.collisionGrid[-1].append([])
		
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
			
		
	def update(self):
		"""Runs the game."""
		self.floaters.update()
		# for floater in self.onScreen:
			# floater.update()
			
		# grid = self.collisionGrid
		# # empty the collisionGrid
		# for col in grid:
			# for cell in range(len(col)):
				# col[cell] = []
		# #refill the grid:
		# size = ((self.boundries[0][1] - self.boundries[0][0]) 
						# / len(grid))
		# for floater in self.floaters:
			# x = int(floater.x / size)
			# y = int(floater.y / size)
			# grid[x][y].append(floater)
			# floater.collisionCell = x,y
		# # collision:
		# for col in range(len(grid) - 1):
			# for row in range(len(grid[col]) - 1):
				# floaters = grid[col][row]
				# #the cells below, right, and below-right:
				# others = []
				# others.extend(grid[col+1][row])
				# others.extend(grid[col  ][row+1])
				# others.extend(grid[col+1][row+1])
				# for i in range(len(floaters)):
					# #test against others in this cell:
					# for j in range(i + 1, len(floaters)):
						# collide(floaters[i], floaters[j])
					# #test against others in later adjacent cells.
					# for j in others:
						# collide(floaters[i], j)
		# # (don't need to check prior adjacent because the other floater 
		# # already did.	
		# # the sun is too big for a grid.  Check it against all:
		# if self.sun:
			# for floater in self.floaters:
				# collide(self.sun, floater)
		# #see collide() at bottom of this module.
		
		#keep ships inside system boundries for now:
		edge = self.boundries
		if self.drawEdgeWarning:
			self.drawEdgeWarning -= 1. * self.game.dt
			if self.drawEdgeWarning <=0:
				self.drawEdgeWarning = False
		
		for floater in self.floaters:
			if (floater.x < edge[0][0] and floater.dx < 0 
			or floater.x > edge[0][1] and floater.dx > 0):
				if isinstance(floater, Ship):
					floater.dx = 0
					if floater == self.game.player:
						self.drawEdgeWarning = 1.
				else:
					floater.kill()
			if (floater.y < edge[1][0] and floater.dy < 0 
			or floater.y > edge[1][1] and floater.dy > 0):
				if isinstance(floater, Ship):
					floater.dy = 0
					if floater == self.game.player:
						self.drawEdgeWarning = 1.
				else:
					floater.kill()
		
		#list floaters that are on screen now:
		self.onScreen = []
		offset = (self.game.player.x - self.game.width / 2, 
				self.game.player.y - self.game.height / 2)
		for floater in self.floaters:
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
			self.ships.add(floater)
		if isinstance(floater, Planet):
			self.planets.add(floater)
		
	def empty(self):
		self.ships.empty()
		self.floaters.empty()
		self.planets.empty()

class SolarA1(SolarSystem):
	tinyFighters = []
	maxFighters = 15
	respawnTime = 30
	fightersPerMinute = 2
	def __init__(self, game, player, numPlanets = 10):
		SolarSystem.__init__(self, game)
		self.sun = (Sun( game, 0, 0, radius = 4000, mass = 180000, 
					color = (255, 255, 255), image = None)) # the star
		planetImage = loadImage('res/planets/Rocky 1.bmp')
		#place player:
		angle = randint(0,360)
		distanceFromSun = randint(8000, 18000)
		player.x = 20000
		player.y = 4000
		#add asteroids:
		for i in range(500):
			x = randint(-30000, 30000) 
			y = randint(-30000, 30000) 
			radius = randint(10, 60)
			dx = randint( -20, 20)
			dy = randint( -20, 20)
			self.add(Asteroid(game, x, y, dx, dy, radius))
		race1 = game.race1
		race2 = game.race2
		self.add(self.sun)
		self.fighterTimer = 40
		#add planets:
		planets = [
			Planet(game, -1935, -5889, 240, 600, (220,50,0), race = race1,
					life = .3, resources = 1.8, name = 'a', image = planetImage),
			Planet(game, 3868, 7385, 800, 2000, (220,50,0), race = race2,
					life = 1.5, resources = 1.0, name = 'b'),
			Planet(game, -6379, 4000, 1120, 2800, (220,50,0), race = race1,
					life = 1.5, resources = 1.0, name = 'c'),
			Planet(game, 6072, -9942, 1200, 3000, (220,50,0), race =  race1,
					life = 2.0, resources = .8, name = 'd'),
			Planet(game, 12294, 9696, 800, 2000, (220,50,0), race = race2,
					life = 1.0, resources = .6, name = 'e'),
			Planet(game, -16528, -13975, 2000, 5000, (220,50,0), race = race1,
					life = .1, resources = .5, name = 'f'),
			Planet(game, -3689, 19050, 1400, 3500, (220,50,0), race = race2,
					life = .6, resources = 1.4, name = 'g'),
			Planet(game, 24865, -2585, 400, 1000, (220,50,0), race = race2,
					life = .8, resources = .8, name = 'h', image = planetImage),
			]
		for p in planets:
			self.add(p)
			
	def update(self):
		SolarSystem.update(self)
		
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
			self.fighterTimer -= 1. * self.game.dt * 0

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
	if a.tangible and b.tangible and collisionTest(a, b):
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
			#shield ship/free part
			if isinstance(b, Part) and b.parent == None:
				ship_freePart_collision(a, b)
				return True
			#crash against ship's shields, if any:
			hit = False
			if (b.hp >= 0 and (sign(b.x - a.x) == - sign(b.dx - a.dx) 
							or sign(b.y - a.y) == - sign(b.dy - a.dy))):
				# moving into ship, not out of it.
				crash(a,b)
				hit = True
				#if this ship no longer has shields, start over:
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
		if isinstance(b, Ship): a,b = b,a
		if isinstance(a, Ship):
			#ship/free part
			if isinstance(b, Part) and b.parent == None:
				ship_freePart_collision(a, b)
				return True
							
			#recurse to ship parts
			hit = False
			for part in a.parts:
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
			if ship.hp > 0:
				#damage shields
				temp = ship.hp
				ship.hp -= damage
				damage -= ship.hp
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
		for part in ship.parts:
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
		if ship == planet.game.player and not ship.landed:
			planet.game.pause = True
			ship.landed = planet
			ship.game.menu.parts.reset()
		ship.dx, ship.dy = planet.dx, planet.dy

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
		ship.game.menu.parts.inventoryPanel.reset() #TODO: make not suck
	
def explosion_push(explosion, floater):
	"""The push of an explosion.  The rest of the effect is handled by the
	collision branching, which continues."""
	force = (explosion.force / 
			not0(dist2(explosion, floater)) * explosion.radius ** 2)
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
	
