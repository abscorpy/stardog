
from utils import *
from menuElements import *
import stardog
from parts import Dummy

class Menu(TopLevelPanel):
	"""The top level menu object. Menu(mouse, rect) -> new Menu"""
	activeMenu = None
	color = (100, 100, 255, 250)
	def __init__(self, game, rect, thisShip):
		TopLevelPanel.__init__(self, rect)
		subFrameRect = Rect(84, 2, \
					self.rect.width - 86, self.rect.height-4)
		self.thisShip = thisShip
		self.parts = PartsPanel(subFrameRect, thisShip)
		self.keys = Keys(subFrameRect, thisShip)
		self.skills = Skills(subFrameRect)
		self.store = Store(subFrameRect)
		x = 2
		y = 2
		h = 24
		w = 80
		#TODO: rewrite these buttons as one Selecter. 
		self.panels.append(Button(Rect(x,y,w,h), \
				lambda : self.setActiveMenu(self.parts), "Parts", BIG_FONT))
		y += h + 2
		self.panels.append(Button(Rect(x,y,w,h), \
				lambda : self.setActiveMenu(self.keys), "Keys", BIG_FONT))
		y += h + 2
		self.panels.append(Button(Rect(x,y,w,h), \
				lambda : self.setActiveMenu(self.skills), "Skills", BIG_FONT))
		y += h + 2
		self.panels.append(Button(Rect(x,y,w,h), \
				lambda : self.setActiveMenu(self.store), "Store", BIG_FONT))
		y += h + 2
		self.setActiveMenu(self.parts)

	def setActiveMenu(self, menu):
		if self.activeMenu:
			self.panels.remove(self.activeMenu)
		self.activeMenu = menu
		self.panels.append(menu)
	
	def update(self):
		Panel.update(self)
		if self.activeMenu:
			self.activeMenu.update()

class PartsPanel(Panel):
	selectedPart = None
	selectedPort = None
	def __init__(self, rect, thisShip):
		Panel.__init__(self, rect)
		self.thisShip = thisShip
		x, y, w, h = rect.left, rect.top, rect.width, rect.height
		inventoryTop = y + h - PartTile.height - 6
		remove = Button(Rect(x + 2, \
				inventoryTop - 18, 100, 16), self.remove, " REMOVE")
		add = Button(Rect(x + 100 + 6, \
				inventoryTop - 18, 100, 16), self.add, " ADD/SWAP")
		paint = Button(Rect(x + 200 + 10, \
				inventoryTop - 18, 100, 16), self.paint, " PAINT PART")
		self.inventoryPanel = InventoryPanel(\
				Rect(x + 2, inventoryTop, w - 4, PartTile.height + 4), \
				thisShip.inventory)
		self.portPanel = \
				PortPanel(Rect(x + 2, y + 2, w / 2 - 2, inventoryTop - 4 - 18),\
				thisShip)
		x += w / 2
		self.descriptionShip = PartDescriptionPanel(\
				Rect(x + 2, y + 2, w / 2 - 4, inventoryTop / 2 - 4))
		y += inventoryTop / 2
		self.descriptionInventory = PartDescriptionPanel(\
				Rect(x + 2, y, w / 2 - 4, inventoryTop / 2 - 4))
		self.addPanel(self.descriptionShip)
		self.addPanel(self.descriptionInventory)
		self.addPanel(self.portPanel)
		self.addPanel(self.inventoryPanel)
		self.addPanel(remove)
		self.addPanel(add)
		self.addPanel(paint)
	
	def update(self):
		if self.portPanel.selected \
		and self.portPanel.selected.port.part != self.descriptionShip.part:
			self.descriptionShip.setPart(self.portPanel.selected.port.part)
		if self.inventoryPanel.selected \
		and self.inventoryPanel.selected.part != self.descriptionInventory.part:
			self.descriptionInventory.setPart(self.inventoryPanel.selected.part)
	
	def remove(self):
		"""removes the selected part from the ship and updates menus"""
		if self.portPanel.selected:
			self.descriptionInventory.setPart(self.portPanel.selected.port.part)
			self.descriptionShip.setPart(None)
			self.portPanel.unequip(self.portPanel.selected.port)
			self.thisShip.reset()
			self.portPanel.reset()
			self.inventoryPanel.reset()

	def add(self):
		"""adds the selected part to the ship and updates menus"""
		if self.portPanel.selected and self.inventoryPanel.selected:
			self.thisShip.inventory.remove(self.inventoryPanel.selected.part)
			self.descriptionInventory.setPart(self.portPanel.selected.port.part)
			self.remove()
			self.portPanel.selected.port.addPart(\
						self.inventoryPanel.selected.part)
			self.descriptionShip.setPart(self.inventoryPanel.selected.part)
			self.thisShip.reset()
			self.portPanel.reset()
			self.inventoryPanel.reset()
			self.inventoryPanel.selected = None
			self.portPanel.selected = None
			
	def paint(self):
		"""paints the selected part to match this ship."""
		if self.inventoryPanel.selected:
			part = self.inventoryPanel.selected.part
			part.color = self.thisShip.color
			part.image = colorShift(pygame.transform.rotate(part.baseImage, \
						-part.dir), part.color).convert()
			part.image.set_colorkey((255,255,255))
			self.inventoryPanel.reset()
					
