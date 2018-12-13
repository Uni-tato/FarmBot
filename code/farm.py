#literally does nothing yet.
import datetime
import time
from random import randint
import weakref

import items


class Farm:
    def __init__(self, name, plotCount = 2):
        self.name = name
        self.plotCount = plotCount
        self.plots = [Plot() for i in range(plotCount)]


class Plot:
    def __init__(self):
            self.crop = None
            self.completeTime = None

    def plant(self, crop): #currently only working for crops, not trees.
        self.crop = crop
        #now = datetime.datetime.now()
        #timeTaken = datetime.timedelta(minutes = crop.time)
        #self.completeTime = now + timeTaken
        self.completeTime = time.time() + crop.time * 60

    def harvest(self):
        if self.crop is None:
            return None
        #now = datetime.datetime.now()
        #if now >= self.completeTime:
        if time.time() >= self.completeTime:
            item_name = self.crop.item
            itemCount = randint(self.crop.minItem,self.crop.maxItem)
            self.crop = None
            self.completeTime = None
            return items.Item(item_name, amount=itemCount)
            #return {item:itemCount} #if these return none then I will need to make item a copy.
        else:
            return None

    def time_left(self):
        if self.crop is None:
            return None

        time_remaining = self.completeTime - time.time()
        if time_remaining <= 0:
            return 0
        else:
            return round(time_remaining/60, 1)
class Crop:
    def __init__(self, name, *, manager):
        self.name = name
        self._manager = weakref.proxy(manager)

    @property
    def seed(self):
        return self._manager.get_seed(self.name)

    @property
    def item(self):
        return self._manager.get_item(self.name)

    @property
    def minItem(self):
        return self._manager.get_min_items(self.name)

    @property
    def maxItem(self):
        return self._manager.get_max_items(self.name)

    @property
    def minLifeTime(self):
        return self._manager.get_min_lifetime(self.name)

    @property
    def maxLifeTime(self):
        return self._manager.get_max_lifetime(self.name)

    @property
    def emoji(self):
        return self._manager.get_emoji(self.name)

    @property.setter
    def emoji(self, new_emoji):
        self._manager._crops[self.name]["emoji"] = new_emoji

    def init_emoji(self, client):
        for emoji in client.get_all_emojis():
            if emoji.name == self.emoji:
                self.emoji = str(emoji)
                return

        self.emoji = ":" + self.emoji + ":"


class Tree:
    def __init__(self,name,time,seed,item,minItem,maxItem,minLifetime,maxLifetime):
        self.name = name
        self.time = time
        self.seed = seed
        self.item = item
        self.minItem = minItem
        self.maxItem = maxItem 
        self.minLifetime = minLifetime
        self.maxLifetime = maxLifetime

