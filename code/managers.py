import random
import csv

from util import FarmbotCSVDialect
from farm import Crop
from items import Item


class CropManager:
    def __init__(self, crops_file_text):
        self.crops = []
        # The internal data storage for crops
        self._crops = {}
        # TODO: Implement a general version of the csv parsing.
        reader = csv.DictReader(
            (row for row in crops_file_text if not row.startswith("#")),
            dialect=FarmbotCSVDialect,
        )
        for row in reader:
            min_item = int(row["minItem"])
            max_item = int(row["maxItem"])
            self._crops[row["name"]] = {
                "seed": row["seed"],
                "item": row["item"],
                "minItem": min_item,
                "maxItem": max_item,
                "minLifetime": int(row["minLifetime"]),
                "maxLifetime": int(row["maxLifetime"]),
                "emoji": row["emoji"],
                "time": random.randint(min_item, max_item),
            }
            self.crops.append(Crop(row["name"], manager=self))

    def _get_inner(self, crop, field):
        try:
            crop_info = self._crops[crop]
        except KeyError:
            # TODO: Replace with a non-user-facing error?
            raise ValueError(f"`{crop}` is not a valid crop.")

        return crop_info[field]

    def get_time(self, crop):
        return self._get_inner(crop, "time")

    def get_item(self, crop):
        return self._get_inner(crop, "item")

    def get_seed(self, crop):
        return self._get_inner(crop, "seed")

    def get_min_items(self, crop):
        return self._get_inner(crop, "minItem")

    def get_max_items(self, crop):
        return self._get_inner(crop, "maxItem")

    def get_min_lifetime(self, crop):
        return self._get_inner(crop, "minLifetime")

    def get_max_lifetime(self, crop):
        return self._get_inner(crop, "maxLifetime")

    def get_emoji(self, crop):
        return self._get_inner(crop, "emoji")

    # Returns whether it is a `Crop` or `Tree`.
    def get_type(self, crop):
        raise NotImplementedError


class MarketManager:
    def __init__(self, items_file_text):
        self.items = []
        # The internal data storage for crops
        self._items = {}
        # TODO: Implement a general version of the csv parsing.
        reader = csv.DictReader(
            (row for row in items_file_text if not row.startswith("#")),
            dialect=FarmbotCSVDialect,
        )
        for row in reader:
            self._items[row["name"]] = {
                "buy": row["buy"],
                "sell": row["sell"],
                "emoji": row["emoji"],
            }
            self.items.append(Item(row["name"], manager=self))

    def _get_inner(self, item, field):
        try:
            item_info = self._items[item]
        except KeyError:
            # TODO: Replace with a non-user-facing error?
            raise ValueError(f"`{item}` is not a valid item.")

        return item_info[field]

    def get_buy_price(self, item_name):
        return self._get_inner(item_name, "buy")

    def get_sell_price(self, item_name):
        return self._get_inner(item_name, "sell")

    def get_emoji(self, item_name):
        return self._get_inner(item_name, "emoji")
