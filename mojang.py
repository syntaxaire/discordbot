import urllib.request, json




def mojang_status():
    with urllib.request.urlopen("https://status.mojang.com/check") as url:
        data = json.loads(url.read().decode())
        #data=[{'minecraft.net': 'yellow'},{'session.minecraft.net': 'red'},{'account.mojang.com': 'red'},{'authserver.mojang.com': 'green'},{'sessionserver.mojang.com': 'green'},{'api.mojang.com': 'green'},{'textures.minecraft.net': 'green'},{'mojang.com': 'green'}]
        yellow=[]
        red=[]
        for service in data:
            for s,t in service.items():
                if t=="yellow":
                    yellow.append(s)
                elif t=="red":
                    red.append(s)
    return [red,yellow]



def mojang_status_requested():
    status=mojang_status()
    message=[]
    if status[0]:
        message.append("aw fuck, looks like %s %s broke (lol)" % (", ".join(status[0]), "are" if len(status[0]) > 1 else "is"))
    if status[1]:
            if status[0]:
                message.append("also %s could be having problems" % ", ".join(status[1]))
            else:
                message.append("looks like %s could be having problems" % ",".join(status[1]))
    if not status[0] and not status[1]:
        message.append("praise notch, it works")
    return message

def mojang_status_loop():
    pass

def mojang_user_to_uuid(username):
    with urllib.request.urlopen("https://api.mojang.com/users/profiles/minecraft/%s" % (username)) as url:
        data = json.loads(url.read().decode())
    return data['id']

def mojang_get_user_avatar(username):
    with urllib.request.urlopen("https://sessionserver.mojang.com/session/minecraft/profile/%s" % mojang_user_to_uuid(username)) as url:
        data = json.loads(url.read().decode())
        a=data['properties'][0]['value']
    return a

