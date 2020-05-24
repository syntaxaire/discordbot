import base64
import json
import logging
import urllib.request

from PIL import Image

log = logging.getLogger('bot.' + __name__)


class Mojang:

    def __init__(self):
        self.command = {'mojang': 'mojang'}

    ################################################################################
    #                               commands                                       #
    ################################################################################

    def do_mojang(self, message):
        msg = self.mojang_status_requested()
        for t in msg:
            return t

    ################################################################################
    #                               end commands                                   #
    ################################################################################

    def return_commands(self):
        return self.command

    @staticmethod
    def mojang_status():
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
        # todo: probably should finish this
        pass

    @staticmethod
    def mojang_user_to_uuid(username):
        with urllib.request.urlopen("https://api.mojang.com/users/profiles/minecraft/%s" % username) as url:
            data = json.loads(url.read().decode())
        return data['id']

    def mojang_get_user_avatar(self, username):
        uuid = self.mojang_user_to_uuid(username)
        payload = base64.decode(self._get_avatar_payload(uuid), )

    @staticmethod
    def _get_avatar_payload(uuid: int):
        with urllib.request.urlopen("https://sessionserver.mojang.com/session/minecraft/profile/%s" % uuid) as url:
            data = json.loads(url.read().decode())
        return data['properties'][0]['textures']

    @staticmethod
    def get_face_from_skin(skin: Image) -> Image:
        """Return the portion of a Minecraft skin that represents the face."""
        face_zone = (8, 8, 16, 16)
        return skin.crop(face_zone)
