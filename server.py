import pickle
import random
from flask import Flask, request, jsonify
from unigram import Unigram
from unigram_excerpt import UnigramExcerpt
from bigram import Bigram
from bigram_excerpt import BigramExcerpt
from trigram import Trigram
from trigram_excerpt import TrigramExcerpt
app = Flask(__name__)

unigram = Unigram('chat_processed.txt')
unigram_generator = UnigramExcerpt(unigram)
bigram = Bigram('chat_processed.txt')
bigram_generator = BigramExcerpt(bigram)
trigram = Trigram('chat_processed.txt')
trigram_generator = TrigramExcerpt(trigram)

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/api/suggestions')
def suggestions():
    text = request.args.get('text').strip()
    words = text.split()
    key = []
    # set key
    if len(words) == 1:
        key = words[0]
    elif len(words) > 1:
        key = tuple(words[-2:])
    # key fallthrough
    if len(key) == 2:
        if key in trigram.word_map:
            suggestions = trigram.word_map[key]
            suggestions = random.sample(suggestions, 6 if len(suggestions) >= 6 else len(suggestions))
        else: # fallthrough to bigram
            key = key[-1]
    if isinstance(key, basestring):
        if key in bigram.word_map:
            suggestions = bigram.word_map[key]
            suggestions = random.sample(suggestions, 6 if len(suggestions) >= 6 else len(suggestions))
        else: # fallthrough to unigram
            key = []
    if len(key) == 0:
        suggestions = unigram_generator.generate(3)
        suggestions = [suggestion.title() for suggestion in suggestions]

    suggestions = set(suggestions)
    suggestions = [{'text': suggestion} for suggestion in suggestions]
    return jsonify(suggestions=suggestions)

if __name__ == '__main__':
    app.run(debug=True)
