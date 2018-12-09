import datetime
import asyncio

import discord
from discord.ext.commands import Bot

import ask
import players as play
import farm

prefix = 'fm '
# `Bot` is a subclass of `discord.Client` so it can be used anywhere that `discord.Client` can be used.
client = Bot(command_prefix=prefix)
ask.init(client) # ask.py wants access to the client too!

@client.command(pass_context=True)
async def create(ctx, *args):
    name = " ".join(args).strip()
    # Disallows users to create a farm if they already have one.
    if play.players.get(ctx.message.author) is not None:
        await client.say("Sorry bud but you've already got a farm!")
        return
    elif name == "":
        await client.say("You can't create a farm with no name!")
        return
    # The player does not have a farm at this point.
    play.players[ctx.message.author] = play.Player(ctx.message.author)

    answer = await ask.ask(ctx.message, f"Are you sure you wish to start a new farm called `{name}`?")
    if answer:
        play.players[ctx.message.author].farm = farm.Farm(name)
        await client.say("Farm created!")


@client.command(pass_context=True)
async def plant(ctx, *seed_name):
    plant = " ".join(seed_name).strip()

    try:
        current_player = play.players[ctx.message.author]
    except KeyError:
        await client.say("You don't have a farm!")
        return

    if plant not in current_player.items:
        await client.say("You don't have that item!")
        return

    for plot in current_player.farm.plots:
        if plot.crop is None:
            # TODO: Implement this.
            pass


@client.event
async def on_reaction_add(reaction, user):
    # Don't act when the bot itself has added a reaction.
    if user == client.user:
        return

    message = reaction.message
    for question in ask.questions:
        # The message reacted to is a question (that hasn't been answered already cause it's in ask.questions)
        if question.message.id == message.id and user == question.origMessage.author:
            # And the right person has reacted too it!
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


# Will try and get a token from code/token.txt
# If this fails (file does not exist) then it asks for the token and creates the file
try:
    file = open("token.txt")
except OSError:
    token = input("Please input the Discord Token: ")
    file = open("token.txt", "w+")
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

