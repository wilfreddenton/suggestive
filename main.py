import re
import nltk
from training_set import TrainingSet
from excerpt import Excerpt

train_set = TrainingSet('chat.txt')
excerpt = Excerpt(train_set)
words = excerpt.generate(100)
words = [word for word in words if re.match('U\d+', word) is None]
review = " ".join(words)
print review
