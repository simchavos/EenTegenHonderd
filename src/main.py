import random
import discord

client = discord.Client()

# Parsing questions
qanda = {}

f = open("questions.txt", encoding='utf8')
lines = f.readlines()
i = 1

for line in lines:
    lineq, lineno, linea = line.split("/")
    qanda[i] = (lineq, lineno, linea)
    i += 1

# Necessary variables
total_disqualified = set()
een = 0
q = ''
qint = 0
stage = -1
diction = {}
participants = set()
start_string = "If you haven't joined already, react with an emoji to join!"

# NOT STATIC:
cmd_channel = 0
com_channel = 0


# TODO
# Bij TV programma als de één het fout heeft, wordt uit de nieuwe mensen nieuwe kandidaat
# gekozen.

# Kimberly doet niet mee maar geeft fout antwoord
# Verwijder kandidaat uit de game !in

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
        return

    # My discord user id
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
            # Should insert channel to send messages to:
            com_channel = message.guild.get_channel(820375100116566036)
            await com_channel.send(start_string)
        elif message.content == '!in':
            await ingame()


async def handle_q():
    """
    Handles the first step, question
    Pre: stage == 0
    Post stage == 1
    """
    global stage, q, qint, een

    if qint >= len(qanda):
        await com_channel.send('All out of questions! The winner is <@' + str(een) + '>!')
        print('Winnaar: ' + str(een))
        return

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

    await com_channel.send('All answers have been received and no new answers are accepted!')
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
        await com_channel.send('Everyone was correct!')
        await com_channel.send('**The correct answer was indeed ' + qanda[qint][1] + ': ' + qanda[qint][2] + "**")
        return

    # Speler heeft het alleen goed
    if (een in participants.difference(total_disqualified)) and (len(participants.difference(total_disqualified)) == 1):
        await com_channel.send('The candidate, <@' + str(een) + '>, has beaten all players!')
        print('Winnaar: ' + str(een))
        await com_channel.send('**The correct answer was ' + qanda[qint][1] + ': ' + qanda[qint][2] + "**")
        await reset()
        return

    # Iedereen heeft het fout
    if len(participants.difference(total_disqualified)) == 0:
        await com_channel.send('Everyone is out of the game!')
        await reset()
        return

    ret = 'The following players are out of the game:'

    for disq in disqualified:
        ret += ' <@' + str(disq) + '>,'

    await com_channel.send(ret[:-1] + '!')

    if (een in disqualified) and (len(participants.difference(total_disqualified)) == 1):
        await com_channel.send('The winner is <@' + str(participants.difference(disqualified).pop()) + '>!')
        print('Winnaar: ' + str(participants.difference(disqualified).pop()))
        await com_channel.send('**The correct answer was ' + qanda[qint][1] + ': ' + qanda[qint][2] + "**")
        await reset()
        return

    if een in disqualified:
        await com_channel.send('The candidate, ' + '<@' + str(een) + '>, is out of the game!')
        await kies()

    await com_channel.send('**The correct answer was ' + qanda[qint][1] + ': ' + qanda[qint][2] + "**")


async def reset():
    global een, total_disqualified, stage

    een = 0
    total_disqualified = set()
    stage = -1
    await com_channel.send(start_string)


async def ingame():
    if len(participants.difference(total_disqualified)) == 0:
        await com_channel.send('No one is in the game!')
        return

    ret = 'The following players are still in the game:'

    for speler in participants.difference(total_disqualified):
        ret += ' <@' + str(speler) + '>,'

    ret = ret[:-1]

    await com_channel.send(ret + '! The candidate is <@' + str(een) + '>!')


async def kies():
    global een, stage

    if len(participants.difference(total_disqualified)) == 0:
        await cmd_channel.send('Er zijn geen spelers!')
        return

    stage = 0
    een = random.choice(tuple(participants.difference(total_disqualified)))

    await com_channel.send('The new candidate is <@' + str(een) + '>!')


def get_disqualified():
    global diction, qanda, qint, participants, total_disqualified

    local_participants = set()
    disqualified = set()

    for dict in diction.items():
        if dict[1] != qanda[qint][1]:
            disqualified.add(dict[0])
        local_participants.add(dict[0])

    diction = {}

    return disqualified.union(participants.difference(total_disqualified).difference(local_participants))


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
