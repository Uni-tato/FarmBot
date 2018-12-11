from csv import DictReader

from util import FarmbotCSVDialect

class Item:
    def __init__(self, name, buyCost, sellCost):
        self.name = name
        self.buyCost = buyCost
        self.sellCost = sellCost


class Container:
    def __init__(self, name, items = {}):
        self.name = name
        self.items = items

    def append(self, items):
        if type(items) == Container:
            items = items.items # Allows easier addition of 2 containers eg. Container1.append(Container2).
        for item in items:
            if item in self.items:
                self.items[item] += items[item]
            else:
                self.items[item] = items[item]

    def remove(self, items):
        if type(items) == Container:
            items = items.items
        for item in items:
            if item not in self.items: # return an error if the container does not have (enough of) an item.
                raise valueError(f"Item: \"{item}\" not present in Container.")
            elif items[item] > self.items[item]:
                raise valueError(f"More \"{item}\"s removed than in Container.")
            
            elif items[item] = self.items[item]:
                del self.items[item]
            else:
                self.items[item] -= items[item]


items = []
with open("item.txt", "r") as item_file:
    reader = DictReader((row for row in item_file if not row.startswith("#")), dialect=FarmbotCSVDialect)
    for row in reader:
        name = row["name"]
        buy = row["buy"]
        sell = row["sell"]

        items.append(Item(name, buy, sell))

# lines = open('items.txt','r').readlines()
# for line in lines:
#     if line[0] != '#':
#         line = line.split(',')
#         line[-1] = line[-1].replace('\n','')
#         name = line[0]
#         buy = line[1]
#         sell = line[2]
#         item = Item(name,buy,sell)
#         items.append(item)
