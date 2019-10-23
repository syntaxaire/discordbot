class ButtChunk:
    def __init__(self, sentence):
        self._original_sentence = sentence
        self.chunk_tags = []
        self.status = False
        self.build_chunk_word_list()

    def __iter__(self):
        self.iterpos = 0
        return self

    def __next__(self):
        try:
            self.iterpos += 1
            return self.chunk_tags[self.iterpos-1]

        except IndexError:
            raise StopIteration

    def get_sentence(self):
        return self._original_sentence

    def get_status(self):
        return self.status

    def build_chunk_word_list(self):
        for chunk in self._original_sentence.noun_chunks:
            if len(chunk.text.split()) > 1:
                characters_to_strip = ['"', "'"]
                chunk_stripped = ''.join(i for i in chunk.text if i not in characters_to_strip)
                chunk_num_words = len(chunk_stripped.split(' '))
                first_word = str(chunk).split(" ")[0]
                last_word = str(chunk).split(" ")[-1]
                original_sentence = str(self._original_sentence).split(' ')
                first_word_matches = (i for i, e in enumerate(original_sentence) if e == first_word)
                for starting_index in first_word_matches:
                    possible_last_chunk_word_index = starting_index + chunk_num_words - 1
                    if original_sentence[possible_last_chunk_word_index] == last_word:
                        # found the chunk position in the sentence. it is from starting
                        # index to possible_last_chunk_word
                        for i in range(starting_index, possible_last_chunk_word_index+1):
                            self.status = True
                            self.chunk_tags.append(
                                (self._original_sentence[i].text,
                                 self._original_sentence[i].tag_,
                                 self._original_sentence[i].lemma_,
                                 self._original_sentence[i].shape_)
                            )
                    print (self.chunk_tags)