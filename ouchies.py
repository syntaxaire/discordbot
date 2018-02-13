import json


class Oww:

    def load(self):
        self.player={}
        try:
            with open('ouchies.txt') as f:
                return json.load(f)
        except Exception:
                pass

    def __init__(self):
        self.player=self.load()



    def save(self):
        with open('ouchies.txt', 'w') as f:
            json.dump(self.player, f, ensure_ascii=False)


    def top10deaths(self):
        deathlist={}

        #unpack each person's death count.
        for key,items in self.player.items():
            totaldeaths=0
            for k,i in items.items():
                totaldeaths=totaldeaths+i

            deathlist[key]=totaldeaths

        #sort this shit
        return self.sort10(deathlist)

    def top10reasons(self):
        reasonlist = {}

        # unpack each person's death count.
        for key, items in self.player.items():
            #this time though we are going to count death reasons up, ignoring the person

            for k, i in items.items():
                if k not in reasonlist:
                    reasonlist[k]=0
                reasonlist[k] = reasonlist[k] + i
        return self.sort10(reasonlist)




    def profile(self,player):
        reasonlist={}
        try:
            person=self.player[player]
            for k, i in person.items():
                if k not in reasonlist:
                    reasonlist[k]=0
                reasonlist[k] = reasonlist[k] + i

            return(self.sortunlimited(reasonlist))
        except KeyError:
            return("No deaths recorded")

    def sortunlimited(self,reasonlist):
        i = 1
        cmsg = ''
        for d in sorted(reasonlist.items(), key=lambda x: x[1], reverse=True):
            if i != 1:
                cmsg = cmsg + ', '
            cmsg = cmsg + d[0] + '(' + str(d[1]) + ')'
            i = i + 1
        return cmsg

    def sort10(self,reasonlist):
        i = 1
        cmsg = ''
        for d in sorted(reasonlist.items(), key=lambda x: x[1], reverse=True):
            if i == 11:
                break
            else:
                if i != 1:
                    cmsg = cmsg + ', '
                cmsg = cmsg + d[0] + '(' + str(d[1]) + ')'
                i = i + 1
        return cmsg


    def record(self, message):
        m = message.split()
        if m[1] not in self.player:
            self.player[m[1]] = {}

        #now i need to combine the death reason into a string, which will be words in positions 2-n of the death message 'm'
        dmsg=''
        for i in m[2:]:
            dmsg=dmsg+" "+i
        dmsg=dmsg.strip()
        if dmsg not in self.player[m[1]]:
            self.player[m[1]][dmsg] = 0
        self.player[m[1]][dmsg] = self.player[m[1]][dmsg] + 1

        self.save()
