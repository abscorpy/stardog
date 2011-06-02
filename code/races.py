#races.py

from utils import *
from strafebat import *
from planet import Sun

class Race:
	planets = []
	parts = []
	adjectives = []
	playerRepute = 0
	playerCredits = 0
	enemies = []
	allies = []
	ships = []
	shipScripts = []
	script = None
	
	def __init__(self, game, name, color = (255,0,0)):
		self.game = game
		self.name = name
		self.color = color
		self.targetPlanet = None
		
	def update(self, dt):
		#find geographic mean of planets in system:
		x,y = 0,0
		count = 0
		enemies = []
		for planet in self.game.curSystem.planets:
			if isinstance(planet, Sun):
				continue
			if planet.race == self:
				x += planet.x
				y += planet.y
				count += 1
			else: 
				enemies.append(planet)
		if not enemies:
			print "%s owns the entire system!"%(self,)
			return
		if count:
			x /= count
			y /= count
		# set target to enemy closest to mean.
		self.targetPlanet = min(enemies, key = lambda p: dist(p.x,p.y,x,y))
		
	
	def updateShip(self, ship, dt):
		if self.targetPlanet:
			ship.planet = self.targetPlanet
		
	def updatePlanet(self, planet):
		planet.population += (1 * planet.life * self.game.dt)
		planet.buildProgress += (planet.population / 1000. * planet.resources 
									* self.game.dt)
		#print planet.name, planet.population, planet.buildProgress, planet.shipValue
		#start building new ship:
		if not planet.shipInProgress:
			angle = randint(0, 360)
			x = planet.x + cos(angle) * (planet.radius + 300)
			y = planet.y + sin(angle) * (planet.radius + 300)
			planet.shipInProgress = Strafebat(self.game, 
									x, y, color = self.color, race = self)
			planet.shipValue = planet.shipInProgress.value
		#complete ship construction:
		if planet.buildProgress >= planet.shipValue:
			planet.buildProgress = 0
			self.game.curSystem.add(planet.shipInProgress)
			planet.shipInProgress.planet = planet
			planet.shipInProgress = None
			
			
			
			
