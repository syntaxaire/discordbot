import re


def plurality(word, count):
    return word + "s" if (count > 1 or count == 0) else word


def loud_noises(word, count):
    return str(count) + " " + plurality(word, count) if count > 0 else ""


def is_word_in_text(word, text):
    pattern = r'(^|[^\w]){}([^\w]|$)'.format(word)
    pattern = re.compile(pattern, re.IGNORECASE)
    matches = re.search(pattern, text)
    return bool(matches)
