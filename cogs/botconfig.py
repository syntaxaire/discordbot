import logging
from discord.ext.commands import Bot, Cog, Context, command, has_permissions
from shared import shitpost
from shared import guild_configs

log = logging.getLogger('bot.' + __name__)


class BotConfig(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    @has_permissions(administrator=True)
    async def config(self, ctx: Context, *args):
        log.info("got config command from %s in channel %s. arguments are %s" %
                 (str(ctx.message.author.name), str(ctx.message.channel.name), str(*args)))
        arguments = args[0]
        if arguments == "allow":
            guild_configs[ctx.message.guild.id].add_channel_to_allowed_channel_list(ctx.message.channel.id)
            await ctx.send(
                shitpost.do_butting_raw_sentence(
                    "Buttbot will now talk in this wonderful channel and respond to any message"))

        if arguments == "remove":
            await ctx.send(
                shitpost.do_butting_raw_sentence("Buttbot will longer reply to messages in this channel"))
            self.config.remove_channel_from_allowed_channel_list(
                ctx.message.channel.id)

        if arguments == "botallow":
            await ctx.send(
                shitpost.do_butting_raw_sentence("I will now reply to the bot on this guild"))
            self.config.add_whitelisted_bots(args[1])

        if arguments == "botremove":
            await ctx.send(
                shitpost.do_butting_raw_sentence("I will no longer reply to the bot on this guild"))
            self.config.remove_whitelisted_bots(args[1])

    @config.error
    async def config_error(self, error, ctx: Context):
        await ctx.send("You do not have permission to run this command in this channel")
