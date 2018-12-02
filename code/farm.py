

class Farm:
    def __init__(self, plotCount = 1):
        self.plotCount = plotCount
        plots = [Plot() for i in range(plotCount)]


class Plot:
    def __init__(self):
            self.crop = None
            self.completeTime = None


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