#literally does nothing yet.
import datetime
from random import randint


class Farm:
    def __init__(self, name, plotCount = 1):
        self.name = name
        self.plotCount = plotCount
        plots = [Plot() for i in range(plotCount)]


class Plot:
    def __init__(self):
            self.crop = None
            self.completeTime = None

    def plant(self, crop): #currently only working for crops, not trees.
        self.crop = crop
        now = datetime.datetime.now()
        timeTaken = datetime.timedelta(minutes = crop.time)
        self.completeTime = now + timeTaken

    def harvest():
        now = datetime.datetime.now()
        if now >= self.completeTime:
            item = self.crop.item
            itemCount = randint(self.crop.minItem,self.crop.maxItem)
            self.crop = None
            self.completeTime = None
            return {item:itemCount} #if these return none then I will need to make item a copy.


class Crop:
    def __init__(self,name,time,seed,item,minItem,maxItem):
        self.name = name
        self.time = time
        self.seed = seed
        self.item = item
        self.minItem = minItem
        self.maxItem = maxItem


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
