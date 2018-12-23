"""Handle `Item`s and `Container`s."""
import weakref


class Item:
    """Represents a "stack" of items.

    All `Item`s are the same, except in their `amount` and `name`
    attributes. This is because this is essentially a proxy for the
    `MarketManager`, which provides all the values for price, emoji,
    etc."""

    def __init__(self, name, amount=1, *, manager):
        self.name = name
        self.amount = amount
        self._manager = weakref.proxy(manager)

    @property
    def buy_cost(self):
        """Get price to buy this item."""
        return self._manager.get_buy_price(self.name)

    @property
    def sell_cost(self):
        """Get price when selling this item."""
        return self._manager.get_sell_price(self.name)

    @property
    def emoji(self):
        """Get the emoji of this item."""
        return self._manager.get_emoji(self.name)

    @emoji.setter
    def emoji(self, new_emoji):
        """Set the emoji of this item."""
        self._manager._items[self.name]["emoji"] = new_emoji

    def init_emoji(self, client):
        """Initialise the emoji for this item.

        This needs to loop through the available server emojis
        because the server-specific "fm_wheat" emoji will *not*
        be a valid emoji upon output. Calling `str` on the actual
        emoji object (supplied by `client.get_all_emojis`) will
        provide the server-specific emoji string,
        e.g., ":fm_wheat:123456", which is what we want."""
        for emoji in client.get_all_emojis():
            if emoji.name == self.emoji:
                self.emoji = str(emoji)
                return

        self.emoji = ":" + self.emoji + ":"

    @property
    def category(self):
        """Get the category of this item."""
        return self._manager.get_category(self.name)


# USAGE EXAMPLES:
# player.has(Item), player.has("wheat")
# - returns True if item is present, False if not
#
# player.items += Item, player.items += "wheat", player.items += Container
# ALL EQUIVILANT TO player.items.append()
# player.items -= Item, player.items -= "wheat", player.items -= Container
# ALL EQUIVILANT TO player.items.remove()
# - will add/remove an item/items from the players inventory,
#   returns an error if not present or if too many are removed
#
# player.items[Item], player.items["wheat"]
# - returns the item object
#
# for item in player.items:
# - returns each item object
class Container:
    """Stores `Item`s.

    This attempts to make interactions with the players' inventory as
    low-friction as possible by overloading operators
    such as `+` and `-`."""

    # TODO: Change default value of `items_input` to avoid problems
    #       with the late-binding of names.
    def __init__(self, items_input=[], *, manager):
        # Hold a reference to the `MarketManager` to use in instantiating `Item`s.
        self._manager = manager

        # This if statement makes it so that Container can accept
        # both an item or list of items as an input
        if isinstance(items_input, Item):
            self.items = [items_input]
        elif isinstance(items_input, list):
            self.items = items_input

    def has(self, input_):
        """Check if player has `input_` item.

        `input_` can be a `str` representing an item, e.g., "wheat"
        OR an instance of `Item`, which additionally checks if
        the player has greater than or equal to the amount of items
        in the stack of items represented by `input_`."""
        name = None
        if isinstance(input_, str):
            name = input_
        elif isinstance(input_, Item):
            name = input_.name

        for item in self.items:
            if name == item.name:
                if isinstance(input_, Item):
                    return item.amount >= input_.amount
                return True
        return False

    def __add__(self, other):
        # target_item = items in the container that's being added from
        def add_item(tar_item):
            # sorce_item = items in the container that's being added too
            found = False
            for sor_item in self.items:
                if sor_item.name == tar_item.name:
                    sor_item.amount += tar_item.amount
                    found = True
                    break
            if not found:
                # if the target item does not exist in the source, then we must create it there
                self.items.append(
                    Item(tar_item.name, amount=tar_item.amount, manager=self._manager)
                )

        if isinstance(other, Container):
            for item in other:
                add_item(item)

        elif isinstance(other, Item):
            add_item(other)

        elif isinstance(other, str):
            add_item(Item(other, manager=self._manager))

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
                        raise ValueError(
                            f'More "{tar_item.name}"\'s removed than in Container.'
                        )
                    return
            raise ValueError(f'Item "{tar_item.name}" not present in Container.')

        if isinstance(other, Container):
            for item in other:
                remove_item(item)

        elif isinstance(other, Item):
            remove_item(other)

        elif isinstance(other, str):
            remove_item(Item(other, manager=self._manager))

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

    def __len__(self):
        return len(self.items)

    # Alex still gets his .append() and .remove() he had before
    def append(self, items):
        """Add `items` to this container."""
        self.__add__(items)

    def remove(self, items):
        """Remove `items` from this container."""
        if isinstance(items, Container):
            items = items.items
        for item in items:
            # return an error if the container does not have (enough of) an item.
            if item not in self.items:
                raise ValueError(f'Item: "{item}" not present in Container.')
            elif items[item] > self.items[item]:
                raise ValueError(f'More "{item}"s removed than in Container.')

            elif items[item] == self.items[item]:
                del self.items[item]
            else:
                self.items[item] -= items[item]
        self.__sub__(items)

    def sort(self):
        """Sort this container by the name of its items."""
        # sort the contents of the container alphabetically
        # this is done automatically whenever an item is added/removed from the Container
        self.items.sort(key=lambda item: item.name)
