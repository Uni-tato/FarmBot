class Item:
    def __init__(self, name, buyCost, sellCost):
        self.name = name
        self.buyCost = buyCost
        self.sellCost = sellCost


class Container:
    def __init__(self, name, items = {}):
        self.name = name
        self.items = items

    def append(items):
        if type(items) == Container:
            items = items.items
        for item in items:
            if item in self.items:
                self.items[item] += items[item]
            else:
                self.items[item] = items[item]


items = []
lines = open('items.txt','r').readlines()
for line in lines:
    if line[0] != '#':
        line = line.split(',')
        line[-1] = line[-1].replace('\n','')
        name = line[0]
        buy = line[1]
        sell = line[2]
        item = Item(name,buy,sell)
        items.append(item)