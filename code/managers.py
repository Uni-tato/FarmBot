from util import FarmbotCSVDialect

import csv


# TODO: Figure out what methods should be here. Flesh out the events mechanic more.
class EventManager:
    pass


# Crops and trees are handled by this class.
class CropManager:
    def __init__(self, crops_file_text):
        self._crops = {}
        # TODO: Implement a general version of the csv parsing.
        reader = csv.DictReader(
            (row for row in crops_file if not row.startswith("#")),
            dialect=FarmbotCSVDialect,
        )
        for row in reader:
            self._crops[row["name"]] = {
                "seed": row["seed"],
                "item": row["item"],
                "minItem": int(row["minItem"]),
                "maxItem": int(row["maxItem"]),
                "minLifeTime": int(row["minLifeTime"]),
                "maxLifetime": int(row["maxLifetime"]),
                "emoji": row["emoji"],
            }

    def _get_inner(self, crop, field):
        try:
            crop_info = self._crops[crop]
        except KeyError:
            # TODO: Replace with a non-user-facing error?
            raise ValueError(f"`{crop}` is not a valid crop.")

        return crop_info[field]

    def get_item(self, crop):
        return _get_inner(crop, "item")

    def get_seed(self, crop):
        return _get_inner(crop, "seed")

    def get_min_items(self, crop):
        return _get_inner(crop, "minItem")

    def get_max_items(self, crop):
        return _get_inner(crop, "maxItem")

    def get_min_lifetime(self, crop):
        return _get_inner(crop, "minLifeTime")

    def get_max_lifetime(self, crop):
        return _get_inner(crop, "minItem")

    def get_emoji(self, crop):
        return _get_inner(crop, "minItem")

    # Returns whether it is a `Crop` or `Tree`.
    def get_type(self, crop):
        return _get_inner(crop, "minItem")


class MarketManager:
    def __init__(self, items_file_text):
        self.items = {}
        # TODO: Implement a general version of the csv parsing.
        reader = csv.DictReader(
            (row for row in item_file if not row.startswith("#")),
            dialect=FarmbotCSVDialect,
        )
        for row in reader:
            self.items[row["name"]] = {
                "buy": row["buy"],
                "sell": row["sell"],
                "emoji": row["emoji"],
            }

    def _get_inner(self, item, field):
        try:
            item_info = self.items[item]
        except KeyError:
            # TODO: Replace with a non-user-facing error?
            raise ValueError(f"`{item}` is not a valid item.")

        return item_info[field]

    def get_buy_price(self, item_name):
        return _get_inner(item_name, "buy")

    def get_sell_price(self, item_name):
        return _get_inner(item_name, "sell")

    def get_emoji(self, item_name):
        return _get_inner(item_name, "emoji")
