# another example: (which I encourage you to try out)
#await ask.ask(message, "You really shouldn't react with a pig", answers={"🐷":"pig","🐮":"cow"}, timeout=10)
# which will return "pig" if the user reacts with the pig, "cow" if the user reacts with the cow,
# and None if the user didn't respond within 10 seconds
import time
import asyncio

import discord

colourAsked = 0x00ff00
colourAnswered = 0xf4d85a
colourTimedOut = 0xddbb8b

# this variable and function let ask.py have access to the client
client = None
def init(Client):
    global client
    client = Client

# stores all question objects currently waiting to be answered
questions = []
class Question:
    def __init__(self, origMessage, content, answers, timeout):
        self.origMessage = origMessage
        self.content = content
        self.answers = answers
        self.embed = self.getEmbed()
        # time when question was sent (current time)
        self.time = time.time()

        # ends up being True if the user answered or False if it timed out.
        self.answered = None
        # the emoji the user reacts with, should they answer.
        self.emoji = None
        # will end up being answers.get(emoji)
        self.answer = None


    def getEmbed(self):
        embed = discord.Embed(title = self.content, color = colourAsked)
        return embed

    def setMessage(self,message):
        self.message = message

    def getAnsweredEmbed(self):
        embed = discord.Embed(title = "~~"+self.content+"~~", color = colourAnswered)
        return embed

    def getTimedOutEmbed(self):
        embed = discord.Embed(title = "~~"+self.content+"~~", color = colourTimedOut)
        return embed

    def getAnsweredReply(self):
        reply = self.origMessage.author.name + " answered with: " + self.emoji
        return reply

    def getTimedOutReply(self):
        reply = self.origMessage.author.name + " took too long to answer."
        return reply

# origMessage: the message that triggered the question (used for channel and author)
# content: the question that'll be asked
# OPTIONAL:
# answers: a dictionary whos keys are the emojis (characters) and values their returned values (any data type)
#     - MAKE SURE THAT `NONE` IS NEVER A POSSIBLE ANSWER, since this is what the function returns if it times out
# timeout: the duration of the question
async def ask(origMessage, content, *, answers={'👍':True,'👎':False}, timeout=30):
    # these 2 lines make the whole function MUCH more readable :)
    channel = origMessage.channel
    author = origMessage.author
    # generate the quesition object fully and send the message object
    question = Question(origMessage, content, answers, timeout)
    question.message = await client.send_message(channel, author.mention, embed=question.embed)
    questions.append(question)

    # make the bot react with the necceccary reactions
    for emoji in answers:
        await client.add_reaction(question.message, emoji)

    while True:
        if question.answered:
            # question has been answered
            await client.edit_message(question.message, question.getAnsweredReply(), embed=question.getAnsweredEmbed())
            break
        if time.time() >= question.time + timeout:
            # question has been timedout (how do you spell this!?!?)
            question.answer = None
            question.answered = False
            await client.edit_message(question.message, question.getTimedOutReply(), embed=question.getTimedOutEmbed())
            break
        # this lets other async functions still run while this is waiting for a reaction
        await asyncio.sleep(1.0)

    # do the final touches, which include clearing reactions and deleating the question object
    await client.clear_reactions(question.message)
    questions.remove(question)
    # return the given answer
    return question.answer


