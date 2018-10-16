import asyncio

from discord.ext.commands import Bot

import butt_library as butt_lib
from butt_statistics import ButtStatistics
from buttbot import buttbot
from config import *
from phraseweights import PhraseWeights

weights = PhraseWeights()
stat_module = ButtStatistics(stat_db, db_secrets[0], db_secrets[1], test_environment)

client = Bot(description="a bot for farts", command_prefix="", pm_help=False)

channel_configs = butt_lib.load_all_config_files()  # global that will hold channel IDs that have configs
command_channels = {}

if test_environment == True:
    command_channels["408168696834424832"] = buttbot(client, "development.ini", db_, db_secrets[0], db_secrets[1],
                                                     stat_module, weights, True)
    command_channels["199981748098957312"] = buttbot(client, "DPT_document.ini", db_, db_secrets[0], db_secrets[1],
                                                     stat_module, weights, True)
else:
    for i in channel_configs:
        command_channels[i.split("/")[1][:-4]] = buttbot(client, i, db_, db_secrets[0], db_secrets[1], stat_module,
                                                         weights, False)


@client.event
async def on_ready():
    print('Logged in as ' + client.user.name + ' (ID:' + client.user.id + ') | Connected to ' + str(
        len(client.servers)) + ' servers | Connected to ' + str(len(set(client.get_all_members()))) + ' users')
    print('--------')
    print('Use this link to invite {}:'.format(client.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    print('--------')
    print('You are running FartBot V4.0.00')
    print('Created by Poop Poop')
    print('--------')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author == "BroBot#4514":
        # we dont give a shit about anything this bot says
        return

    # try:
    try:
        if str(message.content)[:1] == "&" or str(message.content).partition(" ")[2][0] == "&":
            # command sent from inside of mc server
            send_to_butt_instance = command_channels[message.server.id].command_dispatch
            await send_to_butt_instance(message)
            return  # dont pass to chat dispatcher
    except IndexError:
        # this message was sent from a regular discord client
        if str(message.content)[:1] == "&":
            send_to_butt_instance = command_channels[message.server.id].command_dispatch
            await send_to_butt_instance(message)
            return

    try:
        send_to_butt_instance = command_channels[message.server.id].chat_dispatch
        await send_to_butt_instance(message)
    except KeyError:
        # no chat dispatcher for this so we are going to default to the 💩💩 channel
        # send_to_butt_instance = default_channel.chat_dispatch
        pass


async def serialize_stats():
    await client.wait_until_ready()
    await asyncio.sleep(5)
    while not client.is_closed:
        stat_module.serialize_all_stats_to_disk()
        await asyncio.sleep(120)


async def send_stats_to_db():
    await client.wait_until_ready()
    await asyncio.sleep(5)
    while not client.is_closed:
        stat_module.send_stats_to_db()
        await asyncio.sleep(300)


async def serialize_weights():
    await client.wait_until_ready()
    await asyncio.sleep(5)
    while not client.is_closed:
        weights.save_to_file()
        if test_environment:
            await asyncio.sleep(10)
        else:
            await asyncio.sleep(300)


client.loop.create_task(serialize_stats())
client.loop.create_task(send_stats_to_db())
client.loop.create_task(serialize_weights())
client.run(secretkey)
