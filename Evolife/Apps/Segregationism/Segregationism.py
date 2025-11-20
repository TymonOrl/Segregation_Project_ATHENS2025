#!/usr/bin/env python3
""" @brief  Emergence of segregationism:
Though individual agents show only slight preference for being surrounded by similar agent, homogeneous patches emerge.
"""
		
#============================================================================#
# EVOLIFE  http://evolife.telecom-paris.fr             Jean-Louis Dessalles  #
# Telecom Paris  2025-11-18                                www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
#============================================================================#
# Documentation: https://evolife.telecom-paris.fr/Classes/annotated.html     #
#============================================================================#


##############################################################################
# Segregationism (after Thomas Schelling's work)                             #
##############################################################################

# Thomas Schelling (1971) studied the dynamics of residential segregation
		# to elucidate the conditions under which individual decisions about where to live
		# will interact to produce neighbourhoods that are segregated by race.
		# His model shows that this can occur even though individuals do not act
		# in a coordinated fashion to bring about these segregated outcomes.
		# Schelling proposed a prototype model in which individual agents are of two types,
		# say red and blue, and are placed randomly on the squares of a checkerboard.
		# The neighbourhood of an agent is defined to be the eight squares adjoining his location.
		# Each agent has preferences over the composition of his neighbourhood,
		# defined as the proportion of reds and blues. In each period, the most dissatisfied
		# agent moves to an empty square provided a square is available that he prefers
		# to his current location. The process continues until no one wants to move.

		# The typical outcome is a highly segregated state, although nobody actually
		# prefers segregation to integration. 


from PIL import Image # Loading city maps

import sys
sys.path.append('..')
sys.path.append('../../..')

import Evolife.Ecology.Observer				as EO
import Evolife.Scenarii.Parameters 			as EPar
import Evolife.Graphics.Evolife_Window 	as EW
import Evolife.Ecology.Individual			as EI
import Evolife.Ecology.Group				as EG
import Evolife.Ecology.Population			as EP
import Evolife.Graphics.Landscape			as Landscape


import random
# random.seed(4444)

Land = None	# to be instantiated
Observer = None	# to be instantiated
choices = [1, 2, 3]    # 1:low budget, 2: medium, 3:high
weights = [0.3, 0.6, 0.1]   # probabilities for budgets 1, 2, 3
price_choices = [1, 2, 3]    # 1:low price, 2: medium, 3:high
price_weights = [0.2, 0.6, 0.2]   # probabilities for prices 1, 2, 3
CUSTOM_COLOURS = [
			'red10', 'red7', 'red4',
			'blue10', 'blue7', 'blue4'
		]

class Observer(EO.Observer):
	def Field_grid(self):
		# return  [(30,0,'#EEAA99',340, 30, 40, '#EEAA99', 340)]
		return  []

class Scenario(EPar.Parameters):
	def __init__(self):
		# Parameter values
		
		import os
		base_path = os.path.dirname(__file__)
		params_path = os.path.join(base_path, '_Params.evo')

		EPar.Parameters.__init__(self, CfgFile=params_path)
		
		#EPar.Parameters.__init__(self, CfgFile='_Params.evo')	# loads parameters from configuration file
		#############################
		# Global variables		    #
		#############################

		AvailableColours = ['red', 'blue', 'brown', 'yellow', 7] + list(range(8, 21))	# corresponds to Evolife colours
		self.Colours = AvailableColours[:self['NbColours']]	
		#self.Budgets = [1, 2, 3]   
		self.addParameter('NumberOfGroups', self['NbColours'])	# may be used to create coloured groups

	def new_agent(self, Indiv, parents):	pass
	
