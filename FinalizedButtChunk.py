class FinalizedButtChunk:
    text = ""
    weight = 0
    tag = ""

    def __init__(self, original_spacy_object, weight, previous_word_tag, similarities):
        self.text = original_spacy_object.text
        self.tag = original_spacy_object.tag_
        self.lemma = original_spacy_object.lemma_
        self.shape = original_spacy_object.shape_
        self.weight = weight
        self.previous_word_tag = previous_word_tag
        self.original_spacy_object = original_spacy_object
        self.similarities = similarities
