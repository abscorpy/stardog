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
	def __init__(self, game, x, y, color = (200,100,0)):
		roll = rand()
		self.target = game.player
		self.circling = False
		Ship.__init__(self, game, x, y, script = StrafebatScript(game), color = color)
		cockpit =StrafebatCockpit(game)
		gyro = Gyro(game)
		gun = StrafebatGun(game)
		engine = Engine(game)
		generator = Generator(game)
		battery = Battery(game)
		shield = Shield(game)
		rGun = RightGun(game)
		lGun = LeftGun(game)
		for part in [cockpit, gyro, gun, engine, generator, battery, shield, rGun, lGun]:
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
			generator.addPart(rGun, 0)
		if .7 < roll < .8:
			battery.addPart(lGun, 0)
		self.energy = self.maxEnergy


class StrafebatScript(AIScript):
	"""A scripts with basic physics calculation functions."""
	interceptSpeed = 100.
	returnSpeed = 50.
	acceptableError = 2
	sensorRange = 10000
	shootingRange = 400
	def update(self, ship):
		# if too close to planet
		if dist2(ship.planet, ship) < (300 + ship.planet.radius) ** 2: \
		#and (sign(ship.dx - ship.planet.dx) == - sign(ship.x - ship.planet.x) \
		#or sign(ship.dy - ship.planet.dy) == - sign(ship.y - ship.planet.y)): 
			if self.turnTowards(ship, ship.planet, 180):
				ship.forward()# move away from planet.
				return
				
		# find closest ship:
		ships = ship.game.curSystem.ships.sprites()
		target, distance2 = self.closestShip(ship, ships)
		
		if not target:# no target
			self.intercept(ship, ship.planet, self.returnSpeed)
			return
		
		if distance2 < self.shootingRange ** 2 \
		and ship.guns: # within range.
			self.interceptShot(ship, target)
			return
			
		self.intercept(ship, target, self.interceptSpeed)
		
			
	def closestShip(self, ship, ships):
		"""finds the closest ship not-friendly to this one."""
		target = None
		distance2 = self.sensorRange ** 2
		for ship2 in ships:
			tmp = dist2(ship2, ship)
			if tmp < distance2 \
			and ship2 != ship \
			and (not isinstance(ship2, Strafebat) \
				or ship2.planet != ship.planet):
					distance2 = tmp
					target = ship2
		return target, distance2
		
class StrafebatGun(Gun):
	shootDir = 180
	shootPoint = -20, 0
	bulletDamage = .5
	energyCost = 1
	name = "fore gun dam=.5"
	image = None
	def __init__(self,  game, parent = None):
		if StrafebatGun.image == None:
			StrafebatGun.image = pygame.image.load("res/parts/strafebatgun" \
												+ ext).convert()
			StrafebatGun.image.set_colorkey((0,0,0))
		self.baseImage = StrafebatGun.image
		Gun.__init__(self,  game, parent = None)
	
	
class StrafebatCockpit(Cockpit):
	pass