class ShipPanel(Selecter):
	selected = None
	scale = 1,1
	text = None
	
	def __init__(self, rect, thisShip):
		Selecter.__init__(self, rect)
		self.thisShip = thisShip
		self.reset()
					
	def reset(self):
		self.scale = 2,2
		s = self.thisShip
		text = "Parts: %s/%s     Efficiency: %s\nMass: %s KG     Forward Thrust: %s N\nMoment: %s KG m      Torque: %s N m\nMax DPS: %s\nEnergy: %s/%s\nShields: %s/%s"\
				%(s.numParts, s.partLimit, s.efficiency, s.mass, \
				s.forwardThrust, int(s.moment), s.torque, \
				s.dps, s.energy, s.maxEnergy, s.hp, s.maxhp)
		self.removePanel(self.text)
		self.text = TextBlock(Rect(0,0,400,100), text, color = (100,200,0))
		self.addPanel(self.text)
		Panel.reset(self)
		
	def draw(self, surface, rect):
		double = pygame.transform.scale2x(self.thisShip.baseImage)
		self.image.blit(double, (100, 100))
		Selecter.draw(self, surface, rect)

class PartDescriptionPanel(Panel):
	"""displays descriptions of parts."""
	def __init__(self, rect):
		Panel.__init__(self, rect)
		self.part = None
		self.text = None
		self.name = None
		
	def setPart(self, part):
		self.part = part
		self.removePanel(self.text)
		self.removePanel(self.name)
		if not part or isinstance(part, Dummy):
			if self.image:
				self.image.fill((0,0,0,0))
			return
		self.image = pygame.Surface((self.rect.width, self.rect.height), \
					hardwareFlag).convert()
		self.image.set_colorkey((0,0,0))
		bigImage = pygame.transform.scale2x(self.part.image)
		bigImage.set_colorkey((255,255,255)) # idk why this one's white.
		self.image.blit(bigImage, (self.rect.width - 80, 60 - bigImage.get_height() / 2))
		string = part.stats()
		string += '\nFunctions: '
		for function in part.functions:
			string += function.__name__+' '
		if not part.functions: string += 'None'
		string += '\n'
		for adj in part.adjectives:
			string += "\n  %s: %s"%(str(adj.__class__).split('.')[-1], adj.__doc__)
		x, y, w, h = self.rect.left, self.rect.top, self.rect.width, self.rect.height
		self.name = Label(Rect(x + 4, y + 4, w, 20), part.name, FONT, (100, 200, 0))
		self.text = TextBlock(Rect(x + 4, y + 24, w, h), string, SMALL_FONT, (0, 150, 0))
		self.addPanel(self.name)
		self.addPanel(self.text)
	
	def reset(self):
		self.setPart(self.part)
		Panel.reset(self)
	
