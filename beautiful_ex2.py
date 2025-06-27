import pandas as pd
from bs4 import BeautifulSoup
import requests
from io import StringIO

url = 'https://finance.naver.com/item/sise_day.naver?code=000660&page=1'
html = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text
bs = BeautifulSoup(html, 'lxml')
pgrr = bs.find('td', class_='pgRR')
# print(pgrr.a['href'])
# print(pgrr.prettify())

# 마지막 페이지 추출
s= str(pgrr.a['href']).split('=')
last_page = s[-1]
# print(last_page)


# 일별 시세 읽어오는 코드
df = pd.DataFrame()
sise_url = 'https://finance.naver.com/item/sise_day.naver?code=000660'

datas = []

for page in range(1, int(last_page) + 1):
    url = '{}&page={}'.format(sise_url, page)
    html = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text
    datas.append(pd.read_html(StringIO(html), header=0)[0])
    
df = pd.concat(datas, ignore_index=True)
df = df.dropna()
print(df)