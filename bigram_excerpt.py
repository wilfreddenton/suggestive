import random

class BigramExcerpt:
    def __init__(self, training_set):
        self.training_set = training_set
        self.result = None

    def _bootstrap_result(self):
        self.result = []
        self.result.append(self.training_set.random_token())

    def _current_token(self):
        return self.result[-1]

    def _current_token_choices(self):
        return self.training_set.word_map[self._current_token()] if self._current_token() in self.training_set.word_map else None

    def _add_word(self):
        word_choices = self._current_token_choices()
        self.result.append(word_choices[random.randint(0, len(word_choices) - 1)])

    # def _finalize_result(self):

    def generate(self, word_count):
        self._bootstrap_result()
        while len(self.result) < word_count:
            self._add_word()
        # self.finalize_result()
        return self.result
