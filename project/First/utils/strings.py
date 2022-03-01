
def most_frequent_words(text):
    all_words = text.split()
    words = filter(lambda w: len(w) > 1, all_words)
    words_count = {}
    for word in words:
        if word in words_count.keys():
            words_count[word] += 1
        else:
            words_count[word] = 1
    words_count_list = sorted(words_count.items(), key=lambda ws: (ws[1], ws[0]), reverse=True)
    words_count_list = list(filter(lambda item: item[1] > 1, words_count_list))
    return words_count_list
