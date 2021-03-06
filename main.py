import os
from collections import OrderedDict
import discord

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

print("start pollbot with TOKEN={}".format(os.environ['TOKEN']))

client = discord.Client()

class Poll:
    def __init__(self, author, title):
        self.author = author
        self.title = title
        self.message = None
        self.choices = OrderedDict()

    def embed(self):
        def fmt(i, prop, voters):
            names = sorted(user.mention for user in voters)
            if len(voters) == 0:
                return "{} [{}]".format(emojis[i], prop)
            if len(voters) == 1:
                return "{} [{}] {}".format(emojis[i], prop, names[0])
            if len(voters) == 2:
                return "{} [{}] {} and {}".format(emojis[i], prop, *names)
            if len(voters) == 3:
                return "{} [{}] {}, {} and {}".format(emojis[i], prop, *names)
            return "{} [{}] {}, {} and {} other people".format(emojis[i], prop, *names[:2], len(voters) - 2)

        text = "\n".join(fmt(i, prop, voters) for i, (prop, voters) in enumerate(self.choices.items()))

        em = discord.Embed(title=self.title, description=text, colour=0xFF0000)
        em.set_author(name=self.author.name, icon_url=self.author.avatar_url)
        return em

    def end_embed(self):
        def fmt(prop, voters):
            names = sorted(user.mention for user in voters)
            if len(voters) == 0:
                return "[{}]".format(prop)
            if len(voters) == 1:
                return "[{}] {}".format(prop, names[0])
            if len(voters) == 2:
                return "[{}] {} and {}".format(prop, *names)
            if len(voters) == 3:
                return "[{}] {}, {} and {}".format(prop, *names)
            return "[{}] {}, {} and {} other people".format(prop, *names[:2], len(voters) - 2)

        text = "\n".join(fmt(prop, voters) for prop, voters in sorted(self.choices.items(), key=lambda x: len(x[1]), reverse=True))

        em = discord.Embed(title=self.title, description=text, colour=0xFF0000)
        em.set_author(name=self.author.name, icon_url=self.author.avatar_url)
        return em


polls = dict()


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('+add '):
        proposition = message.content[5:]
        if len(proposition) == 0:
            return

        if message.channel not in polls:
            polls[message.channel] = Poll(client.user, "set poll title with +title")

        poll = polls[message.channel]

        if proposition not in poll.choices:
            poll.choices[proposition] = set()

            if poll.message is None:
                poll.message = await client.send_message(message.channel, embed=poll.embed())
            else:
                poll.message = await client.edit_message(poll.message, embed=poll.embed())

            await client.add_reaction(poll.message, emojis[len(poll.choices) - 1])


    if message.content.startswith('+title '):
        title = message.content[7:]
        if len(title) == 0:
            return

        if message.channel not in polls:
            polls[message.channel] = Poll(message.author, title)

        poll = polls[message.channel]

        poll.author = message.author
        poll.title = title

        if poll.message is None:
            poll.message = await client.send_message(message.channel, embed=poll.embed())
        else:
            poll.message = await client.edit_message(poll.message, embed=poll.embed())


    if message.content.startswith('+end'):
        if message.channel in polls:
            poll = polls[message.channel]
            poll.message = await client.send_message(message.channel, embed=poll.end_embed())
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
        poll.message = await client.edit_message(poll.message, embed=poll.embed())


@client.event
async def on_reaction_remove(reaction, user):
    # we do not want the bot to reply to itself
    if user == client.user:
        return

    voters = get_voters(reaction)
    if voters is not None and user in voters:
        voters.remove(user)

        poll = polls[reaction.message.channel]
        poll.message = await client.edit_message(poll.message, embed=poll.embed())


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(os.environ['TOKEN'])
