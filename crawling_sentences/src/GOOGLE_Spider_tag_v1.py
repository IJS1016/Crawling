#! /bin/python3.6

################################################################################
# GOOGLE_Spider_tag_v1.py
###############################################################################
# Get contents from a websites in google search.
# 
# CMD input       : GOOGLE_Spider_tag_v1.py set_params_file_name
# 
# Set param spath : '/space/spider/set_params'
# Save path       : '/space/spider/crawl_by_tag'
################################################################################


# ===========================================================
# Import modules
# ===========================================================
import sys
import os
import time
import re
import gzip
import random
from bs4 import BeautifulSoup as bs
import requests
from selenium import webdriver
import urllib.robotparser
from urllib.request import Request, urlopen



# ===========================================================
# Get argv
# ===========================================================
_, param_file = sys.argv


# ===========================================================
# Global Variables
# ===========================================================
#base_dir     = '/space/spider/data/crawl_by_tag'

link_dict    = {}
level_cnt    = 0
total_links  = []


# ===========================================================
# Set Global variables by parsing
# ===========================================================
param_dir = '/space/spider/set_params/'

param_f = open(param_dir+param_file)
for line in param_f : #{
    if re.search('search_word', line) : #{
        search_word = re.split('=|#', line)[1].strip().replace("'", "")
    #}
    elif re.search('base_dir', line) : #{
        base_dir = re.split('=|#', line)[1].strip().replace("'", "") + '/' + search_word.replace(' ', '_') +'/'
    #}
    elif re.search('page_num', line) : #{
        page_num = int(re.split('=|#', line)[1].strip())
    #}
    elif re.search('global_level', line) : #{
        global_level = int(re.split('=|#', line)[1].strip())
    #}
    elif re.search('limit', line) : #{
        limit = int(re.split('=|#', line)[1].strip())
    #}
    elif re.search('tag_list', line) : #{
        tags = re.split('=|#', line)[1].strip()
        tags = re.sub("\[|\]|\'| ",'', tags)
        tag_list = tags.split(',')
    #}

param_f.close()
print(search_word, base_dir, page_num, global_level, limit, tag_list)

# ===========================================================
# Setting PROXY
# ===========================================================
PROXY_HOST = "192.168.100.210"
PROXY_PORT = 3128

profile = webdriver.FirefoxProfile()

profile.set_preference("network.proxy.type", 1)
profile.set_preference("network.proxy.http", PROXY_HOST)
profile.set_preference("network.proxy.http_port", PROXY_PORT)
profile.set_preference('network.proxy.socks', PROXY_HOST)
profile.set_preference('network.proxy.socks_port', PROXY_PORT)
profile.set_preference("network.proxy.ssl", PROXY_HOST)
profile.set_preference("network.proxy.ssl_port", PROXY_PORT)
profile.set_preference('network.proxy.ftp', PROXY_HOST)
profile.set_preference('network.proxy.ftp_port', PROXY_PORT)

profile.update_preferences()


# ===========================================================
# Functions for data processing
# ===========================================================

# make directory for saving files
def make_dir() : #{
    global base_dir, global_level

    print(base_dir)

    # Make Folders(Directory)
    if not (os.path.exists(base_dir)) : #{
        os.mkdir(base_dir)
        os.system(f'chmod 770 {base_dir}')
    #}

    for i in range(1, global_level+1) : #{
        dirr = f'{base_dir}/level{i}'

        if not (os.path.exists(dirr)) : #{
            os.mkdir(dirr)
            os.system(f'chmod 770 {dirr}')
        #}
    #}
#}

# check duplicated link of websites
def check_dup_link(link) : #{
    global link_dict
    check_link = link

    if check_link.startswith('https://') : #{
        check_link = check_link.split('//')[1]
        
        if check_link.startswith('www') : #{
            check_link = check_link[4:]
        #}

        ## Check if link is already added
        start_char = check_link[0]
        if start_char.isnumeric() : start_char = "num"

        if start_char in link_dict.keys() :
            if link in link_dict[start_char] : return False
            else : return True
        #}
        else : return True
    #}
    return False
#}