class PortPanel(ShipPanel):
	def unequip(self, port):
		"""a recursive helper method for remove."""
		if port.part and not isinstance(port.part,Dummy):
			part = port.part
			part.ship.inventory.append(part)
			for recursivePort in part.ports:
				self.unequip(recursivePort)
			part.parent = None
			part.ship.parts.remove(part)
			port.part = None
			self.reset
	
	def reset(self):
		"""remakes this panel to reflect ship changes."""
		ShipPanel.reset(self)
		self.dummify(self.thisShip.basePart)
		self.thisShip.reset()
		self.image.fill((0,0,0,0))
		self.panels = []
		self.selectables = []
		for part in self.thisShip.parts:
			for port in part.ports:
				self.addSelectable(PortButton(port, part, self.thisShip, self))
				self.selectables[-1].resize(self.scale)
		self.addPanel(self.text)
		Panel.reset(self)
		
	def dummify(self, part):
		for port in part.ports:
			if port.part == None:
				port.addPart(Dummy(self.thisShip.game))
			else:
				self.dummify(port.part)

class PartTile(Selectable):
	width = 150
	height = 150
	partImageOffset = 50,50
	def __init__(self, part, rect):
		"""PartTile(part, rect) -> new PartTile.
		The menu interface for a part. Display it like a button!"""
		self.part = part
		Selectable.__init__(self, rect)
		self.image = pygame.Surface((self.width,self.height), \
					hardwareFlag).convert()
		self.image.set_colorkey((0,0,0))
		bigImage = pygame.transform.scale2x(self.part.image)
		bigImage.set_colorkey((255,255,255)) # idk why this one's white.
		self.image.blit(bigImage, PartTile.partImageOffset)
		self.addPanel(Label(rect, part.name))
		self.panels[-1].rect.width = self.rect.width
		string = part.shortStats()
		i = string.find('\n')
		rect = Rect(rect)
		rect.y += 16; rect.x += 2
		self.addPanel(Label(rect, string[:i], color = (200,0,0)))
		self.panels[-1].rect.width = self.rect.width
		rect = Rect(rect)
		rect.y += 60
		self.addPanel(TextBlock(rect, string[i:], color = (0, 150, 0)))

class PortButton(Selectable):
	selectedColor = (200,50,50)
	inactiveColor = (150,150,250)
	activeColor = (250,250,250)
	selected = False
	width = 12
	scale = 2,2
	def __init__(self, port, part, thisShip, parent):
		self.port = port
		self.part = part
		self.thisShip = thisShip
		self.parent = parent
		Selectable.__init__(self, Rect(0,0,self.width,self.width))

	def resize(self, scale = (2,2)):
		self.scale = scale
		x = self.parent.rect.left + self.part.ship.radius * 2 + 5\
				+(self.port.offset[0] * cos(self.part.dir) \
				- self.port.offset[1] * sin(self.part.dir) \
				+ self.part.offset[0] ) * scale[0]#just looks right...
		y = self.parent.rect.top + self.part.ship.radius * 2 + 89\
				+ (self.port.offset[0] * sin(self.part.dir) \
				+ self.port.offset[1] * cos(self.part.dir) \
				+ self.part.offset[1] ) * scale[1]#just looks right...
		self.rect = Rect(x,y,self.width,self.width)
		
	def draw(self, surface, rect):
		if self.port.part: fill = 2 #fill
		else: fill = 2 #outline
		center = (self.rect.left + self.width / 2, \
				 self.rect.top + self.width / 2)
		pygame.draw.circle(surface, self.color, center, self.width / 2, fill)
	
class InventoryPanel(Selecter):
	selected = None
	def __init__(self, rect, partList):
		"""InventoryPanel(rect, partList) -> a Selecter that resets to the 
		provided list of parts."""
		Selecter.__init__(self, rect, vertical = False)
		self.partList = partList
		self.reset()

	def reset(self):
		self.selectables = []
		for part in self.partList:
			self.addSelectable(PartTile(part, \
						Rect(0,0,PartTile.width, PartTile.height)))
		Selecter.reset(self)

