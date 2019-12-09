class ButtChunk:
    def __init__(self, sentence, chunk):
        self._original_sentence = sentence
        self.chunk_tags = []
        self.chunk = ""
        self.text = ""
        self.tag = ""
        self.lemma = ""
        self.shape = ""
        self.vector = []
        self.build_chunk_word_list(chunk)

    def build_chunk_word_list(self, chunk):
        if len(chunk.text.split()) > 1:
            characters_to_strip = ['"', "'"]
            chunk_stripped = ''.join(i for i in chunk.text if i not in characters_to_strip)
            chunk_num_words = len(chunk_stripped.split(' '))
            first_word = str(chunk).split(" ")[0]
            last_word = str(chunk).split(" ")[-1]
            original_sentence = str(self._original_sentence).split(' ')
            first_word_matches = (i for i, e in enumerate(original_sentence) if e == first_word)
            print(chunk)
            for starting_index in first_word_matches:
                possible_last_chunk_word_index = starting_index + chunk_num_words - 1
                try:
                    if original_sentence[possible_last_chunk_word_index] == last_word:
                        # found the chunk position in the sentence. it is from starting
                        # index to possible_last_chunk_word
                        for i in range(starting_index, possible_last_chunk_word_index+1):
                            self.text = self._original_sentence[i].text
                            self.tag = self._original_sentence[i].tag_
                            self.lemma = self._original_sentence[i].lemma_
                            self.shape = self._original_sentence[i].shape_
                            self.vector = self._original_sentence[i].vector
                except IndexError:
                    pass