# 
def add_link(link) : #{
    global link_dict, level_cnt

    check_link = link.split('//')[1]
    if check_link.startswith('www') : #{
        check_link = check_link[4:]
    #}
    start_char = check_link[0]

    if start_char.isnumeric() : #{
        start_char = "num"
    #}

    if start_char in link_dict.keys() : #{
        link_dict[start_char].append(link)
    #}
    else : #{
        link_dict[start_char] = [link]
    #}
    level_cnt += 1

    # print(f"Added {start_char}, {link}")
#}

# check the sentence is english
def is_english(string) : #{
    string = string.replace("\n","")
    if re.search('[^a-zA-Z0-9\?\!\|\"\'\‘\’\&\(\)\_\-\—\–\&\.\,\:\/\@\+\$]+', string.replace(' ', '')) : #{
        print(f'## Not English : {string}')
        return False
    #}
    else: return True
#}


# ===========================================================
# Check for robots.txt to know crawling allowed
# ===========================================================

# check robots txt file to know crawling allowed 
def check_robots_txt(link) : #{
    ## Check robots txt file to know that the cite allow crawling
    
    d_flag = 0
    #domains = [".com/", ".org/", ".co/", ".net/", ".us/", ".aero/", ".arpa/", ".asia/", ".biz/", ".cat/", ".coop/", ".edu/", ".gov/", ".info/", ".int/", ".jobs/", ".mil/", ".mobi/", ".museum/", ".name/", ".org/", ".post/", ".pro/", ".tel/", ".travel/", ".xxx/"]

    domains = [".com", ".org",".net", ".us",  ".co", ".news", ".aero", ".arpa", 
               ".asia", ".biz", ".cat", ".coop", ".edu", ".gov", ".info", ".int",
               ".jobs", ".mil", ".mobi", ".museum", ".name", ".post", ".pro", ".tel",
               ".travel", ".ch", ".tv", ".io", ".me", ".be", ".xxx"]

    # Make basic_link (like http://www.abc.com/)
    for domain in domains : #{
        idx = link.find(domain) 

        if (idx != -1) : #{
            idx += len(domain)
            basic_link = link[:idx] + '/'
            d_flag = 1
            break
        #}

    # Make error when we don't have site domain
    if not(d_flag) : #{
        #other_domains.append(link) 
        return "", False
    #}

    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(basic_link + 'robots.txt')

    # Make error when the site don't have robots.txt
    try :   #{
        rp.read()
    #}
    except : #{
       # print(">> Robots Issue : This Site doesn't have robots.txt")
        return basic_link, True
    #}

    # Make error when the site don't have rule about User-agent: *
    try : 
        rrate = rp.request_rate("*")
    except : #{
        # print(">> Robots Issue : This site doesn't have '*'")
        return basic_link, True
        #}

    return basic_link, rp.can_fetch("*", link)
    #}
#}



# ===========================================================
# Functions for google crawling
# ===========================================================

# open google and search about word
def open_and_search(search_word) : #{
    ## Search word, go through the pages of google and get links

    global limit

    browser = webdriver.Firefox(firefox_profile=profile)
    browser.implicitly_wait(3)

    browser.get('https://www.google.com')

    ## Search
    search = browser.find_element_by_name('q')
    search.clear()
    search.send_keys(search_word)
    search.submit()

    ## Get the links moving through pages
    links = []
    p_num = 1
    
    # while(len(links) <= limit) : #{
    while(p_num <= page_num) : #{
        ## Get url of current page
        time.sleep(5)
        cur_url = browser.current_url

        ## Get the hyperlinks of the page
        links.extend(get_hyperlinks_google(cur_url))
        
        p_num += 1
        ## Get the URL of Page Number 
        next_page_btn = browser.find_elements_by_xpath(f'//*[@id="nav"]/tbody/tr/td[{p_num+1}]/a/span')[0]
        next_page_btn.click()
    #}

    print(">> Google : ", len(links))
    time.sleep(5)
    browser.quit()
    return links
#}

# get hyperlinks of website in google search
def get_hyperlinks_google(page) : #{
    ## Crawl hyperlinks in google
    # req = Request(page)
    # req.add_header('User-Agent', 'Mozilla/5.0')

    # html = urlopen(req)
    # soup = bs(html.read(), "html.parser")

    req = requests.get(page).text
    soup = bs(req, "html.parser")

    web_sites = soup.select("a")
    
    ref = []
    for url in web_sites : #{
        href = url.get('href')

        if not url.get('class') and href.startswith('/url?q') and not('accounts.google' in href) and not('youtube' in href) : #{
            ref.append(href.split("&")[0][7:])
        #}
    #}
    return ref
