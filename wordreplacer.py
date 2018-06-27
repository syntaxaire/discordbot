import json
import time
from random import *

import nltk
import nltk.data
import nltk.tag
from nltk.stem import WordNetLemmatizer

from butt_library import *


class WordReplacer:

    def __init__(self, timer, sentence_max_length, stat_module):
        self.stats = stat_module
        self.wlist = self.load()
        self.timer = timer
        self.used = {}
        self.set_max_sentence_length(sentence_max_length)
        self.command = {"nltk": 'wordreplacer'}

    def set_max_sentence_length(self, length):
        # DPT requested feature
        # a length of 0 will default to any word length.
        if length > 0:
            self.sentence_max_length = length
        else:
            self.sentence_max_length = 9999

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

    def tobuttornottobutt(self, messageobject, author):
        message = messageobject.content
        # code block detection.  We are going to skip processing the entire message.
        if detect_code_block(message) is not True:
            unedited_message = message
            if author == "Progress#6064" or author == "DPTBot#3069":
                stupidDPTshit = ['contracted the Death', 'just gained the achievement', 'just left the server',
                                 'just joined the server']
                if not any(v for v in stupidDPTshit if v in message) and not (
                        message.startswith("*") and message.endswith("*")):
                    # specific catch for DPT death message and other dumb stuff they have go to chat like cheevos

                    # this removes the character preamble for when Progress relays the chat message from in game.
                    # It is not sent to the word classifier to prevent a bunch of silly issues
                    tagged_sentence = self.wordtagger(strip_IRI(message.split(" ", 1)[1]))
                    nouns, targeted = self.findnounsbyprevioustag(tagged_sentence)
                else:
                    return

            else:
                tagged_sentence = self.wordtagger(strip_IRI(message))
                nouns, targeted = self.findnounsbyprevioustag(tagged_sentence)
            self.stats.message_store(messageobject.channel.id)
            try:
                print("------------------------------------------------------------------------------------")
                print("tagged sentence: %s" % self.wordtagger(message))
                print("sentence tag length: %s " % str(len(tagged_sentence)))
                print("-----------------------")
                print("prioritized: %s" % str(targeted))
                print("noun candidates: %s" % self.removestopwords(nouns))

                if targeted == True:
                    print("-------TARGETED--------")
                    print("non prioritized nouns: %s" % self._findnounsbyprevioustag(nouns, False))
                    print("-------IGNORE----------")
                print("nouns ignored: %s" % [n for n in self.wordclassifier(message, "butt") if n not in nouns])
                if not nouns == self.removestopwords(nouns):
                    # stopwords applied
                    print("-------STOPWORD--------")
                    print(
                        "nouns explicitly stopworded: %s " % [n for n in nouns if n not in self.removestopwords(nouns)])

                print("------DECISION TREE--------")
                arewebuttingthisshit = (True if len(nouns) > 1 or targeted == True and len(nouns) > 0 else False)
                print("Butt this sentence? %s" % arewebuttingthisshit)
                arewebuttinglength = (True if len(tagged_sentence) < 50 else "MAYBE (not DPT)")
                print("does it meet length? %s" % arewebuttinglength)
            except UnboundLocalError:
                pass
            try:
                nouns = self.removestopwords(nouns)
            except UnboundLocalError:
                # noun list is empty
                pass
            try:
                if self.checklengthofsentencetobutt(tagged_sentence):
                    # DPT feature.  default is 9999 but DPT wants it to be shorter for more impact.
                    if len(nouns) > 1 or (len(nouns) > 0 and targeted == True):
                        if randint(1, 5) == 3:
                            if 'shitpost' not in self.used or time.time() - self.used['shitpost'] > self.timer:
                                self.used['shitpost'] = time.time()
                                return self.pickwordtobutt(nouns, unedited_message, messageobject)
                            else:
                                self.stats.disposition_store(messageobject.server.id, messageobject.channel.id,
                                                             "Config Timeout", "Config Timeout")
                        else:
                            self.stats.disposition_store(messageobject.server.id, messageobject.channel.id,
                                                         "20% Threshold", "20% Threshold")
            except UnboundLocalError:
                # no tags
                self.stats.disposition_store(messageobject.server.id, messageobject.channel.id,
                                             "No Noun Tags", "No Noun Tags")

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
        tagstoskipword = ['TO']
        if prioritized == True:
            tagstocheck = wordtagstocheckprioritized
        else:
            tagstocheck = wordtagstochecknotprioritized

        for i in range(len(taggedsentence) - 1):  # *jiggling intensifies*
            if taggedsentence[i][1] in tagstocheck:
                try:
                    if taggedsentence[i + 1][1] in tagstoacceptasnouns:
                        # TODO: fix the verb catch
                        # this should catch <verb> <noun> <to> to hopefully catch stuff like "needs/NN to/TO be/VB"
                        nouns.append(taggedsentence[i + 1][0])
                except IndexError:
                    # end of the noun list so we don't really care.
                    pass

        return nouns

    def findnounsbyprevioustag(self, taggedsentence):
        wordtagstocheckprioritized = ['PRP$']  # posessive personal pronoun
        if any(t for t in taggedsentence if t[1] in wordtagstocheckprioritized):
            nouns = self._findnounsbyprevioustag(taggedsentence, True)
            targeted = True
            if len(nouns) == 0:
                # nothing returned from the prioritized check, run a non prioritized check
                nouns = self._findnounsbyprevioustag(taggedsentence, False)
                targeted = False
        else:
            nouns = self._findnounsbyprevioustag(taggedsentence, False)
            targeted = False
        return nouns, targeted

    def removestopwords(self, nouns):
        # list comprehension to remove words that shouldn't be included in the list
        badwords = ['gon', 'dont', 'lol', 'yeah', 'tho', 'lmao', 'yes']
        nouns = [var for var in nouns if var not in badwords]
        return [var for var in nouns if len(var) > 1]  # remove all single character everythings

    def checklengthofsentencetobutt(self, message):
        # DPT feature
        # we need a tagged sentence.
        if len(message) > self.sentence_max_length:
            return False
        else:
            return True

    def pickwordtobutt(self, nouns, unedited_message, messageobject):
        wordsthatarentfunny = ['beat', 'works', 'fucking', 'cares', 'portion', 'way', 'aoe', 'whole', 'uh', 'use',
                               'means', 'gonorrhea'] #actually, gonorrhea is a funny word
        notfunnyfound = False
        if any(t for t in nouns if t in wordsthatarentfunny):
            # one of the tagged words is in the not funny list
            # we're going to remove the unfunny words before picking one to use
            nouns = [var for var in nouns if var not in wordsthatarentfunny]
            notfunnyfound = True

        buttword = randint(0, len(nouns) - 1)  # this is the word we are replacing with butt.
        self.stats.disposition_store(messageobject.server.id, messageobject.channel.id, "Butt Replaced",
                                     # "%s%s" % (nouns[buttword], " (Unfunny=true)" if notfunnyfound else ""),
                                     "%s" % nouns[buttword],
                                     unedited_message)
        lemmatizer = WordNetLemmatizer()
        if lemmatizer.lemmatize(nouns[buttword]) is not nouns[buttword]:
            # the lemmatizer thinks that this is a plural
            return unedited_message.replace(nouns[buttword],
                                            self.buttinpropercase(nouns[buttword], 'butts'))
        else:
            return unedited_message.replace(nouns[buttword],
                                            self.buttinpropercase(nouns[buttword], 'butt'))
