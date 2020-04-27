from shared import db
import logging

log = logging.getLogger('bot.' + __name__)


class ButtConfig:

    def __init__(self, guid: int):
        log.debug("Loading config for guid %d" % guid)
        db["buttbot"].build()
        self.guid = guid
        self.allowed_channels_query = db["buttbot"].do_query("select channel_guid "
                                                             "from allowed_channels ac "
                                                             "inner join config "
                                                             "on config.guid = ac.guid "
                                                             "where ac.guid = %s", (guid,))
        self.stop_phrases_query = db["buttbot"].do_query("select phrase "
                                                         "from stop_processing_phrases spp "
                                                         "inner join config "
                                                         "on config.guid = spp.guid "
                                                         "where spp.guid = %s", (guid,))
        self.allowed_bots_query = db["buttbot"].do_query("select bot_guid "
                                                         "from whitelisted_bots wb "
                                                         "inner join config "
                                                         "on config.guid = wb.guid "
                                                         "where wb.guid = %s", (guid,))
        self.conf = db["buttbot"].do_query("select config.* from config where guid = %s", (guid,))[0]
        log.debug("config loaded for guid %d" % guid)

    @staticmethod
    def do_query(query: str, args=()):
        db["buttbot"].build()
        log.debug('running query: %s' % query)
        if args:
            db["buttbot"].do_query(query, args)
        else:
            db["buttbot"].do_query(query)

    def update_property(self, prop: str, value):
        query = "update config set {0} = %s where guid = %d".format(prop)
        db["buttbot"].do_query(query, (value, self.guid))

    def insert_new_value(self, tab: str, row: str, val):
        query = "insert into {0} ('{1}', guid) values('%s', %d)".format(tab, row)
        self.do_query(query, (val, self.guid))

    def delete_value(self, tab: str, row: str, val):
        query = "delete from {0} where {1} = %s and guid = %d".format(tab, row)
        self.do_query(query, (val, self.guid))

    @property
    def name(self) -> str:
        return self.conf["guild_name"]

    @staticmethod
    @property
    def exists() -> bool:
        return True

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

    @property
    def max_sentence_length(self):
        return self.conf["wordreplacer_max_sentence_length"]

    @property
    def wordreplacer(self):
        return self.conf["wordreplacer"]


class Config(dict):
    def __init__(self):
        super().__init__()
        self.configs = {}
        self.load_config_for_startup()

    def __getattr__(self, attr):
        return self[attr]

    def load_config(self, guid: int):
        does_config_exist = db["buttbot"].do_query("select count(%s) as count", (guid,))[0]
        print(does_config_exist)
        if does_config_exist['count'] > 0:
            self.configs[guid] = ButtConfig(guid)
        else:
            # no
            self.create_config(guid)

    def create_config(self, guid: int):
        log.info("creating configuration for guild %d" % guid)
        db["buttbot"].do_insert("INSERT INTO config (wordreplacer,wordreplacer_max_sentence_length,"
                                "vacuum,command_call_freq,shitpost_call_freq,butt_response_emojis,rip,f, guid) "
                                "select wordreplacer,wordreplacer_max_sentence_length,vacuum,command_call_freq, "
                                "shitpost_call_freq,butt_response_emojis,rip,f, %s as guid "
                                "from config where guid = 101)", (guid,))
        self.configs[guid] = ButtConfig(guid)

    def load_config_for_startup(self):
        guids = db["buttbot"].do_query("select guid from config where 1")
        for g in guids:
            log.debug("found config for %d, building config" % g['guid'])
            self.configs[g['guid']] = ButtConfig(g['guid'])
