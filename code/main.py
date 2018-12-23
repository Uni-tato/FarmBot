"""A Discord bot for a farm idle game."""
import pickle
import os

import discord
from discord.ext.commands import Bot, check

import ask
import players as play
import farm
import items as items_mod  # we can change this to something else, I jsut cant be bothered thinking
import errors
import assist
from managers import CropManager, MarketManager
from util import get_amount, get_name

#### QUICK TO DO LIST: ####
# - Make the `fm plant` command better:
#   print to the user time until compleation? Let user select plots manually?

# TODO: Make `prefix` a constant.
prefix = "fm "
# `Bot` is a subclass of `discord.Client`
# so it can be used anywhere that `discord.Client` can be used.
client = Bot(command_prefix=prefix)

ask.init(client)  # ask.py wants access to the client too!
errors.init(client, play.players)
assist.init(client, prefix)

client.remove_command("help")


# TODO: Rename this so that it doesn't conflict with `builtins.help`.
@client.command(pass_context=True)
async def help(ctx, *args):
    await assist.help(ctx, args)


@client.event
async def on_command_error(error, ctx):
    await errors.on_command_error(error, ctx)


@client.command(pass_context=True)
@check(errors.has_no_farm)
async def create(ctx, *args):
    name = get_name(args, True)
    if name == "":
        await client.say("You can't create a farm with no name!")
        return

    play.players[ctx.message.author] = play.Player(ctx.message.author)

    answer = await ask.ask(
        ctx.message, f"Are you sure you wish to start a new farm called `{name}`?"
    )
    if answer:
        play.players[ctx.message.author].farm = farm.Farm(name)
        await client.say("Farm created!")


@client.command(pass_context=True, aliases=["p", "plan"])
@check(errors.has_farm)
async def plant(ctx, *seed_name):
    plant = get_name(seed_name)
    current_player = play.get(ctx)

    for crop in crop_manager.crops:
        if plant in (crop.seed, crop.name):
            # we've fond the crop that the player was looking for
            if not current_player.has(crop.seed):
                await client.say(f"Uhhhh, you don't have any `{crop.seed}`...")
                return

            # now we need to plant it...
            for index, plot in enumerate(current_player.farm.plots):
                if plot.crop is None:
                    plot.plant(crop)
                    current_player.items -= crop.seed
                    await client.say(
                        f"Planted {crop.emoji} **{crop.name}** in **Plot #{index + 1}**! "
                        f"Time until completion is **{plot.time(str, False)}**."
                    )
                    return

            await client.say("Sorry, but all your plots are full!")
            return

    await client.say(
        f"I wasn't able to find `{plant}`, are you sure you spelt it right?"
    )


@client.command(pass_context=True, aliases=["h", "harv", "har"])
@check(errors.has_farm)
async def harvest(ctx):
    current_player = play.get(ctx)

    reap = items_mod.Container([], manager=market_manager)
    for plot in current_player.farm.plots:
        item = plot.harvest()
        if item is not None:
            reap += item

    if len(reap) == 0:
        await client.say(
            f"Sorry {ctx.message.author.mention}, but there was nothing too harvest!"
        )
        return

    embed = discord.Embed(title="*Harvest Results:*", colour=0xFFE48E)
    text = ""
    for item in reap:
        text += f"{item.emoji} **{item.name}** (x{item.amount})\n"
        current_player.items += item
    embed.add_field(name="**__Items__:**", value=text)

    await client.send_message(
        ctx.message.channel, f"{current_player.player.mention} ->", embed=embed
    )


@client.command(pass_context=True, aliases=["i", "inv", "invin"])
async def inventory(ctx, player=None):
    current_player = play.get(ctx)

    if player is None:
        queried_player = current_player
    else:
        queried_player = play.get(ctx.message.mentions[0])

    # Separate items into categories.
    categories = {}
    for item in queried_player.items:
        category = item.category
        if category not in categories:
            categories[category] = ""
        categories[category] += f"{item.emoji} **{item.name}** x{item.amount}\n"

    # Create and prepare embed.
    embed = discord.Embed(
        title=f"*{queried_player.player.name}'s Inventory:*", colour=0x0080D6
    )
    embed.add_field(name="**Money:**", value=f":moneybag: ${queried_player.money}")
    for category in categories:
        embed.add_field(name=f"**{category}**", value=categories[category])

    await client.send_message(
        ctx.message.channel, f"{current_player.player.mention} ->", embed=embed
    )


@client.command(pass_context=True, aliases=["stat", "stats", "s"])
@check(errors.has_farm)
async def status(ctx):
    current_player = play.get(ctx)
    embed = discord.Embed(
        title=f"***{current_player.farm.name}*** *status:*", colour=0x00D100
    )

    for index, plot in enumerate(current_player.farm.plots):
        text = ""
        if plot.crop is None:
            text = "Empty"
        else:
            text = f"**Crop:** {plot.crop.emoji} {plot.crop.name}\n"
            if plot.time(int) == 0:
                text += f"**Status:** Ready!"
            else:
                text += f"**Status:** {plot.time(str)}"

        embed.add_field(name=f"**__Plot #{index + 1}__:**", value=text)

    await client.send_message(
        ctx.message.channel, f"{current_player.player.mention} ->", embed=embed
    )


