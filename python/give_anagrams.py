#!/usr/bin/python

words = ['dog', 'god', 'smile', 'poop', 'narf', 'nancy', 'madam', 'madman', 'spencer']

# for word in words:
#     newword = list(word)
#     newword.sort()
#     print newword
map(lambda x: ''.join(sorted(list(x))), words)

