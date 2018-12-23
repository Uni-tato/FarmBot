"""Deal with the bot's error-handling."""
import traceback
import sys

from discord.ext.commands import CommandError


client = None
players = None


def init(client_, players_):
    """Provide module with `client` and `players`."""
    global client
    global players
    client = client_
    players = players_


class UserHasFarmError(CommandError):
    """The user needs to NOT have a farm.

    This is used by `discord.py`'s `discord.ext.commands` subpackage
    to enable clean error handling for the `Context` when commands are
    invoked."""

    pass


def has_farm(ctx):
    """Check if the user has created a farm.

    This is required by some commands because, logically, they can't
    happen *without* farms. Examples include the `plant` and `harvest`
    commands."""
    if ctx.message.author in players:
        if players[ctx.message.author].farm is not None:
            return True
    raise UserHasNoFarmError


class UserHasNoFarmError(CommandError):
    """The user needs to have a farm.

    This is used by `discord.py`'s `discord.ext.commands` subpackage
    to enable clean error handling for the `Context` when commands are
    invoked."""

    pass


def has_no_farm(ctx):
    """Check if the user has NOT created a farm.

    This is required by some commands because, logically, they can't
    happen *with* farms. An example is the `create` command."""
    current_user = ctx.message.author
    if current_user not in players or players[current_user].farm is None:
        return True
    raise UserHasFarmError


async def on_command_error(error, ctx):
    """Implement the command error handling."""
    if isinstance(error, UserHasFarmError):
        await client.send_message(
            ctx.message.channel, "Sorry bud but you've already got a farm!"
        )
        return
    if isinstance(error, UserHasNoFarmError):
        await client.send_message(
            ctx.message.channel,
            f"Sorry {ctx.message.author.name}, but you don't have a farm! "
            f"Create one with `{client.command_prefix}create <name>`",
        )
        return

    # show the error - in the final program, this should never be executed!
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
