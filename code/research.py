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
        for tech in self.requirements:
            if tech not in player.technologies:
                return False
        if player.lvl < self.lvl or player.r_tokens < self.cost:
            return False # not necessary, but good redundancy.
        else:
            player.r_tokens -= self.cost
            await self.effect(player)
            

def get_tech(name):
    if name in technologies:
        return technologies[name]
    else:
        raise ValueError(f"Technology: {name} does not exist.")


async def test_function(player):
    await client.say("this function was assinged to an technology object as a parameter")

technologies["test"] = Technology("test",0,1,test_function)