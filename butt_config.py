from shared import db
import logging

log = logging.getLogger('discordbot.' + __name__)


class ButtConfig:

    def __init__(self, guid: int):
        log.debug("Loading config for guid %d" % guid)
        db["buttbot"].build()
        self.guid = guid
        self.allowed_channels_query = db["buttbot"].do_query("select channel_guid "
                                                             "from allowed_channels ac "
                                                             "inner join config "
                                                             "on config.guid = ac.guid "
                                                             "where guid = %d", (guid,))
        self.stop_phrases_query = db["buttbot"].do_query("select phrase "
                                                         "from stop_processing_phrases spp "
                                                         "inner join config "
                                                         "on config.guid = spp.guid "
                                                         "where guid = %d", (guid,))
        self.allowed_bots_query = db["buttbot"].do_query("select bot_guid "
                                                         "from whitelisted_bots wb "
                                                         "inner join config "
                                                         "on config.guid = wb.guid "
                                                         "where guid = %d", (guid,))
        self.conf = db["buttbot"].do_query("select config.* from config where guid = %d", (guid,))[0]
        log.debug("config loaded for guid %d" % guid)

    def update_property(self, prop: str, value):
        db["buttbot"].build()
        log.debug('running query: "update config set {0} = {1} where guid = {2}"', (prop, value, self.guid))
        db["buttbot"].do_query("update config set {0} = {1} where guid = {2}", (prop, value, self.guid))

    def insert_new_value(self, tab: str, row: str, val):
        db["buttbot"].build()
        log.debug("running query: \"insert into {0} ('{1}', guid) values('{2}', {3})", (tab, row, val, self.guid))
        db["buttbot"].do_query("insert into {0} ('{1}', guid) values('{2}', {3})", (tab, row, val, self.guid))

    def delete_value(self, tab: str, row: str, val):
        db["buttbot"].build()
        log.debug("running query: \"delete from {0} where {1} = {2} and guid = {3}", (tab, row, val, self.guid))
        db["buttbot"].do_query("delete from {0} where {1} = {2} and guid = {3}", (tab, row, val, self.guid))

    @property
    def name(self) -> str:
        return self.conf["guild_name"]

    @name.setter
    def name(self, pla: str):
        self.update_property("guild_name", pla)

    @property
    def allowed_bots(self) -> list:
        return self.allowed_bots_query

    @property
    def allowed_channels(self) -> list:
        return self.allowed_channels_query

    @property
    def emojis(self) -> list:
        return self.conf["butt_response_emojis"]

    @property
    def banned_users(self) -> list:
        # TODO: need table
        pass

    @property
    def stop_phrases(self) -> list:
        return self.stop_phrases_query

    def add_channel_to_allowed_channel_list(self, channel: int):
        self.insert_new_value("allowed_channels", "channel_guid", channel)

    def remove_channel_from_allowed_channel_list(self, channel: int):
        self.delete_value("allowed_channels", "channel_guid", channel)

    @property
    def rip(self) -> bool:
        return self.conf["rip"]

    @rip.setter
    def rip(self, setting):
        self.update_property("rip", setting)

    @property
    def f(self) -> bool:
        return self.conf["f"]

    @f.setter
    def f(self, setting: bool):
        self.update_property("f", setting)

    def add_always_ignore(self, user_guid: int):
        # todo: need table
        pass

    def remove_always_ignore(self, user_guid: int):
        # todo: need table
        pass

    def add_whitelisted_bots(self, user_guid: int):
        self.insert_new_value("whitelisted_bots", "bot_guid", user_guid)

    def remove_whitelisted_bots(self, user_guid: int):
        self.delete_value("whitelisted_bots", "bot_guid", user_guid)