#}

# ===========================================================
# Functions for website crawling
# ===========================================================
def crawl_websites(link_list, level) : #{

    next_links = []

    for link in link_list : #{
        #check duplicate link
        if check_dup_link(link) : #{
            basic_url, robot_result = check_robots_txt(link)

            #check robot.txt
            if robot_result      : 
                next_links.extend(crawl_one_website(link, level))

            elif basic_url == "" : continue
            else                 : pass #print(f'>> Can Not crawling : {link}')
        #}
        else : #{
            pass
            #print(f'>> Already Exists : {link}')
        #}
    #}

    next_links = sorted(next_links)    #<< hyperlinks of next level
    return next_links
#}

def crawl_one_website(link, level) : #{
    global global_level, tag_list, base_dir
    
    all_contents = {}

    ## Checks if link exists
    # req = Request(link)
    # req.add_header('User-Agent', 'Mozilla/5.0')


    try : #{
        # html = urlopen(req)
        # soup = bs(html.read(), "html.parser")

        req = requests.get(link).text
        soup = bs(req, "html.parser")

        ## Get the contents of the websites
        for tag in tag_list : #{
            if tag == 'h' : #{
                all_contents.update(get_content_by_tag(tag, soup))
            #}
            else : #{
                all_contents[tag] = get_content_by_tag(tag, soup)
            #}
        #}

        ## Save all contents
        if is_english(all_contents['title']) : #{
            write_files(all_contents, f'{base_dir}/level{level}/')
            add_link(link)
            print(f">> Crawling Done {link}")
        #}

    #}
    except : #{
        print(f">> Page Not Found -({level}) : {link}")
        all_contents['a'] = []
    #}
    
    return all_contents['a']
#}

# get content by each tag
def get_content_by_tag(tag, soup) : #{
    global limit

    if tag == 'title' : #{
        result = soup.find(tag).text
    #}
    elif tag == 'h' : #{
        result = {}

        for i in range(1,7) : #{
            head_wh = soup.find_all(f'h{i}')
            heading = []

            for h in head_wh : #{
                heading.append(h.text)
            #}
            if len(heading) != 0 : #{
                result[f'h{i}'] = heading
            #}
        #}
    #}
    elif tag == 'p' : #{
        result = []
        para_list = soup.find_all(['p', 'li'])

        for p in para_list : #{
            result.append(p.text)
        #}
    #}
    elif tag == 'a' : #{
        result = []
        hyper_links = soup.select("a")

        for hl in hyper_links : #{
            h = hl.get('href')
            if h is not None and h.startswith('https') : #{
                result.append(h)
            #}
        #}

        if len(result) >= limit : #{
            result = random.sample(result, limit)
        #}
    #}
    else : #{
        result = []
        elem_list = soup.find_all(tag)
        
        for e in elem_list : #{
            result.append(e.text)
        #}
    #}
    return result
#}


# ===========================================================
# Functions for saving content in files
# ===========================================================

def write_files(data, lpath) : #{
    ## Write all data of one dictionary
    ## lpath is level path

    title     = data["title"]
    title_dir = title.replace(' ', '_')

    dirr = lpath + title_dir
    if not os.path.exists(dirr): #{
        os.mkdir(dirr)
        # os.system(f'chmod 770 {dirr}')
    #}

    for k in data.keys() : #{
        if k == 'title' : continue
        if len(data[k]) != 0 : #{
            write_file(dirr+'/'+ k, data[k])
        #}
    #}   
#}

def write_file(fd, cont) : #{
    with gzip.open(fd+".gz", "wt") as f: #{
        for line in cont  : #{
            line = line.replace("\n","")
            f.write(line+'\n')
        #}
    #}
#}


# ===========================================================
# MAIN
# ===========================================================
make_dir()

cur_level    = 1                                # import current level
google_links = open_and_search(search_word)     # search at google and get hyperlinks
cur_links    = google_links

while(cur_level <= global_level) : #{
    level_cnt = 0
    cur_links = crawl_websites(cur_links, cur_level)
    print(f"\n  Finished Level {cur_level} (Page : {level_cnt})... Next : {len(cur_links)}\n\n")
    cur_level += 1
    total_links.append(level_cnt)
#}

print(f'Total Number of links per level : {sum(total_links)}\n{total_links}')
