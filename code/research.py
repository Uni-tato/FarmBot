"""ok, so basically dont touch this yet, or I will hunt you down and murder you! *winkey face*"""
import discord # I dont think I actually need this here

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
    if name in technologies:
        return technologies[name]
    else:
        raise ValueError(f"Technology: {name} does not exist.")


''' just a reminder of how this stuff works
async def test_function(player):
    await client.say("this function was assinged to a technology object as a parameter")
technologies["test"] = Technology("test",0,1,test_function)

async def test_function2(player):
    await client.say("This technology requires the previous one.")
technologies["test2"] = Technology("test2",0,1,test_function2,["test"])
'''

def init_crops(crops):
    for crop in crops:
        name = crop.name
        lvl = crop.unlock_at_lvl
        cost = crop.research_cost
        effect = get_crop_effect(name)
        technologies[name] = Technology(name,lvl,cost,effect)


def get_crop_effect(crop):
    return lambda player : player.available_crops.append(crop)

'''
def myfunc(n):
  return lambda a : a * n

mytripler = myfunc(3)
'''