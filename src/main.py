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
start_string = "If you haven't joined already, react with a 👍 if you want to join!"

# NOT STATIC:
cmd_channel = 0
com_channel = 0

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

    #todo - Enter user id
    if message.author.id == 0:
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
            #todo - enter message channel
            com_channel = message.guild.get_channel(0)

            await com_channel.send(start_string)
        elif message.content == '!in':
            await ingame()
        elif message.content == '!bliep':
            cmd_channel = message.channel
            #todo enter message channel
            com_channel = message.guild.get_channel(0)

            await com_channel.send('Bloep!')
            await cmd_channel.send('CMD')


async def handle_q():
    """
    Handles the first step, question
    Pre: stage == 0
    Post stage == 1
    """
    global stage, q, qint, een

    if qint >= len(qanda):
        await com_channel.send('All out of questions! The winner is <@' + str(een) + '>!')
        print('Winner: ' + str(een))
        return

    if een == 0:
        await cmd_channel.send('No player has been chosen!')
        return

    if stage != 0:
        await cmd_channel.send('Wrong stage')
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
        await cmd_channel.send('Wrong stage')
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
        await cmd_channel.send('Wrong stage')
        return

    stage = 0
    disqualified = get_disqualified()
    total_disqualified = total_disqualified.union(disqualified)

    # Iedereen heeft het goed
    if len(disqualified) == 0:
        await com_channel.send('Everyone was correct!')
        await com_channel.send('**The correct answer was indeed ' + qanda[qint][1] + ': ' + qanda[qint][2] + "**")
        await com_channel.send('_ _')
        return

    # Speler heeft het alleen goed
    if (een in participants.difference(total_disqualified)) and (len(participants.difference(total_disqualified)) == 1):
        await com_channel.send('The candidate, <@' + str(een) + '>, has beaten all players!')
        print('Winnaar: ' + str(een))
        await com_channel.send('**The correct answer was ' + qanda[qint][1] + ': ' + qanda[qint][2] + "**")
        await com_channel.send('_ _')
        await reset()
        return

    # Iedereen heeft het fout
    if len(participants.difference(total_disqualified)) == 0:
        await com_channel.send('Everyone is out of the game!')
        await com_channel.send('_ _')
        await reset()
        return

    ret = 'The following players are out of the game:'

    for disq in disqualified:
        ret += ' <@' + str(disq) + '>,'

    await com_channel.send(ret[:-1] + '!')

    if (een in disqualified) and (len(participants.difference(total_disqualified)) == 1):
        await com_channel.send('The winner is <@' + str(participants.difference(total_disqualified).pop()) + '>!')
        print('Winnaar: ' + str(participants.difference(total_disqualified).pop()))
        await com_channel.send('**The correct answer was ' + qanda[qint][1] + ': ' + qanda[qint][2] + "**")
        await com_channel.send('_ _')
        await reset()
        return

    if een in disqualified:
        await com_channel.send('The candidate, ' + '<@' + str(een) + '>, is out of the game!')
        await kies()

    await com_channel.send('**The correct answer was ' + qanda[qint][1] + ': ' + qanda[qint][2] + "**")
    await com_channel.send('_ _')


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

#todo - Enter private bot key
client.run('private key')
