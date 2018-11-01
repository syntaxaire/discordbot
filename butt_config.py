import configparser


class ButtConfig:

    def __init__(self, conf):
        self.config_file_name = conf
        self.config_file = configparser.ConfigParser()
        self.config_file.read_file(open(conf))
        try:
            self.guild_guid = conf.split("/")[1][:-4]
        except IndexError:
            #we are loading a test config file, not a real one.
            self.guild_guid = conf[:-4]

    def get(self, section, key):
        # passthrough function for backwards compatibility
        return self.config_file.get(section, key)

    def getboolean(self, section, key):
        # passthrough function for backwards compatibility
        return self.config_file.getboolean(section, key)

    def _process_list_from_configparser(self, section, key):
        return self.get(section, key).split(",")

    def get_guild_guid(self):
        return self.guild_guid

    def get_plain_language_name(self):
        return self.get('discordbot', 'plain_language_name')

    def set_plain_language_name(self, pla):
        self.config_file.set('discordbot', 'plain_language_name', bool(pla))
        self.save_config()

    def get_all_allowed_bots(self):
        return self._process_list_from_configparser('discordbot', 'whitelisted_bots')

    def get_all_emojis(self):
        return self._process_list_from_configparser('discordbot', 'butt_response_emojis')

    def get_all_banned_users(self):
        return self._process_list_from_configparser('discordbot', 'always_ignore')

    def get_all_stop_phrases(self):
        return self._process_list_from_configparser('wordreplacer', 'stop_processing_phrases')

    def add_channel_to_allowed_channel_list(self, channel):
        if channel not in self.config_file.get("allowed_channels", "channels"):
            self.config_file.set("allowed_channels", "channels",
                                 "%s,%s" % (self.config_file.get("allowed_channels", "channels"), channel))
            self.save_config()

    def remove_channel_from_allowed_channel_list(self, channel):
        channels = self.config_file.get("allowed_channels", "channels").split(",")
        try:
            channels.remove(channel)
            self.config_file.set("allowed_channels", "channels", ",".join(channels))
            self.save_config()
        except ValueError:
            # channel provided not in list
            pass

    def save_config(self):
        with open(self.config_file_name, 'w') as fp:
            self.config_file.write(fp)

    def get_channel_name(self):
        return self.getboolean('discordbot', 'plain_language_name')

    def set_channel_name(self, name):
        self.config_file.set('discordbot', 'plain_language_name', name)
        self.save_config()

    def get_rip_setting(self):
        return self.getboolean('discordbot', 'rip')

    def set_rip_config(self, setting):
        self.config_file.set('discordbot', 'rip', bool(setting))
        self.save_config()

    def get_f_setting(self):
        return self.getboolean('discordbot', 'rip')

    def set_f_config(self, setting):
        self.config_file.set('discordbot', 'rip', bool(setting))
        self.save_config()

    def add_always_ignore(self, user_guid):
        if user_guid not in self.config_file.get("discordbot", "always_ignore"):
            self.config_file.set("discordbot", "always_ignore",
                                 "%s,%s" % (self.config_file.get("discordbot", "always_ignore"), user_guid))
            self.save_config()

    def remove_always_ignore(self, user_guid):
        users = self.config_file.get("discordbot", "always_ignore").split(",")
        try:
            users.remove(user_guid)
            self.config_file.set("discordbot", "always_ignore", ",".join(users))
            self.save_config()
        except ValueError:
            # user provided not in list
            pass

    def add_whitelisted_bots(self, user_guid):
        if user_guid not in self.config_file.get("discordbot", "whitelisted_bots"):
            self.config_file.set("discordbot", "whitelisted_bots",
                                 "%s,%s" % (self.config_file.get("discord_bot", "whitelisted_bots"), user_guid))
            self.save_config()

    def remove_whitelisted_bots(self, user_guid):
        users = self.config_file.get("discordbot", "whitelisted_bots").split(",")
        try:
            users.remove(user_guid)
            self.config_file.set("discordbot", "whitelisted_bots", ",".join(users))
            self.save_config()
        except ValueError:
            # user provided not in list
            pass
