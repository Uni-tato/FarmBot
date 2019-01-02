"""ok, so basically dont touch this yet, or I will hunt you down and murder you! *winkey face*"""
#import discord # I dont think I actually need this here

client = None # Set in main.py
technologies = {} # dict of names:technology

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


def init_crops(crops):
    '''Creates the Technology objects for all crops'''
    for crop in crops:
        name = crop.name
        lvl = crop.unlock_at_lvl
        cost = crop.research_cost
        effect = get_crop_tech(crop)
        technologies[name] = Technology(name,lvl,cost,effect)

def get_crop_tech(crop):
    '''Creates functions for crop technology.'''
    async def crop_tech(player):
        player.available_crops.append(crop)
        await client.say(f"{player.player.mention}, you can now plant and grow {crop.name}(s)")
    return crop_tech

async def unlock_free(player,lvl_range):
    '''Used to automatically unlock any new free technologies.'''
    for tech in technologies.values():
        if tech.cost == 0 and tech.lvl in lvl_range:
            await tech.research(player)