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


crops = []
import os; print(os.getcwd())
with open("crops.txt", "r") as crops_file:
    reader = DictReader(row for row in crops_file if not row.startswith("#"))
    for row in reader:
        name = row["name"]         
        time = int(row["time"])
        seed = row["seed"]
        item = row["item"]
        minItem = int(row["minItem"])
        maxItem = int(row["maxItem"])

        crops.append(Crop(name, time, seed, item, minItem, maxItem))

# lines = open('crops.txt','r').readlines()
# for line in lines:
#     if line[0] != '#':
#         line = line.split(',')
#         line[-1] = line[-1].replace('\n','')
#         name = line[0]
#         time = int(line[1])
#         seed = line[2]
#         item = line[3]
#         minItem = int(line[4])
#         maxItem = int(line[5])
#         crop = Crop(name, time, seed, item, minItem, maxItem)
#         crops.append(crop)
#print(crops)
