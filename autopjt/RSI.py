import pyupbit
import talib
import numpy as np
import time
from get_top_5_volume import coin_list  # get_top_5_volume.py에서 가져온 상위 5개 코인 리스트

# RSI와 볼린저 밴드 계산 함수
def calculate_rsi_bollinger_bands(ohlcv):
    close_prices = ohlcv['close'].values
    
    # RSI 계산
    rsi = talib.RSI(close_prices)
    
    # 볼린저 밴드 계산
    upper_band, middle_band, lower_band = talib.BBANDS(close_prices, timeperiod=20)
    
    return rsi[-1], upper_band[-1], middle_band[-1], lower_band[-1]

while True:
    for coin in coin_list:
        try:
            ohlcv = pyupbit.get_ohlcv(coin, interval='day', count=21)
            if ohlcv is not None and len(ohlcv) == 21:
                rsi, upper_band, middle_band, lower_band = calculate_rsi_bollinger_bands(ohlcv)
                print(f'{coin} - RSI: {rsi:.2f}, Upper Bollinger Band: {upper_band:.2f}, Middle Bollinger Band: {middle_band:.2f}, Lower Bollinger Band: {lower_band:.2f}')
            else:
                print(f'{coin} - 데이터 부족')
        except Exception as e:
            print(f'오류 발생: {e}')
    
    print("\n")
    time.sleep(5)
