import random
import discord

client = discord.Client()

qanda = {}
qanda[1] = ('Vraag 1', 'B', 'Antwoord 1')
qanda[2] = ('Vraag 2', 'C', 'Antwoord 2')
qanda[3] = ('Vraag 3', 'A', 'Antwoord 3')
qanda[4] = ('Vraag 4', 'C', 'Antwoord 4')
total_disqualified = set()
een = 0
q = ''
qint = 0
stage = -1
diction = {}
participants = set()
start_string = 'Reageer met een emoji als je meedoet!'

# NOT STATIC:
cmd_channel = 0
com_channel = 0

# TODO
# jeroen is uit de game; jeroen stemt niet maar zit nog in participants. vervolgens wordt er geprint 'de volgende kandidaat uit het spel: jeroen


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    global start_string, com_channel, cmd_channel

    if (message.author == client.user) & (message.content == q):
        await message.add_reaction('🇦')
        await message.add_reaction('🇧')
        await message.add_reaction('🇨')
        await message.add_reaction('🇩')
        return

    if (message.author == client.user) & (message.content == start_string):
        await message.add_reaction('👍')

    if message.author.id == 328140454170198026:
        if message.content == '!q':
            await handle_q()
        elif message.content == '!s':
            await handle_s()
        elif message.content == '!a':
            await handle_a()
        elif message.content == '!kies':
            await kies()
        elif message.content == '!start':
            cmd_channel = message.channel
            com_channel = message.guild.get_channel(810949778900779069)
            await com_channel.send(start_string)
        elif message.content == '!in':
            await ingame()


async def handle_q():
    """
    Handles the first step, question
    Pre: stage == 0
    Post stage == 1
    """
    global stage, q, qint

    if een == 0:
        await cmd_channel.send('Er is geen speler gekozen!')
        return

    if stage != 0:
        await cmd_channel.send('Foute stage')
        return

    stage = 1
    qint += 1
    q = qanda[qint][0]
    await com_channel.send(qanda[qint][0])


async def handle_s():
    """
    Handles the second step, stopping answer accept
    Pre: stage == 1
    Post stage == 2
    """
    global stage

    if stage != 1:
        await cmd_channel.send('Foute stage')
        return

    await com_channel.send('Alle antwoorden zijn binnen en geen nieuwe antwoorden worden meer geaccepteerd!')
    stage = 2


async def handle_a():
    """
    Handles the third step, answer
    Pre: stage == 2
    Post stage == 3
    """
    global stage, total_disqualified, een

    if stage != 2:
        await cmd_channel.send('Foute stage')
        return

    stage = 0
    disqualified = get_disqualified()
    total_disqualified = total_disqualified.union(disqualified)

    # Iedereen heeft het goed
    if len(disqualified) == 0:
        await com_channel.send('Niemand is uit het spel!')
        await com_channel.send('Het goede antwoord was inderdaad ' + qanda[qint][1] + ': ' + qanda[qint][2])
        return

    if (een in participants.difference(total_disqualified)) and (len(participants.difference(total_disqualified)) == 1):
        await com_channel.send('De speler heeft alle kandidaten verslagen!')
        await com_channel.send('Het goede antwoord was ' + qanda[qint][1] + ': ' + qanda[qint][2])
        stage = -1

    ret = 'De volgende kandidaten zijn uit het spel:'

    for disq in disqualified:
        ret += ' <@' + str(disq) + '>,'

    await com_channel.send(ret[:-1] + '!')

    if een in disqualified:
        await com_channel.send('De speler, ' + '<@' + str(een) + '>, is uit het spel! Er moet een nieuwe speler '
                                                                     'worden gekozen.')
        een = 0
        total_disqualified = set()

    await com_channel.send('Het goede antwoord was ' + qanda[qint][1] + ': ' + qanda[qint][2])


async def ingame():
    if len(participants.difference(total_disqualified)) == 0:
        await com_channel.send('Niemand zit in het spel!')
        return

    ret = 'De volgende spelers zitten nog in het spel:'

    for speler in participants.difference(total_disqualified):
        ret += ' <@' + str(speler) + '>,'

    ret = ret[:-1]

    await com_channel.send(ret + '!')


async def kies():
    global een, stage

    if len(participants) == 0:
        await cmd_channel.send('Er zijn geen spelers!')
        return

    stage = 0
    een = random.choice(tuple(participants))

    await com_channel.send('De nieuwe kandidaat is <@' + str(een) + '>!')


def get_disqualified():
    global diction, qanda, qint, participants

    local_participants = set()
    disqualified = set()

    for dict in diction.items():
        if dict[1] != qanda[qint][1]:
            disqualified.add(dict[0])
        local_participants.add(dict[0])

    diction = {}

    return disqualified.union(participants.difference(local_participants))


@client.event
async def on_reaction_add(reaction, user):
    global diction, stage, participants, q

    if user == client.user:
        return

    if stage == -1:
        participants.add(user.id)
        return

    if (user.id not in participants.difference(total_disqualified)) | (stage != 1):
        return

    if (reaction.message.content == q) & (user not in total_disqualified):
        if reaction.emoji == '🇦':
            diction[user.id] = 'A'
        elif reaction.emoji == '🇧':
            diction[user.id] = 'B'
        elif reaction.emoji == '🇨':
            diction[user.id] = 'C'
        elif reaction.emoji == '🇩':
            diction[user.id] = 'D'


client.run('ODEwOTUyOTQ2MjU3NzU2MTgx.YCrIyQ.5_3LxcPy5lVGR4GakKudaZVclBM')