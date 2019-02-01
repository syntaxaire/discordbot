import json
from random import *

import nltk
import nltk.data
import nltk.tag
from nltk.stem import WordNetLemmatizer

import butt_library as buttlib


class WordReplacer:

    def __init__(self, config, stat_module, timer_module, phrase_weights, test_environment):
        self.__config = config
        self.__timer_module = timer_module
        self.__stats = stat_module
        self.__wlist = self.__load_word_list()
        self.__set_max_sentence_length(int(self.__config.get('wordreplacer', 'max_sentence_length')))
        self.__command = {"nltk": 'wordreplacer'}
        self.__test_environment = test_environment
        self.__phraseweights = phrase_weights

        # state variables
        self.should_we_butt = False  # this is the state variable that means butting should continue
        self._priority_nouns = []
        self._non_priority_nouns = []
        self._word_is_plural = False
        self._tagged_sentence = ""
        self._original_sentence = ""
        self._weight_of_picked_word = 0
        self._word_passed_weight_check = False
        self._final_sentence = ""
        self._sentence_contains_stop_words = False
        self._selected_noun_pair_to_butt = []
        self.butted_sentence = ""

    def __state_reset(self):
        self.should_we_butt = False  # this is the state variable that means butting should continue
        self._priority_nouns = []
        self._non_priority_nouns = []
        self._word_is_plural = False
        self._tagged_sentence = ""
        self._original_sentence = ""
        self._weight_of_picked_word = 0
        self._word_passed_weight_check = False
        self._final_sentence = ""
        self._sentence_contains_stop_words = False
        self._selected_noun_pair_to_butt = []
        self.butted_sentence = ""

    def __set_max_sentence_length(self, length):
        # DPT requested feature
        # a length of 0 will default to any word length.
        if length > 0:
            self._sentence_max_length = length
        else:
            self._sentence_max_length = 9999

    @staticmethod
    def __load_word_list():
        try:
            with open('wordlist.txt') as f:
                return json.load(f)
        except Exception:
            pass

    def return_commands(self):
        return self.__command

    ################################################################################
    #                               commands                                       #
    ################################################################################
    def do_nltk(self, message):
        return self.__wordtagger(message)

    ################################################################################
    #                               end commands                                   #
    ################################################################################

    def __save(self):
        with open('wordlist.txt', 'w') as f:
            json.dump(self.__wlist, f, ensure_ascii=False)

    def rspeval(self, message):
        message = message.lower()
        for t in self.__wlist:  # replace everything aaaaaaa
            message = message.replace('butt', self.__wlist[randint(0, len(self.__wlist) - 1)], 1)
        return message

    @staticmethod
    def __wordtagger(message):
        return nltk.pos_tag(nltk.word_tokenize(message))

    def __get_phrase_weight(self, phrase):
        return self.__phraseweights.return_weight(phrase)

    def __is_user_an_allowed_bot(self, author):
        if author in self.__config.get_all_allowed_bots():
            return True
        else:
            return False

    def print_debug_message(self):
        print("--------------------------------------------------------------------------------------------------")
        print("Original message: %s" % self._original_sentence)
        print("Message contain stop phrase? %s" % str(self.__does_message_contain_stop_phrases()))
        print("Message meet length requirement? (server setting: %i) %s" % (
            self._sentence_max_length, self.__check_length_of_sentence_to_butt()))
        print("Tagged sentence: %s" % self._tagged_sentence)
        print("Prioritized noun pair(s): %s" % self._priority_nouns)
        print("Non-Prioritized noun pair(s): %s" % self._non_priority_nouns)
        print("Selected noun pair: %s" % str(self._selected_noun_pair_to_butt))
        print("Passes weight minimum? %s" % self.__check_if_picked_phrase_weight_passes_minimum())
        print("Butted sentence: %s" % self.butted_sentence)
        print("--------------------------------------------------------------------------------------------------")

    def __does_message_contain_stop_phrases(self):
        if not any(v for v in self.__config.get_all_stop_phrases() if v in self._original_sentence) and \
                not (self._original_sentence.startswith("*") and self._original_sentence.endswith("*")):
            return False
        else:
            return True

    def successful_butting(self):
        return self.__check_if_picked_phrase_weight_passes_minimum()

    def perform_text_to_butt(self, messageobject):
        """takes a messageobject from discord and sanity checks the butted phrase to determine if we should butt
        the sentence"""
        # we are going to manipulate this version of the message before sending it to the processing functions.
        # we remove stuff that we dont want to be processed (banned phrases, banned people, banned bots)
        self.__state_reset()
        self._original_sentence = str(messageobject.content)
        if not buttlib.detect_code_block(self._original_sentence):
            # passes code block test
            if not self.__does_message_contain_stop_phrases():
                # message contains no stop phrases, let's proceed
                self.__tag_sentence()
                if self._tagged_sentence and self.__check_length_of_sentence_to_butt():
                    # message is below length limit set on a per-guild basis
                    self.__get_word_pairs_from_all_sources()
                    self.__pick_word_pair_to_butt()
                    if self.__check_if_picked_phrase_weight_passes_minimum():
                        # let's butt
                        self.__make_butted_sentence()

    def do_butting_raw_sentence(self, message):
        """always makes butted sentence.  skip all sanity checks that perform_text_to_butt does."""
        self.__state_reset()
        self._original_sentence = str(message)
        self.__tag_sentence()
        self.__get_word_pairs_from_all_sources()
        self.__pick_word_pair_to_butt()
        self.__make_butted_sentence()

    def __tag_sentence(self, split_for_bot=False):
        """tags sentence properly based if user is a bot. we assume these bots are relaying chat message from
        games such as minecraft or factorio."""
        if split_for_bot:
            # message sender is allowed bot, we should separate the first word out of the message since that
            # is the user the bot is relaying for
            self._tagged_sentence = self.__wordtagger(buttlib.strip_IRI(self._original_sentence.split(" ", 1)[1]))
        else:
            self._tagged_sentence = self.__wordtagger(buttlib.strip_IRI(self._original_sentence))

    def __check_if_picked_phrase_weight_passes_minimum(self):
        if len(self._priority_nouns) + len(self._non_priority_nouns) > 0:
            if len(self._non_priority_nouns) == 1 and len(self._priority_nouns) == 0:
                # catch specific case for 1 non prioritized noun and 0 prioritized nouns
                # we should see what weight this word has and not butt it if it is low.
                if self._non_priority_nouns[0][2] <= 501:
                    # dont send anything, this word probably sucks
                    return False
            return True

    def __get_word_pairs_from_all_sources(self):
        if self.__does_message_have_prioritized_parts_of_speech():
            self._priority_nouns = self.__find_weighted_nouns_by_previous_tag(True)
        self._non_priority_nouns = self.__find_weighted_nouns_by_previous_tag(False)

    def __pick_word_pair_to_butt(self):
        """randomly selects a word pair to be the target of replacement."""
        combined_list = self._priority_nouns + self._non_priority_nouns
        self._selected_noun_pair_to_butt = self.__pick_random_phrase_by_weight(combined_list)

    def __pick_random_phrase_by_weight(self, word_list):
        total_sum_of_weights = self.__sum_all_weights(word_list)
        try:
            randomweight = randrange(1, total_sum_of_weights)
            for i in word_list:
                randomweight = randomweight - i[2]
                if randomweight <= 0:
                    return tuple((i[0], i[1]))
        except ValueError:
            # no words to pick
            return None

    def get_trigger_word(self):
        return self._selected_noun_pair_to_butt[0]

    def get_noun(self):
        return self._selected_noun_pair_to_butt[1]

    @staticmethod
    def __sum_all_weights(word_list):
        return sum(weight for prefix, noun, weight in word_list)

    @staticmethod
    def __butt_in_proper_case(wordtobutt, buttoreplace):
        if wordtobutt.istitle():
            return buttoreplace.title()
        elif wordtobutt.isupper():
            return buttoreplace.upper()
        else:
            return buttoreplace

    def __find_weighted_nouns_by_previous_tag(self, prioritized):
        # we construct a list of nouns if the previously tagged word has a certain tag.
        # we prioritize possessive pronouns (his, her, my, etc)
        nouns = []
        word_tags_to_check_prioritized = ['PRP$']
        word_tags_to_check_not_prioritized = ['DT', 'JJ', 'JJS', 'JJR', 'WP$', 'WP']
        tags_to_accept_as_nouns = ['NN', 'NNS']
        words_that_are_not_adjectives = ['i', 'kevin', 'armour', 'mic']
        if prioritized:
            tagstocheck = word_tags_to_check_prioritized
            source_weight = 25.0
        else:
            tagstocheck = word_tags_to_check_not_prioritized
            source_weight = 1.0

        for i in range(len(self._tagged_sentence) - 1):  # *jiggling intensifies*
            if self._tagged_sentence[i][1] in tagstocheck:
                if self._tagged_sentence[i][0] not in words_that_are_not_adjectives:
                    # fix some words getting tagged weird
                    try:
                        if self._tagged_sentence[i + 1][1] in tags_to_accept_as_nouns:
                            # append weighted version of the word using source weight (prioritized vs non pri mode)
                            if self.__word_passes_stop_word_check(self._tagged_sentence[i + 1][0]):
                                nouns.append((self._tagged_sentence[i][0], self._tagged_sentence[i + 1][0],
                                              self.__get_phrase_weight(
                                                  "%s %s" % (self._tagged_sentence[i][0],
                                                             self._tagged_sentence[i + 1][0])) * source_weight))
                    except IndexError:
                        # end of the noun list so we don't really care.
                        pass
        return nouns

    @staticmethod
    def __word_passes_stop_word_check(word):
        """checks to see if selected word passes stopword check - eliminates common crappy words and internet slang
         that are tagged as nouns but either aren't funny to replace or aren't nouns."""
        stopwords = ['gon', 'dont', 'lol', 'yeah', 'tho', 'lmao', 'yes']
        if len(word) < 2 or word in stopwords:
            return False
        else:
            return True

    def __does_message_have_prioritized_parts_of_speech(self):
        """takes a tagged sentence and checks if it contains a personal posessive pronoun - we want to specially
        target that for funny replaces like "my butt" """
        wordtagstocheckprioritized = ['PRP$']  # posessive personal pronoun
        if any(t for t in self._tagged_sentence if t[1] in wordtagstocheckprioritized):
            return True
        else:
            return False

    def __check_length_of_sentence_to_butt(self):
        """checks to see if the tagged message length is lower than the limit set in the guild configuration file.
        this feature was originally requested by DPT."""
        if len(self._original_sentence) > self._sentence_max_length:
            return False
        else:
            return True

    @staticmethod
    def __replace_an_to_a_in_sentence(message, butt_word):
        """replaces an to a in a sentence, such as in the case where we replace "an apple" with "a butt" """
        message = message.split(" ")
        indexes = buttlib.get_indexes(message, butt_word)
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

    def __make_butted_sentence(self):
        if self.__check_if_words_are_plural(self._selected_noun_pair_to_butt[1]) is True:
            # the lemmatizer thinks that this is a plural
            self.butted_sentence = self._original_sentence.replace(self._selected_noun_pair_to_butt[1],
                                                                   self.__butt_in_proper_case(
                                                                       self._selected_noun_pair_to_butt[1], 'butts'))
        else:
            self.butted_sentence = self._original_sentence.replace(self._selected_noun_pair_to_butt[1],
                                                                   self.__butt_in_proper_case(
                                                                       self._selected_noun_pair_to_butt[1], 'butt'))

    def __check_if_words_are_plural(self, noun):
        """uses the NLTK lemmatizer module to check if a word is plural.  this will also catch words that are not plural
        but are unknown to the NLTK lemmatizer database."""
        lemmatizer = WordNetLemmatizer()
        words_that_arent_plural = ['ass', 'boss']  # FML
        # for match in re.finditer(lemmatizer.lemmatize(noun), unedited_message, flags=re.IGNORECASE):
        # fixes a kara problem
        # unedited_message = unedited_message.replace(match.group(0), self.butt_in_proper_case(match.group(0), 'butt'))
        if noun in words_that_arent_plural:
            return False
        elif lemmatizer.lemmatize(noun) is not noun:
            self.word_is_plural = False
        else:
            self.word_is_plural = True
