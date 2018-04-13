import re
from rfc3987 import parse


def plurality(word, count):
    return word + "s" if (count > 1 or count == 0) else word


def loud_noises(word, count):
    return str(count) + " " + plurality(word, count) if count > 0 else ""


def is_word_in_text(word, text):
    pattern = r'(^|[^\w]){}([^\w]|$)'.format(word)
    pattern = re.compile(pattern, re.IGNORECASE)
    matches = re.search(pattern, text)
    return bool(matches)


def strip_IRI(text):
    words = text.split(" ")
    for w in words:
        try:
            if parse(w, rule="IRI"):
                words.remove(w)
        except ValueError:
            # we expect this to happen when the text is not an IRI, so we can ignore this
            pass
    return " ".join(words)


def detect_code_block(text):
    words = text.split(" ")
    for w in words:
        if w == "```" or w[:3] == "```" or w[-3:] == "```":
            return True
    return False
