"""A Discord bot for a farm idle game."""
import pickle
import os
import weakref
import asyncio
import time
import random

import discord
from discord.ext.commands import Bot, check

import ask
import players as play
import farm
import items as stuff
import errors
import assist
from managers import CropManager, MarketManager
from util import get_amount, get_name

#### QUICK TO DO LIST: ####
# - Make the `fm plant` command better:
#   print to the user time until compleation? Let user select plots manually?

# TODO: Make `prefix` a constant.
prefix = "fm "
# Autosave interval is in minutes. Making this larger does NOT improve performance.
autosave_interval = 0.5
client = Bot(command_prefix=prefix)


client.remove_command("help")
# TODO: Rename this so that it doesn't conflict with `builtins.help`.
@client.command(pass_context=True)
async def help(ctx, *args):
    await assist.help(ctx, args)


@client.event
async def on_command_error(error, ctx):
    await errors.on_command_error(error, ctx)


@client.command(pass_context=True, aliases=["flip", "f", "cf"])
async def coinflip(ctx, *args):
    current_player = play.get(ctx)
    amount = get_amount(args)

    if amount < 1:
        await client.say("Please flip a amount greater than 1.")
        return

    if amount > 1000:
        await client.say("Sorry, you're not aloud to coinflip more than 1k! Why? idk.")
        return

    if current_player.money < amount:
        await client.say("You don't have enough money... \\:P")
        return

    if random.random() > 0.5:
        current_player.money -= amount
        await client.say(f"Oof - you lost $**{amount}**! You've now got $**{current_player.money}** remaining.")
    else:
        current_player.money += amount
        await client.say(f"Congratulations - you won $**{amount}**! You've now got $**{current_player.money}**!")
    return


@client.command(pass_context=True)
@check(errors.has_no_farm)
async def create(ctx, *args):
    name = get_name(args, True)
    if name == "":
        await assist.help(ctx, args)
        return

    play.get(ctx)

    answer = await ask.ask(
        ctx.message, f"Are you sure you wish to start a new farm called `{name}`?"
    )
    if answer:
        play.players[ctx.message.author].farm = farm.Farm(name)
        await client.say("Farm created!")


@client.command(pass_context=True, aliases=["p", "plan"])
@check(errors.has_farm)
async def plant(ctx, *args):
    if len(args) == 0:
        await assist.help(ctx, args)
        return

    current_player = play.get(ctx)
    plant = get_name(args)
    plots = current_player.farm.get_empty_plots()

    if len(plots) is 0:
        plot = current_player.farm.plots[0]
        for plot_ in current_player.farm.plots:
            if plot_.time() < plot.time():
                plot = plot_
        await client.say(f"Sorry, but all your plots are full! On the bright side, **Plot #{current_player.farm.plots.index(plot)+1}** will finish in **{plot.time(str)}**!")
        return

    if args[0] is "*":
        if len(args) >= 2:
            # fm plant * wheat
            command_type = 1
        else:
            # fm plant *
            command_type = 2
            # TODO: do this
            # The idea here (`fm plant *`) is that the bot will automatically plant the highest-valued seeds in the players inventory.
            # And will keep on planting untill 1. no more plots, 2. no more seeds.
            # Returning a message for the user to see will be a pain :P
            await assist.help(ctx, args)
            return
    else:
        # fm plant 3 wheat / fm plant wheat
        command_type = 0

    # find the corresponding crop
    for crop_ in crop_manager.crops:
        if plant in (crop_.name, crop_.seed):
            crop = crop_
            break
    else:
        await client.say(f"I wasn't able to find `{plant}`, are you sure you spelt it right?")
        return

    if command_type is 0:
        # fm plant 3 wheat
        amount = get_amount(args)
        plots = plots[:amount]

        if amount < 1:
            await client.say("Sorry but that's not a valid amount! Please type in a number greater than 1.")
            return
        if not current_player.has(stuff.Item(crop.seed, amount)):
            await client.say(f"Sorry, but you don't have enough `{crop.seed}`. Buy more with `{prefix}buy {crop.seed}`!")
            return

    elif command_type is 1:
        # fm plant * wheat
        if current_player.has(crop.seed):
            amount = current_player.items[crop.seed].amount
        else:
            await client.say(f"Sorry, but you don't have enough `{crop.seed}`. Buy more with `{prefix}buy {crop.seed}`!")
            return

        amount = min(amount, len(plots))
        plots = plots[:amount]


    # Actually plant the crop in each plot.
    for plot in plots:
        plant_time = round(time.time())
        plot.plant(crop, plant_time)
        current_player.items -= crop.seed

    # Make the output look hella nice.
    plot_indexes = f"**Plot #{plots[0].n}**"
    if len(plots) != 1:
        plot_indexes = "**Plots** "
        for plot in plots[:-1]:
            plot_indexes += f"**#{plot.n}**, "
        plot_indexes += f"& **#{plots[-1].n}**"

    await client.say(
            f"Planted {crop.emoji} **{crop.name}** in {plot_indexes}! "
            f"Time until completion is **{plots[0].time(str, False)}**."
    )
    return


