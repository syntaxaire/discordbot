import asyncio
from discord.ext.commands import Bot
from config import *  # dont post this to github you moron
from wordreplacer import *
from vacuum import *
from butt_library import *
import random
from buttbot import buttbot

used = {}  # stores last used time of RIP/F
shitpost = WordReplacer()
shitpost.config(shitpost_call_freq)


async def do_send_message(channel, message, cooldown=None):
    # this shit sends the messages to the peeps
    await asyncio.sleep(1)
    await client.send_typing(channel)
    if cooldown:
        await asyncio.sleep(cooldown)
    else:
        await asyncio.sleep(randint(2, 5))
    await client.send_message(channel, message)  # dont remove await from here or this shit will break


async def do_react(message, emoji, cooldown=None):
    if cooldown:
        await asyncio.sleep(cooldown)
    else:
        await asyncio.sleep(randint(2, 5))
    await client.add_reaction(message, emoji)

    # async def my_background_task():
    # print("LOGGER::Logger loaded.  Waiting until I connect to Discord")
    await client.wait_until_ready()
    # print("LOGGER::Connected to discord, start processing.")
    while not client.is_closed:
        # vacuum.playtime_log()
        await asyncio.sleep(10)  # task runs every 10 seconds
        # vacuum.playtime_scraper()
        # print("LOGGER:I logged player location at this time.")


client = Bot(description="a bot for farts", command_prefix="", pm_help=False)
progress_bot = buttbot(client)


@client.event
async def on_ready():
    print('Logged in as ' + client.user.name + ' (ID:' + client.user.id + ') | Connected to ' + str(
        len(client.servers)) + ' servers | Connected to ' + str(len(set(client.get_all_members()))) + ' users')
    print('--------')
    print('Use this link to invite {}:'.format(client.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    print('--------')
    print('You are running FartBot V1.6.05')
    print('Created by Poop Poop')
    print('--------')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    channels = {"💩💩": progress_bot.dispatch}
    if "&" in message.content:
        functiontocall = channels[message.server.name]
        back = await functiontocall(message)

    # shitposting follows

    if is_word_in_text("rip", message.content) == True:
        if (str(message.author) == 'Progress#6064' and message.content[:4] == 'RIP:') or (
                str(message.author) == '💩💩#4048' and message.content[:4] == 'RIP:'):
            pass
            # vacuum.add_death_message(message.content)s
        else:
            if 'rip' not in used or time.time() - used['rip'] > min_call_freq:
                used['rip'] = time.time()
                if randint(1, 20) == 5:
                    await do_send_message(message.channel, 'Ya, butts', randint(2, 5))
                else:
                    await do_send_message(message.channel, 'Ya, RIP', randint(2, 5))

    elif is_word_in_text("F", message.content) == True:
        if 'f' not in used or time.time() - used['f'] > min_call_freq:
            used['f'] = time.time()
            await do_send_message(message.channel, 'Ya, F', randint(2, 5))
        else:
            if randint(1, 100) == 44:
                await do_send_message(message.channel, 'suck my dick F under cooldown')

    elif is_word_in_text("thanks buttbot", message.content) is True or is_word_in_text("thanks\\, buttbot",
                                                                                       message.content) is True:
        if 'reply' not in used or time.time() - used['reply'] > min_call_freq:
            used['reply'] = time.time()
            replies = ['fuck off', 'youre welcome', 'your butt', 'i wish didnt have to look at you are posts',
                       'ur whale cum']
            await do_send_message(message.channel, replies[randint(1, len(replies))], randint(2, 5))
    elif is_word_in_text("thanks for trying buttbot", message.content) is True or is_word_in_text(
            "thanks for trying\\, buttbot", message.content) is True:
        if 'reply' not in used or time.time() - used['reply'] > min_call_freq:
            used['reply'] = time.time()
            replies = ['fuck off', 'youre welcome', 'your butt', 'i wish didnt have to look at you are posts',
                       'ur whale cum']
            await do_send_message(message.channel, replies[randint(1, len(replies))], randint(2, 5))

    elif is_word_in_text('butt', message.content) == True:
        if randint(1, 6) == 3:
            rshitpost = shitpost.rspeval(message.content)
            if rshitpost:
                await do_send_message(message.channel, rshitpost)
        elif randint(1, 3) == 3:
            await do_react(message, random.choice(["👌", "👍"]))

    else:
        # here's where im going to evaluate all other sentences for shitposting
        # rshitpost=shitpost.eval(message.content)
        # NLTK test
        if str(message.author) == "Progress#6064" and (
                is_word_in_text("left the game", message.content) or is_word_in_text("joined the game",
                                                                                     message.content)):
            # this is a join or part message and we are going to ignore it
            pass
        else:
            rshitpost = shitpost.eval_sentence_nltk(message.content, str(message.author))
            pass
        try:
            if rshitpost:
                await do_send_message(message.channel, rshitpost)
        except UnboundLocalError:
            pass


# client.loop.create_task(my_background_task())
client.run(secretkey)
