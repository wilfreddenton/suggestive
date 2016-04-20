import pickle
import random
import re
import nltk
import threading
import os
import glob
from collections import Counter
from data_processor import process_message
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
unigram_lock = threading.Lock()
bigram = Bigram('chat_processed.txt')
bigram_generator = BigramExcerpt(bigram)
bigram_lock = threading.Lock()
trigram = Trigram('chat_processed.txt')
trigram_generator = TrigramExcerpt(trigram)
trigram_lock = threading.Lock()

training_flag = False

class TrainThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def _make_corpus(self):
        messages = ''
        with open('messages.txt') as m:
            messages = " ".join(m.read().split('\n'))
        messages = process_message(messages)
        chat = ''
        with open('chat_processed.txt') as c:
            chat = c.read()
        with open('corpus.txt', 'w') as cor:
            cor.write(chat.strip() + " " + messages.strip())

    def run(self):
        global unigram
        global bigram
        global trigram
        global training_flag
        training_flag = True
        print 'training'
        # delete old pickles
        for filename in glob.glob("*_word_map.dat"):
            os.remove(filename)
        self._make_corpus()
        new_unigram = Unigram('corpus.txt')
        unigram_lock.acquire()
        unigram.tokens = new_unigram.tokens
        unigram.bag_of_words = new_unigram.bag_of_words
        unigram_lock.release()
        new_bigram = Bigram('corpus.txt')
        bigram_lock.acquire()
        bigram.tokens = new_bigram.tokens
        bigram.word_map = new_bigram.word_map
        bigram_lock.release()
        new_trigram = Trigram('corpus.txt')
        trigram_lock.acquire()
        trigram = new_trigram
        trigram.tokens = new_trigram.tokens
        trigram.word_map = new_trigram.word_map
        trigram_lock.release()
        training_flag = False
        print 'done'

@app.route('/')
def home():
    # prep message file
    with open('messages.txt', "w") as m:
        m.write('')
    return app.send_static_file('index.html')

def filter_suggestions(suggestions):
    count = Counter(suggestions)
    ordered_suggestions = count.most_common()
    if len(suggestions) >= 7:
        high_prob_suggestions = ordered_suggestions[0:4]
        suggestions = ordered_suggestions[4:]
        suggestions = random.sample(suggestions, 3 if len(suggestions) >= 3 else len(suggestions))
        suggestions = high_prob_suggestions + suggestions
    else:
        suggestions = count.most_common()
    max_count = ordered_suggestions[0][1]
    suggestions = [(s[0], s[1] / float(max_count)) for s in suggestions]
    return suggestions

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
    key = []
    # set key
    if len(words) == 1:
        key = words[0]
    elif len(words) > 1:
        key = tuple(words[-2:])
    # key fallthrough
    if len(key) == 2 and not isinstance(key, basestring):
        trigram_lock.acquire()
        if key in trigram.word_map:
            suggestions = trigram.word_map[key]
            suggestions = filter_suggestions(suggestions)
        else: # fallthrough to bigram
            key = key[-1]
        trigram_lock.release()
    if isinstance(key, basestring):
        bigram_lock.acquire()
        if key in bigram.word_map:
            suggestions = bigram.word_map[key]
            suggestions = filter_suggestions(suggestions)
        else: # fallthrough to unigram
            key = []
        bigram_lock.release()
    if len(key) == 0:
        unigram_lock.acquire()
        suggestions = unigram.bag_of_words
        unigram_lock.release()
        suggestions = filter_suggestions(suggestions)
        suggestions = [(s[0][0].upper()+s[0][1:], s[1]) if len(words) == 0 else s for s in suggestions]
    # look at previous messages
    with open('messages.txt') as m:
        messages = m.readlines()
    if len(messages) > 0:
        if len(messages) > 5:
            messages = messages[-5:]
        messages = map(nltk.word_tokenize, messages)
        tags = map(nltk.pos_tag, messages)
        tags = reduce(lambda x,y: x+y, tags)
        nouns = [pair[0] for pair in tags if pair[1] in ['NN', 'NNS', 'NNP', 'NNPS'] and pair[0].lower() not in words]
        nouns = set(nouns)
        nouns = random.sample(nouns, 3 if len(nouns) >= 3 else len(nouns))
        suggestion_texts = [s[0] for s in suggestions]
        nouns = [(n, 1) for n in nouns if n not in suggestion_texts]
        suggestions += nouns
    suggestions = set(suggestions)
    suggestions = [{'text': s[0], 'relevance': s[1]} for s in suggestions]
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
    messages = messages.strip()
    if len(messages.split('\n')) % 2 == 0 and not training_flag:
        thread = TrainThread()
        thread.start()
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