@client.command(pass_context=True, aliases=["h", "harv", "har"])
@check(errors.has_farm)
async def harvest(ctx):
    current_player = play.get(ctx)

    reap = stuff.Container([])
    for plot in current_player.farm.plots:
        item = plot.harvest()
        if item is not None:
            reap += item

    if len(reap) == 0:
        await client.say(
            f"Sorry {ctx.message.author.mention}, but there was nothing to harvest!"
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
        await assist.help(ctx, args)
        return

    current_player = play.get(ctx)
    amount = get_amount(args)
    plant = get_name(args)

    if market_manager.exists(plant):
        item = stuff.Item(plant, amount)
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
        await assist.help(ctx, args)
        return

    # First parse the info given to us...
    current_player = play.get(ctx)
    amount = get_amount(args)
    item_name = get_name(args)

    # Then check if the item is actually a real item...
    if market_manager.exists(item_name):
        item = stuff.Item(item_name, amount)
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
        answers={"💸": True, "❌": False},
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
        await assist.help(ctx, args)
        return

    amount = get_amount(args)
    name = get_name(args)

    if not market_manager.exists(name):
        await client.say(f"`{name}` isn't a real item...")
        return

    item = stuff.Item(name, amount)
    current_player.items += item
    await client.say(
        f"Gave {item.emoji} **{item.name}** (x{item.amount}) to {current_player.player.name}"
    )
    await log(f"Gave {item.name} (x{item.amount}) to {current_player.player.name}")


@client.command(pass_context=True)
async def dplots_add(ctx, *args):
    current_player = play.get(ctx)
    amount = get_amount(args)
    if amount < 1:
        return

    plots_n = len(current_player.farm.plots)
    current_player.farm.plots += [farm.Plot(plots_n + n + 1) for n in range(amount)]

    await client.say(f"Added {amount} new plot{'s' if amount > 1 else ''} to {current_player.player.mention}'s farm.\nTotal plots = {len(current_player.farm.plots)}")
    await log(f"Added {amount} new plot(s) to {current_player.player.name}'s farm")


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


async def log(txt):
    with open("../debug.log", "a") as f:
        f.write(time.strftime(f"[%H:%M:%S, %d/%m/%y]: {txt}\n"))


async def save():
    try:
        os.remove("../players.dat")
    except FileNotFoundError:
        pass
    f = open("../players.dat", "wb+")
    pickle.dump(play.players, f)
    f.close()


async def reload():
    try:
        f = open("../players.dat", "rb")
    except Exception:
        print("reloading error - no save detected, ignore this error")

    else:
        play.players.clear()
        play.players.update(pickle.load(f))
        f.close()
        print('reloaded')

        # Here we reapply any instance of a manager in play.players, cause they don't like being serialized.
        for player_i in play.players:
            player = play.players[player_i]

            player.items._manager = market_manager
            for item in player.items:
                item._manager = weakref.proxy(market_manager)

            if player.farm != None:
                for plot in player.farm.plots:
                    if plot.crop != None:
                        plot.crop._manager = weakref.proxy(crop_manager)


async def loop():
    await client.wait_until_ready()
    autosave_counter = 0
    while not client.is_closed:
        await asyncio.sleep(5.0)

        autosave_counter += 1
        if autosave_counter * 5 >= autosave_interval * 60:
            autosave_counter = 0
            await save()


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

    await reload()

    for item in market_manager.items:
        item.init_emoji(client)
    for crop in crop_manager.crops:
        crop.init_emoji(client)


if __name__ == "__main__":
    ask.init(client)
    errors.init(client, play.players)
    assist.init(client, prefix)

    with open("txt/crops.csv", "r") as crops_file:
        crop_manager = CropManager(crops_file.readlines())

    with open("txt/items.csv", "r") as items_file:
        market_manager = MarketManager(items_file.readlines())

    play.init(market_manager)
    farm.init(market_manager)
    stuff.init(market_manager)

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
        client.loop.create_task(loop())
        client.run(token)
