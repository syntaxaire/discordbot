import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
import platform
import re
import time
from random import *
from secretkey import * #dont post this to github you moron

min_call_freq = 15  # RIP/F cooldown in seconds
shitpost_call_freq=30
used = {}  # stores last used time of RIP/F
deaths = {}

def is_word_in_text(word, text):
    pattern = r'(^|[^\w]){}([^\w]|$)'.format(word)
    pattern = re.compile(pattern, re.IGNORECASE)
    matches = re.search(pattern, text)
    return bool(matches)

def do_record_death(message):
    m=message.partition(' ')
    if m[0] not in deaths:
        deaths[m[0]]=0
    deaths[m[0]]=deaths[m[0]]+1

async def do_death_report(channel):
    i=1
    cmsg=''
    for d in sorted(deaths.items(), key=lambda x: x[1],reverse=True):
        if i==10:
            break
        else:
            if i!=1 and i!=9:
                cmsg=cmsg+ ', '

            cmsg=cmsg + d[0] + '('+str(d[1])+')'
            i=i+1
    await do_send_message(channel,cmsg,2)


async def do_send_message(channel,message,cooldown=None):
    #this shit sends the messages to the peeps
    if cooldown:
        await asyncio.sleep(cooldown)
    else:
        await asyncio.sleep(2)
    await client.send_message(channel,message)


shit_post_words=['bot','brand','cloud','anime','elevator','tool','backpack','hammer','lasso','twilight','mana','cat']

async def eval_shit_post(channel,message):
    if randint(1,5)==3:
        for s in shit_post_words:
            if is_word_in_text(s,message):
                #found it
                #people want this to spew garbage so give the garbage to the people
                if ('shitpost' not in used or time.time() - used['shitpost'] > shitpost_call_freq):
                    used['shitpost'] = time.time()
                    for t in shit_post_words: #replace everything aaaaaaa
                        message=message.replace(t,'butt')
                    await do_send_message(channel, message,2)
                    break

client = Bot(description="a bot for farts", command_prefix="", pm_help=False)

@client.event
async def on_ready():
    print('Logged in as ' + client.user.name + ' (ID:' + client.user.id + ') | Connected to ' + str(
        len(client.servers)) + ' servers | Connected to ' + str(len(set(client.get_all_members()))) + ' users')
    print('--------')
    print('Use this link to invite {}:'.format(client.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    print('--------')
    print('You are running FartBot V1.0.5')
    print('Created by Poop Poop')

@client.event
async def on_message(message):
    print('getting messages ' + message.content)
    if message.author == client.user:
        return

    if is_word_in_text("rip", message.content) == True:
        print('rip message')
        if ('rip' not in used or time.time() - used['rip'] > min_call_freq):
            used['rip'] = time.time()
            await do_send_message(message.channel,'Ya, RIP',randint(2,5))
        else:
            print('suck my dick RIP under cooldown')
    elif is_word_in_text("F", message.content) == True:
        print('rip message')
        if ('f' not in used or time.time() - used['f'] > min_call_freq):
            used['f'] = time.time()
            await do_send_message(message.channel,'Ya, F',randint(2,5))
        else:
            if randint(1,100) == 44:
                await do_send_message(message.channel,'suck my dick F under cooldown')
            else:
                print('suck my dick F under cooldown')
    elif is_word_in_text('test died',message.content):
            do_record_death(message.content)
    elif is_word_in_text('!ouchies',message.content):
            await do_death_report(message.channel)
    else:
        #here's where im going to evaluate all other sentences for shitposting
        await eval_shit_post(message.channel,message.content)

client.run(secretkey)