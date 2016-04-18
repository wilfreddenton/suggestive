import random

class TrigramExcerpt:
    def __init__(self, training_set):
        self.training_set = training_set
        self.result = None

    def _bootstrap_result(self):
        self.result += self.training_set.random_duple()

    def _current_duple(self):
        return tuple(self.result[-2:])

    def _current_duple_choices(self):
        return self.training_set.word_map[self._current_duple()] if self._current_duple() in self.training_set.word_map else None

    def _single_token_duple_matches(self, duple):
        matching_duples = []
        for key in self.training_set:
            t1, t2 = self.training_set[key][0], self.training_set[key][1]
            if (t1 != duple[0] and t2 == duple[1]) or (t1 == duple[0] and t2 != duple[1]):
                matching_duples.append(key)
        return matching_duples

    def _add_word(self):
        word_choices = self._current_duple_choices()
        if not word_choices:
            matching_duples = self._single_token_duple_matches(self._current_duple())
            word_choices = self.training_set.word_map[matching_duples[random.randint(0, len(matching_duples) - 1)]]
        self.result.append(word_choices[random.randint(0, len(word_choices) - 1)])

    # def _finalize_result(self):

    def generate(self, word_count):
        self.result = []
        self._bootstrap_result()
        while len(self.result) < word_count:
            self._add_word()
        # self.finalize_result()
        return self.result
