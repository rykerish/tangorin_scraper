# [Tangorin](https://tangorin.com/) scraper for Anki flashcards

First of all, a quick disclaimer: this script doesn't actually create Anki flashcards. It creates a `my_kanji.tsv` file which you can then import into Anki.

You are free to modify and share the script as you wish (see [license](https://github.com/rykerish/tangorin_scraper/blob/main/LICENSE)). However, note that if you change it, the Anki template (`Template.apkg`) will probably not be valid anymore.

Last updated: 21/06/2021

## Initialising

Made using Python 3.8.5

Import `Template.apkg` into Anki to have the card template. The code will not work if you try to download media without having Anki installed.

This script requires [Cairo](https://www.cairographics.org/download/) to function. Install it using your favourite package manager, or from the previous link (not tested on Windows, may or may not work).

Finally, it reads the list of kanji to add from the file `new_kanjis.txt`, which contains **1 kanji per line** (as in the example). For now, this file must be written by hand.

### On Linux / OS X

Run `pip install -r requirements.txt`

### On Windows 10

Run `py -m pip install -r requirements.txt`

### On Windows < 10

Run `python3 -m pip install -r requirements.txt`

## Running

Run the script and follow the instructions if need be (I have tried to make them as clear as possible).

### On Linux / OS X

`python scrape_tangoring.py`

### On Windows 10

`py scrape_tangoring.py`

### On Windows < 10

`python3 scrape_tangoring.py`

## Importing into Anki

Open Anki, click "Import File" and choose the resulting `my_kanjis.tsv` file.

Set the card Type to `my_kanji` (from the Template), and select your target deck; fields should be separated by Tab.

***Make sure the "Allow HTML in fields" option is checked or you won't have audio and images.***

Unless you modified the script, the field mapping should be done automatically.

Now you can just import and practice!

