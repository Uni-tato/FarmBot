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