@client.command(pass_context=True)
async def buy(ctx, *args):
    if len(args) == 0:
        return

    current_player = play.get(ctx)
    amount = get_amount(args)
    plant = get_name(args)

    if market_manager.exists(plant):
        item = items_mod.Item(plant, amount=amount, manager=market_manager)
    else:
        await client.say(f"`{plant}` isn't a real item...")
        return

    # Ensure that the user cannot buy an invalid number of items.
    if item.amount < 1:
        await client.say(f"You can't buy less than **1** item!")
        return

    if current_player.money < item.buy_cost * item.amount:
        await client.say(
            f"Sorry {current_player.player.name} but you don't have enough money! "
            f"(Only **${current_player.money}** instead of **${item.buy_cost * item.amount}**)"
        )
        return

    name_and_amount = f"{item.name} x{item.amount}"
    total_price = item.buy_cost * item.amount

    answer = await ask.ask(
        ctx.message,
        f"**Are you sure you want to buy {item.emoji} **{name_and_amount}** for **${total_price}**?**",
        answers={"💸": True, "❌": False},
    )
    if answer:
        current_player.money -= item.buy_cost * item.amount
        current_player.items += item
        await client.say(
            f"Bought {item.emoji} **{item.name} (x{item.amount})**! "
            f"Money Remaining: $**{current_player.money}**."
        )


@client.command(pass_context=True)
async def sell(ctx, *args):
    if len(args) == 0:
        return

    # First parse the info given to us...
    current_player = play.get(ctx)
    amount = get_amount(args)
    item_name = get_name(args)

    # Then check if the item is actually a real item...
    if market_manager.exists(item_name):
        item = items_mod.Item(item_name, amount=amount, manager=market_manager)
    else:
        await client.say(f"`{item_name}` isn't a real item...")
        return

    # Ensure that the user cannot sell an invalid number of items.
    if item.amount < 1:
        await client.say(f"You can't sell less than **1** item!")
        return

    # Then check if the user actually *has* this item...
    if not current_player.has(item):
        await client.say(f"Sorry, but you don't have enough of this item to sell!")
        return

    # Then we confirm if the user really wants to sell this...
    total_price = item.sell_cost * item.amount
    answer = await ask.ask(
        ctx.message,
        f"Are you *sure* you wish to sell {item.emoji} **{item.name}** (x{item.amount}) "
        f"for $**{total_price}**?",
    )
    if answer in (False, None):
        return

    # And only **then** we know we can sell it:
    current_player.items -= item
    current_player.money += total_price
    await client.say(f"Sold! You now have $**{current_player.money}**.")


@client.command(pass_context=True)
async def dgive(ctx, *args):
    current_player = play.get(ctx)
    if len(args) == 0:
        return

    amount = 1
    plant = ""
    try:
        int(args[0])
    except ValueError:
        plant = " ".join(args).strip()
    else:
        amount = int(args[0])
        plant = " ".join(args[1:]).strip()

    if not market_manager.exists(plant):
        await client.say(f"`{plant}` isn't a real item...")
        return

    # Someone has gotta do something about how we add items to inventories.
    item = items_mod.Item(plant, amount=amount, manager=market_manager)
    current_player.items += item
    await client.say(
        f"Gave {item.emoji} **{item.name}** (x{item.amount}) to {current_player.player.name}"
    )


@client.command(pass_context=True)
async def items(ctx):
    # Separate items into categories.
    categories = {}
    for item in market_manager.items:
        category = item.category
        if category not in categories:
            categories[category] = ""

        item_header = f"{item.emoji} **{item.name}**"
        buy_text = f"buy: **${item.buy_cost}**"
        sell_text = f"sell: **${item.sell_cost}**"

        categories[category] += f"{item_header}:\n\t {buy_text}, {sell_text}.\n"

    # Create and prepare embed.
    embed = discord.Embed(title="**__FarmBot Items.__**", colour=0x0080D6)
    for category in categories:
        embed.add_field(name=f"**{category}**", value=categories[category])

    current_player = play.get(ctx)
    await client.send_message(
        ctx.message.channel, f"{current_player.player.mention} ->", embed=embed
    )


@client.command()
async def save():
    try:
        os.remove("../players.dat")
    except FileNotFoundError:
        pass
    f = open("../players.dat", "wb+")

    pickle.dump(play.players, f)

    f.close()

    await client.say("saved!")


@client.command()
async def reload():
    try:
        f = open("../players.dat", "rb")
    except Exception:
        await client.say("Sorry, but there's nothing to reload!")
    else:
        play.players = pickle.load(f)
        f.close()
        await client.say("Reloaded!")


@client.event
async def on_reaction_add(reaction, user):
    # Don't act when the bot itself has added a reaction.
    if user == client.user:
        return

    message = reaction.message
    for question in ask.questions:
        # The message reacted to is an unanswered question that was answered by the right person
        if question.message.id == message.id and user == question.orig_message.author:
            for emoji in question.answers:
                if emoji == reaction.emoji:
                    # The correct user has reacted to a question with a valid emoji
                    question.emoji = emoji
                    question.answer = question.answers.get(emoji)
                    question.answered = True
                    return


@client.event
async def on_ready():
    print("FarmBot is online")

    for item in market_manager.items:
        item.init_emoji(client)
    for crop in crop_manager.crops:
        crop.init_emoji(client)


if __name__ == "__main__":
    with open("txt/crops.txt", "r") as crops_file:
        crop_manager = CropManager(crops_file.readlines())

    with open("txt/items.txt", "r") as items_file:
        market_manager = MarketManager(items_file.readlines())

    play.init(market_manager)
    farm.init(market_manager)

    # Will try and get a token from code/token.txt
    # If this fails (file does not exist) then it asks for the token and creates the file
    try:
        f = open("txt/token.txt")
    except FileNotFoundError:
        token = input("Please input the Discord Token: ")
        f = open("txt/token.txt", "w+")
        f.write(token)
    else:
        token = f.read()
    finally:
        f.close()
        client.run(token)