class Keys(Panel):
	bindingMessage = pygame.image.load("res/keybind.gif")
	"""the Keys panel of the menu."""
	def __init__(self, rect, thisShip):
		Panel.__init__(self, rect)
		self.thisShip = thisShip
		self.keyboardRect = Rect(self.rect.left + 2, self.rect.height - 204, \
							self.rect.width - 4, 202)
		self.functions = FunctionSelecter(\
					Rect(self.rect.width / 2 + self.rect.left,\
					self.rect.top, self.rect.width / 4 - 4,\
					self.rect.height - self.keyboardRect.height - 26), thisShip)
		self.addPanel(self.functions)
		self.bindings = BindingSelecter( \
					Rect(self.rect.width * 3 / 4 + self.rect.left,\
					self.rect.top, self.rect.width / 4 - 4,\
					self.rect.height - self.keyboardRect.height - 26), thisShip)
		self.addPanel(self.bindings)
		buttonTop = self.rect.height - self.keyboardRect.height - 24
		self.addPanel(Button(Rect(self.rect.width - 204, buttonTop, 100, 20), \
					self.bind, "Bind"))
		self.addPanel(Button(Rect(self.rect.width - 106, buttonTop, 100, 20), \
					self.unbind, "Unbind"))
		self.addPanel(PartFunctionsPanel(Rect(self.rect.left + 2, \
					self.rect.top + 2, 	self.rect.width / 2 - 4, \
					self.rect.height - self.keyboardRect.height - 2), thisShip))
		self.toggleMouseButton = Button(Rect(self.rect.left, self.rect.bottom - 20, 
								200,20), self.toggleMouse, "Turn Mouse Off")
		self.addPanel(self.toggleMouseButton)
		

	def toggleMouse(self):
		self.thisShip.game.mouseControl = not self.thisShip.game.mouseControl
		if self.thisShip.game.mouseControl:
			self.toggleMouseButton.image = FONT.render('Turn Mouse Off',\
						True, self.color)
		else: 
			self.toggleMouseButton.image = FONT.render('Turn Mouse On',\
						True, self.color)
		
	def unbind(self):
		"""Removes the currently selected binding."""
		if self.bindings.selected:
			self.thisShip.script.unbind(self.bindings.selected.keyNum, \
						self.bindings.selected.function)
			self.bindings.reset()
				
	def bind(self):
		"""binds the current function to a key it captures"""
		if self.functions.selected and isinstance(self.functions.selected, \
												FunctionSelectable):
			screen = self.thisShip.game.screen
			screen.blit(self.bindingMessage, (screen.get_width() / 2  \
								- self.bindingMessage.get_width() / 2, \
								screen.get_height() / 2))
			pygame.display.flip()
			key = self.captureKey()
			self.thisShip.script.bind(key, self.functions.selected.function)
			self.bindings.reset()
		
	def captureKey(self):
		"""Warning: Enters a loop for upto five seconds!
		captures the first pressed key and returns its number.""" 
		start = pygame.time.get_ticks()
		print 'cap key'
		while pygame.time.get_ticks() < start + 5000:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = 0
					return
				elif event.type == pygame.KEYDOWN:
					return event.key
		return 0
		
class PartFunctionsPanel(ShipPanel):
	labels = []
	
	def reset(self):
		ShipPanel.reset(self)
		for panel in self.labels:
			self.panels.remove(panel)
		self.labels = []
		for part in self.thisShip.parts:
			pos = part.offset[0] * self.scale[0] + self.rect.centerx - 100, \
					part.offset[1] * self.scale[1] + self.rect.centery
			self.labels.append(Label(Rect(pos,(20,20)), str(part.number), \
					font = BIG_FONT))
			self.addPanel(self.labels[-1])
		Panel.reset(self)
		
