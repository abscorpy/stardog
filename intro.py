#intro.py
from menuElements import *

squareWidth = 80
squareSpacing = squareWidth + 10

class IntroMenu(TopLevelPanel):
	color = (100, 100, 255, 250)
	def __init__(self, game, rect):
		TopLevelPanel.__init__(self, rect)
		self.game = game
		self.running = True
		self.colorChoose()
		
	def colorChoose(self):
		self.panels = []
		self.addPanel(Label(Rect(100,30,200,20), \
				"Choose a color:", color = (250,250,250),\
				font = BIG_FONT))
		for x in range((self.rect.width - 100) / (squareSpacing)):
			for y in range((self.rect.height - 120) / (squareSpacing)):
				self.addPanel(ColorButton(self, \
						Rect(x * squareSpacing + 50, y * squareSpacing + 70,\
						squareWidth, squareWidth),\
						(randint(0,255),randint(0,255),randint(0,255))))
						
	def typeChoose(self):
		self.panels = []
		x = self.rect.left + 50
		y = self.rect.top + 100
		self.addPanel(TypeButton(self, Rect(x,y,100,120), 'fighter'))
		x += 200
		self.addPanel(TypeButton(self, Rect(x,y,100,120), 'interceptor'))
		x += 200
		self.addPanel(TypeButton(self, Rect(x,y,100,120), 'destroyer'))
			
	def chooseColor(self, color):
		self.game.playerColor = color
		self.typeChoose()
	
	def chooseType(self, type):
		self.game.playerType = type
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
		
class TypeButton(Button):
	def __init__(self, parent, rect, type):
		self.image = colorShift(loadImage('res/'+type+'.bmp', None),
						parent.game.playerColor,None)
		self.parent = parent
		self.type = type
		Button.__init__(self, rect, self.choose, None)
		
	def choose(self):
		self.parent.chooseType(self.type)
	
	