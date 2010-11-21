#intro.py
from menuElements import *

class IntroMenu(TopLevelPanel):
	color = (100, 100, 255, 250)
	def __init__(self, game, rect):
		TopLevelPanel.__init__(self, rect)
		self.game = game
		self.addPanel(Label(Rect(100,30,200,20), \
				"Choose a color:", color = (250,250,250),\
				font = BIG_FONT))
		self.running = True
		for x in range((self.rect.width - 100) / 60):
			for y in range((self.rect.height - 120) / 60):
				self.addPanel(ColorButton(self, \
						Rect(x * 60 + 50, y * 60 + 70, 50, 50),\
						(randint(0,255),randint(0,255),randint(0,255))))
			
	def chooseColor(self, color):
		self.game.playerColor = color
		self.running = False
	
class ColorButton(Button):
	def __init__(self, parent, rect, color):
		self.myColor = color
		self.parent = parent
		Button.__init__(self, rect, self.choose, None)
		
	def draw(self, surface, rect):
		pygame.draw.rect(surface, self.myColor, self.rect) 
		Panel.draw(self, surface, rect)
		
	def choose(self):
		self.parent.chooseColor(self.myColor)
		