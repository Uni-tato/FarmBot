#literally does nothing yet.
import datetime
import time
import random
import weakref

import items


market_manager = None
def init(market_manager_):
    global market_manager
    market_manager = market_manager_


class Farm:
    def __init__(self, name, plot_count = 2):
        self.name = name
        self.plot_count = plot_count
        self.plots = [Plot() for i in range(plot_count)]


class Plot:
    def __init__(self):
        self.crop = None
        self._start_time = None
        self._first_planted_time = None
        self._num_harvests = 0
    
    @property
    def complete_time(self):
        return self._start_time + self.crop.time*60

    def plant(self, crop):
        current_time = round(time.time())

        self.crop = crop
        self._start_time = current_time
        # A temporary work-around to be able to detect when trees should die.
        if self.crop.type == "tree" and self._num_harvests == 0 or self.crop.type == "crop":
            self._first_planted_time = current_time

    def harvest(self):
        current_time = time.time()
        if self.crop is None or current_time < self.complete_time:
            return None

        # The crop can now be harvested.
        item_name = self.crop.item
        item_count = random.randint(self.crop.min_item, self.crop.max_item)

        if self.crop.type == "crop":
            self.crop = None
        elif self.crop.type == "tree":
            # The life of a tree is not set in stone.
            lifetime = random.randint(self.crop.min_lifetime, self.crop.max_lifetime) * 60
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

        return items.Item(
            item_name,
            amount=item_count,
            manager=market_manager
        )
        #return {item:item_count} #if these return none then I will need to make item a copy.

    def time(self, data_type, from_present = True):
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
                return round(time_int/60, 1)

        elif data_type is str:
            # We need to nicely format time_int into a non-cancerous string.
            if time_int < 60:
                return f"{time_int} sec"
            elif time_int < 60*60:
                return f"{round(time_int/60, 1)} min"
            elif time_int < 60*60*24:
                return f"{round(time_int/60/60, 1)} hour"
            elif time_int < 60*60*24*365:
                return f"{round(time_int/60/60/24, 1)} days"
            else:
                raise ValueError("time is waaaaay too long")


class Crop:
    def __init__(self, name, *, manager):
        self.name = name
        self._manager = weakref.proxy(manager)

    @property
    def time(self):
        return self._manager.get_time(self.name)

    @property
    def seed(self):
        return self._manager.get_seed(self.name)

    @property
    def item(self):
        return self._manager.get_item(self.name)

    @property
    def min_item(self):
        return self._manager.get_min_items(self.name)

    @property
    def max_item(self):
        return self._manager.get_max_items(self.name)

    @property
    def min_lifetime(self):
        return self._manager.get_min_lifetime(self.name)

    @property
    def max_lifetime(self):
        return self._manager.get_max_lifetime(self.name)

    @property
    def emoji(self):
        return self._manager.get_emoji(self.name)

    @emoji.setter
    def emoji(self, new_emoji):
        self._manager._crops[self.name]["emoji"] = new_emoji

    def init_emoji(self, client):
        for emoji in client.get_all_emojis():
            if emoji.name == self.emoji:
                self.emoji = str(emoji)
                return

        self.emoji = ":" + self.emoji + ":"

    @property
    def type(self):
        return self._manager.get_type(self.name)

