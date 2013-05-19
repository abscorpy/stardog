#planet.py


from utils import *
from floaters import *
import parts
import stardog

class Planet(Floater):
	maxRadius = 1000000 # no gravity felt past this (approximation).
	PLANET_DAMAGE = .001
	LANDING_SPEED = 200 #pixels per second. Under this, no damage.
	g = 5000 # the gravitational constant.
	
	def __init__(self, game, x, y, radius = 100, mass = 10000, \
					color = (100,200,50), image = None):
		Floater.__init__(self, game, x, y, radius = radius, image = image)
		self.mass = mass
		self.hp = 100
		self.color = color
		self.damage = {}
		if image == None:
			self.image = None
	
	def update(self):
		self.hp = 100
		for other in self.game.curSystem.floaters.sprites():
			if  not isinstance(other, Planet) \
			and not collisionTest(self, other) \
			and abs(self.x - other.x) < self.maxRadius \
			and abs(self.y - other.y) < self.maxRadius:
				#accelerate that floater towards this planet:
				accel = self.g * (self.mass) / dist2(self, other)
				angle = atan2(self.y - other.y, self.x - other.x)
				other.dx += cos(angle) * accel / self.game.fps
				other.dy += sin(angle) * accel / self.game.fps
	
	def draw(self, surface, offset = (0,0)):
		if self.image:
			pos = int(self.x - self.image.get_width()  / 2 - offset[0]), \
				  int(self.y - self.image.get_height() / 2 - offset[1])
			surface.blit(self.image, pos)
				  
		else:
			pos = int(self.x - offset[0]), \
				  int(self.y - offset[1])
			pygame.draw.circle(surface, self.color, pos, int(self.radius))
		
	def takeDamage(self, damage):
		pass