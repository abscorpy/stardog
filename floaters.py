#floaters.py

from utils import *
from pygame.locals import *
import stardog

FPS = 200
MISSILE_RADIUS = 50

def setVolume(channel, floater1, floater2):
	"""sets volume for a channel based on the distance between
	 the player and floater."""
	if channel and floater1 and floater2:
		channel.set_volume(.25 / (min(1, \
						(floater2.x - floater1.x) ** 2 + \
						(floater2.y - floater1.y) ** 2 + .0001)))

BULLET_IMAGE = pygame.image.load("res/shot" + ext).convert()
BULLET_IMAGE.set_colorkey((0,0,0))
DEFAULT_IMAGE = pygame.image.load("res/default" + ext).convert()
DEFAULT_IMAGE.set_colorkey((0,0,0))


		
class Ballistic:
	"""an abstraction of a Floater.  Just has a x,y,dx,dy."""
	def __init__(self, x, y, dx = 0, dy = 0):
		self.x, self.y = x, y
		self.dx, self.dy = dx, dy
			
class Floater(pygame.sprite.Sprite, Ballistic):
	"""creates a floater with position (x,y) in pixels, speed (dx,dy) 
	in pixels per second, direction dir 
	where 0 is pointing right and 270 is pointing up, radius radius 
	(for collision testing), and with the image image.  Image should be a 
	string of a file name without an axtension- there should be both a .gif 
	and	a .bmp, which is used depends on the pygame support on the run
	system."""
	x, y = 0., 0.
	dx, dy = 0., 0.
	dir = 0
	hp = 1
	radius = 10
	baseImage = None
	color = (200, 200, 0)
	mass = 1

	def __init__(self, game, x, y, dx = 0., dy = 0., dir = 270, radius = 10, \
			image = None):
		pygame.sprite.Sprite.__init__(self)
		self.game = game
		self.dir = dir
		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy
		self.radius = radius
		if (not image):
			image = DEFAULT_IMAGE
		#rotate() takes a counter-clockwise angle. 
		self.image = pygame.transform.rotate(image, -self.dir).convert()
		self.image.set_colorkey((0,0,0))
		self.rect = self.image.get_rect()

	def update(self):
		"""updates this floater based on its variables"""
		self.x += self.dx / self.game.fps
		self.y += self.dy / self.game.fps
		self.rect.center = (self.x, self.y)
		# if self.hp <= 0:
			# self.kill()

	def takeDamage(self, damage, other):
		self.hp -= damage
		if self.hp <= 0:
			self.kill()

	def draw(self, surface, offset = (0,0)):
		"""Blits this floater onto the surface. """
		pos = self.x - self.image.get_width()  / 2 - offset[0], \
			  self.y - self.image.get_height() / 2 - offset[1]
		surface.blit(self.image, pos)

class Bullet(Floater):
	def __init__(self, game, gun, image = None):
		dir = gun.dir + gun.ship.dir
		cost = cos(dir) #cost is short for cos(theta)
		sint = sin(dir)
		x = gun.x + gun.shootPoint[0] * cost\
						- gun.shootPoint[1] * sint + gun.ship.dx / game.fps
		y = gun.y + gun.shootPoint[0] * sint\
						+ gun.shootPoint[1] * cost + gun.ship.dy / game.fps
		dir += gun.shootDir # not needed for the offset, but needed for the dir.
		self.speed = gun.bulletSpeed
		dx = self.speed * cos(dir) + gun.ship.dx
		dy = self.speed * sin(dir) + gun.ship.dy
		if image == None:
			image = BULLET_IMAGE
		Floater.__init__(self, game, x, y, dx = dx, dy = dy, \
							dir = dir, radius = gun.bulletRadius, \
							image = image)
		self.image.set_colorkey((255,255,255))
		self.range = gun.bulletRange
		self.hp = gun.bulletDamage
		self.life = 0.
		self.ship = gun.ship
		if 'target' in gun.ship.__dict__:
			self.target = gun.ship.target

	def update(self):
		self.life += 1. / self.game.fps
		Floater.update(self)
		if self.life > self.range:
			self.kill()

class UnguidedMissile(Bullet):
	life = 0
	explode = False

	def __init__(self, game, ship):
		Bullet.__init__(self, game, ship)
		self.image = pygame.transform.rotate(MISSILE_IMAGE, -self.dir)
		self.image.set_colorkey((0,0,0))
		self.dx = MISSILE_SPEED * cos(ship.dir) + ship.dx
		self.dy = MISSILE_SPEED * sin(ship.dir) + ship.dy
		self.time = (dist(ship.target[0], ship.target[1], self.game.width / 2, \
                          self.game.height / 2) - ship.radius) / MISSILE_SPEED

	def update(self):
		self.life += 1
		self.dir = (self.dir + 180) % 360 - 180
		Floater.update(self)
		if self.life > self.time:
			self.kill()

	def detonate(self):
		explosion = Explosion(self.game, self.x, self.y, \
					self.dx - cos(self.dir) * MISSILE_SPEED / 2, \
					self.dy - sin(self.dir) * MISSILE_SPEED / 2, \
				MISSILE_RADIUS, MISSILE_TIME, MISSILE_DAMAGE)
		self.game.curSystem.add(explosion)

	def kill(self):
		self.detonate()
		if soundModule:
			setVolume(missileSound.play(), self, self.game.player)
		Floater.kill(self)

class Explosion(Floater):
	life = 0

	def __init__(self, game, x, y, dx = 0, dy = 0, radius = 10,\
				time = 1, damage = 0):
		image = pygame.Surface((radius * 2, radius * 2), flags = hardwareFlag).convert()
		image.set_colorkey((0,0,0))
		Floater.__init__(self, game, x, y, dx, dy, radius = 0,\
				image = image)			
		self.maxRadius = int(radius)
		self.radius = 0
		self.time = time
		self.damage = damage
		self.hp = 0

	def update(self):
		Floater.update(self)
		self.life += 1
		if self.life > self.time:
			Floater.kill(self)
		#grow or shrink: size peaks at time / 2:
		if self.life < self.time / 4:
			self.radius = int(self.maxRadius * self.life * 4 / self.time)
		else:
			self.radius = int(self.maxRadius * (self.time * 4 / 3 \
						- self.life * 4 / 3) / self.time)
		self.image.fill((0, 0, 0, 0))
		#draw the explosion this frame:
		#TODO: move this into a draw method.
		for _circle in range(self.radius / 4):
			color = (randint(100, 155), randint(000, 100), randint(0, 20), \
					randint(100, 255))
			radius = randint(self.radius / 4, self.radius / 2)
			r = randint(0, self.radius - radius)
			theta = randint(0, 360)
			offset = (int(cos(theta) * r + self.maxRadius), \
					  int(sin(theta) * r + self.maxRadius))
			pygame.draw.circle(self.image, color, offset, radius)

	def kill(self):
		self.hp = self.damage / FPS
		











