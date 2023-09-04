import pyupbit

tickers = pyupbit.get_tickers("KRW")  # KRW를 통해 거래되는 코인만 불러오기
dic_ticker = {}

# 모든 코인에 대한 'day' 기간의 데이터를 한 번만 불러와 캐시
ohlcv_data = {}
for ticker in tickers:
    ohlcv_data[ticker] = pyupbit.get_ohlcv(ticker, 'day')

for ticker in tickers:
    df = ohlcv_data[ticker]
    if df is not None and not df.empty:
        last_row = df.iloc[-1]
        volume_money = last_row['close'] * last_row['volume']
        dic_ticker[ticker] = volume_money
    
# 거래대금 큰 순으로 ticker를 정렬
sorted_ticker = sorted(dic_ticker.items(), key=lambda x: x[1], reverse=True)
coin_list = [coin[0] for coin in sorted_ticker[:5]]

print(coin_list)
