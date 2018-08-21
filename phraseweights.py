import json
import time


class PhraseWeights:
    def __init__(self):
        # weighted phrases
        self.phrases = self.load_from_file()
        # butted messages we need to store
        self.messages = []

    def load_from_file(self):
        try:
            with open('phrase_weight_list.txt') as f:
                return json.load(f)
        except Exception:
            pass

    def save_to_file(self):
        #print("saving weights to file")
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

    def process_reactions(self, reactions):
        negativeemojis = '😕', '🙁', '☹', '😨', '😦', '😧', '👎', '😠', '😭', '😖', '👎'
        downvotes = 0
        upvotes = 0
        for items in reactions:
            if items.emoji in negativeemojis:
                downvotes = downvotes + items.count
            else:
                upvotes = upvotes + items.count
        return (upvotes - downvotes)*20  #set weight change to 20 for each vote

    def add_message(self, guid, trigger_word, noun):
        self.messages.append([time.time(), guid, trigger_word, noun])

    def get_messages(self):
        return self.messages

    def remove_message(self, time, guid, trigger_word, noun):
        self.messages.remove([time, guid, trigger_word, noun])
