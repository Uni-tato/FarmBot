import discord
import traceback, sys
from discord.ext.commands import CommandError


client = None
players = None
def init(Client, Players):
    global client
    global players
    client = Client
    players = Players


class UserHasFarmError(CommandError):
    pass
def has_farm(ctx):
    if ctx.message.author in players:
        return True
    raise UserHasNoFarmError


class UserHasNoFarmError(CommandError):
    pass
def has_no_farm(ctx):
    if ctx.message.author not in players:
        return True
    raise UserHasFarmError


async def on_command_error(error, ctx):
    if isinstance(error, UserHasFarmError):
        await client.send_message(ctx.message.channel, "Sorry bud but you've already got a farm!")
        return
    elif isinstance(error, UserHasNoFarmError):
        await client.send_message(ctx.message.channel, f"Sorry {ctx.message.author.name}, but you don't have a farm! Create one with `{client.command_prefix}create <name>`")
        return

    # show the error - in the final program, this should never be executed!
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

