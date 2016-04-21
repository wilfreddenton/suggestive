# goal: create feature vectors for each of the documents in neg and pos
# the feature vectors are counts associated with word IDs which are
# the position of the count in the vector
import re
import nltk

contractions = {
    "aint":"ain't",
    "arent":"aren't",
    "arnt":"aren't",
    "cant":"can't",
    "cause":"because",
    "couldve":"could've",
    "couldnt":"couldn't",
    "didnt":"didn't",
    "doesnt":"doesn't",
    "dont":"don't",
    "hadnt":"hadn't",
    "hasnt":"hasn't",
    "havent":"haven't",
    "havnt":"haven't",
    "hed":"he'd",
    "hes":"he's",
    "howd":"how'd",
    "howll":"how'll",
    "hows":"how's",
    "id":"I'd",
    "il":"I'll",
    "ill":"I'll",
    "im":"I'm",
    "iv":"I've",
    "ive":"I've",
    "isnt":"isn't",
    "itd":"it'd",
    "itll":"it'll",
    "lets":"let's",
    "mightve":"might've",
    "mightv":"might've",
    "mustnt":"mustn't",
    "musnt":"mustn't",
    "neednt":"needn't",
    "shes":"she's",
    "shouldve":"should've",
    "shouldv":"should've",
    "shouldnt":"shouldn't",
    "thatd":"that'd",
    "thats":"that's",
    "thered":"there'd",
    "theres":"there's",
    "theyd":"they'd",
    "theyll":"they'll",
    "theyre":"they're",
    "theyve":"they've",
    "theyv":"they've",
    "wasnt":"wasn't",
    "weve":"we've",
    "werent":"weren't",
    "whatll":"what'll",
    "whatre":"what're",
    "whats":"what's",
    "whatve":"what've",
    "whatv":"what've",
    "whens":"when's",
    "whenve":"when've",
    "whenv":"when've",
    "whered":"where'd",
    "wheres":"where's",
    "whereve":"where've",
    "wherev":"where've",
    "wholl":"who'll",
    "whol":"who'll",
    "whos":"who's",
    "whove":"who've",
    "whov":"who've",
    "whys":"why's",
    "whyve":"why've",
    "whyv":"why've",
    "willve":"will've",
    "willv":"will've",
    "wont":"won't",
    "wouldve":"would've",
    "wouldv":"would've",
    "wouldnt":"wouldn't",
    "yall":"y'all",
    "yal":"y'all",
    "youd":"you'd",
    "youll":"you'll",
    "youl":"you'll",
    "youre":"you're",
    "youve":"you've",
    "youv":"you've"
}

def fix_contractions(words):
    post = words[:]
    for i, word in enumerate(post):
        word = word.lower()
        if word in contractions:
            post[i] = contractions[word]
    return post

def split_sentences(posts):
    new_posts = []
    for i, post in enumerate(posts):
        text = "\n---\n".join(post)
        sents = re.split(r'[.?!]+', text)
        if len(sents) > 1:
            sents = [s.split('\n---\n') for s in sents]
            new_posts += sents
        else:
            new_posts.append(post)
    return new_posts

def join_contraction(match_obj):
    return match_obj.group(1) + match_obj.group(2) + ' '

def upcase_contraction(match_obj):
    return ' ' + match_obj.group(2)[0].upper()+match_obj.group(2)[1:] + ' '

def process_post(post):
    # fix contractions
    post = fix_contractions(post)
    text = " ".join(post)
    # remove keywords
    text = re.sub(r'(ACTION|JOIN|NICK|PART)', '', text)
    # remove urls
    text = re.sub(r'(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?]))', '', text)
    # remove usernames
    text = re.sub(r'U\d+', '', text)
    # remove possesives since usernames are gone
    text = re.sub(r'(^|\s+)\'s?(\s+|$)',' ', text)
    # lowercase everything
    text = text.lower()
    # uppercase lone i
    text = re.sub(r'(^|\s+)i(\s+|$)', ' I ', text)
    # combine contractions
    text = re.sub(r'(\w+)\s([^iI]?\'\w+)(\s+|$)', join_contraction, text)
    # remove digits
    text = re.sub(r'(^|\s+)\d+(\s+|$)', ' ', text)
    # remove lone punctuation and random chars
    text = re.sub(r'(^|\s+)[_+-.,!?@#$%^&*();\/\\|<>"\s]+(\s+|$)',' ', text)
    # remove lone characters
    text = re.sub(r'(^|\s+)[^aI](\s+|$)', ' ', text)
    # upcase I contractions
    text = re.sub(r'(^|\s+)(i\'\w+)(\s+|$)', upcase_contraction, text)
    # strip leading and trailing spaces
    text = text.strip()
    return text

def process(posts):
    posts = split_sentences(posts)
    posts = map(process_post, posts)
    posts = [post for post in posts if post != '' and re.match(r'^\s+$', post) is None]
    text = "\n---------\n".join(posts)
    return text

with open('chat_processed.txt', 'w') as cp:
    posts = nltk.corpus.nps_chat.posts()
    text = process(posts)
    cp.write(text)
