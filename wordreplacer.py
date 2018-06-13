import json
import time
from random import *

import nltk
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

    def toButtOrNotToButt(self, message, author):
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
                nouns = self.findNounsBySecondaryTag(self.wordtagger(strip_IRI(message)))
            # list comprehension to remove words that shouldn't be included in the list
            badwords = ['i', 'gon', 'beat', 'dont', 'lol', 'yeah', 'tho']

            nouns = [var for var in nouns if var not in badwords]

            if randint(3, 3) == 3: #TODO: fix for prod
                if 'shitpost' not in self.used or time.time() - self.used['shitpost'] > self.timer:
                    self.used['shitpost'] = time.time()
                    lemmatizer = WordNetLemmatizer()
                    buttword = randint(0, len(nouns) - 1)  # this is the word we are replacing with butt.
                    if lemmatizer.lemmatize(nouns[buttword]) is not nouns[buttword]:
                        # the lemmatizer thinks that this is a plural
                        return unedited_message.replace(nouns[buttword],
                                                        self.buttInProperCase(nouns[buttword], 'butts'))
                    else:
                        return unedited_message.replace(nouns[buttword],
                                                        self.buttInProperCase(nouns[buttword], 'butt'))

    def buttInProperCase(self, wordToButt, buttToReplace):
        if wordToButt.istitle():
            return buttToReplace.title()
        elif wordToButt.isupper():
            return buttToReplace.upper()
        else:
            return buttToReplace

    def findNounsBySecondaryTag(self, taggedSentence):
        # we are going to look for a few speech patterns:
        # (the) noun
        index = 0
        nounList = []
        for a in taggedSentence:
            try:
                nextWord = taggedSentence[index + 1]
            except IndexError:
                # nextword is empty, dont give a crap about this
                nextWord = None
            wordTagsToCheckPrioritize = ['PRP','PRP$']
            wordTagsToCheckForNoun = ['DT', 'JJ', 'JJS', 'JJR', 'CD']
            wordsThatMayBeMispelled = ['teh']
            tagsToAcceptAsNouns = ['NN', 'NNS']
            if a[1] in wordTagsToCheckForNoun or a[0] in wordsThatMayBeMispelled:
                # we want to check adjectives and determiners
                try:
                    if nextWord[1] in tagsToAcceptAsNouns:
                        # word has a noun tag
                        nounList.append(nextWord[0])
                except TypeError:
                    # tag is empty for this word
                    pass

            index += 1
        print("new tag: %s" % nounList)
        return nounList

    def buttWord(self,word):
        pass

    def wordReplacer(self,word):
        pass