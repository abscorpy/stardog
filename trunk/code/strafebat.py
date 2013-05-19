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
	shootingRange = 400
		
	def attack(self, ship, target):
		if ship.guns and dist2(ship, target) < self.shootingRange ** 2:
			speed = ship.guns[0].speed
			time = dist(ship.x, ship.y, target.x, target.y) / speed
			dummy = Ballistic(target.x, target.y, \
											target.dx - ship.dx, target.dy - ship.dy)
			pos = self.predictBallistic(dummy, time)
			angle = atan2(pos[1] - ship.y, pos[0] - ship.x)
			if self.turnToDir(ship, angle):
					ship.shoot()
			return True
		return False

class StrafebatCockpit(Cockpit):
	pass
