import random
import re
from training_set import TrainingSet
from excerpt import Excerpt

train_set = TrainingSet('input.txt')
excerpt = Excerpt(train_set)
tweets = " ".join(excerpt.generate(1000)).split(' --------- ')
tweets = [tweet for tweet in tweets if re.match('---------', tweet) is None and len(tweet) >= 20 and len(tweet) <= 140]
print "\n---------\n".join(tweets)
