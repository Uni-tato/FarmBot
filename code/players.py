"""Implement player code."""
import asyncio

import discord
from discord.ext.commands import Context

import items


client = None # set to bots client by main.py 

# This'll be a dictionary where the keys are the player discord objects,
# and the values are this custom player class
players = {}


market_manager = None


def init(market_manager_):
    """Provide module with `market_manager`."""
    global market_manager
    market_manager = market_manager_


class Player:
    """Represents the users that play the game."""

    def __init__(self, player):
        # This'll be the discord object that represents the player
        self.player = player

        self.farm = None

        self.items = items.Container(
            [items.Item("wheat seeds", manager=market_manager)], manager=market_manager
        )

        self.money = 10

        self.xp = 0 # Currently does not increase. 
        self.lvl = 1
        self.r_tokens = 0 # Research points used to unlock/upgrade stuff.
        self.technologies = []

        self.buy_multiplier = 1
        self.sell_multiplier = 1
        self.available_crops = ["wheat"]
        self.max_plots = 2 # Players will still need to buy more plots for their farm(s)
        self.auto_harvest_lvl = 0

    async def lvl_check(self,ctx):
    	should_be = (self.xp//5)+1 #anyone is welcome to improve this.
    	if self.lvl != should_be:
    		self.lvl = should_be
    		self.r_tokens += 1
    		await level_up(ctx,self.lvl)

    def has(self, item_name):
        """Check if player has `item_name` in inventory.

        If `item_name` is a `str`:
            It just checks if player *has* the item.
        If `item_name` is an `Item`:
            It checks if player has the item *and* has
            a greater than or equal to amount than the
            input item."""
        return self.items.has(item_name)


# TODO: Rename argument to something meaningful.
def get(i):
    """Get a `Player` representing `ctx.message.author`.

    Also automagically creates the player object if there isn't one already."""
    if isinstance(i, discord.Member):
        member = i
    elif isinstance(i, Context):
        member = i.message.author
    else:
        # TODO: Should this just raise an exception?
        return None

    if member not in players:
        players[member] = Player(member)
    return players[member]

async def level_up(ctx,lvl): # almost definitely unnecessary fot this to be a separate function.
	await client.send_message(
		ctx.message.channel,
		f"Congratulations {ctx.message.author.mention}, you are now level:{lvl}.")
		# TODO make something to automatically unlock free technologies.