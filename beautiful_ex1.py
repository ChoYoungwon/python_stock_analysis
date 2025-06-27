from bs4 import BeautifulSoup
import requests
url = 'https://finance.naver.com/item/sise_day.naver?code=000660&page=1'
html = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text
bs = BeautifulSoup(html, 'lxml')
pgrr = bs.find('td', class_='pgRR')
# print(pgrr.a['href'])
# print(pgrr.prettify())

# 마지막 페이지 추출
s= str(pgrr.a['href']).split('=')
last_page = s[-1]
print(last_page)