#literally does nothing yet.

class Farm:
    def __init__(self, plotCount = 1):
        self.plotCount = plotCount
        plots = [Plot() for i in range(plotCount)] #creates an array of plots


class Plot:
    def __init__(self):
            self.crop = None #the crop thay is currently planted
            self.completeTime = None #the time that the crop should finish growing.


class Crop:
    def __init__(self,name,time,seed,item,minItem,maxItem):
        self.name = name #the name of the crop
        self.time = time #the time it takes for the crop to grow (might use a "min", "max" version in the future)
        self.seed = seed #the item used to plant this crop
        self.item = item #the item that this crop grows
        self.minItem = minItem #the minimum amount of items this crop grows
        self.maxItem = maxItem # "  maximum    "    "   "     "    "    "


class Tree: #basically the same as crop, but lasts longer and gives items throughout its life.
    def __init__(self,name,time,seed,item,minItem,maxItem,minLifetime,maxLifetime):
        self.name = name #the type of tree.
        self.time = time #the time between harvests.
        self.seed = seed #the seed that grows this tree.
        self.item = item #the item that this tree grows.
        self.minItem = minItem #the minimum amount of items per harvest.
        self.maxItem = maxItem
        self.minLifetime = minLifetime
        self.maxLifetime = maxLifetime


class Item:
    def __init__(self,name,buy,sell):
        self.name = name
        self.buy = buy
        self.sell = sell
