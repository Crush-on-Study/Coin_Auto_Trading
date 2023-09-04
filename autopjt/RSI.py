import pyupbit
import ta

# get_top_5_volume.py에서 이미 구한 coin_list를 가져옴
from get_top_5_volume import coin_list

for ticker in coin_list:
    # OHLCV 데이터 가져오기
    df = pyupbit.get_ohlcv(ticker, interval='day', count=20)  # 최근 20일 데이터 가져오기

    # RSI 계산
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()

    # 볼린저 밴드 계산
    bollinger = ta.volatility.BollingerBands(df['close'])
    df['bollinger_mavg'] = bollinger.bollinger_mavg()
    df['bollinger_hband'] = bollinger.bollinger_hband()
    df['bollinger_lband'] = bollinger.bollinger_lband()

    # 결과 출력
    print(f"종목: {ticker}")
    print(df[['rsi', 'bollinger_mavg', 'bollinger_hband', 'bollinger_lband']].tail())
    print("\n")
