import json


class Oww:

    def load(self):
        self.dt={}
        try:
            with open('ouchies.txt') as f:
                return json.load(f)
        except Exception:
                pass


    def __init__(self):
        self.dt=self.load()


    def save(self):
        with open('ouchies.txt', 'w') as f:
            json.dump(self.dt, f, ensure_ascii=False)


    def msg(self):
        i=1
        cmsg=''
        if self.dt.items is not None:
            for d in sorted(self.dt.items(), key=lambda x: x[1],reverse=True):
                if i==11:
                    break
                else:
                    if i!=1:
                        cmsg=cmsg+ ', '
                    cmsg=cmsg + d[0] + '('+str(d[1])+')'
                    i=i+1
            return cmsg


    def record(self, message):
        m = message.split()
        if m[1] not in self.dt:
            self.dt[m[1]] = 0
        self.dt[m[1]] = self.dt[m[1]] + 1
        self.save()
