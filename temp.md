## set_vectors

### morphemes
morphemes = {}
    for morpheme in igt.get('m'):
        morphemes[morpheme.id] = morpheme.value()

### words
words = {}
for line in igt.get('t'):
    line = str(line.value()).lower().split()
    for word in line:
        words[word] = True