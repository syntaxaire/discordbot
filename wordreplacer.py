import json
from random import *

import nltk
import nltk.data
import nltk.tag
from nltk.stem import WordNetLemmatizer

from butt_library import *


class WordReplacer:

    def __init__(self, config, stat_module, timer_module, test_environment):
        self.config = config
        self.timer_module = timer_module
        self.stats = stat_module
        self.wlist = self.load_word_list()
        self.set_max_sentence_length(int(self.config.get('wordreplacer', 'max_sentence_length')))
        self.command = {"nltk": 'wordreplacer'}
        self.test_environment = test_environment

    def set_max_sentence_length(self, length):
        # DPT requested feature
        # a length of 0 will default to any word length.
        if length > 0:
            self.sentence_max_length = length
        else:
            self.sentence_max_length = 9999

    def load_word_list(self):
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

    def rspeval(self, message):
        message = message.lower()
        if self.timer_module.check_timeout('rsp', 'shitpost'):
            for t in self.wlist:  # replace everything aaaaaaa
                message = message.replace('butt', self.wlist[randint(0, len(self.wlist) - 1)], 1)
            return message

    def wordtagger(self, message):
        return nltk.pos_tag(nltk.word_tokenize(message))

    def getwordweight(self, word, source_weight):
        # dummy for now
        return 100 * source_weight

    def isuseranallowedbot(self, author):
        if author in self.config.get_all_allowed_bots():
            return True
        else:
            return False

    def doesmessagecontainstopphrases(self, message):
        if not any(v for v in self.config.get_all_stop_phrases() if v in message) and \
                not (message.startswith("*") and message.endswith("*")):
            return False
        else:
            return True

    def performtexttobutt(self, messageobject):
        # we are going to manipulate this version of the message before sending it to the processing functions.
        # we remove stuff that we dont want to be processed (banned phrases, banned people, banned bots)
        message = messageobject.content

        if not detect_code_block(message):
            # passes code block test
            if not self.doesmessagecontainstopphrases(str(messageobject.content)):
                # message contains no stop phrases, let's proceed
                self.stats.message_store(messageobject.channel.id)
                if self.isuseranallowedbot(str(messageobject.author)):
                    # message sender is allowed bot, we should separate the first word out of the message since that
                    # is the user the bot is relaying for
                    tagged_sentence = self.wordtagger(strip_IRI(message.split(" ", 1)[1]))
                else:
                    tagged_sentence = self.wordtagger(strip_IRI(message))
                nouns=self.returnnounsfromallsources(tagged_sentence)

    def returnnounsfromallsources(self, tagged_sentence):
        prioritzed_sentence = self.doesmessagehaveprioritizedpartsofspeech(tagged_sentence)
        if prioritzed_sentence:
            prioritized_nouns = self._findweightednounsbyprevioustag(tagged_sentence, True)
        non_prioritized_nouns = self._findweightednounsbyprevioustag(tagged_sentence, False)
        combined_list=prioritized_nouns+non_prioritized_nouns
        print(self.pickrandomwordbyweight(combined_list))


    def pickrandomwordbyweight(self,word_list):
        total_sum_of_weights = self.sumallweights(word_list)
        randomweight = randrange(1,total_sum_of_weights)
        for i in word_list:
            randomweight=randomweight-i[1]
            if randomweight<=0:
                return i[0]

    def sumallweights(self,word_list):
        return sum(weight for words, weight in word_list)

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

            try:
                nouns = self.removestopwords(nouns)
            except UnboundLocalError:
                # noun list is empty
                pass
            else:
                try:
                    if self.checklengthofsentencetobutt(tagged_sentence):
                        # DPT feature.  default is 9999 but DPT wants it to be shorter for more impact.
                        if len(nouns) > 1 or (len(nouns) > 0 and targeted == True):
                            if randint(1, 5) == 3:
                                if self.timer_module.check_timeout('shitpost', 'shitpost'):
                                    new_sentence, replaced_with = self.pickwordtobutt(nouns, unedited_message,
                                                                                      messageobject)
                                    return self.replace_an_to_a_in_sentence(new_sentence, replaced_with)
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

    def _findweightednounsbyprevioustag(self, taggedsentence, prioritized):
        # we construct a list of nouns if the previously tagged word has a certain tag.
        # we prioritize possessive pronouns (his, her, my, etc)
        nouns = []
        wordtagstocheckprioritized = ['PRP$']
        wordtagstochecknotprioritized = ['DT', 'JJ', 'JJS', 'JJR', 'WP$', 'WP']
        tagstoacceptasnouns = ['NN', 'NNS']
        tagstoskipword = ['TO']
        wordsthatarenotadjectives = ['i']  # lower case i is tagged as a adjective for some reason
        if prioritized == True:
            tagstocheck = wordtagstocheckprioritized
            source_weight = 25.0
        else:
            tagstocheck = wordtagstochecknotprioritized
            source_weight = 1.0

        for i in range(len(taggedsentence) - 1):  # *jiggling intensifies*
            if taggedsentence[i][1] in tagstocheck:
                if taggedsentence[i][0] not in wordsthatarenotadjectives:  # fix some words getting tagged weird
                    try:
                        if taggedsentence[i + 1][1] in tagstoacceptasnouns:
                            #append weighted version of the word using source weight (prioritized vs non pri mode)
                            nouns.append((taggedsentence[i + 1][0], self.getwordweight(taggedsentence[i + 1][0],
                                                                                       source_weight)))
                    except IndexError:
                        # end of the noun list so we don't really care.
                        pass
        return nouns

    def doesmessagehaveprioritizedpartsofspeech(self, taggedsentence):
        wordtagstocheckprioritized = ['PRP$']  # posessive personal pronoun
        if any(t for t in taggedsentence if t[1] in wordtagstocheckprioritized):
            return True
        else:
            return False

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

    def replace_an_to_a_in_sentence(self, message, butt_word):
        message = message.split(" ")
        print(message)
        indexes = get_indexes(message, butt_word)
        if indexes:
            # we found one or more instances of butt, we need to check the list index i-1 of that butt word to see if we
            # need to replace an with a.
            for i in indexes:
                try:
                    if message[i - 1] == "an":
                        message[i - 1] = "a"
                except IndexError:
                    # could be possible but we don't care
                    pass
        return " ".join(message)

    def pickwordtobutt(self, nouns, unedited_message, messageobject):
        wordsthatarentfunny = ['beat', 'works', 'fucking', 'cares', 'portion', 'way', 'aoe', 'whole', 'uh', 'use',
                               'means', 'gonorrhea', 'self', 'bit', 'hour', 'minute', 'second', 'year', 'hours',
                               'minutes', 'seconds', 'years', 'lot', 'feel', 'feels', 'couple',
                               'some', 'cost', 'look', 'level', 'time']  # actually, gonorrhea is a funny word
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
                                            self.buttinpropercase(nouns[buttword], 'butts')), 'butts'
        else:
            return unedited_message.replace(nouns[buttword],
                                            self.buttinpropercase(nouns[buttword], 'butt')), 'butt'


"""
    def printdebugmessage(self):
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
"""
