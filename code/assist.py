import discord
# Cause `help` is a key word, `assist` is the next best thing :)

commands = ["dgive", "sell", "buy", "plant", "harvest", "inv", "status", "create", "help"]
usages = [
	"dgive [item amount = 1] <item name>",
	"sell [item amount = 1] <item name>",
	"buy [item amount = 1] <item name>",
	"plant <item name / crop name>",
	"harvest",
	"inv",
	"status",
	"create <farm name>",
	"help [command]"]

descriptions = [
	"Will give the player the specified item in the optional amount. Used *only* for debugging.",
	"Sell the item for its current market price * by the optional quantity. Player must have the item.",
	"Buy the item for its current market price * by the optional quantity. Player must have enough money.",
	"Plant the given item in the first avaliable plot, creating a new crop/tree. Player must have the item.",
	"Harvest any harvestable plots automatically. Will also give the player all the items from the harvest.",
	"Show the players current inventory.",
	"Show the status of the players farm.",
	"Create a new farm if one hasn't been already made. Farm must have a name.",
	"Show how to use the avaliable commands."]

descriptions_short = [
	"Give items cheatly.",
	"Sell items.",
	"Buy items.",
	"Plant crops/trees.",
	"Harvest plots.",
	"Show inventory.",
	"Show status of plots.",
	"Create new farm.",
	"Get information on a command."]



prefix = None
client = None
def init(client_, prefix_):
    global client
    global prefix
    client = client_
    prefix = prefix_


async def help(ctx, args):

	if len(args) is 0:
		await generic(ctx, args)
		return

	else:
		command = args[0]
		if command not in commands:
			await client.say(f"Sorry, but I don't know what the `{command}` command is! For help, do `{prefix}help`.")
			return
	i = commands.index(command)

	embed = discord.Embed(title=f"*Help for* `{prefix}{command}`:", colour=0x808080)
	embed.add_field(name=f"**Usage:**", value=f"`{prefix}{usages[i]}`", inline=False)
	embed.add_field(name="**Description:**", value=f"{descriptions[i]}", inline=False)

	await client.send_message(ctx.message.channel, f"{ctx.message.author.mention} ->", embed=embed)

async def generic(ctx, args):
	embed = discord.Embed(title="*Help for* ***FarmBot:***", colour=0x808080)

	text = ""
	for command in commands:
		i = commands.index(command)
		text += f"    `{command}` - {descriptions_short[i]}\n"
	embed.add_field(name="**Commands:**", value=text)

	embed.add_field(name="**Usage:**", value=f'''Do `{prefix}help <command name>` to get more information on a specific command.\
		Also note that `<foo>` means foo's *compulsory* and `[bar]` means bar's *optional.*''')

	await client.send_message(ctx.message.channel, f"{ctx.message.author.mention} ->", embed=embed)
