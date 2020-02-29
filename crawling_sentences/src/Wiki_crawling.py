#! /bin/python3.6

import sys
import os
import re
from bs4 import BeautifulSoup as bs
from urllib.request import Request, urlopen
import wikipediaapi


# -------------------------------------------
# Get argv
# -------------------------------------------
_, search_word, level = sys.argv
global_level = int(level)


# -------------------------------------------
# Global variables
# -------------------------------------------
base_dir     = f'/space/web_crawling/wiki_data/{search_word}'

wiki = wikipediaapi.Wikipedia(
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI)



# -------------------------------------------
# Functions for data processing
# -------------------------------------------
def is_ascii(s) : #{
    try :
        return all(ord(c) < 128 for c in s)
    except TypeError :
        print(f">> {s} is not ascii")
        return False
#}

def make_dir() : #{
    global base_dir

    bb = base_dir.split("/")

    # Make Folders(Directory)
    if not (os.path.exists(base_dir)) : #{
        os.mkdir(base_dir)
        os.system(f'chmod 770 {base_dir}')
    #}

    for i in range(2, global_level+1) : #{
        ln = str(i)
        dirr = f'{base_dir}/level{ln}'

        if not (os.path.exists(dirr)) : #{
            os.mkdir(dirr)
            os.system(f'chmod 770 {dirr}')
        #}
    #}
#}

# -------------------------------------------
# Functions for crawling
# -------------------------------------------

def get_hyperlinks(word) : #{

    words = wiki.page(word).links.keys()
    results = []

    for i in words: #{
        if is_ascii(i) : #{
            results.append(i.replace(" ","_"))
        #}
    #}

    return results
#}

def parsing_BS(word) : #{
    # Get the content from wikipedia page
    result = []
    url = 'https://en.wikipedia.org/wiki/'+word
    try : #{
        website = Request(url)
        html    = urlopen(website).read()
        soup    = bs(html, "html.parser")
        contents = soup.find_all("p")
    
        for l in contents :  #{
            line = re.sub("\[\d+\]", "", l.get_text())  # remove [num]
            line = re.sub("\{.+\}" ,"", line)            # remove {fomular}
            result.append(line.replace("\n","")+"\n")
        #}

        result = ''.join(result)
    #}
    except : #{
        # print(f">> Page Not Found : {word} - {url}")
        pass
    #}

    return result
#}

def save_text(word, level) : #{
    global wiki, base_dir

    if level == 1 : dir_name = f'{base_dir}/'
    else : dir_name = f'{base_dir}/level{level}/'

    f_n = dir_name+word.replace("/", "-")+'.txt'
    # print(f"(lv:{level})  {word}")
    
    content = parsing_BS(word)
    if len(content) != 0 :
        with open(os.path.join(f_n), 'wt') as f: #{
            f.write(content)
        #}
    #}
#}



def crawl_one_wiki(word, level) : #{
    global global_level

    save_text(word, level)
    
    next_words = []
    if level + 1 <= global_level : #{
        next_words = get_hyperlinks(word)
        # print(f"(lv:{level})  {word}   {len(next_words)}")
    #}

    return next_words
#}


def crawl_wiki(word_list, level) : #{

    next_words = []
    for word in word_list : #{
        next_words.extend(crawl_one_wiki(word, level))
    #}

    next_words = sorted(next_words)
    return next_words
#}



# -------------------------------------------
# MAIN
# -------------------------------------------

make_dir()

cur_level = 1
cur_words = [search_word]

while (cur_level <= global_level) : #{
    cur_words = crawl_wiki(cur_words, cur_level)
    print(f"Finished Level{cur_level}... Next : {len(cur_words)}")
    cur_level += 1
#}
