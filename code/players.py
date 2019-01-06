"""Implement player code."""
import asyncio
from math import floor

import discord
from discord.ext.commands import Context

import items
import research as res
from farm import Crop


client = None # set to bots client by main.py 

# This'll be a dictionary where the keys are the player discord objects,
# and the values are this custom player class
players = {}


market_manager = None


def init(market_manager_, crop_manager_):
    """Provide module with `market_manager`."""
    global market_manager, crop_manager
    market_manager = market_manager_
    crop_manager = crop_manager_


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
        self.available_crops = []
        self.max_plots = 2 # Players will still need to buy more plots for their farm(s)
        self.auto_harvest_lvl = 0
        self.xp_multiplier = 1


    async def lvl_check(self,ctx):
        '''Checks if the player should level up, and does so if necessary.'''
        lvl_1_xp = 50
        should_be = floor((self.xp/lvl_1_xp)**0.8)+1 #anyone is welcome to improve this.
        if self.lvl != should_be:
            await self.lvl_up(ctx,should_be)

    async def lvl_up(self,ctx,lvl): # almost definitely unnecessary fot this to be a separate function.
        '''Stuff that happens when the player levels up.'''
        lvl_range = range(self.lvl+1, lvl+1)
        self.r_tokens += (lvl - self.lvl)
        self.lvl = lvl
        await client.send_message(
            ctx.message.channel,
            f"Congratulations {ctx.message.author.mention}, you are now level:{lvl}.")
        await res.unlock_free(self,lvl_range)

    def has(self, item_name):
        """Check if player has `item_name` in inventory.

        If `item_name` is a `str`:
            It just checks if player *has* the item.
        If `item_name` is an `Item`:
            It checks if player has the item *and* has
            a greater than or equal to amount than the
            input item."""
        return self.items.has(item_name)

    def can_plant(self, item):
        """Checks if a player has researched a crop.

        Works with both strings (crop names) and the crop object itself."""
        if isinstance(item, Crop):
            return item.name in self.available_crops
        elif isinstance(item, str):
            return item in self.available_crops
        else:
            return False

    def give_xp(self, amount):
        """Gives the player xp."""
        self.xp += round(amount*self.xp_multiplier,2)
        self.xp = round(self.xp,2)


# TODO: Rename argument to something meaningful.
async def get(i):
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
        player = Player(member)
        players[member] = player
        await res.unlock_free(player,(0,1))
    return players[member]