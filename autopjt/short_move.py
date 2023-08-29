import login
import pyupbit
import time

upbit = pyupbit.Upbit(login.id, login.pw)

def get_ma(symbol, interval, period):
    df = pyupbit.get_ohlcv(symbol, interval=interval, count=period)
    ma = df['close'].rolling(window=period).mean()
    return ma.iloc[-1]

def buy_logic(symbol, interval, short_periods, long_periods):
    short_mas = [get_ma(symbol, interval, period) for period in short_periods]
    long_mas = [get_ma(symbol, interval, period) for period in long_periods]
    
    for i in range(len(short_periods)):
        if short_mas[i] <= long_mas[i]:
            return False
    
    return True

def sell_logic(symbol, interval, short_periods, long_periods):
    short_mas = [get_ma(symbol, interval, period) for period in short_periods]
    long_mas = [get_ma(symbol, interval, period) for period in long_periods]
    
    for i in range(len(short_periods)):
        if short_mas[i] >= long_mas[i]:
            return False
    
    return True

def main():
    symbol = 'KRW-BTC'
    interval = 'minute1'
    short_periods = [5, 20]  # 단기 이동평균 기간
    long_periods = [60, 120]   # 장기 이동평균 기간
    
    while True:
        if buy_logic(symbol, interval, short_periods, long_periods):
            # 매수 로직
            print("매수 조건 만족 - 매수 실행")
            # 실제 매수 코드 작성
            # upbit.buy_market_order(symbol, krw_to_invest)
        
        if sell_logic(symbol, interval, short_periods, long_periods):
            # 매도 로직
            print("매도 조건 만족 - 매도 실행")
            # 실제 매도 코드 작성
            # upbit.sell_market_order(symbol, current_holding)

        time.sleep(60)  # 1분에 한 번씩 체크

if __name__ == "__main__":
    main()
