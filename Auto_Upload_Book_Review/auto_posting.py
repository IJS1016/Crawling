from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pyperclip
import time


driver = webdriver.Chrome('./chromedriver') 

# Login on Naver
# 출처 : https://private.tistory.com/119
def login_naver() :
    ##사용할 변수 선언 
    # #네이버 로그인 주소 
    url = 'https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com'
    uid = "PUT_YOUR_ID"
    upw = "PUT_YOUR_PASSWORD"

    driver.get(url) 
    time.sleep(2)
 
    tag_id = driver.find_element_by_name('id') 
    tag_pw = driver.find_element_by_name('pw') 

    # id 입력 
    # # 입력폼 클릭 -> paperclip에 선언한 uid 내용 복사 -> 붙여넣기 
    tag_id.click()
    pyperclip.copy(uid)
    tag_id.send_keys(Keys.COMMAND, 'v') # Window인 경우 Keys.CONTROL
    time.sleep(1) 

    # pw 입력 # 입력폼 클릭 -> paperclip에 선언한 upw 내용 복사 -> 붙여넣기
    tag_pw.click() 
    pyperclip.copy(upw) 
    tag_pw.send_keys(Keys.COMMAND, 'v') # Window인 경우 Keys.CONTROL
    time.sleep(1) 

    #로그인 버튼 클릭
    login_btn = driver.find_element_by_id('log.login') 
    login_btn.click() 
    time.sleep(2)

    url = "MODOO_WRITE_PAGE_URL"
    driver.get(url) 
    time.sleep(5)

# AUTO POSTING ON MODOO WEBPAGES
def auto_posting(title, contents) :
    # 글쓰기 페이지 이동
    #title_path = '/html/body/div[1]/div[2]/div[3]/div[1]/div/div/div/div/div/div/div/div/table/tbody/tr[2]/td/input'
    title_d = driver.find_element_by_xpath('//*[@id="input_title"]')
    #title = driver.find_element_by_xpath(title_path)
    title_d.send_keys(title)
    time.sleep(1)

    content_full_x_path = '/html/body/div[1]/div[2]/div[3]/div[1]/div/div/div/div/div/div/div/div/table/tbody/tr[3]/td/div/div'

    content_d = driver.find_element_by_xpath(content_full_x_path)
    content_d.send_keys(contents)
    time.sleep(1)

    summit_full_x_path = '/html/body/div[1]/div[2]/div[3]/div[1]/div/div/div/div/div/div/div/div/div/a[2]'
    summit = driver.find_element_by_xpath(summit_full_x_path)
    summit.click()
    time.sleep(2)

    url = "MODOO_WRITE_PAGE_URL"
    driver.get(url) 
    time.sleep(2)

def parsing_reviews(path) :
    f = open(path, 'r')
    lines = f.readlines()
    f.close()

    for idx, line in enumerate(lines) :
        print(line)
        if "<<TITLE>>" in line :
            print("TITLE")
            title_idx = idx + 1
            start_idx = idx + 2

        elif "<<LINE_END>>" in line :
            auto_posting(lines[title_idx], lines[start_idx:idx])
            print("WRITTEN ", lines[title_idx])
        

# MAIN #
login_naver()
review_path = 'Reviews_test.txt'
parsing_reviews(review_path)


