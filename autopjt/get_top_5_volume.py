import requests
from bs4 import BeautifulSoup

# CoinMarketCap에서 당일 기준 거래량 상위 5개 종목 가져오기
url = "https://coinmarketcap.com/exchanges/upbit/"
res = requests.get(url)
bs = BeautifulSoup(res.text, 'html.parser')
selector = "tbody > tr > td > div > a"
columns = bs.select(selector)
ticker_list = [x.text.strip().replace('/', '-') for x in columns if x.text.strip()]
real_ticker_list = ticker_list[:5]

# real_ticker_list 수정
real_ticker_list = ['KRW-' + ticker.split('-')[0] for ticker in real_ticker_list]

# 업비트 API를 통해 시장 정보를 가져옴
upbit_url = "https://api.upbit.com/v1/market/all?isDetails=true"
response = requests.get(upbit_url)
data = response.json()

# 거래량 상위 5개 코인 중에서 유의종목이 아닌 것을 필터링
filtered_ticker_list = []

for market_info in data:
    market_name = market_info["market"]
    market_warning = market_info.get("market_warning")
    
    if "KRW-" in market_name and market_name in real_ticker_list:
        if market_warning == 'CAUTION': # 유의종목 필터링
            continue
        
        else:
            filtered_ticker_list.append(market_name)

# filtered_ticker_list를 사용하여 필요한 작업 수행
print("KRW 시장 거래량 상위 5개 종목 중 유의종목이 아닌 종목:", filtered_ticker_list)
