from vacuum import Vacuum
import mojang
import discord_comms
import asyncio



class buttbot:
    def __init__(self,BotObject):
        self.vacuum=Vacuum()
        self.comm=discord_comms.discord_comms()
        self.discordBot=BotObject

    def lastseen(self,player):
        try:
            if player:
                returnz = self.vacuum.lastseen(player)
                if returnz:
                    return returnz
        except IndexError:
            return("who am i looking for?")

    def mojang(self):
        msg = mojang.mojang_status_requested()
        for t in msg:
            return t


    async def dispatch(self,message):
        tokenDict={"mojang":self.mojang}
        try:
            command = message.content.split("&", 1)[1]
        except IndexError:
            #no & found in message.
            command = ''
        if command:
            c2 = command.split(' ')
            func=tokenDict[c2[0]]
            back=func()
            if back:
                await self.doComms(back,message.channel)

    async def doComms(self,message,channel):
        await self.comm.do_send_message(channel,self.discordBot,message)
