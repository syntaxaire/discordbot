import asyncio
import random as rand

from discord.utils import get


class DiscordComms:
    def __init__(self):
        pass

    @staticmethod
    async def do_send_message(channel, client, message, cooldown=None):
        # this shit sends the messages to the peeps
        await asyncio.sleep(1)
        await client.send_typing(channel)
        if cooldown:
            await asyncio.sleep(cooldown)
        else:
            await asyncio.sleep(rand.randint(2, 5))
        msg = await client.send_message(channel, message)  # dont remove await from here or this shit will break
        return msg

    @staticmethod
    async def do_react(message, client, emoji, cooldown=None):
        if cooldown:
            await asyncio.sleep(cooldown)
        else:
            await asyncio.sleep(rand.randint(2, 5))
        if emoji[0] == ":":
            # custom emoji for channel. we need to get it
            emoji = get(client.get_all_emojis(), name=emoji[1:])
        await client.add_reaction(message, emoji)

    @staticmethod
    async def do_react_no_delay(message, client, emoji):
        if emoji[0] == ":":
            # custom emoji for channel. we need to get it
            emoji = get(client.get_all_emojis(), name=emoji[1:])
        await client.add_reaction(message, emoji)
