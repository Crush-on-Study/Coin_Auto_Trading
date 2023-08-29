import login,pyupbit
import pandas as pd
import time
import requests

upbit = pyupbit.Upbit(login.id,login.pw)

# RSI 지수 구하는 함수
## RSI : 주가의 상승과 하락의 상대적 강도를 나타내는 지표 -> 쉽게 말해서 과매수 구간인지? 과매도 구간인지?
def get_rsi(symbol, interval, period):
    df = pyupbit.get_ohlcv(symbol, interval=interval, count=period + 1)
    delta = df['close'].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)  # 음수를 양수로 변환하여 계산
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / (avg_loss + 1e-6)  # 0으로 나누는 것을 피하기 위해 작은 값을 더해줌
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]


# 매수 함수
def buy_logic():
    pass

# 매도 함수
def sell_logic():
    pass

# 상위 5종목 코인 조회
def get_top_tickers(count=5):
    url = f"https://api.upbit.com/v1/market/all"
    response = requests.get(url) # get방식으로 url 조회
    data = response.json() # json 타입으로 데이터 전달
    
    markets = [{"market" : market["market"]} for market in data]
    # 결과 : market : "krw-btc" , market : "krw-eth"... 이런 식이군.
    tickers = [market["market"] for market in data if market["market"].startswith("KRW")]
    
    tickers_volumes = []
    for chunk in [tickers[i:i+100] for i in range(0,len(tickers),100)]:
        url = f"https://api.upbit.com/v1/ticker?markets={','.join(chunk)}"
        response = requests.get(url)
        data = response.json()
        tickers_volumes.extend(data)
        
    sorted_tickers = sorted(tickers_volumes, key=lambda x: x["acc_trade_volume_24h"], reverse=True)
    top_tickers = [ticker["market"] for ticker in sorted_tickers[:count]]
    
    return top_tickers
    
    
# 메인 함수
def main():
    interval = "minute1" # 1분봉
    period = 14 # 14일 기준
    buy_threshold = 30
    sell_threshold = 70
    volume_threshold = 5
    
    while True:
        all5_tickers = get_top_tickers(volume_threshold) # 상위 5개 뽑아와.
        for ticker in all5_tickers:
            rsi = get_rsi(ticker,interval,period)
            print(f'종목 : {ticker}, 현재 RSI 지수 : {rsi}')

            if rsi <= buy_threshold: # 매수 구간에 도달한 경우
                # 그리고 그게 거래량 상위 5위 안에 드는 경우
                # 매수 한다.
                buy_logic()
            
            elif sell_threshold-10 <= rsi <= sell_threshold+10:
                # 매도 한다.
                sell_logic()
        
        time.sleep(10) # 10초에 1번씩 체크

if __name__ == "__main__":
    main()
