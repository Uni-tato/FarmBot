import weakref

# Each item object now has an associated amount - think stacks of items in Minecraft,
# Where an item in your inventory can have a 1 or 2 or 64 value, signifying its amount
class Item:
    def __init__(self, name, amount = 1, *, manager):
        self.name = name
        # TODO: Remove this? Make `Container` handle item numbers. 
        self.amount = amount
        self._manager = weakref.proxy(manager)

    @property
    def buyCost(self):
        return self._manager.get_buy_price(self.name)

    @property
    def sellCost(self):
        return self._manager.get_sell_price(self.name)

    @property
    def emoji(self):
        return self._manager.get_emoji(self.name)

    @property.setter
    def emoji(self, new_emoji):
        self._manager._items[self.name]["emoji"] = new_emoji

    def init_emoji(self, client):
        for emoji in client.get_all_emojis():
            if emoji.name == self.emoji:
                self.emoji = str(emoji)
                return

        self.emoji = ":" + self.emoji + ":"

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
# - returns each item object
class Container:
    ### NO. NO CONTAINER NAMES. PLEASE. ###
    #def __init__(self, name, items = []):
    #    self.name = name
    def __init__(self, items_input = []):
        # This if statement makes it so that Container can accept both an item or list of items as an input
        if isinstance(items_input, Item):
            self.items = [items_input]
        elif isinstance(items_input, list):
            self.items = items_input

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
            add_item(Item(other))

        else:
            raise ValueError("Unsupported additon on Container object")

        self.sort()
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

        self.sort()
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

    def __len__(self):
        return len(self.items)

    # Alex still gets his .append() and .remove() he had before
    def append(self, items):
        self.__add__(items)

    def remove(self, items):
        if type(items) == Container:
            items = items.items
        for item in items:
            if item not in self.items: # return an error if the container does not have (enough of) an item.
                raise valueError(f"Item: \"{item}\" not present in Container.")
            elif items[item] > self.items[item]:
                raise valueError(f"More \"{item}\"s removed than in Container.")
            
            elif items[item] == self.items[item]:
                del self.items[item]
            else:
                self.items[item] -= items[item]
        self.__sub__(items)

    def sort(self):
        # sort the contents of the container alphabetically
        # this is done automatically whenever an item is added/removed from the Container
        self.items.sort(key=get_name)


def get_name(item):
    return item.name
