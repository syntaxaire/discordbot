import asyncio
import random as rand


class discord_comms:
    def __init__(self):
        pass

    async def do_send_message(self, channel, client, message, cooldown=None):
        # this shit sends the messages to the peeps
        await asyncio.sleep(1)
        await client.send_typing(channel)
        if cooldown:
            await asyncio.sleep(cooldown)
        else:
            await asyncio.sleep(rand.randint(2, 5))
        await client.send_message(channel, message)  # dont remove await from here or this shit will break

    async def do_react(self, channel, message, client, emoji, cooldown=None):
        if cooldown:
            await asyncio.sleep(cooldown)
        else:
            await asyncio.sleep(rand.randint(2, 5))
        await client.add_reaction(message, emoji)
