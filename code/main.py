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
    # Disallows users to create a farm if they already have one.
    if play.players.get(ctx.author) is not None:
        await ctx.send("Sorry bud but you've already got a farm!")
        return
    # The player does not have a farm at this point.
    play.players[ctx.author] = play.Player(ctx.author)

    name = " ".join(args)
    answer = ask.ask(ctx.message, f"Are you sure you wish to start a new farm called `{name}`?")
    if answer:
        play.players[ctx.author].farm = farm.Farm(name)
        await ctx.send("Farm created!")


@client.command(pass_context=True)
async def plant(ctx, *seed_name):
    plant = " ".join(seed_name)
    current_player = play.players[ctx.author]

    if plant not in current_player.items:
        await ctx.send("You don't have that item!")
        return

    for plot in current_player.farm.plots:
        if plot.crop is None:
            # TODO: Implement this.
            pass



commands = {"create":create}

@client.event
async def on_message(message):
    #print(message.author,message.content)
    if message.author == client.user:
        return

    # Stooooofin's magic - basically, commands[] becomes the message segmented into words (lower case)
    # While parts[] becomes the message segmented into parts that lead to the end (raw)
    # E.G. The message "farm create My Farm!" would make:
    # commands = ["farm", "create", "my", "farm!"]
    # parts = ["farm create My Farm!", "create My Farm!", "My Farm!", "Farm!"]
    segments = []
    parts = []
    word = ''
    for char in message.content:
        if char == ' ':
            segments.append(word.lower())
            for i in range(len(parts)):
                parts[i] = parts[i] + " " + word
            parts.append(word)
            word = ''
        else:
            word += char
    segments.append(word.lower())
    for i in range(len(parts)):
        parts[i] = parts[i] + " " + word
    parts.append(word)

    if segments[0] == prefix:
        if len(segments) <= 1:
            # the message is just the prefix - don't do anything!
            return

        if segments[1] in commands:
            await commands[segments[1]](message, segments, parts)
            return

        ###### Where to put this code will become a problem ######
        # the player can't do anything if they don't have a farm / their player object!
        #if not message.author in play.players:
        #    await client.send_message(message.channel, "Sorry " + message.author.name + ", but you don't have a farm! Create one with `farm create <name>`")
        #    return

@client.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    if user != client.user:
        for question in ask.questions:
            if question.message.id == message.id:
                # The message reacted to is a question (that hasn't been answered already cause it's in ask.questions)
                if user == question.origMessage.author:
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

