import configparser
import butt_library
from shutil import copyfile


class ButtConfig:

    def __init__(self, conf: str):
        self.config_file_name = conf
        self.config_file = configparser.ConfigParser()
        self.config_file.read_file(open(conf))
        try:
            self.guild_guid = conf.split("/")[1][:-4]
        except IndexError:
            # we are loading a test config file, not a real one.
            self.guild_guid = conf[:-4]

    def get(self, section: str, key: str):
        # passthrough function for backwards compatibility
        return self.config_file.get(section, key)

    def getboolean(self, section: str, key: str) -> bool:
        # passthrough function for backwards compatibility
        return self.config_file.getboolean(section, key)

    def _process_list_from_configparser(self, section: str, key: str, return_type="string") -> list:
        # discord.py 1.2.4 makes guid type integer, we need to know now what type to avoid issues
        if return_type == "integer":
            return [int(i) for i in self.get(section, key).split(",") if i]
        else:
            return [str(i) for i in self.get(section, key).split(",") if i]

    @property
    def guid(self):
        return str(self.guild_guid)

    @property
    def name(self) -> str:
        return self.get('discordbot', 'plain_language_name')

    @name.setter
    def name(self, pla: str):
        self.config_file.set('discordbot', 'plain_language_name', str(pla))
        self.save_config()

    @property
    def db(self) -> str:
        return self._process_list_from_configparser('vacuum', 'database')[0]

    @property
    def allowed_bots(self) -> list:
        return self._process_list_from_configparser('discordbot', 'whitelisted_bots')

    @property
    def allowed_channels(self) -> list:
        return self._process_list_from_configparser('allowed_channels', 'channels', "integer")

    @property
    def emojis(self) -> list:
        return self._process_list_from_configparser('discordbot', 'butt_response_emojis')

    @property
    def banned_users(self) -> list:
        return self._process_list_from_configparser('discordbot', 'always_ignore')

    @property
    def stop_phrases(self) -> list:
        return self._process_list_from_configparser('wordreplacer', 'stop_processing_phrases')

    def add_channel_to_allowed_channel_list(self, channel: int):
        # channel comes as an integer in discord.py 1.2.4, let's cast
        channel = str(channel)
        if channel not in self.config_file.get("allowed_channels", "channels"):
            self.config_file.set("allowed_channels", "channels",
                                 "%s,%s" % (self.config_file.get("allowed_channels", "channels"), channel))
            self.save_config()

    def remove_channel_from_allowed_channel_list(self, channel: int):
        # channel comes as an integer in discord.py 1.2.4, let's cast
        channel = str(channel)
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

    @property
    def rip(self) -> bool:
        return self.getboolean('discordbot', 'rip')

    @rip.setter
    def rip(self, setting):
        self.config_file.set('discordbot', 'rip', bool(setting))
        self.save_config()

    @property
    def f(self) -> bool:
        return self.getboolean('discordbot', 'rip')

    @f.setter
    def f(self, setting: bool):
        self.config_file.set('discordbot', 'rip', bool(setting))
        self.save_config()

    def add_always_ignore(self, user_guid: int):
        # guid comes as an integer in discord.py 1.2.4, let's cast
        user_guid = str(user_guid)
        if user_guid not in self.config_file.get("discordbot", "always_ignore"):
            self.config_file.set("discordbot", "always_ignore",
                                 "%s,%s" % (self.config_file.get("discordbot", "always_ignore"), user_guid))
            self.save_config()

    def remove_always_ignore(self, user_guid: int):
        # guid comes as an integer in discord.py 1.2.4, let's cast
        user_guid = str(user_guid)
        users = self.config_file.get("discordbot", "always_ignore").split(",")
        try:
            users.remove(user_guid)
            self.config_file.set("discordbot", "always_ignore", ",".join(users))
            self.save_config()
        except ValueError:
            # user provided not in list
            pass

    def add_whitelisted_bots(self, user_guid: int):
        # guid comes as an integer in discord.py 1.2.4, let's cast
        user_guid = str(user_guid)
        if user_guid not in self.config_file.get("discordbot", "whitelisted_bots"):
            self.config_file.set("discordbot", "whitelisted_bots",
                                 "%s,%s" % (self.config_file.get("discordbot", "whitelisted_bots"), user_guid))
            self.save_config()

    def remove_whitelisted_bots(self, user_guid: int):
        # guid comes as an integer in discord.py 1.2.4, let's cast
        user_guid = str(user_guid)
        users = self.config_file.get("discordbot", "whitelisted_bots").split(",")
        try:
            users.remove(user_guid)
            self.config_file.set("discordbot", "whitelisted_bots", ",".join(users))
            self.save_config()
        except ValueError:
            # user provided not in list
            pass


class Config:

    def __init__(self):
        self.loaded_configs = {}
        channel_configs = butt_library.load_all_config_files()
        for i in channel_configs:
            self.loaded_configs[int(i.split("/")[1][:-4])] = ButtConfig(i)

    def config(self, guid: int) -> ButtConfig:
        try:
            return self.loaded_configs[guid]
        except ValueError:
            # not currently loaded, let's return it
            self.create_config(guid)
            self.loaded_configs[guid] = ButtConfig("config/%d.ini" % guid)
            return self.loaded_configs[guid]

    @staticmethod
    def create_config(guid: int):
        copyfile("config/_config_template", "config/%d.ini" % guid)
