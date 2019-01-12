"""A Discord bot for a farm idle game."""
import pickle
import os
import weakref
import asyncio
import time
import random
import datetime

import discord
from discord.ext.commands import Bot, check

import ask
import players as play
import farm
import items as stuff #nice.
import errors
import assist
from managers import CropManager, MarketManager
from util import get_amount, get_name
import research as res
import gambling as gamble
import colours as colour

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


@client.command(pass_context=True)
@check(errors.has_no_farm)
async def create(ctx, *args):
    name = get_name(args, True)
    if name == "":
        await assist.help(ctx, args)
        return

    current_player = play.get(ctx)

    answer = await ask.ask(
        ctx.message, f"Are you sure you wish to start a new farm called `{name}`?"
    )
    if answer:
        current_player.farm = farm.Farm(name)
        await client.say(f"Farm: `{name}`, created.")
        await res.unlock_free(current_player,(0,1))


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
        await client.say(f"Sorry {current_player.player.mention}, all your plots are full.\nPlot **#{current_player.farm.plots.index(plot)+1}** will finish in **{plot.time(str)}**.")
        return

    # find the corresponding crop
    for crop_ in crop_manager.crops:
        if plant in (crop_.name, crop_.seed):
            crop = crop_
            break
    else:
        await client.say(f"Sorry {current_player.player.mention}, `{plant}` is not a valid plant or seed.\nFor a list of all items, including seeds, type: `{prefix}items`.")
        return

    if not current_player.can_plant(crop):
        await client.say(f"Sorry {current_player.player.mention}, but you need to research {crop.emoji} `{crop.name}` before you can plant it.")
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

    if command_type is 0:
        # fm plant 3 wheat
        amount = get_amount(args)
        plots = plots[:amount]

        if amount < 1:
            await client.say(f"Sorry {current_player.player.mention}, you cannot plant `{amount}` {crop.emoji} `{plant} {crop.type}`s.")
            return
        if not current_player.has(stuff.Item(crop.seed, amount)):
            await client.say(f"Sorry {current_player.player.mention}, you do not have enough `{crop.seed}`.\nBuy more with `{prefix}buy {crop.seed}`.")
            return

    elif command_type is 1:
        # fm plant * wheat
        if current_player.has(crop.seed):
            amount = current_player.items[crop.seed].amount
        else:
            await client.say(f"Sorry {current_player.player.mention}, you do not have enough `{crop.seed}`.\nBuy more with `{prefix}buy {crop.seed}`.")
            return

        amount = min(amount, len(plots))
        plots = plots[:amount]

    # Actually plant the crop in each plot.
    for plot in plots:
        plant_time = round(time.time())
        plot.plant(crop, plant_time)
        current_player.items -= crop.seed

    xp = 0
    for item in market_manager.items:
        if item.name == crop.seed:
            xp = item.buy_cost*len(plots)

    # Make the output look hella nice.
    plot_indexes = f"**Plot #{plots[0].n}**"
    if len(plots) != 1:
        plot_indexes = "**Plots** "
        for plot in plots[:-1]:
            plot_indexes += f"**#{plot.n}**, "
        plot_indexes += f"& **#{plots[-1].n}**"

    await client.say(
            f"Planted {crop.emoji} `{crop.name}` in {plot_indexes}."
            f"\nTime until completion is **{plots[0].time(str, False)}**."
    )
    current_player.give_xp(xp)
    await current_player.lvl_check(ctx)
    return


@client.command(pass_context=True, aliases=["h", "harv", "har"])
@check(errors.has_farm)
async def harvest(ctx):
    current_player = play.get(ctx)

    reap = stuff.Container([])
    xp = 0
    for plot in current_player.farm.plots:
        item = plot.harvest()
        if item is not None:
            reap += item
            xp += item.buy_cost*item.amount

    if len(reap) == 0:
        await client.say(
            f"Sorry {ctx.message.author.mention}, but there was nothing to harvest."
        )
        return

    embed = discord.Embed(title="*Harvest Results:*", colour=colour.INFO)
    text = ""
    for item in reap:
        text += f"{item.emoji} **{item.name}** (x{item.amount})\n"
        current_player.items += item
    embed.add_field(name="**__Items:__**", value=text)
    embed.add_field(name="**__xp gained:__**", value = xp)

    await client.send_message(
        ctx.message.channel, f"{current_player.player.mention} ->", embed=embed
    )
    current_player.give_xp(xp)
    await current_player.lvl_check(ctx)


@client.command(pass_context=True, aliases=["i", "inv", "invin", "inventor"])
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
        title=f"*{queried_player.player.name}'s Inventory:*", colour=colour.INFO
    )
    embed.add_field(name="**Money:**", value=f":moneybag:: ${queried_player.money},\n{rt_emoji}:{queried_player.r_tokens}")
    embed.add_field(name="**Level:**", value = f"{queried_player.lvl}: {queried_player.xp}xp.")
    for category in categories:
        embed.add_field(name=f"**{category}:**", value=categories[category])

    await client.send_message(
        ctx.message.channel, f"{current_player.player.mention} ->", embed=embed
    )


