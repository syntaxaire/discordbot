import json
import time


class PhraseWeights:
    def __init__(self):
        # weighted phrases
        self.phrases = self.load_from_file()
        # butted messages we need to store
        self.messages = []

    @staticmethod
    def load_from_file():
        try:
            with open('phrase_weight_list.txt') as f:
                return json.load(f)
        except IOError:
            pass

    def save_to_file(self):
        with open('phrase_weight_list.txt', 'w') as f:
            json.dump(self.phrases, f, ensure_ascii=False, default=str)

    def add(self, phrase, weight):
        self.phrases[phrase.lower()] = weight

    def adjust_weight(self, phrase, weight):
        try:
            self.phrases[phrase.lower()] = self.phrases[phrase.lower()] + weight
            if self.phrases[phrase.lower()] <= 0:
                # minimum of 1
                self.phrases[phrase.lower()] = 1
        except KeyError:
            # no stored weight for this phrase so we will add it
            self.add(phrase, 1000 + weight)

    def return_weight(self, phrase_to_search):
        try:
            return self.phrases[phrase_to_search.lower()]
        except KeyError:
            # no stored weight for this phrase so we will use the default weight
            return 1000

    @staticmethod
    def process_reactions(reactions):
        negativeemojis = '😕', '🙁', '☹', '😨', '😦', '😧', '👎', '😠', '😭', '😖', '👎', '💤', '🚫', '🔫', '❎'
        negative_emoji_guid = ['504537001845063680']
        downvotes = 0
        upvotes = 0
        for items in reactions:
            if items.emoji in negativeemojis or items.emoji.id in negative_emoji_guid:
                downvotes = downvotes + items.count
                print("negative")
            else:
                upvotes = upvotes + items.count
        return (upvotes - downvotes) * 20  # set weight change to 20 for each vote

    def add_message(self, guid, trigger_word, noun):
        self.messages.append([time.time(), guid, trigger_word, noun])

    def get_messages(self):
        return self.messages

    def remove_message(self, _time, guid, trigger_word, noun):
        self.messages.remove([_time, guid, trigger_word, noun])
