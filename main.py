import os
from collections import OrderedDict
import discord

client = discord.Client()

class Poll:
    def __init__(self):
        self.message = None
        self.choices = OrderedDict()


polls = dict()
emojis = [
    "\N{REGIONAL INDICATOR SYMBOL LETTER A}", "\N{REGIONAL INDICATOR SYMBOL LETTER B}",
    "\N{REGIONAL INDICATOR SYMBOL LETTER C}", "\N{REGIONAL INDICATOR SYMBOL LETTER D}",
    "\N{REGIONAL INDICATOR SYMBOL LETTER E}", "\N{REGIONAL INDICATOR SYMBOL LETTER F}",
    "\N{REGIONAL INDICATOR SYMBOL LETTER G}", "\N{REGIONAL INDICATOR SYMBOL LETTER H}",
    "\N{REGIONAL INDICATOR SYMBOL LETTER I}", "\N{REGIONAL INDICATOR SYMBOL LETTER J}",
    "\N{REGIONAL INDICATOR SYMBOL LETTER K}", "\N{REGIONAL INDICATOR SYMBOL LETTER L}",
    "\N{REGIONAL INDICATOR SYMBOL LETTER M}", "\N{REGIONAL INDICATOR SYMBOL LETTER N}",
    "\N{REGIONAL INDICATOR SYMBOL LETTER O}", "\N{REGIONAL INDICATOR SYMBOL LETTER P}",
    "\N{REGIONAL INDICATOR SYMBOL LETTER Q}", "\N{REGIONAL INDICATOR SYMBOL LETTER R}",
    "\N{REGIONAL INDICATOR SYMBOL LETTER S}", "\N{REGIONAL INDICATOR SYMBOL LETTER T}",
    "\N{REGIONAL INDICATOR SYMBOL LETTER U}", "\N{REGIONAL INDICATOR SYMBOL LETTER V}",
    "\N{REGIONAL INDICATOR SYMBOL LETTER W}", "\N{REGIONAL INDICATOR SYMBOL LETTER X}",
    "\N{REGIONAL INDICATOR SYMBOL LETTER Y}", "\N{REGIONAL INDICATOR SYMBOL LETTER Z}"
]

def make_embed(choices, user):
    def fmt(i, game, voters):
        names = sorted(user.name for user in voters)
        if len(voters) == 0:
            return "{} no one wants to play {}".format(emojis[i], game)
        if len(voters) == 1:
            return "{} {} wants to play {}".format(emojis[i], names[0], game)
        if len(voters) == 2:
            return "{} {} and {} want to play {}".format(emojis[i], *names, game)
        if len(voters) == 3:
            return "{} {}, {} and {} want to play {}".format(emojis[i], *names, game)
        return "{} {} people want to play {}".format(emojis[i], len(voters), game)

    text = "\n".join(fmt(i, game, voters) for i, (game, voters) in enumerate(choices.items()))

    em = discord.Embed(title='List of choices', description=text, colour=0xFF0000)
    em.set_author(name='Poll Bot', icon_url=user.avatar_url)
    return em


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('+play'):
        games = message.content.split()[1:]

        if message.channel not in polls:
            polls[message.channel] = Poll()

        poll = polls[message.channel]

        for game in games:
            poll.choices[game] = set()

        em = make_embed(poll.choices, message.author)

        if poll.message is None:
            poll.message = await client.send_message(message.channel, embed=em)
        else:
            poll.message = await client.edit_message(poll.message, embed=em)

        for i in range(len(poll.choices)):
            if emojis[i] not in [reaction.emoji for reaction in poll.message.reactions]:
                await client.add_reaction(poll.message, emojis[i])


    if message.content.startswith('+reset'):
        if message.channel in polls:
            del polls[message.channel]


def get_voters(reaction):
    if reaction.custom_emoji:
        return None

    if reaction.message.channel in polls:
        poll = polls[reaction.message.channel]
        if reaction.message.id == poll.message.id:
            if reaction.emoji in emojis:
                i = emojis.index(reaction.emoji)
                return poll.choices[list(poll.choices.keys())[i]]

    return None


@client.event
async def on_reaction_add(reaction, user):
    # we do not want the bot to reply to itself
    if user == client.user:
        return

    voters = get_voters(reaction)
    if voters is not None and user not in voters:
        voters.add(user)

        poll = polls[reaction.message.channel]
        em = make_embed(poll.choices, user)
        poll.message = await client.edit_message(poll.message, embed=em)


@client.event
async def on_reaction_remove(reaction, user):
    # we do not want the bot to reply to itself
    if user == client.user:
        return

    voters = get_voters(reaction)
    if voters is not None and user in voters:
        voters.remove(user)

        poll = polls[reaction.message.channel]
        em = make_embed(poll.choices, user)
        poll.message = await client.edit_message(poll.message, embed=em)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(os.environ['TOKEN'])
