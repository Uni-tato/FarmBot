import datetime
import asyncio

import discord
from discord.ext.commands import Bot, check, CommandError

import ask
import players as play
import farm
import items
import errors
from managers import CropManager, MarketManager
from util import get_amount, get_name

#### QUICK TO DO LIST: ####
# - Make a method on Crop that returns the time untill completioin in a nice string e.g. "9.1hours" and not "456mins"
# - Make the `fm plant` command better - print to the user time until compleation? Let user select plots manually?

prefix = 'fm '
# `Bot` is a subclass of `discord.Client` so it can be used anywhere that `discord.Client` can be used.
client = Bot(command_prefix=prefix)

ask.init(client) # ask.py wants access to the client too!
errors.init(client, play.players)


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

    answer = await ask.ask(ctx.message, f"Are you sure you wish to start a new farm called `{name}`?")
    if answer:
        play.players[ctx.message.author].farm = farm.Farm(name)
        await client.say("Farm created!")


@client.command(pass_context=True)
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
            for plot in current_player.farm.plots:
                if plot.crop is None:
                    plot.plant(crop)
                    current_player.items -= crop.seed
                    await client.say(f"Planted {crop.emoji} **{crop.name}** in **Plot #{current_player.farm.plots.index(plot)+1}**!\n\
Time until completion is **{plot.time(str, False)}**.")
                    return

            await client.say("Sorry, but all your plots are full!")
            return

    await client.say(f"I wasn't able to find `{plant}`, are you sure you spelt it right?")


@client.command(pass_context=True)
@check(errors.has_farm)
async def harvest(ctx, *args):
    current_player = play.get(ctx)

    loot = items.Container([], manager=market_manager)
    for plot in current_player.farm.plots:
        item = plot.harvest()
        if item is not None:
            loot += item

    if len(loot) == 0:
        await client.say(f"Sorry {ctx.message.author.mention}, but there was nothing too harvest!")
        return
    else:
        embed = discord.Embed(title="*Harvest Results:*", colour=0xffe48e)
        text = ""
        for item in loot:
            text += f"{item.emoji} **{item.name}** (x{item.amount})\n"
            current_player.items += item
        embed.add_field(name="**__Items__:**", value=text)

        await client.send_message(ctx.message.channel, f"{current_player.player.mention} ->", embed=embed)


@client.command(pass_context=True)
async def inv(ctx, *args):
    current_player = play.get(ctx)

    embed = discord.Embed(title=f"*{current_player.player.name}'s Inventory:*", colour=0x0080d6)
    embed.add_field(name="**__Money__:**", value=f":moneybag: ${current_player.money}")

    items_text = ""
    seeds_text = ""
    if len(current_player.items) > 0:
        for item in current_player.items:
            if item.name.endswith(("seeds", "pellets")):
                seeds_text += f"{item.emoji} **{item.name}** (x{item.amount})\n"
            else:
                items_text += f"{item.emoji} **{item.name}** (x{item.amount})\n"

        if items_text is not "":
            embed.add_field(name="**__Items__:**", value=items_text)
        if seeds_text is not "":
            embed.add_field(name="**__Seeds__:**", value=seeds_text)

    await client.send_message(ctx.message.channel, f"{current_player.player.mention} ->", embed=embed)


@client.command(pass_context=True)
@check(errors.has_farm)
async def status(ctx, *args):
    current_player = play.get(ctx)
    embed = discord.Embed(title=f"***{current_player.farm.name}*** *status:*", colour=0x00d100)

    for plot in current_player.farm.plots:
        text = ""
        if plot.crop is None:
            text = "Empty"
        else:
            text = f"**Crop:** {plot.crop.emoji} {plot.crop.name}\n"
            if plot.time(int) is 0:
                text += f"**Time Left:** Ready!"
            else:
                text += f"**Time Left:** {plot.time(str)}"

        index = current_player.farm.plots.index(plot)
        embed.add_field(name=f"**__Plot #{index+1}__:**", value=text)

    await client.send_message(ctx.message.channel, f"{current_player.player.mention} ->", embed=embed)


@client.command(pass_context=True)
async def buy(ctx, *args):
    if len(args) == 0:
        return

    current_player = play.get(ctx)
    amount = get_amount(args)
    plant = get_name(args)

    if market_manager.exists(plant):
        item = items.Item(plant, amount=amount, manager=market_manager)
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

    answer = await ask.ask(ctx.message,
        f"**Are you sure you want to buy {item.emoji} **{item.name} x{item.amount}** for **${item.buy_cost * item.amount}**?**",
        answers={"💸":True,"❌":False}
    )
    if answer:
        current_player.money -= item.buy_cost * item.amount
        current_player.items += item
        await client.say(f"Bought {item.emoji} **{item.name} (x{item.amount})**! Money Remaining: $**{current_player.money}**.")


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
        item = items.Item(item_name, amount=amount, manager=market_manager)
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
    answer = await ask.ask(ctx.message, f"Are you *sure* you wish to sell {item.emoji} **{item.name}** (x{item.amount}) for $**{item.sell_cost * item.amount}**?")
    if answer in (False, None):
        return

    # And only **then** we know we can sell it:
    current_player.items -= item
    current_player.money += item.sell_cost * item.amount
    await client.say(f"Sold! You now have $**{current_player.money}**.")


@client.command(pass_context=True)
async def dgive(ctx, *args):
    current_player = play.get(ctx)
    if len(args) == 0:
        return

    amount = 1; plant = ""
    try:
    # Then check if the item is actually a real item...
        int(args[0])
    except ValueError:
        plant = " ".join(args).strip()
    else:
        amount = int(args[0])
        plant = " ".join(args[1:]).strip()

    if not market_manager.exists(plant):
        await client.say(f"`{plant}` isn't a real item...")
        return

    item = items.Item(plant, amount=amount, manager=market_manager)
    current_player.items += item
    await client.say(f"Gave {item.emoji} **{item.name}** (x{item.amount}) to {current_player.player.name}")


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
    
'''
test = discord.Embed(title="yas")
test.add_field(name="I'm a field name", value="and I'm it's value")
test.add_field(name="And I'm another field name!", value="and I'm another value!")
test.add_field(name="This time, we're not inline!", value="Yep, we aren't indeed!", inline=False)
await client.send_message(message.channel, "I'm some content", embed = test)
'''
'''
for emoji in client.get_all_emojis():
    print(emoji.name)
    await client.add_reaction(message, emoji)
'''

