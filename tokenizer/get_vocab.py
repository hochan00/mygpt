import sys
from collections import Counter


def get_vocab(train_file, vocab_file):

    c = Counter()

    for line in train_file:
        for word in line.strip("\r\n ").split(" "):
            if word:
                c[word] += 1

    for key, f in sorted(c.items(), key=lambda x: x[1], reverse=True):
        vocab_file.write(key + " " + str(f) + "\n")


if __name__ == "__main__":
    train_file = open(sys.argv[1])
    vocab_file = open(sys.argv[2], "w")
    get_vocab(train_file, vocab_file)
