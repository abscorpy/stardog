#stardog.py

debug = True
FPS = 30
FULL = False; RESOLUTION = 1024, 800 #test
#FULL = True; RESOLUTION = None #play

from utils import *
import pygame
from pygame.locals import *
import sys

if __name__=="__main__":
	#command line resolution selection:
	if len(sys.argv) > 1:
		try:
			if sys.argv[1] == 'f' or sys.argv[1] == 'full':
				FULL = True
				RESOLUTION = None
			else:
				FULL = False
			if len(sys.argv) == 4 \
			and 300 <= int(sys.argv[2]) < 4000 \
			and	300 <= int(sys.argv[3]) < 4000:
				RESOLUTION = int(sys.argv[2]), int(sys.argv[3])
		except:
			print("bad command line arguments.")
	#set up the disply:
	pygame.init()
	#pygame.display.init()
	if not RESOLUTION:
		RESOLUTION = pygame.display.list_modes()[0]
	if FULL:
		screen = pygame.display.set_mode(RESOLUTION, \
						hardwareFlag | pygame.FULLSCREEN | pygame.SRCALPHA)
	else:
		screen = pygame.display.set_mode(RESOLUTION, \
							hardwareFlag | pygame.SRCALPHA)

from menus import *
from scripts import *
from solarSystem import *
from gui import *
from planet import *
from spaceship import *
from strafebat import *
from intro import *
# import yaml
# import yamlpygame

class Game:
	"""Game(resolution = None, fullscreen = False)
	-> new game instance. Multiple game instances
	are probably a bad idea."""
	menu = None
	def __init__(self, screen):
		self.pause = False
		stardog.debug = True
		self.pause = False
		self.fps = FPS
		self.screen = screen
		self.top_left = 0, 0
		self.width = screen.get_width()
		self.height = screen.get_height()
		self.mouseControl = True
		#key polling:
		self.keys = []
		for _i in range (322):
			self.keys.append(False)
		#mouse is [pos, button1, button2, button3,..., button6].
		#new Apple mice think they have 6 buttons.
		self.mouse = [(0, 0), 0, 0, 0, 0, 0, 0]
		#pygame setup:
		self.clock = pygame.time.Clock()
		
		self.hud = HUD(self) # the heads up display
		
						
		self.playerScript = InputScript(self)
		
	def run(self):
		"""Runs the game."""
		
		self.running = True
		while self.running:
			# initialize starting ships:
			# eventually this will be replaced by loading solarSystems 
			# from files. 
			intro = IntroMenu(self, Rect(100, 100, self.width - 200,\
						self.height - 200))
			while self.running and intro.running:
				#event polling:
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						pygame.quit()
						return
					intro.handleEvent(event)
				intro.update()
				self.screen.fill((0, 0, 0, 0))
				intro.draw(self.screen)
				pygame.display.flip()
			#setup initial state:
			self.player = playerShip(self, 0,0, script = self.playerScript,
							color = self.playerColor, type = self.playerType)
			self.curSystem = SolarA1(self, self.player)
			self.curSystem.add(self.player)
			
			self.menu = Menu(self, Rect(100, 100, self.width - 200,\
					self.height - 200), self.player)
			for x in range(10):
				self.clock.tick()
			#The in-round loop (while player is alive and has enemies):
			while self.running and self.curSystem.ships.has(self.player):
				#event polling:
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						self.running = 0
					elif event.type == pygame.MOUSEBUTTONDOWN:
						self.mouse[event.button] = 1
						self.mouse[0] = event.pos
					elif event.type == pygame.MOUSEBUTTONUP:
						self.mouse[event.button] = 0
						self.mouse[0] = event.pos
					elif event.type == pygame.MOUSEMOTION:
						self.mouse[0] = event.pos
					elif event.type == pygame.KEYDOWN:
						self.keys[event.key % 322] = 1
					elif event.type == pygame.KEYUP:
						self.keys[event.key % 322] = 0
					if self.pause:
						self.menu.handleEvent(event)
						
				#game-level key input:
				if self.keys[K_DELETE % 322]:
					self.keys[K_DELETE % 322] = False
					self.player.kill() #suicide
				if self.keys[K_RETURN % 322]:
					self.pause = not self.pause #pause/menu
					self.keys[K_RETURN % 322] = False
					if self.pause:
						self.menu.reset()
				stardog.debug = False
				if self.keys[K_BACKSPACE % 322]:
					stardog.debug = True #print debug information
					self.keys[K_BACKSPACE % 322] = False
					print "Debug:"
				#ctrl+q or alt+F4 quit:
				if self.keys[K_LALT % 322] and self.keys[K_F4 % 322] \
				or self.keys[K_RALT % 322] and self.keys[K_F4 % 322] \
				or self.keys[K_LCTRL % 322] and self.keys[K_q % 322] \
				or self.keys[K_RCTRL % 322] and self.keys[K_q % 322]:
					self.running = False
					
					
				#unpaused:
				if not self.pause:
					#update action:
					self.curSystem.update()
					self.top_left = self.player.x - self.width / 2, \
							self.player.y - self.height / 2
							
				#draw the layers:
				self.screen.fill((0, 0, 0, 0))
				self.curSystem.draw(self.screen, self.top_left)
				self.hud.draw(self.screen, self.player)
				
				#paused:
				if self.pause:
					self.menu.update()
					self.menu.draw(self.screen)
					
				#frame maintainance:
				pygame.display.flip()
				self.clock.tick(FPS)#aim for FPS but adjust vars for self.fps.
				self.fps = max(1, int(self.clock.get_fps()))
	
if __name__ == '__main__':
	try:
		pass
		import psyco
		#psyco.full()
	except ImportError:
		print 'this game may run faster if you install psyco.'
	game = Game(screen)
	game.run()
