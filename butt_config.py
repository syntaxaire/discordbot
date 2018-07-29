import configparser


class butt_config():

    def __init__(self, conf):
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
