import unicodedata
import os
import re
import requests
import sys

from bs4 import BeautifulSoup
from contextlib import suppress
from hashlib import md5

def pretty_print(dict_items):
    for k, v in dict_items:
        print(f"  {k}: {v}", flush=True)

def get_anki_path(folder):
    os_ = re.sub(r'[0-9]', '', sys.platform)
    default_anki_path = {
        'darwin': os.path.join(os.getenv('HOME'), 'Library/Application Support'),
        'win': os.getenv('APPDATA'),
        'cygwin': os.getenv('APPDATA'),
        'linux': os.getenv('XDG_DATA_HOME') or os.path.join(os.getenv('HOME'),'.local/share')
    }
    anki_path = os.path.join(default_anki_path[os_], "Anki2")
    anki_users = []
    while not os.path.exists(anki_path):
        print(f"{anki_path} is not a valid path.", flush=True)
        anki_path = input("Please enter the location where Anki stores its data:  ")
        print('', flush=True)
    for dir_ in os.listdir(anki_path):
        path_ = os.path.join(anki_path, dir_)
        if os.path.isdir(path_) and 'collection.media' in os.listdir(path_):
            anki_users.append(dir_)

    if not len(anki_users):
        raise FileNotFoundError("No user found in Anki directory.")
    elif len(anki_users) == 1:
        i = 0
    else:
        i = -1
        while i not in range(0, len(anki_users), 1):
            pretty_print(enumerate(anki_users))
            with suppress(ValueError): i = int(input("Select user folder (enter number): "))
    anki_path = os.path.join(anki_path, anki_users[i], 'collection.media', folder)
    with suppress(FileExistsError): os.mkdir(os.path.join(anki_path))
    return anki_path

def get_soup_from_link(link):
    response = requests.get(link)

    # Store the webpage contents
    webpage = response.content

    if(response.status_code != 200):
        return None

    # Create a BeautifulSoup object out of the webpage content
    return BeautifulSoup(webpage, "html.parser")

def drop_from_list(l, sub):
    for k in sub:
        with suppress(ValueError): l.remove(k)
    return l

def convert_tag(tag):
    if len(tag)==1:
        return str(tag[0])
    return tag

def clean_html(tag):
    return re.sub(r'(<.*?>)', '', convert_tag(tag))

def kanji_to_id(kanji):
    return md5(kanji.encode('utf-8')).hexdigest()

def drop_first_lvl(tag):
    return re.sub(r'^<.*?>(.*)<\/.*?>$', r'\1', convert_tag(tag))

def join(l, sep='・'):
    res = sep.join(l)
    return res or 'None'

def update_fields(tag):
    alt = tag.get('alt')
    body = drop_first_lvl(str(tag))
    svg = f"""<svg alt="{alt}" class="k-sod" viewBox="0 0 109 109" height="10em" width="10em" """ + \
    """stroke="#e1e4e7"><rect width="109" height="109" stroke-width="4" fill="white"></rect>""" + \
    body + "</svg>"
    return svg

def clean_fig(fig):
    svgs = fig.find_all('svg')
    return list(map(update_fields, svgs))

def new_size(images, delta=10):
    widths, heights = [], []
    for imgs in images:
        ws, hs = [], []
        for i in imgs:
            w, h = i.size
            ws.append(w)
            hs.append(h)
        widths.append(ws)
        heights.append(hs)
    total_width = max(sum(w) for w in widths)-(3*(max(map(len, images))-1))
    max_height = sum(max(h)+delta for h in heights) - delta
    return total_width, max_height
