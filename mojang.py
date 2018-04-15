import json
import urllib.request


class mojang:

    def __init__(self):
        self.command=['mojang',]

    def do_mojang(self):
        msg = self.mojang_status_requested()
        for t in msg:
            return t

    def commands(self):
        return self.command()

    def mojang_status(self):
        with urllib.request.urlopen("https://status.mojang.com/check") as url:
            data = json.loads(url.read().decode())
            yellow = []
            red = []
            for service in data:
                for s, t in service.items():
                    if t == "yellow":
                        yellow.append(s)
                    elif t == "red":
                        red.append(s)
        return [red, yellow]


    def mojang_status_requested(self):
        status = self.mojang_status()
        message = []
        if status[0]:
            message.append(
                "aw fuck, looks like %s %s broke (lol)" % (", ".join(status[0]), "are" if len(status[0]) > 1 else "is"))
        if status[1]:
            if status[0]:
                message.append("also %s could be having problems" % ", ".join(status[1]))
            else:
                message.append("looks like %s could be having problems" % ",".join(status[1]))
        if not status[0] and not status[1]:
            message.append("praise notch, it works")
        return message


    def mojang_status_loop(self):
        #todo: probably should finish this
        pass


    def mojang_user_to_uuid(self,username):
        with urllib.request.urlopen("https://api.mojang.com/users/profiles/minecraft/%s" % username) as url:
            data = json.loads(url.read().decode())
        return data['id']


    def mojang_get_user_avatar(self,username):
        with urllib.request.urlopen(
                "https://sessionserver.mojang.com/session/minecraft/profile/%s" % mojang_user_to_uuid(username)) as url:
            data = json.loads(url.read().decode())
        return data['properties'][0]['value']
