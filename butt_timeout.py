import time


class Timeout:
    def __init__(self, config):
        # load the shitpost and command call frequencies out of the passed config.
        self.config = config
        self.type = dict()
        self.type['shitpost'] = int(self.config.get('discordbot', 'shitpost_call_freq'))
        self.type['command'] = int(self.config.get('discordbot', 'command_call_freq'))
        self.timeout_storage_variable = {}

    def check_timeout(self, timeout_member_name, timeout_type):
        """Checks timeout variable for specific action.  Returns True if the action is able to proceed and false if the
        action can't"""
        self._check_timeout_type(timeout_type)
        if timeout_member_name not in self.timeout_storage_variable or \
                time.time() - self.timeout_storage_variable[timeout_member_name] > self.type[timeout_type]:
            self.timeout_storage_variable[timeout_member_name] = time.time()
            return True
        else:
            return False

    @staticmethod
    def _check_timeout_type(timeout_type):
        # make sure the timeout_type sent to the object is useful.
        if not (timeout_type == "shitpost" or timeout_type == "command"):
            raise ValueError("Timeout type was not shitpost or command.")
