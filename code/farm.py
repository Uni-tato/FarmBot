#literally does nothing yet.
import datetime
import time
from random import randint
import weakref

import items


market_manager = None
def init(market_manager_):
    global market_manager
    market_manager = market_manager_


class Farm:
    def __init__(self, name, plotCount = 2):
        self.name = name
        self.plotCount = plotCount
        self.plots = [Plot() for i in range(plotCount)]


class Plot:
    def __init__(self):
        self.crop = None
        self._start_time = None
    
    @property
    def completeTime(self):
        return self._start_time + self.crop.time*60

    def plant(self, crop):
        self.crop = crop
        self._start_time = time.time()

    def harvest(self):
        if self.crop is None:
            return None
        if time.time() >= self.completeTime:
            item_name = self.crop.item
            itemCount = randint(self.crop.minItem, self.crop.maxItem)
            self.crop = None
            return items.Item(
                item_name,
                amount=itemCount,
                manager=market_manager
            )
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
    def time(self):
        return self._manager.get_time(self.name)

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

    @emoji.setter
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

