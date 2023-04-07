#라이브러리
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from html2text import html2text
import pandas as pd
import time
import datetime
import platform #구동환경 확인
from webdriver_manager.chrome import ChromeDriverManager #mac chromedriver 세팅

#함수
#game information crawling
def game_info(steam_game):
    game_df = pd.DataFrame(columns=['ID','Title','Genre','Developer','Publisher','Franchies',
                                    'Release_date','Recent_reviews','All_reviews','URL','scraptime'])
    #추가되는 culum에 따라 순서를 보기 좋게 배열할 것
    
    #move_page
    driver.get(steam_game)
    
    #age check
    if 'agecheck' in driver.current_url:
        element_year = driver.find_element_by_id('ageYear')
        element_month = driver.find_element_by_id('ageMonth')
        element_day = driver.find_element_by_id('ageDay')
        element_OK = driver.find_element_by_link_text('View Page')

        element_year.send_keys('1990')
        element_month.send_keys('march')
        element_day.send_keys('26')
        element_OK.click()
        time.sleep(2)
    else:
        pass

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    soup_detail = soup.find('div',{'class':'block responsive_apppage_details_left game_details underlined_links'})\
        .find('div',{'class':'details_block'})

    #url
    url = driver.current_url

    #game_code
    game_code = driver.current_url.split('/')[4]

    #game_title
    game_title = soup.find('div',{'class':'apphub_AppName'}).get_text()

    #genre
    a = soup_detail.get_text().split('Genre:')[1].split('Developer:')[0]
    genre = ' '.join(html2text(''.join(map(str,a))).split())

    #developer
    b=soup.findAll('div',{'class':'dev_row'})[0].find('div',{'class','summary column'}).get_text()
    developer = ' '.join(html2text(''.join(map(str,b))).split())

    #publisher
    try:
        c=soup.findAll('div',{'class':'dev_row'})[1].find('div',{'class','summary column'}).get_text()
        publisher = ' '.join(html2text(''.join(map(str,c))).split())
    except:
        publisher = 'N/A'

    #franchies (있을 경우)
    try:
        d = soup_detail.get_text().split('Franchise:')[1].split('Release Date: ')[0]
        franchies = ' '.join(html2text(''.join(map(str,d))).split())
    except:
        franchies = 'N/A'

    #release_date
    release_date = soup.find('div',{'class':'release_date'}).find('div',{'class':'date'}).get_text()

    #recent_reviews
    e=soup.find('div',{'id':'review_histogram_recent_section'}).find('div',{'class':'summary_section'})\
        .get_text().strip().split('Recent Reviews:')
    recent_reviews = ' '.join(html2text(''.join(map(str,e))).split())

    #all_reviews
    f = soup.find('div',{'id':'review_histogram_rollup_section'}).find('div',{'class':'summary_section'})\
        .get_text().strip().split('Overall Reviews:')
    all_reviews = ' '.join(html2text(''.join(map(str,f))).split())

    #concat dataframe
    info=pd.DataFrame([{'ID':game_code, 'Title':game_title, 'Genre':genre, 'Developer':developer,
                        'Publisher':publisher, 'Franchies':franchies, 'Release_date':release_date,
                        'Recent_reviews':recent_reviews, 'All_reviews':all_reviews, 
                        'URL':url, 'scraptime':datetime.datetime.now()}])
    game_df=pd.concat([game_df,info],ignore_index=True)

    return game_df