class Individual(EI.Individual):
	""" Defines individual agents
	"""
	def __init__(self, Scenario, ID=None, Newborn=True, location=None):
		EI.Individual.__init__(self, Scenario, ID=ID, Newborn=Newborn)
		self.satisfied = False	# if false, the individual will move
		self.location = location # initialize the location
		self.BaseColour = None
		self.Budget = None
		self.setColourAndBudget('black', None)


	def setColourAndBudget(self, Colour, Budget):	
		self.BaseColour = Colour
		if Colour == 'red':
			if Budget == 1:
				self.Colour = 'red10'
			elif Budget == 2:
				self.Colour = 'red7'
			else:
				self.Colour = 'red4'
		elif Colour == 'blue':
			if Budget == 1:
				self.Colour = 'blue10'
			elif Budget == 2:
				self.Colour = 'blue7'
			else:
				self.Colour = 'blue4'
		else:
			self.Colour = Colour
		self.Budget = Budget
		if self.location:
			Land.Modify(self.location, self.Colour) # update color on Land
			self.display()
		else:
			self.moves(free=True)

	def locate(self, NewPosition, Erase=True):
		"""	place individual at a specific location on the ground 
		"""
		if NewPosition is not None \
			and not Land.Modify(NewPosition, self.Colour, check=True): 	# new position on Land
			return False		 # NewPosition is not available  
		if Erase and self.location \
			and not Land.Modify(self.location, None): 	# erasing previous position on Land
			print('Error, agent %s badly placed' % self.ID)
		self.location = NewPosition
		self.display()
		return True

	def display(self):
		Observer.record((self.ID, self.location + (self.Colour, -1))) # for ongoing display on Field
		
	def decisionToMove(self):
		return not self.satisfaction()

	def satisfaction(self):
		if self.Colour == 'black':	return True
		self.satisfied = True	# default
		if self.location is None:	return False # may happen if there is no room left	
		Statistics = Land.InspectNeighbourhood(self.location, self.Scenario['NeighbourhoodRadius'])	# Dictionary of colours
		# print(Statistics, end=' ')
		#Same = Statistics[self.Colour]
		#Different = sum([Statistics[C] for C in self.Scenario.Colours if C != self.Colour])	
		# Sum all shades belonging to the same base colour
		Same = sum(Statistics.get(col, 0) for col in CUSTOM_COLOURS 
           			if col.startswith(self.BaseColour))

		Different = sum(Statistics.get(col, 0) for col in CUSTOM_COLOURS
                		if not col.startswith(self.BaseColour))
		
		if self.Scenario['Correction'] == 0:
			# compute satisfaction 
			# by combining 'Same', 'Different' and self.Scenario.Parameter('Tolerance')
			# (see the meaning of 'Tolerance' in Starter).
			percentDiff = 100 * Different / (Same + Different)
			self.satisfied = percentDiff <= self.Scenario['Tolerance']
		else:
			if (Same + Different) and \
					(100 * Different) / (Same + Different) > self.Scenario['Tolerance']:	
				self.satisfied = False		
		return self.satisfied

	def moves(self, free=False, Position=None): #First move is free of charge !
		# print 'moving', self
		global Land
		if Position:
			return self.locate(Position)
		else:
			# pick a random location and go there 
			# Agents with any budgets can move to any places at initialization 
			for ii in range(20): # should work at first attempt most of the time (people gets tired at finding houses too ;)
				Landing = Land.randomPosition(Content=None, check=True)	# selects an empty cell
				if Landing:
					housePrice = Land.getHousePrice(Landing)   # get the house price of the selected cell
					if self.Budget :
						if free or (self.Budget >= housePrice):   # with enough budget, agents can move
							if self.locate(Landing):
								return True
				
				elif ii == 0:	Land.statistics()   # need to update list of available positions
			print("Unable to move to", Position)
			return False

	def __str__(self):
		return "(%s,%s) --> " % (self.ID, self.Colour) + str(self.location)

class Group(EG.Group):
	"""	The group is a container for individuals.
		Individuals are stored in self.members
	"""

	def __init__(self, Scenario, ID=1, Size=100):
		EG.Group.__init__(self, Scenario, ID, Size)
		self.Colour = None
		
	def setColourAndBudget(self, Colour):
		self.Colour = Colour
		#self.Budget = random.choice([1, 2, 3])   # randomly assign budgets to agents in a group
		for member in self.members:	
			Budget = random.choices(choices, weights=weights, k=1)[0]
			member.setColourAndBudget(Colour, Budget)	# gives colour and budget to all members
		
	def createIndividual(self, ID=None, Newborn=True, location=None):
		# calling local class 'Individual'
		Indiv = Individual(self.Scenario, ID=self.free_ID(), Newborn=Newborn, location=location)
		# Individual creation may fail if there is no room left
		# if Indiv.location == None:	return None
		return Indiv
		
	def satisfaction(self):	return 100 * sum([int(I.satisfied) for I in self]) / len(self) if len(self) else 100
	
