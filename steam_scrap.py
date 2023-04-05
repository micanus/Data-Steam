#라이브러리
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import time
from html2text import html2text
import datetime
import platform

#함수
def game_info(steam_game):
    game_df = pd.DataFrame(columns=['ID','Title','Genre','Developer','Publisher','Franchies','Release_date','Recent_reviews','All_reviews','URL','scraptime'])
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
    soup_detail = soup.find('div',{'class':'block responsive_apppage_details_left game_details underlined_links'}).find('div',{'class':'details_block'})

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
    e=soup.find('div',{'id':'review_histogram_recent_section'}).find('div',{'class':'summary_section'}).get_text().strip().split('Recent Reviews:')
    recent_reviews = ' '.join(html2text(''.join(map(str,e))).split())

    #all_reviews
    f = soup.find('div',{'id':'review_histogram_rollup_section'}).find('div',{'class':'summary_section'}).get_text().strip().split('Overall Reviews:')
    all_reviews = ' '.join(html2text(''.join(map(str,f))).split())

    #append dataframe #append제거 관련 concat 변경
    #game_df=game_df.append({'ID':game_code, 'Title':game_title, 'Genre':genre, 'Developer':developer, 'Publisher':publisher, 'Franchies':franchies, 'Release_date':release_date, 'Recent_reviews':recent_reviews, 'All_reviews':all_reviews, 'URL':url, 'scraptime':datetime.datetime.now()}, ignore_index = True)
    info=pd.DataFrame([{'ID':game_code, 'Title':game_title, 'Genre':genre, 'Developer':developer,
                        'Publisher':publisher, 'Franchies':franchies, 'Release_date':release_date,
                        'Recent_reviews':recent_reviews, 'All_reviews':all_reviews, 'URL':url, 'scraptime':datetime.datetime.now()}])
    game_df=pd.concat([game_df,info],ignore_index=True)

    return game_df

#chromedriver 위치는 사용자 환경에 맞춰 수정 필요
runningSystem=platform.system() #구동환경 확인
#run webdriver
if runningSystem=="Windows":  #windows os
    driver = webdriver.Chrome('/Download/chromedriver') 
elif runningSystem=="Darwin": #mac os
    from webdriver_manager.chrome import ChromeDriverManager
    driver = webdriver.Chrome(ChromeDriverManager().install())

url = "https://store.steampowered.com/app/391220"

#steam_url = pd.read_excel('game_url_list.xlsx')
#game_list=steam_url['game_list'].tolist()

#html = requests.get(url)
#html = html.content
#soup = BeautifulSoup(html, 'html.parser')
#soup_detail = soup.find('div',{'class':'block responsive_apppage_details_left game_details underlined_links'}).find('div',{'class':'details_block'})
#print(soup_detail)
a=game_info(url)
print(a)