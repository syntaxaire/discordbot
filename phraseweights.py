import time


class PhraseWeights():
    def __init__(self, db):
        # weighted phrases
        # butted messages we need to store
        self.messages = []
        self.db = db

    def adjust_weight(self, word, weight):
        if weight == 0:
            # no further processing.
            print("word %s: not adjusting weight since voted weight is %d" %
                  (word, weight)
                  )
            pass
        else:
            db_word_weight = self.return_weight(word)
            weight = db_word_weight + weight
            print("word %s is getting weight %d adjusted to %d" % (word, db_word_weight, weight))
            self.db.do_insert(
                "INSERT into phraseweights (word, weight) VALUES (%s, %s) ON DUPLICATE KEY UPDATE weight = weight + %s",
                (word, weight, weight))

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
        print("processing reactions")
        print(reactions)
        for items in reactions:
            print("new reaction")
            print(items.emoji)
            try:
                if items.emoji in negativeemojis or items.emoji.id in negative_emoji_guid:
                    print("downdoot")
                    downvotes = downvotes + items.count
                else:
                    print("updoot")
                    upvotes = upvotes + items.count
            except AttributeError:
                # items.emoji.id not defined
                if items.emoji in negativeemojis:
                    print("downdoot and also it blew up")
                    downvotes = downvotes + items.count
                else:
                    print("updoot and also it blew up")
                    upvotes = upvotes + items.count
        return (upvotes - downvotes) * 20  # set weight change to 20 for each vote

    def add_message(self, message, noun):
        self.messages.append([time.time(), message, noun])

    def get_messages(self):
        return self.messages

    def remove_message(self, _time, message, noun):
        self.messages.remove([_time, message, noun])
