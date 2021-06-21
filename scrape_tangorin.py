#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import io
import os
import pandas as pd
import re
import sys
import unicodedata
import utils

from cairosvg import svg2png
from inspect import signature
from PIL import Image
from tqdm import tqdm

root = utils.get_anki_path('my_kanji')


# In[ ]:


def clean_readings(readings):
    clean = utils.drop_first_lvl(readings)
    clean = re.sub(r'<ruby>(.*?)<\/ruby>', r'\1', clean)
    clean = re.sub(r'<rt class="roma">.*?<\/rt>', '', clean)
    clean_list = clean.split("・")
    readings_dict = {'onyomi': [], 'kunyomi': []}
    for reading in clean_list:
        kana_type = unicodedata.name(re.sub('~', '', utils.clean_html(reading))[0]).split()[0]
        yomi = 'onyomi' if kana_type == 'KATAKANA' else 'kunyomi'
        readings_dict[yomi].append(reading)
    return {k: utils.join(v, '・') for k, v in readings_dict.items()}

def list_to_dict(l, fields):
    l = list(filter(len, l))
    d = {}
    for i in range(0, len(l), 2):
        fld = l[i].lower()
        if fld in fields:
            res = l[i+1]
            res = clean_readings(res)['kunyomi'] if fld == 'nanori' else utils.clean_html(res)
            d[fld] = res
    return d

def info_dict(info, fields):
    clean = utils.drop_first_lvl(info)
    clean_list = list_to_dict(re.split(r'<dt>(.*?):<\/dt>(<dd.*?>.*?<\/dd>)', clean), fields)
    return clean_list

def clean_info(info, kanji, fields=['strokes', 'radical', 'parts', 'nanori']):
    d = info_dict(info, fields)
    parts_soup = utils.get_soup_from_link("https://jisho.org/search/"+kanji+"%20%23kanji")
    d.update(info_dict(re.sub('\n', '', str(parts_soup.find_all('dl', 'dictionary_entry on_yomi')[1])), fields))
    return {field: (d[field] if field in d.keys() else "None") for field in fields}
    
def clean_grades(tags):
    d = {'jōyō': 'None', 'jlpt': 'None'}
    for tag in tags:
        t = tag.get('title')
        if "Jōyō" in t:
            d['jōyō'] = re.findall(r"^Jōyō Kanji (.*?)([a-z]{2} Grade)?$", t)[0][0]
        else:
            d['jlpt'] = re.findall(r"[0-9]+", t)[0]
    return d


# In[ ]:


def clean_stroke_order(l, kanji, delta=10, root=root):
    name = utils.kanji_to_id(kanji) +'.jpg'
    path = os.path.join(root, name)
    images = [[Image.open(io.BytesIO(svg2png(svg_))) for svg_ in utils.clean_fig(fig)] for fig in l]
    width, height = utils.new_size(images, delta)
    h = int((height+delta)/len(images))

    new_im = Image.new('RGB', (width, height), color='white')

    y_offset = 0
    for imgs in images:
        x_offset = 0
        for im in imgs:
            new_im.paste(im, (x_offset, y_offset))
            x_offset += im.size[0]-3
        y_offset += h
    new_im.save(path)
    return f"<img src='{os.path.join(os.path.basename(root), name)}'/>"


# In[ ]:


def clean_words(words):
    res = ''
    words = words[0].find_all('div')
    for w in words:
        clean = utils.clean_html(clean_readings([w])['kunyomi'])
        res += clean + '<br>'
    return '<p>' + res + '</p>'


# In[ ]:


fields = {'kanji': ('dt', 'k-kanji', utils.clean_html), 'readings': ('p', 'k-readings', clean_readings),
         'meanings': ('p', 'k-meanings', utils.clean_html), 'info': ('dl', 'k-info', clean_info),
         'grades': ('abbr', 'entry-label', clean_grades), 'stroke_order': ('figure', 'k-fig', clean_stroke_order),
         'words': ('dd', 'k-ex', clean_words)}


# In[ ]:


def scrap_kanjis(kanji_list, site='https://tangorin.com/kanji/', fields=fields):
    for kanji in tqdm(kanji_list):
        soup = utils.get_soup_from_link(site+kanji)
        d = {}
        for fld, (fld_type, class_, clean_f) in fields.items():
            data = soup.find_all(fld_type, class_=class_)
            clean = clean_f(data) if len(signature(clean_f).parameters) == 1 else clean_f(data, kanji)
            try:
                d.update(clean)
            except:
                d[fld] = clean
        d.update({'index': utils.kanji_to_id(kanji), 'keyword': d['meanings'].split(';')[0]})
        try:
            res_df = res_df.append(d, ignore_index=True)
        except:
            res_df = pd.DataFrame(d, index=[0])
    res_df = res_df.set_index('index')
    res_df.index.name = None
    return res_df


# In[ ]:


def main():
    with open('new_kanjis.txt') as f:
        file = f.read()
        if not len(file):
            return
        kanji_list = list(filter(len, file.split('\n')))
    filename = 'kanjis.tsv'
    sep = '\t'
    try:
        df = pd.read_csv(filename, sep=sep, index_col=0)
        kanji_list = utils.drop_from_list(kanji_list, df['kanji'].to_list())
        if len(kanji_list):
            df = pd.concat([df, scrap_kanjis(kanji_list)])
    except:
        df = scrap_kanjis(kanji_list)
    df = df.drop_duplicates(subset='kanji')
    display(df)
    df.to_csv(filename, sep=sep)
if __name__ == "__main__":
    main()


# In[ ]:




