import asyncio
from discord.ext.commands import Bot
from config import *  #dont post this to github you moron
from ouchies import *
from wordreplacer import *


used = {}  # stores last used time of RIP/F
ouch = Oww()
shitpost=WordReplacer()
shitpost.config(shitpost_call_freq)


def is_word_in_text(word, text):
    pattern = r'(^|[^\w]){}([^\w]|$)'.format(word)
    pattern = re.compile(pattern, re.IGNORECASE)
    matches = re.search(pattern, text)
    return bool(matches)

async def do_send_message(channel,message,cooldown=None):
    #this shit sends the messages to the peeps
    if cooldown:
        await asyncio.sleep(cooldown)
    else:
        await asyncio.sleep(2)
    await client.send_message(channel,message)



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
    print('--------')

    print('loaded ouchies.txt')
#    print (ouch.msg())

@client.event
async def on_message(message):
    print('getting messages ' + message.content)
    if message.author == client.user:
        return
    try:
        command=message.content.split("&",1)[1]
    except IndexError:
        # finally:
        command=''

    if command:
        print("main::command::found command")
        c2=command.split(' ')
        if c2[0] == "buttword":
            print("main::command:buttword ")
            #buttword is restricted so lets check the author
            if str(message.author) in channel_admins:
                print("main::command::buttword::author in admins")
                #passes admin test. process here
                try:
                    if c2[1] == 'list':
                        returnz = shitpost.buttword('list', '')
                        if returnz:
                            print('buttword:: return from arg')
                            await do_send_message(message.channel, returnz)
                        else:
                            print('buttword:: no return from function')
                    elif c2[1] and c2[2]:
                        returnz = shitpost.buttword(c2[1], c2[2])
                        if returnz:
                            print('buttword:: return from arg')
                            await do_send_message(message.channel, returnz)
                        else:
                            print('buttword:: no return from function')
                    else:
                        await do_send_message(message.channel, 'add remove list')
                except IndexError:
                    print("main::buttword::caught index exception")
                    await do_send_message(message.channel, 'add remove list')

            else:
                print('main::command::buttword::author NOT in admins: '+str(message.author))
                #pass #here is the end of the admin check test.

        elif c2[0]=="howchies":
            if ('howouchies' not in used or time.time() - used['howouchies'] > ouchies_call_freq):
                used['howouchies'] = time.time()
                await do_send_message(message.channel, 'Heres whats killing you: ' + ouch.top10reasons())

        elif c2[0]=="ouchies":
            try:
                if c2[1]:
                    #personal profile
                    await do_send_message(message.channel,"Deaths for "+c2[1]+": "+ouch.profile(c2[1]))



            except IndexError:
                if ('ouchies' not in used or time.time() - used['ouchies'] > ouchies_call_freq):
                    used['ouchies'] = time.time()
                    await do_send_message(message.channel, 'Top 10 ouchies: ' + ouch.top10deaths())

        elif c2[0]=="commands" or c2[0]=="help":
            await do_send_message(message.channel,'ouchies, howchies, buttword (but only if ur a cool kid)')



#shitposting follows



    elif is_word_in_text("rip", message.content) == True:
        if (str(message.author)=='Progress#6064' and message.content[:4] == 'RIP:') or (str(message.author)=='💩💩#4048' and message.content[:4] == 'RIP:'):
            print('heres where we would process a death message')
            ouch.record(message.content)
        else:
            print('rip message')
            if ('rip' not in used or time.time() - used['rip'] > min_call_freq):
                used['rip'] = time.time()
                if randint(1,20)==5:
                    await do_send_message(message.channel,'Ya, butts',randint(2,5))
                else:
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



    elif is_word_in_text('butt', message.content)==True:
        print('we have a butt here')
        rshitpost=shitpost.rspeval(message.content)
        if rshitpost:
            await do_send_message(message.channel,rshitpost)
    else:
        #here's where im going to evaluate all other sentences for shitposting
         rshitpost=shitpost.eval(message.content)
         if rshitpost:
            await do_send_message(message.channel,rshitpost)

client.run(secretkey)