"""Handle questions asked to player."""
import time
import asyncio

import discord

import colours as colour

# this variable and function let ask.py have access to the client
client = None


def init(client_):
    """Provide module with `client`."""
    global client
    client = client_


# stores all question objects currently waiting to be answered
questions = []


class Question:
    """Represents a question asked to the user."""

    # TODO: Make use of `timeout` argument.
    def __init__(self, orig_message, content, answers, timeout):
        self.orig_message = orig_message
        self.content = content
        self.answers = answers
        self.embed = self.get_embed()
        # time when question was sent (current time)
        self.time = time.time()

        # ends up being True if the user answered or False if it timed out.
        self.answered = None
        # the emoji the user reacts with, should they answer.
        self.emoji = None
        # will end up being answers.get(emoji)
        self.answer = None

        self.message = None

    def get_embed(self):
        """Get the embed object to be used in this question."""
        embed = discord.Embed(title=self.content, color=colour.ACTIVE)
        return embed

    def set_message(self, message):
        """Set the message which represents the question to be asked."""
        self.message = message

    def get_answered_embed(self):
        """Get an embed object that represents an answered question."""
        if self.answer != False:
            colour_ = colour.CONFIRMED
        else:
            colour_ = colour.DENIED
        embed = discord.Embed(title="~~" + self.content + "~~", color=colour_)
        return embed

    def get_timed_out_embed(self):
        """Get an embed object that represents a timed out question."""
        embed = discord.Embed(title="~~" + self.content + "~~", color=colour.DENIED)
        return embed

    def get_answered_reply(self):
        """Get the bot's reply if the user answered in time."""
        reply = self.orig_message.author.name + " answered with: " + self.emoji
        return reply

    def get_timed_out_reply(self):
        """Get the bot's reply if the user did not answer in time."""
        reply = self.orig_message.author.name + " took too long to answer."
        return reply


async def ask(orig_message, content, *, answers={"👍": True, "👎": False}, timeout=30):
    """Ask the user a question.

    orig_message: the message that triggered the question (used for channel and author)
    content: the question that'll be asked

    OPTIONAL:
    answers: a dictionary whose keys are the emojis (characters)
             and values their returned values (any data type)
        - MAKE SURE THAT `NONE` IS NEVER A POSSIBLE ANSWER,
          since this is what the function returns if it times out
    timeout: the duration of the question
    """
    # these 2 lines make the whole function MUCH more readable :)
    channel = orig_message.channel
    author = orig_message.author
    # generate the quesition object fully and send the message object
    question = Question(orig_message, content, answers, timeout)
    question.message = await client.send_message(
        channel, author.mention, embed=question.embed
    )
    questions.append(question)

    # make the bot react with the necceccary reactions
    for emoji in answers:
        await client.add_reaction(question.message, emoji)

    while True:
        if question.answered:
            # question has been answered
            await client.edit_message(
                question.message,
                question.get_answered_reply(),
                embed=question.get_answered_embed(),
            )
            break
        if time.time() >= question.time + timeout:
            # question has been timedout (how do you spell this!?!?)
            question.answer = None
            question.answered = False
            await client.edit_message(
                question.message,
                question.get_timed_out_reply(),
                embed=question.get_timed_out_embed(),
            )
            break
        # this lets other async functions still run while this is waiting for a reaction
        await asyncio.sleep(1.0)

    # do the final touches, which include clearing reactions and deleating the question object
    await client.clear_reactions(question.message)
    questions.remove(question)
    # return the given answer
    return question.answer
