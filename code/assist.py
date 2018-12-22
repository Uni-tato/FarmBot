import discord

# Cause `help` is a key word, `assist` is the next best thing :)

commands = {
    "dgive": {
        "usage": "dgive [item amount = 1] <item name>",
        "description": "Will give the player the specified item in the optional amount. Used *only* for debugging.",
        "short_description": "Give items cheatly.",
    },
    "sell": {
        "usage": "sell [item amount = 1] <item name>",
        "description": "Sell the item for its current market price * by the optional quantity. Player must have the item.",
        "short_description": "Sell items.",
    },
    "buy": {
        "usage": "buy [item amount = 1] <item name>",
        "description": "Buy the item for its current market price * by the optional quantity. Player must have enough money.",
        "short_description": "Buy items.",
    },
    "plant": {
        "usage": "plant <item name / crop name>",
        "description": "Plant the given item in the first avaliable plot creating a new crop/tree. Player must have the item.",
        "short_description": "Plant crops/trees.",
    },
    "harvest": {
        "usage": "harvest",
        "description": "Harvest any harvestable plots automatically. Will also give the player all the items from the harvest.",
        "short_description": "Harvest plots.",
    },
    "inv": {
        "usage": "inv",
        "description": "Show the players current inventory.",
        "short_description": "Show inventory.",
    },
    "status": {
        "usage": "status",
        "description": "Show the status of the players farm.",
        "short_description": "Show status of plots.",
    },
    "create": {
        "usage": "create <farm name>",
        "description": "Create a new farm if one hasn't been already made. Farm must have a name.",
        "short_description": "Create new farm.",
    },
    "help": {
        "usage": "help [command]",
        "description": "Show how to use the avaliable commands.",
        "short_description": "Get information on a command.",
    },
}


prefix = None
client = None


def init(client_, prefix_):
    global client
    global prefix
    client = client_
    prefix = prefix_


async def help(ctx, args):
    # `help` can have 0 or more arguments, so this needs to check
    # the number of args to decide what to display.
    if len(args) == 0:
        await show_all_commands(ctx, args)
        return
    
    command = args[0]
    if command not in commands:
        await client.say(
            f"Sorry, but I don't know what the `{command}` command is! For help, do `{prefix}help`."
        )
        return

    command_info = commands[command]
    usage = command_info["usage"]
    description = command_info["description"]

    embed = discord.Embed(title=f"*Help for* `{prefix}{command}`:", colour=0x808080)
    embed.add_field(name=f"**Usage:**", value=f"`{prefix}{usage}`", inline=False)
    embed.add_field(name="**Description:**", value=f"{description}", inline=False)

    await client.send_message(
        ctx.message.channel, f"{ctx.message.author.mention} ->", embed=embed
    )


async def show_all_commands(ctx, args):
    embed = discord.Embed(title="*Help for* ***FarmBot:***", colour=0x808080)

    text = ""
    for command, command_info in commands.items():
        short_description = command_info["short_description"]
        text += f"`{command}` - {short_description}\n"
    embed.add_field(name="**Commands:**", value=text)

    embed.add_field(
        name="**Usage:**",
        value=f"Do `{prefix}help <command name>` to get more information on a specific command. "
	      f"Also note that `<foo>` means foo's *compulsory* and `[bar]` means bar's *optional*.",
    )

    await client.send_message(
        ctx.message.channel, f"{ctx.message.author.mention} ->", embed=embed
    )

