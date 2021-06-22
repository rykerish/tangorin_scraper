import re
import sys
import unicodedata

def get_kanji_from_voc(filename):
    with open('new_kanjis.txt') as f:
        file = f.read()
        new_line = file[-1:] != '\n'
        l = file.split('\n')

    with open(filename) as voc, open('new_kanjis.txt', 'a') as f:
        if new_line:
            f.write('\n')
        word = re.split(r'【|\t|,', voc.readline())[0]
        while word:
            for kanji in word:
                if unicodedata.name(kanji).startswith('CJK UNIFIED IDEOGRAPH') and kanji not in l:
                    f.write(kanji+'\n')
                    l.append(kanji)
            word = re.split(r'【|\t|,', voc.readline())[0]

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else 'voc.txt'
    get_kanji_from_voc(filename)

