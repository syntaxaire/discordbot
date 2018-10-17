import configparser


class butt_config():

    def __init__(self, conf):
        self.config_file_name = conf
        self.config_file = configparser.ConfigParser()
        self.config_file.read_file(open(conf))

    def get(self, section, key):
        # passthrough function for backwards compatibility
        return self.config_file.get(section, key)

    def getboolean(self, section, key):
        # passthrough function for backwards compatibility
        return self.config_file.getboolean(section, key)

    def _process_list_from_configparser(self, section, key):
        return self.get(section, key).split(",")

    def get_all_allowed_bots(self):
        return self._process_list_from_configparser('discordbot', 'whitelisted_bots')

    def get_all_emojis(self):
        return self._process_list_from_configparser('discordbot', 'butt_response_emojis')

    def get_all_banned_users(self):
        return self._process_list_from_configparser('discordbot', 'always_ignore')

    def get_all_stop_phrases(self):
        return self._process_list_from_configparser('wordreplacer', 'stop_processing_phrases')

    def add_channel_to_allowed_channel_list(self, channel):
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
            #channel provided not in list
            pass

    def save_config(self):
        with open(self.config_file_name, 'w') as fp:
            self.config_file.write(fp)
