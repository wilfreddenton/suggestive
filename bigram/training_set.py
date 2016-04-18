import re
import random
import pickle
import os

class TrainingSet:
    def __init__(self, file):
        with open(file) as f:
            self.source = f.read()
        self.word_map = {}
        self.tokens = []
        self._generate_word_map()

    def random_token(self):
        return self.word_map.keys()[random.randint(0, len(self.word_map) - 1)]

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

    def _generate_word_map(self):
        if os.path.exists('word_map.dat'):
            with open('word_map.dat') as w:
                self.word_map = pickle.load(w)
            return
        tokens = self._tokenize_source()
        while len(tokens) > 1:
            token = tokens[0]
            if token not in self.word_map:
                self.word_map[token] = [tokens[1]]
            else:
                self.word_map[token].append(tokens[1])
            tokens.pop(0)
        with open("word_map.dat", 'w') as w:
            pickle.dump(self.word_map, w)
