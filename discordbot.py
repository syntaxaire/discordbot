import asyncio

from discord.ext.commands import Bot
from config import *
from buttbot import buttbot
from vacuum import *


client = Bot(description="a bot for farts", command_prefix="", pm_help=False)
progress_bot = buttbot(client,'progress_config.ini')

hohle_bot=buttbot(client,'hohle_config.ini')


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
    command_channels = \
        {
            "Die Höhle des Mannes": hohle_bot.command_dispatch,
            "Shithole": progress_bot.command_dispatch
        }
    try:
        if str(message.content)[:1] == "&" or str(message.content).partition(" ")[2][0] == "&":
            # command sent from inside of mc server
            send_to_butt_instance = command_channels[message.server.name]
            await send_to_butt_instance(message)
            return  # dont pass to chat dispatcher
    except IndexError:
        # command sent from normal discord client
        if str(message.content)[:1] == "&":
            send_to_butt_instance = command_channels[message.server.name]
            await send_to_butt_instance(message)
            return  # dont pass to chat dispatcher

    # shitposting follows
    chat_dispatcher_channels = \
        {
            "Die Höhle des Mannes": hohle_bot.chat_dispatch,
            "Shithole": progress_bot.chat_dispatch
        }

    send_to_butt_instance = chat_dispatcher_channels[message.server.name]
    await send_to_butt_instance(message)


client.run(secretkey)
