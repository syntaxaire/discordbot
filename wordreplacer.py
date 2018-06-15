import json
import time
from random import *

import nltk
import nltk.tag, nltk.data
from nltk.corpus import brown
from nltk.stem import WordNetLemmatizer

from butt_library import *


class WordReplacer:

    def __init__(self, timer):
        self.wlist = self.load()
        self.timer = timer
        self.used = {}
        self.command = {"nltk": 'wordreplacer'}

    def load(self):
        try:
            with open('wordlist.txt') as f:
                return json.load(f)
        except Exception:
            pass

    def return_commands(self):
        return self.command

    ################################################################################
    #                               commands                                       #
    ################################################################################
    def do_nltk(self, message):
        return self.wordtagger(message)

    ################################################################################
    #                               end commands                                   #
    ################################################################################

    def save(self):
        with open('wordlist.txt', 'w') as f:
            json.dump(self.wlist, f, ensure_ascii=False)

    def eval(self, message):
        if randint(1, 5) == 3:
            message = message.lower()
            try:
                for s in self.wlist:
                    if is_word_in_text(s, message) or is_word_in_text(s + 's', message):
                        # found it
                        # people want this to spew garbage so give the garbage to the people
                        if 'shitpost' not in self.used or time.time() - self.used['shitpost'] > self.timer:
                            self.used['shitpost'] = time.time()
                            for t in self.wlist:  # replace everything aaaaaaa
                                message = message.replace(t, 'butt')
                            return message
            except TypeError:
                self.wlist = self.load()

    def rspeval(self, message):
        message = message.lower()
        if 'reverseshitpost' not in self.used or time.time() - self.used['reverseshitpost'] > self.timer:
            self.used['reverseshitpost'] = time.time()
            for t in self.wlist:  # replace everything aaaaaaa
                message = message.replace('butt', self.wlist[randint(0, len(self.wlist) - 1)], 1)
            return message

    def wordtagger(self, message):
        return nltk.pos_tag(nltk.word_tokenize(message))


    def wordclassifier(self, message, author):
        nouns = []
        # function to test if something is a noun
        # do the nlp stuff
        li = self.wordtagger(message)
        for w in li:
            if w[0] == "<" or w[0] == ">":
                # ignore this punctuation because for some reason NLTK doesnt always
                pass
            else:
                if w[1] == "NN" or w[1] == "NNP" or w[1] == "NOUN" or w[1] == "NNSP":
                    # NLTK categorized the word as either a noun or proper noun
                    nouns.append(w[0])
        return nouns

    def tobuttornottobutt(self, message, author):
        # code block detection.  We are going to skip processing the entire message.
        if detect_code_block(message) is not True:
            unedited_message = message
            if author == "Progress#6064":
                # this removes the character preamble for when Progress relays the chat message from in game.
                # It is not sent to the word classifier to prevent a bunch of silly issues
                nouns = self.wordclassifier(strip_IRI(message.split(" ", 1)[1]), author)
            else:
                print(":::new sentence: %s" % self.wordtagger(message))
                nouns2 = self.wordclassifier(strip_IRI(message), author)
                print("old tag: %s" % nouns2)
                nouns = self.findnounsbyprevioustag(self.wordtagger(strip_IRI(message)))
                print("new tag: %s" % nouns)
            # list comprehension to remove words that shouldn't be included in the list
            badwords = ['i', 'gon', 'beat', 'dont', 'lol', 'yeah', 'tho']
            nouns = [var for var in nouns if var not in badwords]

            if len(nouns) > 0:
                if randint(1, 5) == 3:
                    if 'shitpost' not in self.used or time.time() - self.used['shitpost'] > self.timer:
                        self.used['shitpost'] = time.time()
                        lemmatizer = WordNetLemmatizer()
                        buttword = randint(0, len(nouns) - 1)  # this is the word we are replacing with butt.
                        if lemmatizer.lemmatize(nouns[buttword]) is not nouns[buttword]:
                            # the lemmatizer thinks that this is a plural
                            return unedited_message.replace(nouns[buttword],
                                                            self.buttinpropercase(nouns[buttword], 'butts'))
                        else:
                            return unedited_message.replace(nouns[buttword],
                                                            self.buttinpropercase(nouns[buttword], 'butt'))

    def buttinpropercase(self, wordtobutt, buttoreplace):
        if wordtobutt.istitle():
            return buttoreplace.title()
        elif wordtobutt.isupper():
            return buttoreplace.upper()
        else:
            return buttoreplace

    def _findnounsbyprevioustag(self, taggedsentence, prioritized):
        # we construct a list of nouns if the previously tagged word has a certain tag.
        # we prioritize possessive pronouns (his, her, my, etc)
        nouns = []
        wordtagstocheckprioritized = ['PRP$']
        wordtagstochecknotprioritized = ['DT', 'JJ', 'JJS', 'JJR', 'CD']
        tagstoacceptasnouns = ['NN', 'NNS']
        if prioritized == True:
            tagstocheck = wordtagstocheckprioritized
        else:
            tagstocheck = wordtagstochecknotprioritized

        for i in range(len(taggedsentence) - 1):  # *jiggling intensifies*
            if taggedsentence[i][1] in tagstocheck:
                if taggedsentence[i + 1][1] in tagstoacceptasnouns:
                    nouns.append(taggedsentence[i + 1][0])

        return nouns

    def findnounsbyprevioustag(self, taggedsentence):
        wordtagstocheckprioritized = ['PRP$']  # posessive personal pronoun

        if any(t for t in taggedsentence if t[1] in wordtagstocheckprioritized):
            nouns = self._findnounsbyprevioustag(taggedsentence, True)
            if len(nouns) == 0:
                # nothing returned from the prioritized check, run a non prioritized check
                nouns = self._findnounsbyprevioustag(taggedsentence, False)
        else:
            nouns = self._findnounsbyprevioustag(taggedsentence, False)
        return nouns

