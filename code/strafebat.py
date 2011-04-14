#strafebat.py

from utils import *
from spaceship import *
from parts import *
from scripts import *
import stardog
from adjectives import *

class Strafebat(Ship):
	strafeRadius = 100
	planet = None
	level = 3
	def __init__(self, game, x, y, color = (200,100,0), race = None):
		roll = rand()
		self.target = game.player
		self.circling = False
		Ship.__init__(self, game, x, y, script = StrafebatScript(game), 
						color = color, race = race)
		self.baseBonuses['damageBonus'] = .5
		cockpit =StrafebatCockpit(game)
		gyro = Gyro(game)
		gun = StrafebatCannon(game)
		engine = Engine(game)
		generator = Generator(game)
		battery = Battery(game)
		shield = Shield(game)
		rCannon = RightCannon(game)
		lCannon = LeftCannon(game)
		for part in [cockpit, gyro, gun, engine, generator, battery, shield, 
						rCannon, lCannon]:
			if rand() > .8:
				addAdjective(part)
				if rand() > .6:
					addAdjective(part)
			part.color = color
		self.addPart(cockpit)
		cockpit.addPart(gun, 0)
		cockpit.addPart(gyro, 2)
		gyro.addPart(engine, 1)
		gyro.addPart(generator, 0)
		if .9 < roll:
			generator.addPart(battery, 0)
			gyro.addPart(shield, 2)
		else: 
			gyro.addPart(battery, 2)
		if .8 < roll < .9:
			generator.addPart(rCannon, 0)
		if .7 < roll < .8:
			battery.addPart(lCannon, 0)
		self.energy = self.maxEnergy


class StrafebatScript(AIScript):
	"""A scripts with basic physics calculation functions."""
	interceptSpeed = 100.
	returnSpeed = 50.
	acceptableError = 2
	sensorRange = 3
	shootingRange = 400
	def update(self, ship):
		# if too close to planet
		if self.avoidPlanet(ship):
			ship.color = (255,255,255)
			if ship.thrusting: ship.color = (255,255,0)
			return
		ship.color = ship.race.color
		# find closest ship:
		ships = ship.game.curSystem.ships.sprites()
		ship.target, distance2 = self.closestEnemyShip(ship, ships)
		if distance2 > self.sensorRange ** 2:
			ship.target = None
		
		if not ship.target:# no target
			self.intercept(ship, ship.planet, self.returnSpeed)
			ship.target = ship.planet
			return
		
		if distance2 < self.shootingRange ** 2 \
		and ship.guns: # within range. Shoot at it.
			self.interceptShot(ship, ship.target)
			return
			
		#see it, but not in range. move towards it.
		self.intercept(ship, ship.target, self.interceptSpeed)
			
	def closestEnemyShip(self, ship, ships):
		"""finds the closest ship not-friendly to this one."""
		target = None
		distance2 = self.sensorRange ** 2
		for ship2 in ships:
			tmp = dist2(ship2, ship)
			if (tmp < distance2 and ship2 != ship and ship2.race != ship.race):
				distance2 = tmp
				target = ship2
		return target, distance2
		
class StrafebatCockpit(Cockpit):
	pass
