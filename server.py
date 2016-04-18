import pickle
import random
import re
import nltk
from flask import Flask, request, jsonify
from unigram import Unigram
from unigram_excerpt import UnigramExcerpt
from bigram import Bigram
from bigram_excerpt import BigramExcerpt
from trigram import Trigram
from trigram_excerpt import TrigramExcerpt
app = Flask(__name__)

# train models
unigram = Unigram('chat_processed.txt')
unigram_generator = UnigramExcerpt(unigram)
bigram = Bigram('chat_processed.txt')
bigram_generator = BigramExcerpt(bigram)
trigram = Trigram('chat_processed.txt')
trigram_generator = TrigramExcerpt(trigram)

@app.route('/')
def home():
    # prep message file
    with open('messages.txt', "w") as m:
        m.write('')
    return app.send_static_file('index.html')

@app.route('/api/suggestions', methods=['GET'])
def suggestions():
    data = request.get_json()
    text = request.args.get('text').strip().lower()
    sents = [sent.strip() for sent in re.split(r'[.?!]', text)]
    if len(sents) > 0:
        words = sents[-1].split()
    else:
        words = []
    words = [word[0].upper()+word[1:] if 'i' == word or 'i\'' in word else word for word in words]
    print words
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
        suggestions = [suggestion.title() if len(words) == 0 else suggestion for suggestion in suggestions]
    # look at previous messages
    with open('messages.txt') as m:
        messages = m.readlines()
    if len(messages) > 0:
        messages = map(nltk.word_tokenize, messages)
        tags = map(nltk.pos_tag, messages)
        tags = reduce(lambda x,y: x+y, tags)
        nouns = [pair[0] for pair in tags if pair[1] in ['NN', 'NNS', 'NNP', 'NNPS'] and pair[0].lower() not in words]
        nouns = set(nouns)
        suggestions += random.sample(nouns, 3 if len(nouns) >= 3 else len(nouns))
    suggestions = set(suggestions)
    suggestions = [{'text': suggestion} for suggestion in suggestions]
    return jsonify(suggestions=suggestions)

@app.route('/api/message', methods=['POST'])
def message():
    data = request.get_json()
    message = data['message']['text']
    with open('messages.txt', "r+") as m:
        messages = m.read()
        messages += message + '\n'
        m.seek(0)
        m.write(messages)
        m.truncate()
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
