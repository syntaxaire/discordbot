import json
import re
import time
from random import *

class WordReplacer:

    def is_word_in_text(self, word, text):
        pattern = r'(^|[^\w]){}([^\w]|$)'.format(word)
        pattern = re.compile(pattern, re.IGNORECASE)
        matches = re.search(pattern, text)
        return bool(matches)

    def __init__(self):
        self.wlist=self.load()
        self.used={}

    def config(self,timer):
        self.timer=timer


    def load(self):
        try:
            with open('wordlist.txt') as f:
                return json.load(f)
        except Exception:
            pass

    def addword(self,word):
        pass

    def save(self):
        with open('wordlist.txt', 'w') as f:
            json.dump(self.wlist, f, ensure_ascii=False)



    def buttword(self,command,arg):
        if command=='add':
            self.wlist.append(arg)
            self.save()
            return 'ok fine, '+arg

        if command=='remove':
            self.wlist.remove(arg)
            self.save()
            return 'ok fuck '+arg

        if command=='list':
            i = 1
            cmsg = ''

            if self.wlist is not None:
                for d in self.wlist:
                    if i != 1:
                        cmsg = cmsg + ', '
                    cmsg = cmsg + d
                    i = i + 1
                return cmsg


    def eval(self, message):
        if randint(1, 5) == 3:
            message = message.lower()
            print ('wordreplace::evaling shitpost')
            for s in self.wlist:
                print(s)
                if self.is_word_in_text(s, message) or self.is_word_in_text(s+'s',message):
                    print('wordreplace::word replacement found')
                    # found it
                    # people want this to spew garbage so give the garbage to the people
                    if ('shitpost' not in self.used or time.time() - self.used['shitpost'] > self.timer):
                        print('worldreplace::timer threshhold met')
                        self.used['shitpost'] = time.time()
                        for t in self.wlist:  # replace everything aaaaaaa
                            message = message.replace(t, 'butt')
                        return message

    def rspeval(self, message):
        print('reverseshitpost:: got it')
        if randint(1, 5) == 3:
            message = message.lower()
            print ('reverseshitpost::evaling shitpost')
            if ('reverseshitpost' not in self.used or time.time() - self.used['reverseshitpost'] > self.timer):
                print('reverseshitpost::timer threshhold met')
                self.used['reverseshitpost'] = time.time()
                for t in self.wlist:  # replace everything aaaaaaa
                    message = message.replace('butt',self.wlist[randint(0,len(self.wlist)-1)],1)
                return message


