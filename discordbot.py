from discord.ext.commands import Bot

from buttbot import buttbot
from config import *
import glob


def load_all_config_files():
    return glob.glob("config/*.ini")

client = Bot(description="a bot for farts", command_prefix="", pm_help=False)

channel_configs=load_all_config_files() #global that will hold channel IDs that have configs
command_channels={}
for i in channel_configs:
    command_channels[i.split("/")[1][:-4]] = buttbot(client, i)


@client.event
async def on_ready():
    print('Logged in as ' + client.user.name + ' (ID:' + client.user.id + ') | Connected to ' + str(
        len(client.servers)) + ' servers | Connected to ' + str(len(set(client.get_all_members()))) + ' users')
    print('--------')
    print('Use this link to invite {}:'.format(client.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    print('--------')
    print('You are running FartBot V2.1.05')
    print('Created by Poop Poop')
    print('--------')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #try:
    if str(message.content)[:1] == "&" or str(message.content).partition(" ")[2][0] == "&":
        # command sent from inside of mc server or from regular client
        send_to_butt_instance = command_channels[message.server.id].command_dispatch
        await send_to_butt_instance(message)
        return  # dont pass to chat dispatcher

    try:
        send_to_butt_instance = command_channels[message.server.id].chat_dispatch
        await send_to_butt_instance(message)
    except KeyError:
        # no chat dispatcher for this so we are going to default to the 💩💩 channel
        #send_to_butt_instance = default_channel.chat_dispatch
        pass



client.run(secretkey)
