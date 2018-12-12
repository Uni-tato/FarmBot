import datetime
import asyncio

import discord
from discord.ext.commands import Bot, check, CommandError

import ask
import players as play
import farm
import items
import errors
import constants

#### QUICK TO DO LIST: ####
# - Make a method on Crop that returns the time untill completioin in a nice string e.g. "9.1hours" and not "456mins"
# - Make the `fm plant` command better - print to the user time until compleation? Let user select plots manually?

prefix = 'fm '
# `Bot` is a subclass of `discord.Client` so it can be used anywhere that `discord.Client` can be used.
client = Bot(command_prefix=prefix)
ask.init(client) # ask.py wants access to the client too!
errors.init(client, play.players)

@client.event
async def on_command_error(ctx, error):
    await errors.on_command_error(ctx, error)

@client.command(pass_context=True)
@check(errors.has_no_farm)
async def create(ctx, *args):
    name = " ".join(args).strip()
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
    plant = " ".join(seed_name).strip()
    current_player = play.players[ctx.message.author]

    for crop in constants.CROPS:
        if plant == crop.seed or plant == crop.name:
            # we've fond the crop that the player was looking for
            if not current_player.has(crop.seed):
                await client.say(f"Uhhhh, you don't have any `{crop.seed}`...")
                return

            # now we need to plant it...
            for plot in current_player.farm.plots:
                if plot.crop is None:
                    plot.plant(crop)
                    current_player.items -= crop.seed
                    await client.say(f"Successfully planted {crop.emoji} **{crop.name}**!")
                    return

            await client.say("Sorry, but all your plots are full!")
            return

    await client.say(f"I wasn't able to find `{plant}`, are you sure you spelt it right?")


@client.command(pass_context=True)
@check(errors.has_farm)
async def harvest(ctx, *args):
    current_player = play.players[ctx.message.author]

    loot = items.Container([])
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
    if ctx.message.author not in play.players:
        play.players[ctx.message.author] = play.Player(ctx.message.author)
    current_player = play.players[ctx.message.author]

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
    current_player = play.players[ctx.message.author]
    embed = discord.Embed(title=f"***{current_player.farm.name}*** *status:*", colour=0x00d100)

    for plot in current_player.farm.plots:
        text = ""
        if plot.crop is None:
            text = "Empty"
        else:
            text = f"**Crop:** {plot.crop.emoji} {plot.crop.name}\n"
            if plot.time_left() is 0:
                text += f"**Time Left:** Ready!"
            else:
                text += f"**Time Left:** {plot.time_left()}min\n"

        index = current_player.farm.plots.index(plot)
        embed.add_field(name=f"**__Plot #{index+1}__:**", value=text)

    await client.send_message(ctx.message.channel, f"{current_player.player.mention} ->", embed=embed)


@client.command(pass_context=True)
async def dgive(ctx, *args):
    if len(args) == 0:
        return

    amount = 1; plant = ""
    try:
        int(args[0])
    except ValueError:
        plant = " ".join(args).strip()
    else:
        amount = int(args[0])
        plant = " ".join(args[1:]).strip()

    if not items.is_item(plant):
        await client.say(f"`{plant}` isn't a real item...")
        return

    if ctx.message.author not in play.players:
        play.players[ctx.message.author] = play.Player(ctx.message.author)
    current_player = play.players[ctx.message.author]

    item = items.Item(plant, amount=amount)
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
        if question.message.id == message.id and user == question.origMessage.author:
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

    for item in constants.ITEMS:
        item.init_emoji(client)
    for crop in constants.CROPS:
        crop.init_emoji(client)


# Will try and get a token from code/token.txt
# If this fails (file does not exist) then it asks for the token and creates the file
try:
    file = open("txt/token.txt")
except OSError:
    token = input("Please input the Discord Token: ")
    file = open("txt/token.txt", "w+")
    file.write(token)
    file.close()
    client.run(token)
else:
    token = file.read()
    file.close()
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

