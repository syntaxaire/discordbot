import json
import re
import time
from random import *
from nltk.corpus import wordnet as wn


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
                return ", ".join(sorted(self.wlist, key=lambda s: s.lower()))


    def eval(self, message):
        if randint(1, 5) == 3:
            message = message.lower()
            try:
                for s in self.wlist:
                    if self.is_word_in_text(s, message) or self.is_word_in_text(s+'s',message):
                        # found it
                        # people want this to spew garbage so give the garbage to the people
                        if ('shitpost' not in self.used or time.time() - self.used['shitpost'] > self.timer):
                            self.used['shitpost'] = time.time()
                            for t in self.wlist:  # replace everything aaaaaaa
                                message = message.replace(t, 'butt')
                            return message
            except TypeError:
                self.wlist=self.load()


    def rspeval(self, message):
        if randint(1, 6) == 3:
            message = message.lower()
            if ('reverseshitpost' not in self.used or time.time() - self.used['reverseshitpost'] > self.timer):
                self.used['reverseshitpost'] = time.time()
                for t in self.wlist:  # replace everything aaaaaaa
                    message = message.replace('butt',self.wlist[randint(0,len(self.wlist)-1)],1)
                return message

    def wordclassifier(self,message):
        nouns = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}
        words=message.split(" ")
        _nouns=[]
        for w in words:
            if words in nouns:
                #replacement candidate
                _nouns.append(w)
        return _nouns

    def eval_sentence(self,message):
        nouns=self.wordclassifier(message)
        return message.replace('butt',nouns[randint(0,len(nouns))])