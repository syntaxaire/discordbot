import configparser
import random
import time
import asyncio

import discord_comms
import mojang as mj
from butt_database import db
from butt_library import is_word_in_text
from vacuum import Vacuum
from wordreplacer import WordReplacer


class buttbot:
    def __init__(self, BotObject, conf):
        self.config = configparser.ConfigParser()
        self.config.read_file(open(conf))
        self.db = db()
        self.vacuum = Vacuum(self.db)
        self.comm = discord_comms.discord_comms()
        self.discordBot = BotObject
        self.used = {}
        self.shitpost = WordReplacer(int(self.config.get('discordbot','shitpost_call_freq')))
        self.mojang = mj.mojang()

        if self.config.getboolean('vacuum', 'enabled') is True:
            self.vacuum.update_url(self.config.get('vacuum', 'vacuum_update_json_url'))
            #self.discordBot.loop.create_task(self.my_background_task()) TODO: unfuck it

    async def my_background_task(self):
        await self.discordBot.wait_until_ready()
        while not self.discordBot.is_closed:
            await asyncio.sleep(10)
            self.vacuum.playtime_scraper()

    async def do_leave(self, message):
        if str(message.author) in self.config.get('discordbot','bot_admin'):
            await self.discordBot.leave_server(message.server)
        else:
            await self.doComms('fuck you youre not my real dad', message.channel)

    async def command_dispatch(self, message):
        try:
            command = message.content.split("&", 1)[1]
        except IndexError:
            # no & found in message.
            command = ''
        if command:
            command, se, arguments = command.partition(' ')
            module=self
            # pick which module has the command, and set the module var to the module object
            if command in self.vacuum.return_commands() and self.config.getboolean('vacuum', 'enabled') is True:
                # vacuum must be turned on for this to work.
                module = self.vacuum

            if command in self.shitpost.return_commands() and self.config.getboolean('wordreplacer', 'enabled') is True:
                # wordreplacer must be turned on for this to work.
                module = self.shitpost

            if command in self.mojang.return_commands() and self.config.getboolean('vacuum', 'enabled') is True:
                # we are using the vacuum config because both of these are for minecraft.
                module = self.mojang
            try:
                if module:
                    func = getattr(module, 'do_' + command)
            except AttributeError:
                # TODO: probably should build a default return all the command thing here.
                pass
            except UnboundLocalError:
                # the module was specifically disabled in the configuration
                pass
            try:
                if module is self:
                    #no module was found for the command.  We are going to try to run it in the base buttbot object
                    back = await func(message)
                else:
                    back = func(arguments)
                if back:
                    await self.doComms(back, message.channel)
            except UnboundLocalError:
                #command not found in any module, including the base buttbot object.  skip for now
                #todo: maybe default return option here too?
                pass

    async def doComms(self, message, channel):
        try:
            if bool(self.config.get('allowed_channels', str(channel))) is True:
                await self.comm.do_send_message(channel, self.discordBot, message)
        except configparser.NoOptionError:
            #channel not in config, skip.
            pass

    async def chat_dispatch(self, message):
        if is_word_in_text("rip", message.content) == True:
            if (str(message.author) == 'Progress#6064' and message.content[:4] == 'RIP:') or (
                    str(message.author) == '💩💩#4048' and message.content[:4] == 'RIP:'):
                self.vacuum.add_death_message(message.content)
            else:
                if 'rip' not in self.used or time.time() - self.used['rip'] > self.min_call_freq:
                    self.used['rip'] = time.time()
                    if random.randint(1, 20) == 5:
                        await self.doComms('Ya, butts', message.channel)
                    else:
                        await self.doComms('Ya, RIP', message.channel)

        elif is_word_in_text("F", message.content):
            if 'f' not in self.used or time.time() - self.used['f'] > self.min_call_freq:
                self.used['f'] = time.time()
                await self.doComms('Ya, F', message.channel)
            else:
                if random.randint(1, 100) == 44:
                    await self.doComms('suck my dick F under cooldown', message.channel)


        elif is_word_in_text('butt', message.content) == True:
            if random.randint(1, 6) == 3:
                rshitpost = self.shitpost.rspeval(message.content)
                if rshitpost:
                    await self.doComms(rshitpost, message.channel)
            elif random.randint(1, 3) == 3:
                await self.comm.do_react(message, self.discordBot, random.choice(["👌", "👍"]))

        else:
            # here's where im going to evaluate all other sentences for shitposting
            # rshitpost=shitpost.eval(message.content)
            # NLTK test
            if is_word_in_text("left the game", message.content) or is_word_in_text("joined the game", message.content):
                # this is a join or part message and we are going to ignore it
                pass
            else:
                rshitpost = self.shitpost.tobuttornottobutt(message.content, str(message.author))
                pass
            try:
                if rshitpost:
                    await self.doComms(rshitpost, message.channel)
            except UnboundLocalError:
                pass
