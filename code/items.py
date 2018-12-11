# Each item object now has an associated amount - think stacks of items in Minecraft,
# Where an item in your inventory can have a 1 or 2 or 64 value, signifying its amount
class Item:
    def __init__(self, name, buyCost = None, sellCost = None, amount = 1):
        self.name = name
        # This lets the Item class be initialized with just the item name
        # e.g. Item("wheat") will automatically fill the buy and sell costs too
        if buyCost == None and sellCost == None:
            for item in items:
                if self.name == item.name:
                    self.buyCost = item.buyCost
                    self.sellCost = item.sellCost
        else:
            self.buyCost = buyCost
            self.sellCost = sellCost
        self.amount = amount

# USAGE EXAMPLES:
# player.has(Item), player.has("wheat")
# - returns True if item is present, False if not
#
# player.items += Item, player.items += "wheat", player.items += Container
# ALL EQUIVILANT TO player.items.append()
# player.items -= Item, player.items -= "wheat", player.items -= Container
# ALL EQUIVILANT TO player.items.remove()
# - will add/remove an item/items from the players inventory, returns an error if not present or if too many are removed
#
# player.items[Item], player.items["wheat"]
# - returns the item object
#
# for item in player.items:
# - returns each item
class Container:
    ### NO. NO CONTAINER NAMES. PLEASE. ###
    #def __init__(self, name, items = []):
    #    self.name = name
    def __init__(self, items = []):
        # This if statement makes it so that Container can accept both an item or list of items as an input
        if isinstance(items, Item):
            self.items = [items]
        elif isinstance(items, list):
            self.items = items

    def has(self, item_name):
        name = None
        if isinstance(item_name, str):
            name = item_name
        elif isinstance(item_name, Item):
            name = item_name.name

        for item in self.items:
            if name == item.name:
                return True
        return False

    def __add__(self, other):
        def add_item(tar_item): # target_item = items in the container that's being added from
            found = False
            for sor_item in self.items: # sorce_item = items in the container that's being added too
                if sor_item.name == tar_item.name:
                    sor_item.amount += tar_item.amount
                    found = True
                    break
            if not found:
                # if the target item does not exist in the source, then we must create it there
                self.items.append(Item(tar_item.name, amount=tar_item.amount))

        if isinstance(other, Container):
            for item in other:
                add_item(item)

        elif isinstance(other, Item):
            add_item(other)

        elif isinstance(other, str):
            remove_item(Item(other))

        else:
            raise ValueError("Unsupported additon on Container object")
        return self

    def __sub__(self, other):
        def remove_item(tar_item):
            for sor_item in self.items[::-1]:
                if sor_item.name == tar_item.name:
                    if sor_item.amount > tar_item.amount:
                        sor_item.amount -= tar_item.amount
                    elif sor_item.amount == tar_item.amount:
                        self.items.remove(sor_item)
                    else:
                        raise ValueError(f"More \"{tar_item.name}\"'s removed than in Container.")
                    return
            raise ValueError(f"Item \"{tar_item.name}\" not present in Container.")

        if isinstance(other, Container):
            for item in other:
                remove_item(item)

        elif isinstance(other, Item):
            remove_item(other)

        elif isinstance(other, str):
            remove_item(Item(other))

        else:
            raise ValueError("Unsupported subtraction on Container object")
        return self

    def __getitem__(self, key):
        name = None
        if isinstance(key, str):
            name = key
        elif isinstance(key, Item):
            name = key.name

        for item in self.items:
            if item.name == name:
                return item
        raise KeyError

    # __iter__ lets the Container object be itterated over, returning the list of items
    def __iter__(self):
        return iter(self.items)

    # Alex still gets his .append() and .remove() he had before
    def append(self, items):
        self.__add__(items)

    def remove(self, items):
        self.__sub__(items)


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