"""ok, so basically dont touch this yet, or I will hunt you down and murder you! *winkey face*"""
from math import floor

from farm import Plot

client = None # Set in main.py
technologies = {} # dict of 'names:technology'

class Technology:
    """any point on the skill/research/technology tree"""
    def __init__(self, name, lvl, cost, effect, requirements = []):
        self.name = name
        self.lvl = lvl
        self.cost = cost
        self.effect = effect
        self.requirements = requirements

    async def research(self, player):
        '''unlocks a new technology, costs research tokens'''
        for req in self.requirements:
            if req not in player.technologies:
                return False
        if player.lvl < self.lvl or player.r_tokens < self.cost:
            return False # not necessary, but good redundancy.
        else:
            player.r_tokens -= self.cost
            player.technologies.append(self.name)
            await self.effect(player)
            

def get_tech(name):
    '''Gets a Technology from a technology name'''
    if name in technologies:
        return technologies[name]
    else:
        raise ValueError(f"Technology: {name} does not exist.")

async def unlock_free(player,lvl_range):
    '''Used to automatically unlock any new free technologies.'''
    for tech in technologies.values():
        if tech.cost == 0 and tech.lvl in lvl_range:
            await tech.research(player)

def init_crops(crops):
    '''Creates the Technology objects for all crops'''
    for crop in crops:
        name = crop.name
        lvl = crop.unlock_at_lvl
        cost = crop.research_cost
        effect = get_crop_effect(crop)
        technologies[name] = Technology(name,lvl,cost,effect)

def get_crop_effect(crop):
    '''Creates functions for crop technology.'''
    async def crop_effect(player):
        player.available_crops.append(crop.name)
        await client.say(f"{player.player.mention}, you can now plant and grow {crop.name}(s)")
    return crop_effect

def init_buy_cost():
    '''creates technology objects for each `buy cost` technology'''
    multipliers = (0.95, 0.9, 0.85)
    for i in range(len(multipliers)):
        name = "buy_cost_"+str(i+1)
        lvl = (i+1)*5
        cost = i+1
        effect = get_buy_cost_effect(multipliers[i])
        requirements = ["buy_cost_"+str(i)] if i != 0 else []
        technologies[name] = Technology(name, lvl, cost, effect, requirements)

def get_buy_cost_effect(multiplier):
    '''Creates functions for `buy cost` technologiess'''
    async def buy_cost_effect(player):
        player.buy_multiplier = multiplier
        await client.say(f"{player.player.mention}, you can now buy items for {multiplier*100}% of the full price.")
    return buy_cost_effect

def init_sell_cost():
    '''creates technology objects for each `sell cost` technology'''
    multipliers = (1.05, 1.1, 1.15)
    for i in range(len(multipliers)):
        name = "sell_cost_"+str(i+1)
        lvl = (i+1)*5
        cost = i+1
        effect = get_sell_cost_effect(multipliers[i])
        requirements = ["sell_cost_"+str(i)] if i != 0 else []
        technologies[name] = Technology(name, lvl, cost, effect, requirements)

def get_sell_cost_effect(multiplier):
    '''Creates functions for `sell cost` technologiess'''
    async def sell_cost_effect(player):
        player.sell_multiplier = multiplier
        await client.say(f"{player.player.mention}, you can now sell items for {multiplier*100}% of the normal sale price.")
    return sell_cost_effect

def init_plot_count():
    '''Creates technology objects to increase max plot count'''
    amount = 13
    for i in range(amount):
        name = "max_plots_"+str(i+1)
        lvl = (i*2)+2
        cost = floor(i/2+1) 
        effect = increase_plot_count
        requirements = ["max_plots_"+str(i+1)] if i != 0 else []
        technologies[name] = Technology(name, lvl, cost, effect, requirements)

async def increase_plot_count(player):
    '''Increases the amount of maximum plots a player can have'''
    player.plot_count += 1
    player.farm.plot_count = player.plot_count
    player.farm.plots.append(Plot(player.plot_count))
    await client.say(f"{player.player.mention}, your farm: {player.farm.name}, now has {player.plot_count} plots.")

def init_auto_count():
    '''Creates technology objects to auto harvest plots'''
    amount = 15
    for i in range(amount):
        name = "automate_plot_"+str(i+1)
        lvl = (i*2)+3
        cost = 3 
        effect = increase_auto_count
        requirements = ["automate_plot_"+str(i)] if i != 0 else []
        requirements += [] if i < 2 else ["max_plots_"+str(i-1)]
        technologies[name] = Technology(name, lvl, cost, effect, requirements)

async def increase_auto_count(player):
    '''Increases the amount of automatic plots a players farm(s) has'''
    player.auto_harvest_lvl += 1
    await client.say(f"{player.player.mention}, your farm(s) will now automatically harvest the first {player.auto_harvest_lvl} plots.")

def init_xp_multiplier():
    '''Creates technology objects to increase xp gain'''
    multipliers = (1.05, 1.1, 1.15)
    for i in range(len(multipliers)):
        name = "xp_multiplier_"+str(i+1)
        lvl = (i*5)+3
        cost = 2
        effect = get_xp_multiplier_effect(multipliers[i])
        requirements = ["xp_multiplier_"+str(i)] if i != 0 else []
        technologies[name] = Technology(name, lvl, cost, effect, requirements)

def get_xp_multiplier_effect(multiplier):
    '''Creates functions to edit xp multiplier'''
    async def xp_multiplier_effect(player):
        player.xp_multiplier = multiplier
        await client.say(f"{player.player.mention}, you will now get {(multiplier-1)*100}% more xp.")
    return xp_multiplier_effect

def init(crops):
    '''creates all the technologies.'''
    init_crops(crops)
    init_buy_cost()
    init_sell_cost()
    init_plot_count()
    init_auto_count()
    init_xp_multiplier()