import json
import re
import time
from random import *
import nltk
from nltk.stem import WordNetLemmatizer


class WordReplacer:

    def is_word_in_text(self, word, text):
        pattern = r'(^|[^\w]){}([^\w]|$)'.format(word)
        pattern = re.compile(pattern, re.IGNORECASE)
        matches = re.search(pattern, text)
        return bool(matches)

    def __init__(self):
        self.wlist = self.load()
        self.used = {}
        # NLTK test
        # self.nouns=set()
        # self.nouns = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}

    def config(self, timer):
        self.timer = timer

    def load(self):
        try:
            with open('wordlist.txt') as f:
                return json.load(f)
        except Exception:
            pass

    def addword(self, word):
        pass

    def save(self):
        with open('wordlist.txt', 'w') as f:
            json.dump(self.wlist, f, ensure_ascii=False)

    def buttword(self, command, arg):
        if command == 'add':
            self.wlist.append(arg)
            self.save()
            return 'ok fine, ' + arg

        if command == 'remove':
            self.wlist.remove(arg)
            self.save()
            return 'ok fuck ' + arg

        if command == 'list':
            return ", ".join(sorted(self.wlist, key=lambda s: s.lower()))

    def eval(self, message):
        if randint(1, 5) == 3:
            message = message.lower()
            try:
                for s in self.wlist:
                    if self.is_word_in_text(s, message) or self.is_word_in_text(s + 's', message):
                        # found it
                        # people want this to spew garbage so give the garbage to the people
                        if ('shitpost' not in self.used or time.time() - self.used['shitpost'] > self.timer):
                            self.used['shitpost'] = time.time()
                            for t in self.wlist:  # replace everything aaaaaaa
                                message = message.replace(t, 'butt')
                            return message
            except TypeError:
                self.wlist = self.load()

    def rspeval(self, message):
        if randint(1, 6) == 3:
            message = message.lower()
            if ('reverseshitpost' not in self.used or time.time() - self.used['reverseshitpost'] > self.timer):
                self.used['reverseshitpost'] = time.time()
                for t in self.wlist:  # replace everything aaaaaaa
                    message = message.replace('butt', self.wlist[randint(0, len(self.wlist) - 1)], 1)
                    # NLTK test
                    # message = message.replace('butt', sample(self.nouns,1)[0].replace('_'," "), 1)
                return message

    def wordclassifier(self, message, author):
        nouns = []
        # function to test if something is a noun
        # do the nlp stuff
        li = nltk.pos_tag(nltk.word_tokenize(message))

        for w in li:
            if w[0] == "<" or w[0] == ">":
                # ignore this punctuation because for some reason NLTK doesnt always
                pass
            else:
                if w[1] == "NN" or w[1] == "NNP" or w[1] == "NOUN" or w[1] == "NNSP":
                    # NLTK categorized the word as either a noun or proper noun
                    nouns.append(w[0])
        return nouns

    def eval_sentence_nltk(self, message, author):
        if author == "Progress#6064":
            # this removes the character preamble for when Progress relays the chat message from in game.
            # It is not sent to the word classifier to prevent a bunch of silly issues like
            message = message.split(" ", 1)[1]

        nouns = self.wordclassifier(message, author)
        #list comprehension to remove words that shouldn't be included in the list
        badwords=['i']

        nouns=[var for var in nouns if var not in badwords]

        if len(nouns) > 1:
            lemmatizer = WordNetLemmatizer()
            buttword = randint(0, len(nouns))  # this is the word we are replacing with butt.
            if randint(1, 5) == 3:
                if ('shitpost' not in self.used or time.time() - self.used['shitpost'] > self.timer):
                    self.used['shitpost'] = time.time()
                if lemmatizer.lemmatize(nouns[buttword]) is not nouns[buttword]:
                    # the lemmatizer thinks that this is a plural
                    return message.replace(nouns[buttword], 'butts')
                else:
                    return message.replace(nouns[buttword], 'butt')
