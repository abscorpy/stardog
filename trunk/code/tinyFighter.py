#tinyFighter.py


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
	timeOut = 30
	level = .5
	def __init__(self, game, x, y, dx = 0, dy = 0, color = (120, 180, 120)):
		self.target = game.player
		self.circling = False
		Ship.__init__(self, game, x, y, dx, dy, 
						script = TinyFighterScript(game), color = color)
		self.baseBonuses['damageBonus'] = .5
		self.addPart(Drone(game))
		self.energy = self.maxEnergy
		self.inventory.append(randItem(self.game, self.level))


class TinyFighterScript(AIScript):
	"""a script for tiny fighters."""
	swarmRadius = 280
	retreatRadius = 300
	shootingRange = 280
	interceptSpeed = 200
	def update(self, ship, dt):
		busy = False
		target = ship.target
		if self.game.debug: print "tiny fighter in stage %s"%(ship.stage,)
		
		if ship.stage == "persue":	
			#pursue until we match speed
			
			#only avoid planets in pursue stage.
			planet = self.findClosestPlanet(Ship, ship.system.planets[0])
			if planet and self.avoidPlanet(ship, planet):
				return
			
			dx = target.dx - ship.dx
			dy = target.dy - ship.dy
			self.persue(ship, target)
			if -50 < dx < 50 and -50 < dy < 50:
				ship.stage = "charge"
				
		elif ship.stage == "charge":
								
			self.attack(ship, target)
			
			if ship.timeOut <= 0:
				ship.stage = "persue"
			ship.timeOut -= dt
			if distance <= self.retreatRadius - self.swarmRadius:
				ship.stage = "retreat"
				
		elif ship.stage == "retreat":
			distance = dist(ship.x, ship.y, target.x, target.y)
			if distance < self.retreatRadius:
				if self.turnToTarget(ship, target, 180):
					ship.forward()
			if distance > self.swarmRadius:
				ship.stage = "persue"
				
	def attack(self, ship, target):
			distance = dist(ship.x, ship.y, target.x, target.y) - self.swarmRadius
			turnTime = ship.moment / ship.torque * 180
			
			if self.relativeSpeed(ship, target) > - self.interceptSpeed:
				if self.turnToTarget(ship, target):
					ship.forward()
			if distance <= self.shootingRange:
					ship.shoot()

	def relativeSpeed(self, ship, target):
		"""relativeSpeed2(ship, target) -> the relative speed between two
		floaters. Note that this is negative if they are getting closer."""
		#distance next second - distance this second (preserves sign):
		return sqrt((ship.x + ship.dx - target.x - target.dx)**2 \
								+ (ship.y + ship.dy - target.y - target.dy)**2) \
						- sqrt((ship.x - target.x)**2 + (ship.y - target.y)**2)
