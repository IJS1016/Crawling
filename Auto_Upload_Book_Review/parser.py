import os
import re
import calendar

# HAVE TO CHECK
# 사진과 같이 올려진 경우에는 내용이 다 불러들여와 지지 않
# 그냥 review 파일 만든 다음에 한번 체크해보고 돌려야 될 듯

# print calendar.monthrange(2016,1) #(4,31)
# print calendar.monthrange(2016,4) #(4,30)

# print calendar.monthrange(2016,1)[1] #31
# print calendar.monthrange(2016,4)[1] #30
#####################################################################################
def change_date_format(date) :
    year, month, day = date.split(".")

    return f'{year}년 {month}월 {day}일'


def get_last_month_day(month) : 
    if month in [1, 3, 5, 7, 8, 10, 12] :
        last_day = 31
        
    elif month in [4, 6, 9, 11] :
        last_day = 30

    # HAVE TO FIXED FOR 윤년
    else : 
        last_day = 29

    return last_day


def get_all_date_lists(start_date, end_date) :
    end_day = [30, 31, 28, 29]
    
    start_year, start_month, start_day = list(map(int, start_date.split(".")))
    end_year,   end_month,   end_day   = list(map(end_date.split(".")))

    all_date_list = []
    last_day = get_last_month_day(start_month)

    while (start_year, start_month, start_day == end_year,   end_month,   end_day) :
        all_date_list.append(change_date_format(f"{start_year}.{start_month}.{start_day}"))

        start_day += 1

        if start_day > last_day :
            start_day    = 1
            start_month += 1

            if start_month > 12 :
                start_month  = 1
                start_year  += 1

            last_day = get_last_month_day(start_month)

    return all_date_list


 
def get_chats_over_a_fixed_date(start_date, end_date, chat_file) :
    start_date_regular_format = change_date_format(start_date)
    end_date_regular_format   = change_date_format(end_date)

    f = open('KakaoTalkChats.txt', 'r')
    lines = f.readlines()
    f.close()

    start = -1
    chats = []

    for idx, line in enumerate(lines[3:]) :
        if (start_date_regular_format in line) and start == -1 :
            start = idx
            
        elif (end_date_regular_format in line):
            chats = lines[start:idx]
            break

    if start == -1 :
        print("!!! HAVE TO SET CORRECT START DATE !!!")
        return 0
    
    if len(chats) == 0 :
        chats = lines[start:]
        
    f = open(chat_file, 'w')

    for c in chats :
        f.write(c)
    f.close()

    print(f">>> SAVED {chat_file}")


def get_reivews(lines) :
    check_tags  = ['책후기', '챌린지도서']
    except_tags = ['인스타']

    calen   = re.compile('\d{4}년 \d+월 \d+일 ')
    tag     = re.compile('#[가-힣]+[0-9]*')

    review_datas = []

    start_idx = -1
    title     = ""

    for idx in range(len(lines)) :
        line = lines[idx]
        if calen.search(line[:15]) and start_idx != -1 :
            print(f"SAVED #책후기 {idx} {line}")

            #print(f"SAVED {start_idx} - {idx}")
            #print(lines[start_idx:idx])
            lines[idx-1] += "<<LINE_END>>\n\n\n"
            review = lines[start_idx+1:idx]
            review.insert(0, title)

            review_datas.append(review)
            start_idx = -1
            idx -= 1
            continue

        elif "#책후기" in line : 
            print(f"START #책후기 {idx} {line}")
            start_idx = idx
            #print(line[:-1])

            tags = tag.findall(line)
            nickname = line.split(',')[1].split(':')[0].split('-')[0].split('_')[0].replace(" ","")

            flag = 0

            for t in tags :
                t = t[1:].replace(" ","")
                #print(t)

                if t in except_tags :
                    flag = 1
                    continue
                
                elif t == nickname or t in check_tags:
                    continue

                else :
                    if flag == 1 :
                        book = "<<!!CHECK_REVIEW!!>>\n" + t
                    else :
                        book = t
                        
                    flag = 0
                
            title = f"<<TITLE>>\n{book} - {nickname}\n"

            


    return review_datas
#####################################################################################
start_date = '2021.5.17'
end_date   = '2021.5.26' # HAVE TO +1

period = f"{start_date}_{end_date}"
chat_file = f"KakaoTalkChats_{period}.txt"
save_file = f"Reviews_{period}.txt"

# MAKE CHAT FILE OVER A WANTED DATA
# if not (os.path.isfile(chat_file)) :
#     get_chats_over_a_fixed_date(start_date, end_date, chat_file)
get_chats_over_a_fixed_date(start_date, end_date, chat_file)

# OPEN THE CHAT FILE
f = open(chat_file, 'r')
lines = f.readlines()
f.close()

# GET REVIEWS
reviews = get_reivews(lines)

# for rd in reviews :
#     for r in rd :
#         print(r)
#     print('\n')


# OPEN THE CHAT FILE
f = open(save_file, 'w')
for lines in reviews : 
    for line in lines :
        f.write(line)
f.close()


print(f">>> SAVED {save_file}")
