import discord_comms
import mojang
from vacuum import Vacuum
from wordreplacer import WordReplacer
from butt_database import db


class buttbot:
    def __init__(self, BotObject):
        self.db=db()
        self.vacuum = Vacuum(self.db)
        self.comm = discord_comms.discord_comms()
        self.discordBot = BotObject
        self.used={}
        self.shitpost=WordReplacer()


    def lastseen(self, player):
        try:
            if player:
                returnz = self.vacuum.lastseen(player)
                if returnz:
                    return returnz
        except IndexError:
            return ("who am i looking for?")

    def mojang(self):
        msg = mojang.mojang_status_requested()
        for t in msg:
            return t

    def playtime(self,player):
        try:
            if player:
                returnz = self.vacuum.playtime_insult(player)
                if returnz:
                    return returnz
        except IndexError:
                return self.vacuum.playtime_global()

    def howchies(self,message):
            if message:
                return("People who died to " + message + ": " + self.vacuum.howchies_profile(message))
            else:
                return('Heres whats killing you: ' + self.vacuum.top_10_death_reasons())


    def nltk(self,message):
        if str(message.author) in self.config.channel_admins:
            return(self.shitpost.wordtagger(message.content))



    async def dispatch(self, message):
        tokenDict = {"mojang": self.mojang,
                     "lastseen": self.lastseen,
                     "playtime": self.playtime,
                     "howchies": self.howchies,
                     "nltk": self.nltk
                     }
        try:
            command = message.content.split("&", 1)[1]
        except IndexError:
            # no & found in message.
            command = ''
        if command:
            command, se, arguments = command.partition(' ')
            func = tokenDict[command]
            back = func(arguments)
            if back:
                await self.doComms(back, message.channel)

    async def doComms(self, message, channel):
        await self.comm.do_send_message(channel, self.discordBot, message)
