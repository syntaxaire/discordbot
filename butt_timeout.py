import time


class Timeout:
    def __init__(self):
        # load the shitpost and command call frequencies out of the passed config.
        self.type = dict()
        self.timeout_storage_variable = {}

    def check_timeout(self, timeout_member_name: str, timeout_duration: int):
        """Checks timeout variable for specific action.  Returns True if the action is able to proceed and false if the
        action can't"""
        if timeout_member_name not in self.timeout_storage_variable or \
                time.time() > self.timeout_storage_variable[timeout_member_name]:
            self.timeout_storage_variable[timeout_member_name] = time.time() + timeout_duration
            return True
        else:
            return False