class FunctionSelecter(Selecter):
	def __init__(self, rect, ship):
		Selecter.__init__(self, rect)
		self.partsList = ship.parts
		self.thisShip = ship
		self.reset()
	
	def reset(self):
		self.selectables = []
		self.addSelectable(PresetSelectable("ship-wide presets", \
					Rect(0, 0, self.rect.width, 16)))
		for function in self.thisShip.functions:
			self.addSelectable(FunctionSelectable(function, \
						Rect(20, 0, self.rect.width, 16)))
					
		for part in self.partsList:
			self.addSelectable(PartHeaderSelectable(part, \
						Rect(0, 0, self.rect.width, 16)))
			for function in part.functions:
				self.addSelectable(FunctionSelectable(function, \
						Rect(20, 0, self.rect.width - 20, 16)))
		Selecter.reset(self)
							
class PresetSelectable(Selectable):
	def __init__(self, string, rect):
		self.name = string
		Selectable.__init__(self, rect)
		self.addPanel(Label(rect, string))
			
class FunctionSelectable(Selectable):
	def __init__(self, function, rect):
		self.function = function
		Selectable.__init__(self, rect)
		self.addPanel(Label(rect, function.__name__))
		
class PartHeaderSelectable(Selectable):
	def __init__(self, part, rect):
		self.part = part
		Selectable.__init__(self, rect)
		if part.number != -1:
			self.addPanel(Label(rect, '#' + str(part.number) + ' ' + part.name))
		else:
			self.addPanel(Label(rect, part.name))

class FunctionSelectable(Selectable):
	def __init__(self, function, rect):
		self.function = function
		Selectable.__init__(self, rect)
		self.addPanel(Label(rect, " " + function.__name__))
		
class BindingSelecter(Selecter):
	def __init__(self, rect, ship):
		Selecter.__init__(self, rect)
		self.bindings = ship.script.bindings
		self.reset()
		
	def reset(self):
		self.selectables = []
		for binding in self.bindings:
			Selecter.addSelectable(self,BindingSelectable(binding, \
						Rect(0, 0, self.rect.width, 20)))
		self.selectables.sort(cmp = lambda x,y: y.keyNum)
		Selecter.reset(self)
		
	def addSelectable(self, selectable):
		self.reset()
		
class BindingSelectable(Selectable):
	def __init__(self, binding, rect):
		self.keyNum = binding[0]
		self.function = binding[1]
		self.partNum = binding[1].im_self.number
		self.name = pygame.key.name(self.keyNum)
		Selectable.__init__(self, rect)
		self.addPanel(Label(rect, \
					" " + self.name + " - ", color = (100,200,100)))
		self.addPanel(Label( \
					Rect(self.panels[-1].rect.right, self.rect.top,0,0), \
					str(self.partNum) + ": ", color = (200,200,100)))
		self.addPanel(Label( \
					Rect(self.panels[-1].rect.right, self.rect.top,0,0), \
					str(self.function.__name__), color = (200,100,100)))	
		
class Skills(Panel):
	def __init__(self, rect):
		Panel.__init__(self, rect)
		self.addPanel(Label(Rect(self.rect.width / 2 - 60, 2, 0, 0),\
			"Skills", BIG_FONT))
		rect = Rect(100,100,100,100)
		self.addPanel(Button(Rect(100,100,100,100), \
					lambda:self.skill('modularity'), None, SMALL_FONT))
		rect = Rect(rect)
		rect.x, rect.y = rect.x + 2, rect.y + 2
		self.panels[-1].addPanel(TextBlock(rect,'Modularity:\nincrease the \nnumber of \nparts your \nship can have \nbefore losing \nefficiency.', SMALL_FONT, (100,200,0), 100))
		
	
	def skill(self, skillName):
		pass

class SkillTreeTab(Selectable):
	pass
class SkillTreeSelector(Selecter):
	pass
	
class Store(Panel):
	def __init__(self, rect):
		Panel.__init__(self, rect)
		self.addPanel(Label(Rect(self.rect.width / 2 - 60, 2, 0, 0),\
			"Store", BIG_FONT))
