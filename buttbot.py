import discord_comms
import mojang as mj
from butt_database import db
from vacuum import Vacuum
from wordreplacer import WordReplacer


class buttbot:
    def __init__(self, BotObject):
        self.db = db()
        self.vacuum = Vacuum(self.db)
        self.comm = discord_comms.discord_comms()
        self.discordBot = BotObject
        self.used = {}
        self.shitpost = WordReplacer()
        self.mojang = mj.mojang()
        self.allcommands = {}

    def do_nltk(self, message):
        if str(message.author) in self.channel_admins:
            return (self.shitpost.wordtagger(message.content))

    def do_howchies(self):
        print("fuck")

    async def dispatch(self, message):
        try:
            command = message.content.split("&", 1)[1]
        except IndexError:
            # no & found in message.
            command = ''
        if command:
            command, se, arguments = command.partition(' ')

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
