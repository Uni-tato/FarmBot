import datetime

import discord
import asyncio

import ask

client = discord.Client()

currentQuestions = [] #questions that still need to be answered
unassignedQuestions = [] #questions that haven't been paired with a message yet (stoof boi I command you to decancerify this)


async def questionTimeout(question,seconds = 30): #removes a question if it hasn't been answered after "seconds" seconds.
    await asyncio.sleep(seconds) #waits for "seconds" seconds (pls note using the asyncio.sleep, not time.sleep, dont make that mistake)
    if question in currentQuestions: #checkes if the question is in current questions (a question will be removed when it is answered)
        reply = question.originalMessage.author.name + " took too long to answer." #gets the new text that the message needs to be updated to.
        embed = question.getTimedOutEmbed() #gets the embed that will be used for a timedout message.
        await client.edit_message(question.message,reply,embed = embed)
        await client.clear_reactions(question.message)
        currentQuestions.remove(question)


@client.event
async def on_ready():
    print("FarmBot is online")


@client.event
async def on_message(message):
    #print(message.author,message.content)
    if message.author == client.user: #if the message was sent by the bot
        if len(message.embeds) > 0: #check for any embeds
            embed = message.embeds[0] #gets the first embed (how do you even send a message with multiple embeds)
            for question in unassignedQuestions: # for each question that has not been paired with a message.
                print(embed['title'][2:-2]) #we can ignore this dude right here.
                if  embed['title'][2:-2] == question.question and message.content == question.originalMessage.author.mention: #detects if the message should be paired with the question
                                                                                                                              #by comparing the embed title (without bold formatting) with the question object
                                                                                                                              #and by comparing the message itself (which should just be a mention) to a mention of the user
                    question.setMessage(message) #assigns the question object it's message.
                    for reaction in question.reactions: #for every suitable reaction
                        await client.add_reaction(question.message, reaction) #add the reaction to the message
                    currentQuestions.append(question) #add the question to current qusetions
                    unassignedQuestions.remove(question) #and remove it from unassinged question

    else: # if the message is not sent by the bot (could still be send by another bot, this is fine, I want to make a bot to play this)
        msg = str(message.content).lower() #store the content of the message (lower case.)
    	
        if msg == "start new farm": #selfexplanitory
            question = "Are you sure you wish to start a new farm?"
            unassignedQuestions.append(ask.question(message,question)) # creates a question object, stick it in unassinged questions
            question = unassignedQuestions[-1] #grabs the question
            embed = unassignedQuestions[-1].getEmbed() #creates the embed for the question
            channel = message.channel
            reply = message.author.mention
            await client.send_message(channel,reply,embed = embed) #sends the message
            await questionTimeout(question) #checks if the question is answered after 30 seconds and removes it otherwise.
            

        if msg == "hey": # this is just what I use to get some dubug info
            await client.send_message(message.channel, "hey")
            print(currentQuestions)


@client.event
async def on_reaction_add(reaction, user): #runs whenever a reaction is added.
    '''
    for message in client.messages:
        print(message)
    '''
    if user != client.user: #we want to ignore the bots reactions
        for question in currentQuestions: #for all the question that need to be answered
            checkCount = 10 #how many messages to check
            if checkCount > len(client.messages): #makes sure we're not trying to check messages we dont have. 
                checkCount = len(client.messages)
            messagei = 0
            while messagei > -checkCount: #checkes the last "checkCount" (10) messages sent.
                messagei -= 1
                if question.message == client.messages[messagei]: #check if the message is assinged to the question (why did I do it this way)
                    if question.originalMessage.author == user: #checks if the person answering the message is the person who was asked the question.
                        #await client.send_message(question.message.channel,"you reacted to the question.") 
                        embed = question.getAnsweredEmbed() #gets the new embed
                        reply = question.originalMessage.author.name + " answered with: " + reaction.emoji
                        await client.edit_message(question.message,reply,embed = embed)
                        await client.clear_reactions(question.message)
                        currentQuestions.remove(question) #removes the question, we dont need him anymore.
                    else:
                        pass #if the person answering the question was the wrong person then DONT send a message telling them that (lets not spam the channel).
                        await client.send_message(question.message.channel, user.mention + " this question isn't for you.")
                    break

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
    print(token) #why are we printing the token here? It serves no purpose.
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