@client.command(pass_context=True, aliases=["stat", "stats", "s"])
@check(errors.has_farm)
async def status(ctx):
    current_player = play.get(ctx)
    embed = discord.Embed(
        title=f"***{current_player.farm.name}*** *status:*", colour=colour.INFO
    )

    for index, plot in enumerate(current_player.farm.plots):
        text = ""
        if plot.crop is None:
            text = "Empty"
        else:
            text = f"**Crop:** {plot.crop.emoji}{plot.crop.name}\n"
            if plot.time(int) == 0:
                text += f"**Status:** Ready!"
            else:
                text += f"**Status:** {plot.time(str)}"

        embed.add_field(name=f"**__Plot #{index + 1}__:**", value=text)

    await client.send_message(
        ctx.message.channel, f"{current_player.player.mention} ->", embed=embed
    )


@client.command(pass_context=True, aliases = ['b'])
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
        await client.say(f"Sorry {current_player.player.mention}, `{plant}` is not a known item.\nFor a list of all items, type: `{prefix}items`.")
        return

    # Ensure that the user cannot buy an invalid number of items.
    if item.amount < 1:
        await client.say(f"Sorry {current_player.player.mention}, but you cannot buy `{amount}` {item.emoji}`{item.name}`s")
        return

    cost = round(item.buy_cost * item.amount * current_player.buy_multiplier, 2)
    if current_player.money < cost:
        await client.say(
            f"Sorry {current_player.player.name}, but you don't have enough money."
            f"\nYou have: **${current_player.money}**, but you need: **${cost}**."
        )
        return

    name_and_amount = f"{item.emoji}`{item.name}` x**{item.amount}** at **{current_player.buy_multiplier * 100}%** price"

    answer = await ask.ask(
        ctx.message,
        f"{current_player.player.mention}, Are you sure you want to buy {name_and_amount} for **${cost}**?",
        answers={"💸": True, "❌": False},
    )
    if answer:
        current_player.money = round(current_player.money-cost,2)
        current_player.items += item
        await client.say(
            f"Bought {name_and_amount} for **${cost}**.\n"
            f"Money Remaining: ${current_player.money}."
        )
        current_player.give_xp(item.buy_cost * item.amount /2)
        await current_player.lvl_check(ctx)


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
        await client.say(f"Sorry {current_player.player.mention}, `{item_name}` is not a known item.")
        return

    # Ensure that the user cannot sell an invalid number of items.
    if item.amount < 1:
        await client.say(f"Sorry {current_player.player.mention}, but you cannot sell `{amount}` {item.emoji}`{item.name}`s")
        return

    # Then check if the user actually *has* this item...
    if not current_player.has(item):
        await client.say(f"Sorry {current_player.player.mention}, but you don't have `{amount}` {item.emoji}`{item.name}`(s)")
        return

    # Then we confirm if the user really wants to sell this...
    total_price = item.sell_cost * item.amount * current_player.sell_multiplier
    answer = await ask.ask(
        ctx.message,
        f"Are you sure you wish to sell {item.emoji}`{item.name}` x{item.amount}"
        f"for ${total_price}?",
        answers={"💸": True, "❌": False},
    )
    if answer in (False, None):
        return

    # And only **then** we know we can sell it:
    current_player.items -= item
    current_player.money += total_price
    await client.say(f"{current_player.player.mention}, you now have **${current_player.money}**.")
    current_player.give_xp(item.sell_cost * item.amount /2)
    await current_player.lvl_check(ctx)


@client.command(pass_context=True, aliases=["flip", "f", "cf"])
async def coinflip(ctx, *args):
    current_player = play.get(ctx)
    amount = get_amount(args)
    if await can_gamble(current_player, amount):
        current_player.gambling_cooldown = datetime.datetime.now() + datetime.timedelta(hours = 1)
        await gamble.coinflip(current_player, amount)


@client.command(pass_context=True, aliases=["bjack"])
async def blackjack(ctx, *args):
    current_player = play.get(ctx)
    amount = get_amount(args)
    if await can_gamble(current_player, amount):
        current_player.gambling_cooldown = datetime.datetime.now() + datetime.timedelta(hours = 1)
        await gamble.blackjack(ctx.message.channel, play.get(ctx), get_amount(args))


@client.command(pass_context=True)
async def hit(ctx, *args):
    await gamble.hit(ctx.message.channel, play.get(ctx))


@client.command(pass_context=True)
async def stand(ctx, *args):
    await gamble.stand(ctx.message.channel, play.get(ctx))


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


@client.command(pass_context=True)
async def dxp(ctx, amount):
    amount = int(amount)
    current_player = play.get(ctx)
    current_player.xp += amount
    await client.say(f"gave {current_player.player.mention} {amount}xp.")
    await current_player.lvl_check(ctx)


