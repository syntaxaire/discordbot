import json


class Oww:

    def load(self):
        with open('ouchies.txt') as f:
            return json.load(f)

    def __init__(self):
        self.dt=self.load()

    def save(self):
        with open('ouchies.txt', 'w') as f:
            json.dump(self.dt, f, ensure_ascii=False)

    def msg(self):
        i=1
        cmsg=''
        for d in sorted(self.dt.items(), key=lambda x: x[1],reverse=True):
            if i==10:
                break
            else:
                if i!=1 and i!=9:
                    cmsg=cmsg+ ', '
                cmsg=cmsg + d[0] + '('+str(d[1])+')'
                i=i+1
        return cmsg

    def record(self, message):
        m = message.partition(' ')
        if m[0] not in self.dt:
            self.dt[m[0]] = 0
        self.dt[m[0]] = self.dt[m[0]] + 1
        self.save()
