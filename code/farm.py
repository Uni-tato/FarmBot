"""Implement farm-related classes and functionality."""
import time
import random
import weakref

import items


market_manager = None
def init(market_manager_):
    """Provide module with `market_manager`."""
    global market_manager
    market_manager = market_manager_


class Farm:
    """Represents farms owned by players.

    This just stores `Plot`s which handle the real work of the
    harvesting and planting mechanic.
    """

    def __init__(self, name, plot_count=2):
        self.name = name
        self.plot_count = plot_count
        self.plots = [Plot(n+1) for n in range(plot_count)]

    def get_empty_plots(self):
        plots = []
        for plot in self.plots:
            if plot.crop is None and plot.enabled:
                plots.append(plot)
        return plots


class Plot:
    """Holds `Crop`s owned by players.

    This handles the harvesting and planting code for crops
    and trees."""

    def __init__(self, n):
        self.n = n
        self.crop = None
        self._start_time = None
        self._first_planted_time = None
        self._num_harvests = 0

        self.enabled = True
        self.disabled = False

    def enable(self):
        self.enabled = True
        self.disabled = False

    def disable(self):
        self.enabled = False
        self.disabled = True

    @property
    def complete_time(self):
        """Get the time that the crop is ready to harvest."""
        return self._start_time + self.crop.time * 60

    def plant(self, crop, plant_time=None):
        """Plant a crop."""
        if plant_time == None:
            current_time = round(time.time())
        else:
            current_time = plant_time

        self.crop = crop
        self._start_time = current_time

        # A temporary work-around to be able to detect when trees should die.
        is_new_tree = self.crop.type == "tree" and self._num_harvests == 0
        is_crop = self.crop.type == "crop"
        if is_new_tree or is_crop:
            self._first_planted_time = current_time

    def harvest(self):
        """Attempt to harvest the currently planted crop."""
        current_time = time.time()
        if self.crop is None or current_time < self.complete_time or self.disabled:
            return None

        # The crop can now be harvested.
        item_name = self.crop.item
        item_count = random.randint(self.crop.min_item, self.crop.max_item)

        if self.crop.type == "crop":
            self.crop = None
        elif self.crop.type == "tree":
            # The life of a tree is not set in stone.
            lifetime = (
                random.randint(self.crop.min_lifetime, self.crop.max_lifetime) * 60
            )
            # The user foregoes any fruit that they don't harvest on time.
            death_time = self._first_planted_time + lifetime

            if current_time > death_time:
                self.crop = None
                self._num_harvests = 0
            else:
                # Replant the tree as if it were another crop but ensure that
                # is *not* as if it is a new plant.
                self._num_harvests += 1
                self.plant(self.crop)

        return items.Item(item_name, item_count)
        # return {item:item_count} #if these return none then I will need to make item a copy.

    def time(self, data_type=int, from_present=True):
        """Get the time remaining until the crop can be harvested."""
        if self.crop is None:
            return False

        # generate time_int in seconds
        time_int = None
        if from_present:
            time_int = self.complete_time - round(time.time())
        else:
            time_int = self.crop.time * 60

        if data_type is int:
            if time_int <= 0:
                return 0
            else:
                return round(time_int / 60, 1)

        elif data_type is str:
            # We need to nicely format time_int into a non-cancerous string.
            if time_int < 60:
                return f"{time_int} sec"
            elif time_int < 60 * 60:
                return f"{round(time_int/60, 1)} min"
            elif time_int < 60 * 60 * 24:
                return f"{round(time_int/60/60, 1)} hour"
            elif time_int < 60 * 60 * 24 * 365:
                return f"{round(time_int/60/60/24, 1)} days"
            else:
                raise ValueError("time is waaaaay too long")


class Crop:
    """Represents crops which can be planted in `Plot`s.

    This is distinct from `Item`s, which can be bought and sold via
    the `MarketManager`.

    This is essentially a proxy to the `CropManager`, meaning that
    `Crop`s don't have any meaningful data by themselves, just a name
    to represent what crop it is (e.g. wheat). This was done in order
    to remain compatible with old code that dealt with `Crop`s as if
    they were entities separate from a `CropManager`."""

    def __init__(self, name, *, manager):
        self.name = name
        self._manager = weakref.proxy(manager)

    @property
    def time(self):
        """Get the time taken until this crop can be harvested.

        This is NOT an absolute time, it is a delta
        (not referring to any class here)."""
        return self._manager.get_time(self.name)

    @property
    def seed(self):
        """Get the seed name of this crop."""
        return self._manager.get_seed(self.name)

    @property
    def item(self):
        """Get the item name of this crop."""
        return self._manager.get_item(self.name)

    @property
    def min_item(self):
        """Get the minimum number of items this crop can yield."""
        return self._manager.get_min_items(self.name)

    @property
    def max_item(self):
        """Get the maximum number of items this crop can yield."""
        return self._manager.get_max_items(self.name)

    @property
    def min_lifetime(self):
        """Get the minimum time until this crop can die.

        This is NOT an absolute time, it is a delta
        (not referring to any class here).

        This is an important property for trees as this determines
        when they die, from which the time until they can
        be harvested is derived."""
        return self._manager.get_min_lifetime(self.name)

    @property
    def max_lifetime(self):
        """Get the maximum time until this crop can die.

        This is NOT an absolute time, it is a delta
        (not referring to any class here).

        This is an important property for trees as this determines
        when they die, from which the time until they can
        be harvested is derived."""
        return self._manager.get_max_lifetime(self.name)

    @property
    def emoji(self):
        """Get the emoji of this crop."""
        return self._manager.get_emoji(self.name)

    # TODO: Don't access non-public attributes of the manager--
    # use a method like `set_emoji` (not implemented)?
    # TODO: Should this *not* be a public setter? I'm not sure
    # if `emoji` gets assigned to outside of its own methods.
    @emoji.setter
    def emoji(self, new_emoji):
        """Set the emoji of this crop."""
        self._manager._crops[self.name]["emoji"] = new_emoji

    def init_emoji(self, client):
        """Initialise the emoji for this crop.

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

        # Any non-server-specific emoji will just get output normally.
        self.emoji = ":" + self.emoji + ":"

    @property
    def type(self):
        """Get the type of this crop.

        This might be expanded to types other than "crop" (normal)
        and "tree"."""
        return self._manager.get_type(self.name)

    @property
    def unlock_at_lvl(self):
        '''Gets the level at which a user can research this crop'''
        return self._manager.get_unlock_at_lvl(self.name)

    @property
    def research_cost(self):
        return self._manager.get_research_cost(self.name)

    def get_crop_data(self, attributes):
        data = {}
        if 'time' in attributes:
            data['time'] = self.time
        if 'seed' in attributes:
            data['seed'] = self.seed
        if 'item' in attributes:
            data['item'] = self.item
        if 'min_item' in attributes:
            data['min_item'] = self.min_item
        if 'max_item' in attributes:
            data['max_item'] = self.max_item
        if 'min_lifetime' in attributes:
            data['min_lifetime'] = self.min_lifetime
        if 'max_lifetime' in attributes:
            data['max_lifetime'] = self.max_lifetime
        if 'emoji' in attributes:
            data['emoji'] = self.emoji
        if 'type' in attributes:
            data['type'] = self.type
        if 'unlock_at_lvl' in attributes:
            data['unlock_at_lvl'] = self.unlock_at_lvl
        if 'research_cost' in attributes:
            data['research_cost'] = self.research_cost
        return data