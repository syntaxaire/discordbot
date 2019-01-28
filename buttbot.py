import asyncio
import random
import time

from discord.utils import get

import butt_config
import butt_timeout
import discord_comms
import mojang as mj
from butt_database import Db
from butt_library import is_word_in_text
from vacuum import Vacuum
from wordreplacer import WordReplacer


class ButtBot:
    def __init__(self, bot_object, conf, db_, db_user, db_pass, stat_module, phrase_weights, test_environment):
        self.discordBot = bot_object
        self.config = butt_config.ButtConfig(conf)
        if not self.config.get_plain_language_name():
            self.configure_buttbot_instance()
        self.test_environment = test_environment
        self.stats = stat_module
        self.timer_module = butt_timeout.Timeout(self.config)
        self.db = Db(db_, db_user, db_pass, test_environment)
        if bool(self.config.get('vacuum', 'enabled')):
            self.vacuum = Vacuum(self.db)
        self.comm = discord_comms.DiscordComms()
        self.phrase_weights = phrase_weights
        self.shitpost = WordReplacer(self.config, self.stats, self.timer_module, phrase_weights, test_environment)
        self.mojang = mj.Mojang()
        self.discordBot.loop.create_task(self.butt_message_processing())
        if self.config.getboolean('vacuum', 'enabled') is True:
            self.vacuum.update_url(self.config.get('vacuum', 'vacuum_update_json_url'))
            self.discordBot.loop.create_task(self.my_background_task())

    async def do_security_log(self, message):
        await self.comm.do_send_message(self.discordBot.get_channel("505226379487346690"), self.discordBot, message, 0)

    async def do_info_log(self, message):
        await self.comm.do_send_message(self.discordBot.get_channel("505226325511110658"), self.discordBot, message, 0)

    async def my_background_task(self):
        await self.discordBot.wait_until_ready()
        while not self.discordBot.is_closed:
            await asyncio.sleep(10)
            self.vacuum.playtime_scraper()

    async def butt_message_processing(self):
        await self.discordBot.wait_until_ready()
        while not self.discordBot.is_closed:
            if self.test_environment:
                await asyncio.sleep(10)
            else:
                await asyncio.sleep(120)
            self.check_stored_reactions()

    def configure_buttbot_instance(self):
        self.config.set_plain_language_name(self.discordBot.get_server("507477640375042049"))

    # noinspection PyUnusedLocal
    async def do_leave(self, message, arguments):
        if (str(message.author) in self.config.get('discordbot', 'bot_admin')) and str(self.discordBot.user) in str(
                message.content):
            await self.discordBot.leave_server(message.server)
        else:
            await self.docomms('fuck you youre not my real dad', message.channel)
            await self.do_security_log("%s tried do_leave in server %s (%s)" %
                                       (message.author.name, message.server.name, message.server.id))

    async def do_config(self, message, arg):
        arguments, junk, guid = arg.partition(' ')
        if arguments == "allow":
            if message.channel.permissions_for(message.author).manage_messages:
                # person has manage messages in this channel
                self.config.add_channel_to_allowed_channel_list(message.channel.id)
                await self.docomms(
                    self.shitpost.do_butting_raw_sentence(
                        "Buttbot will now talk in this wonderful channel and respond to any message")[0],
                    message.channel)
                await self.do_security_log("%s did permit in %s (%s) in server %s (%s)" %
                                           (message.author, message.channel, str(message.channel.id),
                                            message.server.name, str(message.server.id)))
            else:
                # person does not have manage messages in this channel
                await self.docomms(
                    self.shitpost.do_butting_raw_sentence(
                        "You do not have permission to run this command in this channel")[0],
                    message.channel)
                await self.do_security_log("%s tried to permit in %s (%s) in server %s (%s), but no permissions" %
                                           (message.author, message.channel, str(message.channel.id),
                                            message.server.name, str(message.server.id)))
        if arguments == "remove":
            if message.channel.permissions_for(message.author).manage_messages:
                await self.docomms(
                    self.shitpost.do_butting_raw_sentence("Buttbot will longer reply to messages in this channel")[0],
                    message.channel)
                self.config.remove_channel_from_allowed_channel_list(message.channel.id)  # change execution order so it
                # actually sends it
                await self.do_security_log("%s removed in %s (%s) in server %s (%s)" %
                                           (message.author, message.channel, str(message.channel.id),
                                            message.server.name, str(message.server.id)))
            else:
                # person does not have manage messages in this channel
                await self.docomms(
                    self.shitpost.do_butting_raw_sentence(
                        "You do not have permission to run this command in this channel")[0],
                    message.channel)
                await self.do_security_log("%s tried to remove in %s (%s) in server %s (%s), but no permissions" %
                                           (message.author, message.channel, str(message.channel.id),
                                            message.server.name, str(message.server.id)))
        if arguments == "botallow":
            if message.channel.permissions_for(message.author).manage_messages:
                await self.docomms(
                    self.shitpost.do_butting_raw_sentence("I will now reply to the bot on this guild")[0],
                    message.channel)
                self.config.add_whitelisted_bots(guid)  # change execution order so it
                # actually sends it
                await self.do_security_log("%s added bot %s in server %s (%s)" %
                                           (message.author, guid, message.server.name, str(message.server.id)))
            else:
                # person does not have manage messages in this channel
                await self.docomms(
                    self.shitpost.do_butting_raw_sentence(
                        "You do not have permission to run this command in this channel")[0],
                    message.channel)
                await self.do_security_log("%s tried to add bot %s in server %s (%s), but no permissions" %
                                           (message.author, guid, message.server.name, str(message.server.id)))

        if arguments == "botremove":
            if message.channel.permissions_for(message.author).manage_messages:
                await self.docomms(
                    self.shitpost.do_butting_raw_sentence("I will no longer reply to the bot on this guild")[0],
                    message.channel)
                self.config.remove_whitelisted_bots(guid)  # change execution order so it
                # actually sends it
                await self.do_security_log("%s removed bot %s in server %s (%s)" %
                                           (message.author, guid, message.server.name, str(message.server.id)))
            else:
                # person does not have manage messages in this channel
                await self.docomms(
                    self.shitpost.do_butting_raw_sentence(
                        "You do not have permission to run this command in this channel")[0],
                    message.channel)
                await self.do_security_log("%s tried to remove bot %s in server %s (%s), but no permissions" %
                                           (message.author, guid, message.server.name, str(message.server.id)))

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

        if command in self.mojang.return_commands() and self.config.getboolean('mojang', 'enabled') is True:
            # we are using the vacuum config because both of these are for minecraft.
            module = self.mojang
        return module

    async def command_dispatch(self, message):
        if not self.should_i_reply_to_user(message):
            # user is either a bot not on whitelist or is a user on the ignore list
            return
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
                    # noinspection PyUnboundLocalVariable
                    back = await func(message, arguments)
                else:
                    # noinspection PyUnboundLocalVariable
                    back = func(arguments)
                if back:
                    await self.docomms(back, message.channel)
            except UnboundLocalError:
                # command not found in any module, including the base buttbot object.  skip for now
                # todo: maybe default return option here too?
                pass

    async def docomms(self, message, channel):
        if self.allowed_in_channel(channel):
            msg = await self.comm.do_send_message(channel, self.discordBot, message)
            return msg  # returns the message object of the message that was sent to discord

    async def doreact(self, message, channel, emojis):
        if self.allowed_in_channel(channel):
            self.stats.message_store(message.channel.id)
            self.stats.disposition_store(message.server.id, message.channel.id,
                                         "React", emojis, message.content)
            await self.comm.do_react(message, self.discordBot, emojis)

    def _should_i_reply_to_bot(self, author):
        """Checks to see if we should reply to message author - checks bot whitelist and general user ignore list"""
        if author in self.config.get_all_allowed_bots():
            # we should always talk to this bot
            return True
        else:
            return False

    def _should_i_reply_to_user(self, author):
        if author not in self.config.get_all_banned_users():
            return True
        else:
            return False

    def should_i_reply_to_user(self, message):
        if message.author.bot:
            # bot user (flag set by discord server)
            if self._should_i_reply_to_bot(str(message.author)):
                return True
            else:
                return False
        if self._should_i_reply_to_user(str(message.author)):
            return True
        else:
            return False

    async def chat_dispatch(self, message):
        if not self.should_i_reply_to_user(message):
            # user is either a bot not on whitelist or is a user on the ignore list
            return
        elif is_word_in_text("rip", message.content):
            await self._process_RIP_message(message)

        elif is_word_in_text("F", message.content):
            await self._process_F_message(message)

        elif is_word_in_text('butt', message.content) is True or is_word_in_text('butts', message.content) is True:
            await self._process_butt_message(message)

        else:
            await self._process_all_other_messages(message)

    def allowed_in_channel(self, channel):
        allowed_channels = self.config.get("allowed_channels", "channels").split(",")
        if channel.id in allowed_channels:
            return True
        else:
            return False

    def process_cached_reaction_message(self, guid, trigger_word, noun):
        if self.test_environment:
            print("running on id %s" % guid)
        phrase = "%s %s" % (trigger_word, noun)
        msg_ = get(self.discordBot.messages, id=guid)
        votes = self.phrase_weights.process_reactions(msg_.reactions)
        self.phrase_weights.adjust_weight(phrase, votes)

    def check_stored_reactions(self):
        for items in self.phrase_weights.get_messages():
            check_timer = 300
            if self.test_environment:
                check_timer = 15
            if time.time() - items[0] > check_timer:
                self.process_cached_reaction_message(items[1], items[2], items[3])
                self.phrase_weights.remove_message(items[0], items[1], items[2], items[3])

    async def _process_RIP_message(self, message):
        if (str(message.author) == 'Progress#6064' and message.content[:4] == 'RIP:') or (
                str(message.author) == '💩💩#4048' and message.content[:4] == 'RIP:'):
            self.vacuum.add_death_message(message.content)
        else:

            if self.allowed_in_channel(message.channel) and self.config.getboolean('discordbot', 'RIP'):
                self.stats.message_store(message.channel.id)
                if self.timer_module.check_timeout('rip', 'shitpost'):
                    self.stats.disposition_store(message.server.id, message.channel.id,
                                                 "RIP", "RIP")
                    if random.randint(1, 20) == 5:
                        await self.docomms('Ya, butts', message.channel)
                    else:
                        await self.docomms('Ya, RIP', message.channel)
                else:
                    self.stats.disposition_store(message.server.id, message.channel.id,
                                                 "RIP cooldown", "RIP cooldown")

    async def _process_F_message(self, message):
        if self.allowed_in_channel(message.channel) and self.config.getboolean('discordbot', 'F'):
            self.stats.message_store(message.channel.id)
            if self.timer_module.check_timeout('f', 'shitpost'):
                self.stats.disposition_store(message.server.id, message.channel.id,
                                             "F", "F")
                await self.docomms('Ya, F', message.channel)
            else:
                self.stats.disposition_store(message.server.id, message.channel.id,
                                             "F cooldown", "F cooldown")
                if random.randint(1, 100) == 44:
                    await self.docomms('suck my dick F under cooldown', message.channel)

    async def _process_butt_message(self, message):
        if self.allowed_in_channel(message.channel):
            self.stats.message_store(message.channel.id)
            if random.randint(1, 6) == 3:
                if self.timer_module.check_timeout('rsp', 'shitpost'):
                    rshitpost = self.shitpost.rspeval(message.content)
                    if rshitpost:
                        self.stats.disposition_store(message.server.id, message.channel.id,
                                                     "RSP", "RSP", message.content)
                        await self.docomms(rshitpost, message.channel)
                else:
                    self.stats.disposition_store(message.server.id, message.channel.id,
                                                 "RSP cooldown", "RSP cooldown")
            elif random.randint(1, 3) == 3:
                if self.timer_module.check_timeout('rsp_emoji', 'shitpost'):
                    await self.doreact(message, message.channel, random.choice(self.config.get_all_emojis()))

    async def _process_all_other_messages(self, message):
        # here's where im going to evaluate all other sentences for shitposting
        if is_word_in_text("left the game", message.content) or is_word_in_text("joined the game", message.content):
            # this is a join or part message and we are going to ignore it
            pass
        else:
            if self.allowed_in_channel(message.channel):
                # do not send to shitpost module if we aren't allowed to talk in the channel in question.
                if self.test_environment:
                    # always reply in test environment
                    rv = [1, 1, 1]
                else:
                    rv = [1, 5, 3]
                if random.randint(rv[0], rv[1]) == rv[2]:
                    if self.timer_module.check_timeout('shitpost', 'shitpost'):
                        # passed timer check
                        #try:
                        rshitpost = self.shitpost.perform_text_to_butt(message)
                        #except TypeError:
                            # did not return anything, so we don't care
                        #   pass
                        try:
                            # noinspection PyUnboundLocalVariable
                            if rshitpost:
                                # noinspection PyUnboundLocalVariable
                                msg = await self.docomms(rshitpost, message.channel)
                                # am i ever going to implement this?
                                # last opinion was that it was easier to use on mobile versions of discord
                                # but you lose the 'organic feel' of buttbot
                                # await self.comm.do_react_no_delay(msg, self.discordBot, '👍')
                                # await self.comm.do_react_no_delay(msg, self.discordBot, '👎')
                                # noinspection PyUnboundLocalVariable,PyUnboundLocalVariable
                                self.phrase_weights.add_message(msg.id, trigger_word, noun)
                        except UnboundLocalError:
                            pass