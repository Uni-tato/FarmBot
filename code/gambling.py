import sys
import random
import asyncio
import discord

client = None
players = None
prefix = None
def init(client_, players_, prefix_):
    global client
    global players
    global prefix
    client = client_
    players = players_
    prefix = prefix_


async def coinflip(current_player, amount):
    if amount < 1:
        await client.say("Please flip a amount greater than 1.")
        return

    if amount > 1000:
        await client.say("Sorry, you're not aloud to coinflip more than 1k! Why? idk.")
        return

    if current_player.money < amount:
        await client.say("You don't have enough money... \\:P")
        return

    if random.random() > 0.5:
        current_player.money -= amount
        await client.say(f"Oof - you lost $**{amount}**! You've now got $**{current_player.money}** remaining.")
    else:
        current_player.money += amount
        await client.say(f"Congratulations - you won $**{amount}**! You've now got $**{current_player.money}**!")
    return


class Card:
    def __init__(self, name, value, suit):
        self.name = name
        self.value = value
        self.suit = suit

        if self.name in ('Jack', 'Queen', 'King'):
            self.emoji = ":crown:"
        else:
            self.emoji = f":{self.suit.lower()}:"

    def __str__(self):
        return self.name + " of " + self.suit


def get_game(current_player, hide_dealer=True):
    # will return an embed object

    embed = discord.Embed(
        title = f"Blackjack for **{current_player.player.name}**, Bet: $**{current_player.bet}**"
    )
    total = current_player.hand_total(str)
    text = ""
    for card in current_player.hand:
        text += f"{card.emoji} **{card.name}** of {card.suit}\n"
    text += f"\nTotal: **{total}**"
    embed.add_field(name="**Players hand:**", value=text)

    if hide_dealer:
        card = current_player.dealer[0]
        embed.add_field(
            name = "**Dealers hand:**",
            value = f"{card.emoji} **{card.name}** of {card.suit}\n:question: **???**\n\nTotal: **{card.value}**"
        )
    else:
        # same code here as for the player above, just adapted for the dealer
        total = current_player.hand_total(str, "dealer")
        text = ""
        for card in current_player.dealer:
            text += f"{card.emoji} **{card.name}** of {card.suit}\n"
        text += f"\nTotal: **{total}**"
        embed.add_field(name="**Dealers hand:**", value=text)

    return embed


async def blackjack(channel, current_player, amount):

    if amount > current_player.money:
        await client.say("You don't have enough money!")
        return
    else:
        current_player.money -= amount
        current_player.bet = amount

    cards = {"Ace": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7, "Eight": 8, "Nine": 9, "Ten": 10, "Jack": 10, "Queen": 10, "King": 10}
    suits = ["Clubs", "Diamonds", "Hearts", "Spades"]

    for card in cards:
        for suit in suits:
            current_player.cards.append(Card(card, cards[card], suit))
    random.shuffle(current_player.cards)

    for i in range(2):
        card = random.choice(current_player.cards)
        current_player.hand.append(card)
        current_player.cards.remove(card)

        card = random.choice(current_player.cards)
        current_player.dealer.append(card)
        current_player.cards.remove(card)
    
    await client.send_message(
        channel,
        f"{current_player.player.mention} ->",
        embed = get_game(current_player)
    )


async def hit(channel, current_player):
    if current_player.cards == []:
        await client.say(f"Sorry {current_player.player.mention}, but you're not in a game! Start one with `{prefix}bjack <bet>`.")
        return

    new_card = random.choice(current_player.cards)
    current_player.hand.append(new_card)
    current_player.cards.remove(new_card)

    passed = False
    for total in current_player.hand_total():
        if total <= 21:
            passed = True

    if passed:
        await client.send_message(
            channel,
            f"{current_player.player.mention} ->",
            embed = get_game(current_player)
        )

    else:
        await client.send_message(
            channel,
            f"{current_player.player.mention} ->",
            embed = get_game(current_player, hide_dealer=False)
        )
        await client.say("You went bust! You don't win any money!")
        current_player.cards = []
        current_player.hand = []
        current_player.dealer = []


async def stand(channel, current_player):
    if current_player.cards is []:
        await client.say(f"Sorry {current_player.player.mention}, but you're not in a game! Start one with `{prefix}bjack <bet>`.")
        return
    # Dealers turn!
    outcome = ""
    while True:
        total = current_player.hand_total(hand="dealer")

        if all(i > 21 for i in total):
            # dealer went bust, all totals above 21
            outcome = 'bust'
            break

        if any(i >= 17 and i <= 21 for i in total):
            # dealer has finished his turn
            outcome = 'done'
            break
        else:
            card = random.choice(current_player.cards)
            current_player.dealer.append(card)
            current_player.cards.remove(card)

    if outcome == 'bust':
        await client.send_message(
            channel,
            f"{current_player.player.mention} ->",
            embed = get_game(current_player, hide_dealer=False)
        )
        await client.say(f"*Dealer went bust - you win double your bet! ($**{current_player.bet*2}**)")
        current_player.money += current_player.bet *2

    elif outcome == 'done':
        await client.send_message(
            channel,
            f"{current_player.player.mention} ->",
            embed = get_game(current_player, hide_dealer=False)
        )

        player = []
        for total in current_player.hand_total():
            if total <= 21:
                player.append(total)

        dealer = []
        for total in current_player.hand_total(hand="dealer"):
            if total <= 21:
                dealer.append(total)

        if max(player) > max(dealer):
            # player's won
            await client.say(f"Congratulations, you won! You win double your bet! ($**{current_player.bet*2}**)")
            current_player.money += current_player.bet * 2
        elif max(player) < max(dealer):
            # dealer won
            await client.say(f"The dealer won this time, you don't get any money.")
        else:
            # tie
            await client.say(f"Oh wow, it's a tie! You get your money back!")
            current_player.money += current_player.bet

    current_player.cards = []
    current_player.hand = []
    current_player.dealer = []
