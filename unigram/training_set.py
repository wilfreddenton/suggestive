import re
import random
import pickle
import os

class TrainingSet:
    def __init__(self, file):
        with open(file) as f:
            self.source = f.read()
        self.bag_of_words = []
        self.tokens = []
        self._generate_bag_of_words()

    def random_token(self):
        return self.bag_of_words[random.randint(0, len(self.bag_of_words) - 1)]

    def _process_token(self, token):
        return token.replace("\n", "").replace("\r", "")

    def _valid_token(self, token):
        if token == "": return False
        if re.match("^\s+$", token): return False
        return True

    def _tokenize_source(self):
        tokens = re.split("\s+", self.source)
        tokens = [self._process_token(t) for t in tokens if self._valid_token(t)]
        self.tokens = tokens
        return self.tokens

    def _generate_bag_of_words(self):
        if os.path.exists('word_map.dat'):
            with open('word_map.dat') as w:
                self.bag_of_words = pickle.load(w)
            return
        tokens = self._tokenize_source()
        while len(tokens) > 0:
            self.bag_of_words.append(tokens.pop(0))
        with open("word_map.dat", 'w') as w:
            pickle.dump(self.bag_of_words, w)
