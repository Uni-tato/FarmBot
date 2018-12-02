import datetime

import discord

colourAsked = 0x00ff00
colourAnswered = 0xf4d85a
colourTimedOut = 0xddbb8b

class question:
    def __init__(self,message,question,reactions = ['👍', '👎']):
        self.message = None

        self.originalMessage = message
        self.question = question
        self.reactions = reactions

    def getEmbed(self):
        embed = discord.Embed(title = "**"+self.question+"**", color = colourAsked)
        return embed

    def setMessage(self,message):
        self.message = message

    def getAnsweredEmbed(self):
        embed = discord.Embed(title = "~~"+self.question+"~~", color = colourAnswered)
        return embed

    def getTimedOutEmbed(self):
        embed = discord.Embed(title = "~~"+self.question+"~~", color = colourTimedOut)
        return embed