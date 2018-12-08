# This'll be a dictionary where the keys are the player discord objects, and the values are this custom player class
players = {}

class Player():
	def __init__(self, player):
		# This'll be the discord object that represents the player
		self.player = player

		self.farm = None

		self.items = {}

		self.money = 20

		# Here, there will probably be some other stuff such as player upgrades and shit
		# `then with the money you can upgrade your farm, for example get more plots, reduce grow time etc` - Alex
		# These values might be here if they're player specific