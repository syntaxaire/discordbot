import random
import time

import discord_comms
import mojang as mj
from butt_database import db
from butt_library import is_word_in_text
from vacuum import Vacuum
from wordreplacer import WordReplacer


class buttbot:
    def __init__(self, BotObject):
        self.min_call_freq = 1
        self.db = db()
        self.vacuum = Vacuum(self.db)
        self.comm = discord_comms.discord_comms()
        self.discordBot = BotObject
        self.used = {}
        self.shitpost = WordReplacer(self.min_call_freq)
        self.mojang = mj.mojang()
        self.allcommands = {}


    #        self.config=configparser.

    def do_nltk(self, message):
        if str(message.author) in self.channel_admins:
            return (self.shitpost.wordtagger(message.content))

    async def command_dispatch(self, message):
        try:
            command = message.content.split("&", 1)[1]
        except IndexError:
            # no & found in message.
            command = ''
        if command:
            command, se, arguments = command.partition(' ')

            # pick which module has the command, and set the module to the object
            if command in self.vacuum.return_commands():
                module = self.vacuum
            try:
                func = getattr(module, 'do_' + command)
            except AttributeError:
                # TODO: probably should build a default return all the command thing here.
                pass
            back = func(arguments)
            if back:
                await self.doComms(back, message.channel)

    async def doComms(self, message, channel):
        await self.comm.do_send_message(channel, self.discordBot, message)

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
            print("made it to butt: %s" % message.content)
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
                rshitpost = self.shitpost.eval_sentence_nltk(message.content, str(message.author))
                pass
            try:
                if rshitpost:
                    await self.doComms(rshitpost, message.channel)
            except UnboundLocalError:
                pass
