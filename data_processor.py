# goal: create feature vectors for each of the documents in neg and pos
# the feature vectors are counts associated with word IDs which are
# the position of the count in the vector
import re

with open('chat.txt') as c:
    text = c.read()
    text = re.sub(r'\s*[_+-.,!?@#$%^&*();\/\\|<>"\']+\s*',' ', text)
    text = re.sub(r'\s*U\d+\s*', ' ', text)
    text = re.sub(r'\s*\d+\s*', ' ', text)
    text = re.sub(r'\s+[^aAiI]\s+', ' ', text)
    text = re.sub(r'\s+(ACTION|JOIN|PART)\s+', ' ', text)
    with open('chat_processed.txt', 'w') as cp:
        cp.write(text)
