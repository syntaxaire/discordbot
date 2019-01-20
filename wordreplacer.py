import json
from random import *

import nltk
import nltk.data
import nltk.tag
from nltk.stem import WordNetLemmatizer

from butt_library import *


class WordReplacer:

    def __init__(self, config, stat_module, timer_module, phrase_weights, test_environment):
        self.config = config
        self.timer_module = timer_module
        self.stats = stat_module
        self.wlist = self.load_word_list()
        self.set_max_sentence_length(int(self.config.get('wordreplacer', 'max_sentence_length')))
        self.command = {"nltk": 'wordreplacer'}
        self.test_environment = test_environment
        self.phraseweights = phrase_weights

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
        for t in self.wlist:  # replace everything aaaaaaa
            message = message.replace('butt', self.wlist[randint(0, len(self.wlist) - 1)], 1)
        return message

    def wordtagger(self, message):
        return nltk.pos_tag(nltk.word_tokenize(message))

    def get_phrase_weight(self, phrase):
        return self.phraseweights.return_weight(phrase)

    def is_user_an_allowed_bot(self, author):
        if author in self.config.get_all_allowed_bots():
            return True
        else:
            return False

    def does_message_contain_stop_phrases(self, message):
        if not any(v for v in self.config.get_all_stop_phrases() if v in message) and \
                not (message.startswith("*") and message.endswith("*")):
            return False
        else:
            return True

    def simulate_perform_text_to_butt(self, messageobject):
        return self.perform_text_to_butt(messageobject)

    def do_butting_raw_sentence(self, sentence):
        tagged_sentence = self.wordtagger(sentence)
        pri_nouns, non_pri_nouns = self.return_phrases_from_all_sources(tagged_sentence)
        return self.do_butting(pri_nouns, non_pri_nouns, sentence, None, self.wordtagger(sentence))

    def perform_text_to_butt(self, messageobject):
        # we are going to manipulate this version of the message before sending it to the processing functions.
        # we remove stuff that we dont want to be processed (banned phrases, banned people, banned bots)
        # message = messageobject.content.replace("'", '')  #TODO: make this better
        message = messageobject.content  # actually that made it worse
        unedited_message = messageobject.content
        if not detect_code_block(message):
            # passes code block test
            if not self.does_message_contain_stop_phrases(str(messageobject.content)):
                # message contains no stop phrases, let's proceed
                self.stats.message_store(messageobject.channel.id)
                if self.is_user_an_allowed_bot(messageobject.author.id):
                    # message sender is allowed bot, we should separate the first word out of the message since that
                    # is the user the bot is relaying for
                    tagged_sentence = self.wordtagger(strip_IRI(message.split(" ", 1)[1]))
                else:
                    tagged_sentence = self.wordtagger(strip_IRI(message))
                if self.check_length_of_sentence_to_butt(tagged_sentence):
                    pri_nouns, non_pri_nouns = self.return_phrases_from_all_sources(tagged_sentence)
                    if len(pri_nouns) + len(non_pri_nouns) > 0:
                        if len(non_pri_nouns) == 1 and len(pri_nouns) == 0:
                            # catch specific case for 1 non prioritized noun and 0 prioritized nouns
                            if non_pri_nouns[0][2] <= 501:
                                # dont send anything, this word probably sucks
                                return
                        if self.test_environment:
                            # always reply in test environment
                            rv = [1, 1, 1]
                        else:
                            rv = [1, 5, 3]
                        if randint(rv[0], rv[1]) == rv[2]:
                            if self.timer_module.check_timeout('shitpost', 'shitpost'):
                                return self.do_butting(pri_nouns, non_pri_nouns, unedited_message, messageobject,
                                                       tagged_sentence)
                            else:
                                # timeout fail
                                pass
                        else:
                            # 20% chance fail
                            pass
                    else:
                        # not enough nouns
                        pass
                else:
                    # failed length check
                    pass

    def return_phrases_from_all_sources(self, tagged_sentence):
        prioritzed_sentence = self.does_message_have_prioritized_parts_of_speech(tagged_sentence)
        prioritized_nouns = []
        if prioritzed_sentence:
            prioritized_nouns = self._find_weighted_nouns_by_previous_tag(tagged_sentence, True)
        non_prioritized_nouns = self._find_weighted_nouns_by_previous_tag(tagged_sentence, False)
        return prioritized_nouns, non_prioritized_nouns

    def pick_phrase(self, pri_nouns, non_pri_nouns):
        combined_list = pri_nouns + non_pri_nouns
        return self.pick_random_phrase_by_weight(combined_list)

    def print_debug_message(self, message, pri_nouns, nouns, selected):
        if selected is not None:
            print("__________________________________________")
            print(message)
            print("prioritzed nouns: %s" % pri_nouns)
            print("nouns: %s" % nouns)
            print("noun selected: %s" % str(selected))
            print("__________________________________________")
            print("")

    def pick_random_phrase_by_weight(self, word_list):
        total_sum_of_weights = self.sum_all_weights(word_list)
        try:
            randomweight = randrange(1, total_sum_of_weights)
            for i in word_list:
                randomweight = randomweight - i[2]
                if randomweight <= 0:
                    return tuple((i[0], i[1]))
        except ValueError:
            # no words to pick
            return None

    def sum_all_weights(self, word_list):
        return sum(weight for prefix, noun, weight in word_list)

    def butt_in_proper_case(self, wordtobutt, buttoreplace):
        if wordtobutt.istitle():
            return buttoreplace.title()
        elif wordtobutt.isupper():
            return buttoreplace.upper()
        else:
            return buttoreplace

    def _find_weighted_nouns_by_previous_tag(self, taggedsentence, prioritized):
        # we construct a list of nouns if the previously tagged word has a certain tag.
        # we prioritize possessive pronouns (his, her, my, etc)
        nouns = []
        wordtagstocheckprioritized = ['PRP$']
        wordtagstochecknotprioritized = ['DT', 'JJ', 'JJS', 'JJR', 'WP$', 'WP']
        tagstoacceptasnouns = ['NN', 'NNS']
        tagstoskipword = ['TO']
        wordsthatarenotadjectives = ['i', 'kevin', 'armour', 'mic']  # lower case i is tagged as a adjective for some reason
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
                            # append weighted version of the word using source weight (prioritized vs non pri mode)
                            if self.word_passes_stop_word_check(taggedsentence[i + 1][0]):
                                nouns.append((taggedsentence[i][0], taggedsentence[i + 1][0], self.get_phrase_weight(
                                    "%s %s" % (taggedsentence[i][0], taggedsentence[i + 1][0])) * source_weight))
                    except IndexError:
                        # end of the noun list so we don't really care.
                        pass
        return nouns

    def word_passes_stop_word_check(self, word):
        stopwords = ['gon', 'dont', 'lol', 'yeah', 'tho', 'lmao', 'yes']
        if len(word) < 2:
            return False
        elif word in stopwords:
            return False
        else:
            return True

    def does_message_have_prioritized_parts_of_speech(self, taggedsentence):
        wordtagstocheckprioritized = ['PRP$']  # posessive personal pronoun
        if any(t for t in taggedsentence if t[1] in wordtagstocheckprioritized):
            return True
        else:
            return False

    def check_length_of_sentence_to_butt(self, message):
        # DPT feature
        # we need a tagged sentence.
        if len(message) > self.sentence_max_length:
            return False
        else:
            return True

    def replace_an_to_a_in_sentence(self, message, butt_word):
        message = message.split(" ")
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

    def check_word_to_butt(self, noun, unedited_message, messageobject):
        try:
            self.stats.disposition_store(messageobject.server.id, messageobject.channel.id, "Butt Replaced",
                                         # "%s%s" % (nouns[buttword], " (Unfunny=true)" if notfunnyfound else ""),
                                         "%s" % noun,
                                         unedited_message)
        except AttributeError:
            # catching when we use raw sentence mode.  There is no messageobject to get server information from
            # we do not care to add this to the disposition table anyways
            pass
        lemmatizer = WordNetLemmatizer()
        words_that_arent_plural = ['ass']  # FML
        #for match in re.finditer(lemmatizer.lemmatize(noun), unedited_message, flags=re.IGNORECASE):
            # fixes a kara problem
        #    unedited_message = unedited_message.replace(match.group(0), self.butt_in_proper_case(match.group(0), 'butt'))
        if noun in words_that_arent_plural:
            # catch words that the lemmatizer thinks is plural but are not
            return unedited_message.replace(noun, self.butt_in_proper_case(noun, 'butt')), 'butt'
        elif lemmatizer.lemmatize(noun) is not noun:
            # the lemmatizer thinks that this is a plural
            return unedited_message.replace(noun, self.butt_in_proper_case(noun, 'butts')), 'butts'
        else:
            return unedited_message.replace(noun, self.butt_in_proper_case(noun, 'butt')), 'butt'

    def do_butting(self, pri_nouns, non_pri_nouns, unedited_message, messageobject, tagged_sentence):
        picked_phrase = self.pick_phrase(pri_nouns, non_pri_nouns)
        new_sentence, replaced_with = self.check_word_to_butt(picked_phrase[1], unedited_message,
                                                           messageobject)
        if self.test_environment:
            self.print_debug_message(tagged_sentence, pri_nouns, non_pri_nouns, picked_phrase)
        return self.replace_an_to_a_in_sentence(new_sentence, replaced_with), \
               picked_phrase[0], \
               picked_phrase[1]
