import datetime
import asyncio

import discord

# oh oh, we might have a problem with these imports needing to communicate with each other but cant
# e.g. players.py needing the classes in farm.py
# eeehhhh, I'm sure it'll all be fine.
import ask
import players

client = discord.Client()

# This lets ask.py have access to the client variable
# needed for sending messages and stuff in ask.py
ask.init(client)

@client.event
async def on_ready():
    print("FarmBot is online")


@client.event
async def on_message(message):
    #print(message.author,message.content)
    if message.author == client.user: #if the message was sent by the bot
        # we aren't doing anything here... for now. :thonk:
        return

    # if the message is not sent by the bot (could still be send by another bot, this is fine, I want to make a bot to play this)
    msg = str(message.content).lower() #store the content of the message (lower case.)

    if msg == "start new farm":
        # This is a simple example showing how to use the new ask.ask() command.
        answer = await ask.ask(message, "Are you sure you wish to start a new farm?")
        if answer == True:
            print("answered with thumbs up")
        elif answer == False:
            print("answered with thumbs down")
        elif answer == None:
            print("timed out and did not answer")

        # another example: (which I encourage you to try out)
        #await ask.ask(message, "You really shouldn't react with a pig", answers={"🐷":"pig","🐮":"cow"}, timeout=10)
        # which will return "pig" if the user reacts with the pig, "cow" if the user reacts with the cow,
        # and None if the user didn't respond within 10 seconds

    if msg == "hey": # this is just what I use to get some dubug info
        await client.send_message(message.channel, "hey")
        print(questions)


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

