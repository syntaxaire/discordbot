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

    def get_all_whitelisted_bots(self):
        return self.process_list_from_configparser('discordbot', 'whitelisted_bots')

    def get_all_emojis(self):
        return self.get('discordbot', 'butt_response_emojis').split(",")

    def process_list_from_configparser(self, section, key):
        return self.get(section, key).split(",")

    def get_all_blacklisted_users(self):
        return self.process_list_from_configparser('discordbot', 'always_ignore')
