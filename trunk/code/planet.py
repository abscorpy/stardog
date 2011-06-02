#planet.py


from utils import *
from floaters import Floater
from adjectives import randItem
import parts
import partCatalog

import stardog

class Planet(Floater):
	maxRadius = 1000000 # no gravity felt past this (approximation).
	PLANET_DAMAGE = .0004
	LANDING_SPEED = 200 #pixels per second. Under this, no damage.
	g = 5000 # the gravitational constant.
	shipInProgress = None
	shipValue = 0
	hp = 30000
	gravitates = False
	def __init__(self, game, x, y, radius = 100, mass = 1000, 
					color = (100,200,50), image = None, name = 'planet',
					race = None, population = 1, life = 1, resources = 1):
		Floater.__init__(self, game, x, y, radius = radius)
		self.mass = mass #determines gravity.
		self.color = color
		self.damage = {}
		# damage[ship] is the amount of damage a ship has yet to take, 
		# see solarSystem.planet_ship_collision
		self.race = race #race that owns this planet
		self.population = population
		self.life = life #growth rate depends on value.
		self.resources = resources #build rate depends on resources and pop.
		self.buildProgress = 100
		self.name = name
		if image == None:
			self.image = None
		else:
			self.image = pygame.transform.rotate(pygame.transform.scale(
							image, (radius * 2, radius * 2)), -atan2(y,x))
		self.inventory = []
		self.inventory.append(partCatalog.TakeOffEngine(game))
		for x in range(randint(1,4)):
			self.inventory.append(randItem(game, 1))
		self.cities = self.population / 1000
	
	def update(self, dt):
		if self.race:
			self.race.updatePlanet(self)
		for other in self.game.curSystem.floaters:
			if  (other.gravitates 
			and abs(self.x - other.x) < self.maxRadius
			and abs(self.y - other.y) < self.maxRadius
			and not collisionTest(self, other) ):
				#accelerate that floater towards this planet:
				accel = self.g * (self.mass) / dist2(self, other)
				angle = atan2(self.y - other.y, self.x - other.x)
				other.dx += cos(angle) * accel * dt
				other.dy += sin(angle) * accel * dt
			
	def draw(self, surface, offset = (0,0)):
		if self.image:
			pos = (int(self.x - self.image.get_width()  / 2 - offset[0]), 
				  int(self.y - self.image.get_height() / 2 - offset[1]))
			surface.blit(self.image, pos)
		
		else:
			pos = int(self.x - offset[0]), \
				  int(self.y - offset[1])
			pygame.draw.circle(surface, self.color, pos, int(self.radius))
	
	def takeDamage(self, damage, other):
		pass
	
class Sun(Planet):
	PLANET_DAMAGE = 300
	LANDING_SPEED = -999 #no landing on the sun.
	t = 0
	
	def draw(self, surface, offset = (0,0)):
		if self.image:
			pos = (int(self.x - self.image.get_width()  / 2 - offset[0]), 
				  int(self.y - self.image.get_height() / 2 - offset[1]))
			surface.blit(self.image, pos)
		
		else:
			pos = int(self.x - offset[0]), \
				  int(self.y - offset[1])
			for x in range(21):
				color = (255 , 55 + (200 - (20 - x) * abs(10 - self.t % 20)), 100 / 20 * x)
				pygame.draw.circle(surface, color, pos, int(self.radius - 20 * x))
		self.t -= 24. * self.game.dt #speed of throbbing color.
		
		
		
		
		
			
			
