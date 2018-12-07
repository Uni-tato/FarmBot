import datetime
import asyncio

import discord

# oh oh, we might have a problem with these imports needing to communicate with each other but cant
# e.g. players.py needing the classes in farm.py
# eeehhhh, I'm sure it'll all be fine.
import ask
import players as play

client = discord.Client()
ask.init(client) # ask.py wants access to the client too!

@client.event
async def on_ready():
    print("FarmBot is online")


@client.event
async def on_message(message):
    #print(message.author,message.content)
    if message.author == client.user: #if the message was sent by the bot
        # we aren't doing anything here... for now. :thonk:
        return

    # Stooooofin's magic - basically, commands[] becomes the message segmented into words (lower case)
    # While parts[] becomes the message segmented into parts that lead to the end (raw)
    # E.G. The message "farm create My Farm!" would make:
    # commands = ["farm", "create", "my", "farm!"]
    # parts = ["farm create My Farm!", "create My Farm!", "My Farm!", "Farm!"]
    # (so parts[2] could be used to get the name of the farm, which will even support spaces)
    commands = []
    parts = []
    word = ''
    for char in message.content:
        if char == ' ':
            commands.append(word.lower())
            for part_i in range(len(parts)):
                parts[part_i] = parts[part_i] + " " + word
            parts.append(word)
            word = ''
        else:
            word += char
    commands.append(word.lower())
    for part_i in range(len(parts)):
        parts[part_i] = parts[part_i] + " " + word
    parts.append(word)

    msg = str(message.content).lower() #store the content of the message (lower case.)

    if message.content.startswith('farm') or message.content.startswith('Farm'):
        if len(commands) <= 1:
            # the message is just "farm" - don't do anything!
            return

        # is the thing after 'farm' a 'create'? I.E. did the user type in "farm create *"?
        if commands[1] == 'create':
            # a CRAP tonne of error prevention
            if message.author in play.players:
                if not play.players.get(message.author).farm == None:
                    # player already has a farm
                    await client.send_message(message.channel, "Sorry bud but you've already got a farm!")
                    return
            else:
                # if the player doesn't have their object, create one!
                play.players[message.author] = play.Player(message.author)

            try:
                name = parts[2]
            except IndexError:
                # no farm name was provided
                await client.send_message(message.channel, "No farm name was provided.")
            else:
                answer = await ask.ask(message, "Are you sure you wish to start a new farm called `" + name + "`?")
                if answer:
                    play.players[message.author].farm = "FARM OBJECT HERE BUT THAT MODULE'S NOT DONE YET >:("
                    await client.send_message(message.channel, "Farm created!")
            return

        # the player can't do anything if they don't have a farm / their player object!
        if not message.author in play.players:
            await client.send_message(message.channel, "Sorry " + message.author.name + ", but you don't have a farm! Create one with `farm create <name>`")
            return

@client.event
async def on_reaction_add(reaction, user): #runs whenever a reaction is added.
    message = reaction.message
    '''
    for message in client.messages:
        print(message)
    '''
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

