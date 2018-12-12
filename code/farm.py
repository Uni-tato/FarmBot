#literally does nothing yet.
import datetime
import time
from random import randint

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
    def __init__(self,name,time,seed,item,minItem,maxItem, emoji):
        self.name = name
        self.time = time
        self.seed = seed
        self.item = item
        self.minItem = minItem
        self.maxItem = maxItem
        self.emoji = emoji

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


class Item:
    def __init__(self,name,buy,sell):
        self.name = name
        self.buy = buy
        self.sell = sell
