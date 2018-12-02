import datetime

import discord
import asyncio

import ask

client = discord.Client()

currentQuestions = []
unassignedQuestions = []


async def questionTimeout(question,seconds = 30):
    await asyncio.sleep(seconds)
    if question in currentQuestions:
        reply = question.originalMessage.author.name + " took too long to answer."
        embed = question.getTimedOutEmbed()
        await client.edit_message(question.message,reply,embed = embed)
        await client.clear_reactions(question.message)
        currentQuestions.remove(question)


@client.event
async def on_ready():
    print("FarmBot is online")


@client.event
async def on_message(message):
    message.num = 0
    #print(message.author,message.content)
    if message.author == client.user:
        if len(message.embeds) > 0:
            embed = message.embeds[0]
            for question in unassignedQuestions:
                print(embed['title'][2:-2])
                if  embed['title'][2:-2] == question.question and message.content == question.originalMessage.author.mention:
                    question.setMessage(message)
                    for reaction in question.reactions:
                        await client.add_reaction(question.message, reaction)
                    currentQuestions.append(question)
                    unassignedQuestions.remove(question)

    else:
        msg = str(message.content).lower()
    	
        if msg == "start new farm":
            question = "Are you sure you wish to start a new farm?"
            unassignedQuestions.append(ask.question(message,question))
            question = unassignedQuestions[-1]
            embed = unassignedQuestions[-1].getEmbed()
            channel = message.channel
            reply = message.author.mention
            await client.send_message(channel,reply,embed = embed)
            await questionTimeout(question)
            

        if msg == "hey":
            await client.send_message(message.channel, "hey")
            print(currentQuestions)


@client.event
async def on_reaction_add(reaction, user):
    '''
    for message in client.messages:
        print(message)
    '''
    if user != client.user:
        for question in currentQuestions:
            checkCount = 10
            if checkCount > len(client.messages):
                checkCount = len(client.messages)
            messagei = 0
            while messagei > -checkCount:
                messagei -= 1
                if question.message == client.messages[messagei]:
                    if question.originalMessage.author == user:
                        #await client.send_message(question.message.channel,"you reacted to the question.") 
                        embed = question.getAnsweredEmbed()
                        reply = question.originalMessage.author.name + " answered with: " + reaction.emoji
                        await client.edit_message(question.message,reply,embed = embed)
                        await client.clear_reactions(question.message)
                        currentQuestions.remove(question)
                    else:
                        pass
                        await client.send_message(question.message.channel, user.mention + " this question isn't for you.")
                    break

client.run("I'm not leaving this here on a public file.")


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

