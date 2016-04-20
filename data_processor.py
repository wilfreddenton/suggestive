# goal: create feature vectors for each of the documents in neg and pos
# the feature vectors are counts associated with word IDs which are
# the position of the count in the vector
import re

def join_contraction(match_obj):
    return match_obj.group(1) + match_obj.group(2) + ' '

def upcase_contraction(match_obj):
    return ' ' + match_obj.group(1)[0].upper()+match_obj.group(1)[1:] + ' '

def process_message(text):
    text = re.sub(r'\s+(ACTION|JOIN|PART)\s+', ' ', text)
    text = re.sub(r'\s*U\d+\s*', ' ', text)
    text = re.sub(r'\s+\'s?\s+',' ', text)
    text = text.lower()
    text = re.sub(r'\s+i\s+', ' I ', text)
    text = re.sub(r'\s*[_+-.,!?@#$%^&*();\/\\|<>"]+\s*',' ', text)
    text = re.sub(r'\s*\d+\s*', ' ', text)
    text = re.sub(r'\s+[^aI]\s+', ' ', text)
    text = re.sub(r'\s+[^aI]\s+', ' ', text)
    text = re.sub(r'\s+(i\'\w+)\s+', upcase_contraction, text)
    return text

def process(text):
    text = re.sub(r'\s+(ACTION|JOIN|PART)\s+', ' ', text)
    text = re.sub(r'\s*U\d+\s*', ' ', text)
    text = re.sub(r'\s+\'s?\s+',' ', text)
    text = text.lower()
    text = re.sub(r'\s+i\s+', ' I ', text)
    text = re.sub(r'(\w+)\s(\w?\'\w+)(\s|$)', join_contraction, text)
    text = re.sub(r'\s*[_+-.,!?@#$%^&*();\/\\|<>"]+\s*',' ', text)
    text = re.sub(r'\s*\d+\s*', ' ', text)
    text = re.sub(r'\s+[^aI]\s+', ' ', text)
    text = re.sub(r'\s+[^aI]\s+', ' ', text)
    return text

with open('chat.txt') as c:
    text = c.read()
    text = process(text)
    with open('chat_processed.txt', 'w') as cp:
        cp.write(text)