@client.command(pass_context=True, aliases = ["d"])
async def debug(ctx):
    current_player = play.get(ctx)
    await client.say(current_player.farm.plot_count)


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
    embed = discord.Embed(title="**__FarmBot Items.__**", colour=colour.INFO)
    for category in categories:
        embed.add_field(name=f"**{category}**", value=categories[category])

    current_player = play.get(ctx)
    await client.send_message(
        ctx.message.channel, f"{current_player.player.mention} ->", embed=embed
    )


@client.command(pass_context=True, aliases = ["r"])
async def research(ctx, *args):
    name = '_'.join(str(x) for x in args)
    current_player = play.get(ctx)
    if name not in res.technologies:
        await client.say(f"{current_player.player.mention}, {name} is not a valid technology.")
        return None
    tech = res.get_tech(name)
    for req_name in tech.requirements:
        if req_name not in current_player.technologies:
            await client.say(f"{current_player.player.mention} you are missing some required technologies needed for this research.")
            break
    else:
        if current_player.lvl < tech.lvl:
            await client.say(f"{current_player.player.mention} you need to be level {tech.lvl} or greater to research this.")
        elif name in current_player.technologies:
            await client.say(f"{current_player.player.mention} you have already researched this technology.")
        elif current_player.r_tokens < tech.cost:
            await client.say(f"{current_player.player.mention} you do not have enough research tokens to research this technology.")
        else:
            answer = await ask.ask(
                ctx.message,
                f"Are you sure you wish to research {name}?\nIt will cost {tech.cost} research tokens."
            )
            if answer == True:
                await tech.research(current_player)


@client.command(pass_context=True, aliases = ["t","techs"])
async def technologies(ctx):
    current_player = play.get(ctx)
    all_techs = res.technologies
    available_techs = {}
    for name, tech in all_techs.items():
        has_req = True
        for req_name in tech.requirements:
            if req_name not in current_player.technologies:
                has_req = False
        if not has_req:
            continue
        elif current_player.lvl < tech.lvl:
            continue
        elif name in current_player.technologies:
            continue
        available_techs[name] = tech
    embed = discord.Embed(title = "**__Technologies:__**", colour = colour.INFO)
    embed.add_field(name = "**__Tokens:__**", value = f"{rt_emoji} {current_player.r_tokens} tokens")
    for name, tech in available_techs.items():
        embed.add_field(name = f"__{name}:__", value = f"cost: {tech.cost}, unlocked at: {tech.lvl}")
    await client.say(f"{current_player.player.mention} ->", embed = embed)


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

def get_rt_emoji():
    for emoji in client.get_all_emojis():
        if emoji.name == 'fm_rt':
            return str(emoji)

def auto_harvest():
    for member,player in play.players.items():
        amount = player.auto_harvest_lvl
        if player.farm == None:
            continue
        plots = player.farm.plots[:amount]
        reap = stuff.Container([])
        for plot in plots:
            item = plot.harvest()
            if item is not None:
                reap += item
        if len(reap) > 0:
            player.items += reap

async def can_gamble(current_player, amount):
    if datetime.datetime.now() < current_player.gambling_cooldown:
        delta = current_player.gambling_cooldown - datetime.datetime.now()
        total_minutes = round(delta.seconds / 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        time = f"{minutes} minutes"
        if hours != 0:
            time = f"{hours} hours and {time}"
        await client.say(f"Sorry {current_player.player.mention}, you may not gamble again for another {time}.")
    elif current_player.money < 100:
        await client.say(f"Sorry {current_player.player.mention}, you may not gamble if you have less than $100.")
        return False
    elif amount > current_player.money * 0.15:
        await client.say(f"Sorry {current_player.player.mention}, you may not gamble more than 15% of your money.\nTne most you may gamble is: ${round(current_player.money * 0.15, 2)}.")
        return False
    else:
        return True

async def loop():
    await client.wait_until_ready()
    autosave_counter = 0
    while not client.is_closed:
        await asyncio.sleep(5.0)

        autosave_counter += 1
        if autosave_counter * 5 >= autosave_interval * 60:
            autosave_counter = 0
            await save()

            auto_harvest() # We may want to tweak when this fires, but for now this works.


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

    global rt_emoji
    rt_emoji = get_rt_emoji()


if __name__ == "__main__":
    ask.init(client)
    play.client = client # <-- the better way to do it.
    res.client = client
    gamble.init(client, play.players, prefix)
    errors.init(client, play.players)
    assist.init(client, prefix)

    with open("txt/crops.csv", "r") as crops_file:
        crop_manager = CropManager(crops_file.readlines())

    with open("txt/items.csv", "r") as items_file:
        market_manager = MarketManager(items_file.readlines())

    play.init(market_manager, crop_manager)
    farm.init(market_manager)
    stuff.init(market_manager)
    res.init(crop_manager.crops)

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
