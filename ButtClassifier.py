from butt_chunk import ButtChunk


class ButtClassifier:
    def __init__(self, message, phraseweights):
        self.message = message
        self.weights = phraseweights
        self._starting_chunks = message.noun_chunks
        self._chunks_to_investigate = []
        self.classify_butts()
        self._nouns = []
        self._nouns_previous_word_tag = []
        self._vectorized_weight = []
        self.nouns = []

    def classify_butts(self):
        self._nouns = []
        self._nouns_previous_word_tag = []
        self._vectorized_weight = []
        self._extract_nouns_from_chunker()
        self.nouns = []
        if self._nouns:
            for i in range(len(self._nouns)):
                weight = self._get_word_weight(self._nouns[i], self._nouns_previous_word_tag[i])
                self.nouns.append((self._nouns[i], weight))

    def _process_nouns(self):
        print("LOOK HERE: %s" % self._nouns)
        print("previous word tag is %s" % self._nouns_previous_word_tag)

    def _extract_nouns_from_chunker(self):
        # retrieve the nouns from the chunker, and nuke the bad chunks found.
        # the chunker pulls the 'subjects' out of the sentence and returns the full word data for each subject chunk.
        # right now we are blocking single word chunks because most of them are "I, he, we, etc".
        noun_tags = ["NN", "NNS", "NNP"]
        for chunk in self._starting_chunks:
            a = ButtChunk(self.message, chunk)
            if len(chunk.text.split()) > 1:
                if any(x in noun_tags for x in a.tag):
                    self._chunks_to_investigate.append(a)
                    i = 0
                    for x in a.tag:
                        if x in noun_tags:
                            self._nouns.append(a.text[i])
                            try:
                                self._nouns_previous_word_tag.append(a.tag[i - 1])
                            except IndexError:
                                self._nouns_previous_word_tag.append(None)
                        i += 1
                else:
                    if a.text and a.tag:
                        print("no good: %s has tag %s" % (a.text, a.tag))
            else:
                if a.tag in noun_tags:
                    # chunk word count is less than 1. we need to account for this for some phrases
                    print("chunk word length is 1 and contains noun: %s" % chunk.text)

    def _butt_vector_analyser(self, word):
        """check noun vector similarity to spatially funny objects/words/concepts."""
        # TODO: consider reducing weight value for not funny words/objects/concepts
        spatially_funny_objects = ["animal", "people", "structure", "machine", "car"]
        not_funny_objects = ["time", ]
        starting_weight = self.weights.return_weight(word)
        working_weight = starting_weight
        for s in spatially_funny_objects:
            similarity = word.similarity(s)
            if similarity > .4:
                working_weight = working_weight + starting_weight * similarity
        return working_weight

    def _get_word_weight(self, word, previous_tag):
        """combine vector analysis with posessive part-of-speeh increase if the sentence has it"""
        weight = self._butt_vector_analyser(word)
        posessive_POS = ["PRP$"]
        if previous_tag in posessive_POS:
            weight = weight * 25000
        return weight
