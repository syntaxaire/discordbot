import time
from butt_database import Db


class PhraseWeights:
    def __init__(self, db_, db_user, db_pass, test_environment):
        # weighted phrases
        # butted messages we need to store
        self.messages = []
        self.db = Db(db_, db_user, db_pass, test_environment)

    def add(self, word, weight):
        self.db.do_insert("INSERT into phraseweights (word, weight) VALUES (%s, %s)", (word, weight))

    def adjust_weight(self, phrase, weight):
        self.db.do_insert(
            "INSERT into phraseweights (word, weight) VALUES (%s, %s) ON DUPLICATE KEY UPDATE weight = weight + %s",
            (phrase, weight, weight))

    def return_weight(self, phrase):
        # TODO: remove when we no longer need backwards compatibility with existing NLTK implementation
        try:
            phrase_ = phrase.split(" ")
            if len(phrase_) > 1:
                phrase = phrase_[1]
        except AttributeError:
            # single word sent
            pass
        # end delete this
        try:
            db_weight = self.db.do_query("select weight from phraseweights where word=%s", (phrase,))[0]["weight"]
        except IndexError:
            # not in db
            db_weight = 1000
        if not db_weight:
            return 1000
        elif db_weight < 0:
            return 1
        else:
            return db_weight

    @staticmethod
    def process_reactions(reactions):
        negativeemojis = '😕', '🙁', '☹', '😨', '😦', '😧', '👎', '😠', '😭', '😖', '👎', '💤', '🚫', '🔫', '❎'
        negative_emoji_guid = ['504537001845063680']
        downvotes = 0
        upvotes = 0
        for items in reactions:
            try:
                if items.emoji in negativeemojis or items.emoji.id in negative_emoji_guid:
                    downvotes = downvotes + items.count
                else:
                    upvotes = upvotes + items.count
            except AttributeError:
                # items.emoji.id not defined
                if items.emoji in negativeemojis:
                    downvotes = downvotes + items.count
                else:
                    upvotes = upvotes + items.count
        return (upvotes - downvotes) * 20  # set weight change to 20 for each vote

    def add_message(self, guid, noun):
        self.messages.append([time.time(), guid, noun])

    def get_messages(self):
        return self.messages

    def remove_message(self, _time, guid, noun):
        self.messages.remove([_time, guid, noun])