class Population(EP.Population):
	"""	defines the population of agents 
	"""
	def __init__(self, Scenario, Observer):
		"""	creates a population of agents 
		"""
		EP.Population.__init__(self, Scenario, Observer)
		self.Colours = self.Scenario.Colours
		self.Colours.append("black") # black for borders
		print(self.Colours)

		# Populate background with agents that are always happy
		border_group = self.createGroup(ID=42, Size=0)
		self.groups.append(border_group)
		img = Image.open(Gbl['CityFile']).convert("RGB")
		pixels = img.load()
		width, height = img.size
		created_count = 0
		for j in range(width):
			for i in range(height):
				if sum(pixels[i, j]) == 0: #pixel is black
					# All individuals are created in a dedicated group
					if border_group.createIndividual(location = (i, width - j - 1)):
						created_count += 1
				# Set the price index
				if pixels[i, j][2] == 255 : # cyan
					Land.housePrice[i][width - j - 1] = 1
				if pixels[i, j][0] == 255 : # yellow
					Land.housePrice[i][width - j - 1] = 2
				if pixels[i, j][1] == 255: # green
					Land.housePrice[i][width - j - 1] = 3
		print(f"created {created_count} agents on black pixels.")
		border_group.setColourAndBudget('black')

		for Colour in self.Colours[:-1]:
			print(f"creating {Colour} agents")
			# individuals are created with the colour given as ID of their group
			self.groups[self.Colours.index(Colour)].setColourAndBudget(Colour)
		print(self.Colours)
		print(f"population size: {self.popSize}")
		self.Moves = 0  # counts the number of times agents have moved
		self.CallsSinceLastMove = 0  # counts the number of times agents were proposed to move since last actual move

	def createGroup(self, ID=0, Size=0):
		return Group(self.Scenario, ID=ID, Size=Size)

	def satisfaction(self):	return [(gr.Colour, gr.satisfaction()) for gr in self.groups if gr.Colour is not None]
	
	def One_Decision(self):
		""" This function is repeatedly called by the simulation thread.
			One agent is randomly chosen and decides what it does
		"""
		# EP.Population.one_year(self)	# performs statistics
		agent = self.selectIndividual()	# agent who will play the game	
		# print agent.ID, 'about to move'
		self.CallsSinceLastMove += 1
		if agent.decisionToMove() and agent.moves():
			self.Moves += 1
			self.CallsSinceLastMove = 0
		# if self.popSize:	self.Observer.season(self.Moves // self.popSize)  # sets StepId
		self.Observer.season()  # sets StepId
		# print(self.Observer.StepId)
		if self.Observer.Visible():	# time for display
			Satisfactions = self.satisfaction()
			for (Colour, Satisfaction) in Satisfactions:
				self.Observer.curve(Name=f'{Colour} Satisfaction', Value=Satisfaction)
			# if Satisfactions:
				# self.Observer.curve(Name='Global Satisfaction', Value=sum([S for (C,S) in Satisfactions])/len(Satisfactions))
	
		if self.CallsSinceLastMove > 10 * self.popSize:
			return False	# situation is probably stable
		return True	# simulation goes on


if __name__ == "__main__":
	print(__doc__)

	
	#############################
	# Global objects			#
	#############################
	Gbl = Scenario()
	Observer = Observer(Gbl)	  # Observer acontains statistics
	Land = Landscape.Landscape(Gbl['LandSize'])	  # logical settlement grid
	Land.housePrice = [random.choices(price_choices, weights=price_weights, k=Land.Width) for _ in range(Land.Height)]
	Land.setAdmissible(CUSTOM_COLOURS + ['black'])
	Pop = Population(Gbl, Observer)   
	
	# Observer.recordInfo('Background', 'white')
	Observer.recordInfo('FieldWallpaper', Gbl['CityFile']) # Add city for the background
	Observer.recordInfo('DefaultViews',	['Field', 'Legend'])	# Evolife should start with these windows open - these sizes are in pixels

	
	# declaration of curves
	for Col in Gbl.Colours:
		Observer.curve(Name=f'{Col} Satisfaction', Color=Col, Legend=f'average satisfaction of {Col} individuals')
	# Observer.curve(Name='Global Satisfaction', Color='black', Legend='average global satisfaction')
	
	EW.Start(Pop.One_Decision, Observer, Capabilities='RPC', Options={'Run':Gbl.get('Run', False)})

	print("Bye.......")
	
__author__ = 'Dessalles'
