# TODO: Figure out what methods should be here. Flesh out the events mechanic more.
class EventManager:
    pass


# Crops and trees are handled by this class.
class CropManager:
    def __init__(self, crops_file_text):
        # TODO: Implement a general version of the csv parsing.
        self.crops = {}
    
    def get_min_items(self, crop):
        ...

    def get_max_items(self, crop):
        ...

    def get_min_lifetime(self, crop):
        ...

    def get_max_lifetime(self, crop):
        ...

    def get_emoji(self, crop):
        ...

    # Returns whether it is a `Crop` or `Tree`.
    def get_type(self, crop):
        ...


class MarketManager:
    def __init__(self, items_file_text):
        # TODO: Implement a general version of the csv parsing.
        self.items = {}

    def get_buy_price(self, item_name):
        ...

    def get_sell_price(self, item_name):
        ...

    def get_emoji(self, item_name):
        ...
