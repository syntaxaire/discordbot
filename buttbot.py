import asyncio
import configparser
import random
import time

import discord_comms
import mojang as mj
import butt_timeout
from butt_database import db
from butt_library import is_word_in_text
from vacuum import Vacuum
from wordreplacer import WordReplacer


class buttbot:
    def __init__(self, Botobject, conf, db_, db_user, db_pass, stat_module, test_environment):
        self.test_environment = test_environment
        self.stats = stat_module
        self.config = configparser.ConfigParser()
        self.config.read_file(open(conf))
        self.timer_module = butt_timeout.Timeout(self.config)
        self.db = db(db_, db_user, db_pass)
        if bool(self.config.get('vacuum', 'enabled')):
            self.vacuum = Vacuum(self.db)
        self.comm = discord_comms.discord_comms()
        self.discordBot = Botobject
        self.shitpost = WordReplacer(self.config,self.stats, self.timer_module, test_environment)
        self.mojang = mj.mojang()

        if self.config.getboolean('vacuum', 'enabled') is True:
            self.vacuum.update_url(self.config.get('vacuum', 'vacuum_update_json_url'))
            self.discordBot.loop.create_task(self.my_background_task())

    async def my_background_task(self):
        await self.discordBot.wait_until_ready()
        while not self.discordBot.is_closed:
            await asyncio.sleep(10)
            self.vacuum.playtime_scraper()

    async def do_leave(self, message):
        if (str(message.author) in self.config.get('discordbot', 'bot_admin')) and str(self.discordBot.user) in str(
                message.content):
            await self.discordBot.leave_server(message.server)
        else:
            await self.doComms('fuck you youre not my real dad', message.channel)

    def pick_correct_module(self, command):
        # this returns the module that contains the command ran by the user.  The module must support the command and
        # also be enabled to be returned.
        # it defaults to the main buttbot module.
        module = self
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
        return module

    async def command_dispatch(self, message):
        try:
            command = message.content.split("&", 1)[1]
        except IndexError:
            # no & found in message.
            command = ''
        if command:
            command, se, arguments = command.partition(' ')
            module = self.pick_correct_module(command)
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
                    # no module was found for the command.  We are going to try to run it in the base buttbot object
                    back = await func(message)
                else:
                    back = func(arguments)
                if back:
                    await self.doComms(back, message.channel)
            except UnboundLocalError:
                # command not found in any module, including the base buttbot object.  skip for now
                # todo: maybe default return option here too?
                pass

    async def doComms(self, message, channel):
        if self.allowed_in_channel(channel):
            await self.comm.do_send_message(channel, self.discordBot, message)

    async def doreact(self, message, channel, emojis):
        if self.allowed_in_channel(channel):
            self.stats.message_store(message.channel.id)
            self.stats.disposition_store(message.server.id, message.channel.id,
                                         "React", emojis, message.content)
            await self.comm.do_react(message, self.discordBot, emojis)

    async def chat_dispatch(self, message):
        if is_word_in_text("rip", message.content) == True:
            if (str(message.author) == 'Progress#6064' and message.content[:4] == 'RIP:') or (
                    str(message.author) == '💩💩#4048' and message.content[:4] == 'RIP:'):
                self.vacuum.add_death_message(message.content)
            else:
                if self.allowed_in_channel(message.channel):
                    if self.config.getboolean('discordbot', 'RIP'):
                        self.stats.message_store(message.channel.id)
                        if self.timer_module.check_timeout('rip', 'shitpost'):
                            self.stats.disposition_store(message.server.id, message.channel.id,
                                                         "RIP", "RIP")
                            if random.randint(1, 20) == 5:
                                await self.doComms('Ya, butts', message.channel)
                            else:
                                await self.doComms('Ya, RIP', message.channel)
                        else:
                            self.stats.disposition_store(message.server.id, message.channel.id,
                                                         "RIP cooldown", "RIP cooldown")

        elif is_word_in_text("F", message.content):
            if self.allowed_in_channel(message.channel):
                if self.config.getboolean('discordbot', 'F'):
                    self.stats.message_store(message.channel.id)
                    if self.timer_module.check_timeout('f', 'shitpost'):
                        self.stats.disposition_store(message.server.id, message.channel.id,
                                                     "F", "F")
                        await self.doComms('Ya, F', message.channel)
                    else:
                        self.stats.disposition_store(message.server.id, message.channel.id,
                                                     "F cooldown", "F cooldown")
                        if random.randint(1, 100) == 44:
                            await self.doComms('suck my dick F under cooldown', message.channel)

        elif is_word_in_text('butt', message.content) == True or is_word_in_text('butts', message.content) == True:
            if self.allowed_in_channel(message.channel):
                self.stats.message_store(message.channel.id)
                if random.randint(1, 6) == 3:
                    if self.timer_module.check_timeout('rsp', 'shitpost'):
                        rshitpost = self.shitpost.rspeval(message.content)
                        if rshitpost:
                            self.stats.disposition_store(message.server.id, message.channel.id,
                                                         "RSP", "RSP", message.content)
                            await self.doComms(rshitpost, message.channel)
                    else:
                        self.stats.disposition_store(message.server.id, message.channel.id,
                                                     "RSP cooldown", "RSP cooldown")
                elif random.randint(1, 3) == 3:
                    if self.timer_module.check_timeout('rsp_emoji', 'shitpost'):
                        await self.doreact(message, message.channel, random.choice(
                            self.config.get('discordbot', 'butt_response_emojis').split(",")))

        else:
            # here's where im going to evaluate all other sentences for shitposting
            # rshitpost=shitpost.eval(message.content)
            # NLTK test
            if is_word_in_text("left the game", message.content) or is_word_in_text("joined the game", message.content):
                # this is a join or part message and we are going to ignore it
                pass
            else:
                if self.allowed_in_channel(message.channel) or self.test_environment:
                    # do not send to shitpost module if we aren't allowed to talk in the channel in question.
                    # exception: always send if test environment is turned on. the function to send the message to the
                    # discord API will not transmit the message.
                    rshitpost = self.shitpost.tobuttornottobutt(message, str(message.author))
            try:
                if rshitpost:
                    await self.doComms(rshitpost, message.channel)
            except UnboundLocalError:
                pass

    def allowed_in_channel(self, channel):
        allowed_channels = self.config.get("allowed_channels", "channels").split(",")
        if channel.id in allowed_channels:
            return True
        else:
            return False
