# This is guide for GOOGLE_Spider_tag_v1.py
 The program is to get contents from the websites associated with word.

 If you run the program, the program will search the word at google, get some titles, contents and hyperlinks from websites page.
 And, It enters other websites though hyperlinks and collects file contents, titles and hyperlinks recursively.
 It repeat until the global level is satisfied.
 The program saves sentences in gz file.

## Save path is "/space/spider/crawl_by_tag/"

## How to run the program:
  ```c
  GOOGLE_Spider_tag_v1.py set_params_file_name
  ```


## Location of set_params_files is in '/space/spider/set_params/'

## The example of file structure is:
search_word  = 'dog'                                #<< word to search
base_dir     = '/space/spider/crawl_by_tag'   #<< directory to save contents
page_num     = 4				    #<< number of pages to crawl in google
global_level = 2				    #<< number of depth to crawl
limit        = 3				    #<< limit number of hyperlinks per page
tag_list     = ['title', 'h', 'p', 'a'] 	    #<< "title"(must) | "h1-h6" | "p" | "a"(must)


### About tag
    title mean title of website
    h1-h6 mean heading of website
    p mean context of website
    a mean hyperlink of website