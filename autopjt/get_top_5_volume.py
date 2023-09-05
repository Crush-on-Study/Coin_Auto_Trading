import requests
from bs4 import BeautifulSoup
 
url = "https://coinmarketcap.com/exchanges/upbit/"
res = requests.get(url)
 
bs = BeautifulSoup(res.text, 'html.parser')
selector = "tbody > tr > td > div > a"
columns = bs.select(selector)
 
ticker_list = [x.text.strip().replace('/', '-') for x in columns if x.text.strip()]
real_ticker_list = ticker_list[:5]
print(real_ticker_list)
