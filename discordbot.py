import asyncio

from discord.ext.commands import Bot
from config import *
from buttbot import buttbot
from vacuum import *


async def my_background_task():
    # print("LOGGER::Logger loaded.  Waiting until I connect to Discord")
    await client.wait_until_ready()
    # print("LOGGER::Connected to discord, start processing.")
    while not client.is_closed:
        # vacuum.playtime_log()
        await asyncio.sleep(10)  # task runs every 10 seconds
        # vacuum.playtime_scraper()
        # print("LOGGER:I logged player location at this time.")


client = Bot(description="a bot for farts", command_prefix="", pm_help=False)
progress_bot = buttbot(client,'progress_config.ini')
testes_bot=buttbot(client,'testes_config.ini')


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
            "💩💩": testes_bot.command_dispatch,
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
            "💩💩": testes_bot.chat_dispatch,
            "Shithole": progress_bot.chat_dispatch
        }

    send_to_butt_instance = chat_dispatcher_channels[message.server.name]
    await send_to_butt_instance(message)


# client.loop.create_task(my_background_task())
client.run(secretkey)
