import re

text = "have n't you 're I 'll"
def join_contraction(match_obj):
    return match_obj.group(1) + match_obj.group(2) + ' '
text = re.sub(r'(\w+)\s(\w?\'\w+)(\s|$)', join_contraction, text)
print text
