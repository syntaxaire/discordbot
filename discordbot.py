import asyncio
from discord.ext.commands import Bot
from config import *  # dont post this to github you moron
from wordreplacer import *
from vacuum import *
from mojang import *
from butt_library import *

used = {}  # stores last used time of RIP/F
shitpost = WordReplacer()
shitpost.config(shitpost_call_freq)
vacuum = Vacuum()
vacuum.config(vacuum_update_json_url, master_config)


async def do_send_message(channel, message, cooldown=None):
    # this shit sends the messages to the peeps
    await client.send_typing(channel)
    if cooldown:
        await asyncio.sleep(cooldown)
    else:
        await asyncio.sleep(randint(2, 5))
    await client.send_message(channel, message)  # dont remove await from here or this shit will break


async def my_background_task():
    # print("LOGGER::Logger loaded.  Waiting until I connect to Discord")
    await client.wait_until_ready()
    # print("LOGGER::Connected to discord, start processing.")
    while not client.is_closed:
        vacuum.playtime_log()
        # print("LOGGER:I logged player location at this time.")
        await asyncio.sleep(10)  # task runs every 10 seconds


client = Bot(description="a bot for farts", command_prefix="", pm_help=False)


@client.event
async def on_ready():
    print('Logged in as ' + client.user.name + ' (ID:' + client.user.id + ') | Connected to ' + str(
        len(client.servers)) + ' servers | Connected to ' + str(len(set(client.get_all_members()))) + ' users')
    print('--------')
    print('Use this link to invite {}:'.format(client.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    print('--------')
    print('You are running FartBot V1.3.05')
    print('Created by Poop Poop')
    print('--------')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    try:
        command = message.content.split("&", 1)[1]
    except IndexError:
        # finally:
        command = ''
    if command:
        c2 = command.split(' ')
        if c2[0] == "lastseen":
            try:
                if c2[1]:
                    returnz = vacuum.lastseen(c2[1])
                    if returnz:
                        await do_send_message(message.channel, returnz)
            except IndexError:
                print("main::lastseen::exception:no name provided")
                await do_send_message(message.channel, "who am i looking for?")
        elif c2[0] == "mojang":
            msg = mojang_status_requested()
            for t in msg:
                await do_send_message(message.channel, t)

        elif c2[0] == "playtime":
            try:
                if c2[1]:
                    returnz = vacuum.playtime_insult(c2[1])
                    if returnz:
                        await do_send_message(message.channel, returnz)
            except IndexError:
                # TODO: evaluate and complete vacuum.playtime_global()
                await do_send_message(message.channel, "who am i looking for?")

        elif c2[0] == "buttword":
            # buttword is restricted so lets check the author
            if str(message.author) in channel_admins:
                # passes admin test. process here
                try:
                    if c2[1] == 'list':
                        returnz = shitpost.buttword('list', '')
                        if returnz:
                            await do_send_message(message.channel, returnz)

                    elif c2[1] and c2[2]:
                        returnz = shitpost.buttword(c2[1], c2[2])
                        if returnz:
                            await do_send_message(message.channel, returnz)

                    else:
                        await do_send_message(message.channel, 'add remove list')
                except IndexError:
                    print("main::buttword::caught index exception")
                    await do_send_message(message.channel, 'add remove list')

            else:
                print('main::command::buttword::author NOT in admins: ' + str(message.author))
                # pass #here is the end of the admin check test.

        elif c2[0] == "howchies":
            try:
                if c2[1]:
                    # death type profile
                    # construct death message and ship it
                    dmsg = ''
                    for i in c2[1:]:
                        dmsg = dmsg + " " + i
                    dmsg = dmsg.strip()
                    await do_send_message(message.channel,
                                          "People who died to " + dmsg + ": " + vacuum.howchies_profile(dmsg))

            except IndexError:
                if ('howouchies' not in used or time.time() - used['howouchies'] > ouchies_call_freq):
                    used['howouchies'] = time.time()
                    await do_send_message(message.channel, 'Heres whats killing you: ' + vacuum.top_10_death_reasons())
        elif c2[0] == 'nltk':
            if str(message.author) in channel_admins:
                await do_send_message(message.channel, shitpost.wordtagger(message.content))

        elif c2[0] == "ouchies":
            try:
                if c2[1]:
                    # personal profile
                    await do_send_message(message.channel, "Deaths for " + c2[1] + ": " + vacuum.ouchies_profile(c2[1]))

            except IndexError:
                if ('ouchies' not in used or time.time() - used['ouchies'] > ouchies_call_freq):
                    used['ouchies'] = time.time()
                    await do_send_message(message.channel, 'Top 10 ouchies: ' + vacuum.top_10_deaths())

        elif c2[0] == "commands" or c2[0] == "help":
            await do_send_message(message.channel, 'ouchies, howchies, buttword (but only if ur a cool kid)')

    # shitposting follows

    elif is_word_in_text("rip", message.content) == True:
        if (str(message.author) == 'Progress#6064' and message.content[:4] == 'RIP:') or (
                str(message.author) == '💩💩#4048' and message.content[:4] == 'RIP:'):
            vacuum.add_death_message(message.content)
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
        rshitpost = shitpost.rspeval(message.content)
        if rshitpost:
            await do_send_message(message.channel, rshitpost)

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


client.loop.create_task(my_background_task())
client.run(secretkey)
