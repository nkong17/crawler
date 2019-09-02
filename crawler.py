import requests
from bs4 import BeautifulSoup
import telegram
#atom 에서 한글 변환
import sys
import io
import pandas
import os
import time
from datetime import datetime, timedelta
from collections import OrderedDict
from apscheduler.schedulers.blocking import BlockingScheduler
from multiprocessing import Pool



sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

bot = telegram.Bot(token = '870246834:AAHfLHcBHjNPfb7ZJtclCWuZtMaY7O7A5Y0')


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
theaterList = ['0013','0001','0112']

if not os.path.isfile('compare.txt'):
    f = open(os.path.join(BASE_DIR, 'compare.txt'), 'a')
    f.close()

def Compare(movieList):
    temp = []
    cnt = 0
    with open(os.path.join(BASE_DIR, 'compare.txt'), 'r')as f_read:
        before = f_read.readlines()
        before = [line.rstrip() for line in before] #(\n)strip in dt_list
        f_read.close()

        # movieSplit = movieText.split(',')
        # movieTime = movieSplit[0].strip()

        cmpText = '/'.join(before)
        for i in movieList:
            movieText = i.strip()
            if movieText not in cmpText:
                temp.append(i)
                cnt = cnt + 1
                with open(os.path.join(BASE_DIR, 'compare.txt'), 'a') as f_write:
                    f_write.write(i+'\n')
                    f_write.close()
        if cnt > 0:
            Send_Message(temp, cnt)
        else:
            print('4DX 예매가 열리지 않았습니다.')

def Send_Message(temp, cnt):
    for n in temp:
        split_txt = n.split(',')
        mTime = split_txt[0]
        mDate = split_txt[1]
        mTitle = split_txt[2]
        mTheater = split_txt[3]
        msg = '['+mTheater+'] '+mDate + ' ' + mTitle + ' 4DX 예매가 열렸습니다. ' + mTime
        bot.sendMessage(chat_id=858655109, text=msg)
        bot.sendMessage(chat_id=803614577, text=msg)

def SelectMovie(theater):

    now = datetime.now()
    today = now.strftime('%Y%m%d')
    next_week = now + timedelta(days=7)
    next_week = next_week.strftime('%Y%m%d')
    dt_index = pandas.date_range(start=today, end=next_week)
    dt_list = dt_index.strftime("%Y%m%d").tolist()

    theaterName ='';
    if theater in '0001':
        theaterName = '강변'
    if theater in '0013':
        theaterName = '용산'
    if theater in '0112':
        theaterName = '여의도'
    movieList = []
    for day in dt_list:
        url = 'http://www.cgv.co.kr/common/showtimes/iframeTheater.aspx?areacode=01&theatercode='+theater+'&date=' + day

        req = requests.get(url)
        ## HTML 소스 가져오기
        html = req.text

        ## BeautifulSoup으로 html소스를 python객체로 변환하기
        ## 첫 인자는 html소스코드, 두 번째 인자는 어떤 parser를 이용할지 명시.
        ## 이 글에서는 Python 내장 html.parser를 이용했다.
        soup = BeautifulSoup(html, 'html.parser')
        fourdx = soup.select('span.forDX')

        if (fourdx):
            for i in fourdx:
                col_times = i.find_parent('div', class_='col-times')
                typehall  = i.find_parent('div', class_='type-hall')
                title = col_times.select_one('div.info-movie > a > strong').text.strip()
                times = typehall.select('div.info-timetable > ul > li')
                movieTime = '';
                for time in times:
                    if (time is times[-1]):
                        movieTime += time.select_one('em').text.strip()
                    else:
                        movieTime += time.select_one('em').text.strip() + ' '
                    # text = day + ',' + title + ',' + movieTime
                    # movieList.append(text)
                text = movieTime + ',' + day + ',' + title+','+theaterName
                movieList.append(text)
    movieList = list(OrderedDict.fromkeys(movieList))
    Compare(movieList)

# SelectMovie()
if __name__=='__main__':
    def MultiStart():
        pool = Pool(processes=3) #3개의 프로세스를 사용합니다.
        pool.map(SelectMovie, theaterList)
        pool.close()
        pool.join()
    # MultiStart()
    sched = BlockingScheduler()
    sched.add_job(MultiStart, 'interval', seconds=5)
    sched.start()
