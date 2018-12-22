import items

# This'll be a dictionary where the keys are the player discord objects, and the values are this custom player class
players = {}


market_manager = None


def init(market_manager_):
    global market_manager
    market_manager = market_manager_


class Player:
    def __init__(self, player):
        # This'll be the discord object that represents the player
        self.player = player

        self.farm = None

        self.items = items.Container(
            [items.Item("wheat seeds", manager=market_manager)], manager=market_manager
        )

        self.money = 10

        # Here, there will probably be some other stuff such as player upgrades and shit
        # `then with the money you can upgrade your farm, for example get more plots, reduce grow time etc` - Alex
        # These values might be here if they're player specific

    def has(self, item_name):
        return self.items.has(item_name)


# returns the player object corresponding to ctx.message.author
# Also automagically creates the player object if there isn't one already
def get(ctx):
    if ctx.message.author not in players:
        players[ctx.message.author] = Player(ctx.message.author)
    return players[ctx.message.author]
