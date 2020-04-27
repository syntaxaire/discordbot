import asyncio
from pathlib import Path
import datetime
import aiohttp
from discord.ext.commands import Bot
from cogs.bot import BotCommands
from cogs.botconfig import BotConfig
from butt_config import Config

from config import *

LOGDIR = Path('logs')
bot = Bot(description="a bot for farts", command_prefix="$", pm_help=False)


def setup_logger() -> logging.Logger:
    """Create and return the master Logger object."""
    LOGDIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    logfile = LOGDIR / f'{timestamp}.log'
    logger = logging.getLogger('bot')  # the actual logger instance
    logger.setLevel(logging.DEBUG)  # capture all log levels
    console_log = logging.StreamHandler()
    console_log.setLevel(logging.DEBUG)  # log levels to be shown at the console
    file_log = logging.FileHandler(logfile)
    file_log.setLevel(logging.DEBUG)  # log levels to be written to file
    formatter = logging.Formatter('{asctime} - {name} - {levelname} - {message}', style='{')
    console_log.setFormatter(formatter)
    file_log.setFormatter(formatter)
    logger.addHandler(console_log)
    logger.addHandler(file_log)
    return logger


log = setup_logger()
guild_configs = Config()


@bot.event
async def on_ready():
    log.info('Use this link to invite {}:'.format(bot.user.name))
    log.info('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(bot.user.id))
    log.info('--------')
    log.info('You are running FartBot V7.0.00')
    log.info('Created by Poop Poop')
    log.info('--------')
    bot.aiohttp_session = aiohttp.ClientSession()


@bot.event
async def on_server_join(server):
    pass


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author == "BroBot#4514":
        # we dont give a shit about anything this bot says, ever.
        return
    # ensure guild has a config loaded
    try:
        if guild_configs[message.guild.id].exists is True:
            pass
            # loaded
    except KeyError:
        guild_configs.create_config(message.guild.id)

    try:
        if message.content[0] == "$":
            log.debug("sending message to command processor")
            await bot.process_commands(message)
        else:
            # send to butterizer
            pass
    except IndexError:
        print(message)


# async def send_stats_to_db():
#    await bot.wait_until_ready()
#    await asyncio.sleep(5)
#    while not bot.is_closed:
#        stat_module.send_stats_to_db()
#        await asyncio.sleep(300)


async def serialize_weights():
    await bot.wait_until_ready()
    await asyncio.sleep(5)
    while not bot.is_closed:
        if test_environment:
            await asyncio.sleep(10)
        else:
            await asyncio.sleep(300)


# bot.loop.create_task(send_stats_to_db())
bot.add_cog(BotCommands(bot))
bot.add_cog(BotConfig(bot))
# bot.loop.create_task(serialize_weights())
bot.run(secretkey)