#game review crawling
def review_game(steam_game, scroll_pause_time=0, scroll_counter=9):
    review_df = pd.DataFrame(columns=['ID','Date','User_id','play_time','rate_funny','rate_useful',
                                      'recommend','review_text','review_url','tooltip','scraptime'])
    #추가되는 culum에 따라 순서를 보기 좋게 배열할 것

    #move_page
    driver.get(steam_game)
    #review page make
    game_code = driver.current_url.split('/')[4]
    reviews_page = ("https://steamcommunity.com/app/%s/reviews/?browsefilter=toprated&filterLanguage=english" %game_code)
    #move_page
    driver.get(reviews_page)

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    i=0
    while i < scroll_counter: #스크롤당 10건이므로 1000개 이상 확보하기 위해 숫자를 크게 잡음
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(scroll_pause_time)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        i+=1

    #review url list make
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    a = soup.findAll('div', {'class' : "apphub_Card modalContentLink interactable"})
    print("Scraped posts: ", len(a))
    user_article_list = []
    for i in range(len(a)) :
        #user_article_list.append(str(a[i]).split('data-modal-content-url=\"')[-1].split('\" style=')[0])
        user_article_list.append(str(a[i]).split('data-modal-content-url=\"')[-1].split('\" data-panel=')[0])
    #print(user_article_list)

    #review scraping
    count = 0
    #print("total link:", len(user_article_list))
    for user_article in user_article_list:
        #진행도
        if count % 10 ==0:
            print(str(count),"/", len(user_article_list), end='\r') #캐리지 리턴(\r) 사용, 제자리 출력

        response = requests.get(user_article)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # 리뷰 링크
        review_url = user_article 

        # 유저 아이디
        try:
            user_id = soup.find('span', {'class' : "profile_small_header_name"}).get_text().strip()
        except:
            user_id = 'Nonetype_error'

        # 날짜
        try:
            date = soup.find('div',{'class':"recommendation_date"}).get_text()\
                .split('Posted: ')[-1].split('\t')[0]
        except:
            date = ""

        #플레이 타임
        try:
            play_time = soup.find('div',{'class':"playTime"}).get_text()\
                .split('last two weeks / ')[-1].split(' hrs on record')[0]
        except:
            play_time = ""

        #추천,비추천
        try:
            recommend = soup.find('div',{'class':"ratingSummary"}).get_text()
        except:
            recommend = ""

        #증정유무
        try:
            tooltip = soup.find('div',{'class':"received_compensation tooltip"}).get_text()\
                .split('Product received for ')[-1].split('\t')[0]
        except:
            tooltip = ""

        #유저 평가
        ####unuseful의 경우 적용할 것
        try :
            d = soup.find('div',{'class':"ratingBar"}).get_text().split(' found this review helpful')
            rate_useful = d[0].split('\t')[-1]
            #rate_useful = d[0].strip().split(' people')[0] #1차 개선 but, 1 person 고려하여 수정 필요, 유저 평가 개선 수정
        except :
            rate_useful = "" 
        try:
            d = soup.find('div',{'class':"ratingBar"}).get_text().split(' found this review helpful')
            rate_funny = d[1].split(' found this review funny')[0].split('\t')[0]
        except :
            rate_funny = ""

        #평가내용
        try:
            review_text = soup.find('div',{'id':"ReviewText"}).get_text().strip()
        except:
            review_text = ""

        count +=1

        #concat review_df
        review=pd.DataFrame([{'ID':game_code, 'Date':date,'User_id':user_id,
                              'play_time':play_time,'rate_funny':rate_funny,'rate_useful':rate_useful,
                              'recommend':recommend,'review_text':review_text,'review_url':review_url,
                              'tooltip':tooltip,'scraptime':datetime.datetime.now()}])
        review_df=pd.concat([review_df,review],ignore_index=True)

    print("Done")
    return review_df

#run webdriver
runningSystem=platform.system() #구동환경 확인
if runningSystem=="Windows":  #windows os
    driver = webdriver.Chrome('/Download/chromedriver') #chromedriver 위치는 사용자 환경에 맞춰 수정 필요
elif runningSystem=="Darwin": #mac os
    driver = webdriver.Chrome(ChromeDriverManager().install())

#test
#url = "https://store.steampowered.com/app/391220" #test url
#a=game_info(url)
#b=review_game(url,2,9)
#print(a)
#print(b)

#excel file list
steam_url = pd.read_excel('game_url_list.xlsx') #수집대상 steam game url dataframe load
game_list=steam_url['game_list'].tolist() #수집대상 url list

#data frame make
game_df = pd.DataFrame(columns=['ID','Title','Genre','Developer','Publisher','Franchies',
                                'Release_date','Recent_reviews','All_reviews','URL','scraptime'])
review_df = pd.DataFrame(columns=['ID','Date','User_id','play_time','rate_funny','rate_useful',
                                  'recommend','review_text','review_url','tooltip','scraptime'])

#start scraping
for steam_game in game_list:
    game_df=pd.concat(game_df,game_info(steam_game))
    review_df=pd.concat(review_df,review_game(steam_game,2,9))

#save dataframe
game_df.to_excel('game_list_df.xlsx')
review_df.to_excel('game_review_df.xlsx')