file = "input.txt"
with open(file) as f:
    tweets = f.read().replace("\n---------\n", "\n")
with open("tweets.txt", 'w') as o:
    o.write(tweets)
