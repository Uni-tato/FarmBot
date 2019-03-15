"""Implement player code."""
import asyncio
from math import floor
import datetime

import discord
from discord.ext.commands import Context

import items
import research as res
from farm import Crop


client = None # set to bots client by main.py 

# This'll be a dictionary where the keys are the user discord objects,
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

        self.xp = 0
        self.lvl = 1
        self.r_tokens = 0 # Research points used to unlock/upgrade stuff.
        self.technologies = []

        self.buy_multiplier = 1
        self.sell_multiplier = 1
        self.available_crops = []
        self.plot_count = 2
        self.auto_harvest_lvl = 0
        self.xp_multiplier = 1

        self.gambling_cooldown = datetime.datetime.now()
        # All for playing blackjack. :)
        self.cards = []
        self.hand = []
        self.dealer = []
        self.bet = 0


    async def lvl_check(self):
        '''Checks if the player should level up, and does so if necessary.'''
        lvl_1_xp = 50
        if self.xp < 0:
            self.xp = 0
        should_be = floor((self.xp/lvl_1_xp)**0.65)+1 #anyone is welcome to improve this.
        if self.lvl != should_be:
            await self.lvl_up(should_be)

    async def lvl_up(self,lvl): # almost definitely unnecessary fot this to be a separate function.
        '''Stuff that happens when the player levels up.'''
        lvl_range = range(self.lvl+1, lvl+1)
        self.r_tokens += (lvl - self.lvl)
        self.lvl = lvl
        await client.say(
            f"Congratulations {self.player.mention}, you are now level:{lvl}.")
        await res.unlock_free(self,lvl_range)

    def hand_total(self, return_type=list, hand="player"):
        class supa_list(list):
            def __init__(self):
                super().__init__()

            def append(self, other):
                #if other > 21 or other in self:
                if other in self:
                    return
                super().append(other)

        total = supa_list()
        total.append(0)
        hand_ = self.hand
        if hand == "dealer":
            hand_ = self.dealer
        for card in hand_:
            if card.name == "Ace":
                new_total = supa_list()
                for i in range(len(total)):
                    new_total.append(total[i] + 1)
                    new_total.append(total[i] + 11)
                total = new_total
            else:
                for i in range(len(total)):
                    total[i] += card.value

        if return_type == list:
            return total
        elif return_type == str:
            string = ""
            for string_ in total[:-1]:
                string += str(string_) + ", "
            string += str(total[-1])
            return string

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
        player = Player(member)
        players[member] = player
    return players[member]