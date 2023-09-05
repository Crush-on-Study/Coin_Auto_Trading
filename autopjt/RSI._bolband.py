import pyupbit
import ta

# get_top_5_volume.py에서 이미 구한 coin_list를 가져옴
from get_top_5_volume import real_ticker_list

# real_ticker_list 수정
real_ticker_list = ['KRW-' + ticker.split('-')[0] for ticker in real_ticker_list]

# 업비트 KRW 시장의 코인 목록 가져오기
upbit_coins = pyupbit.get_tickers(fiat="KRW")

# real_ticker_list에 포함된 코인 중 업비트 KRW 시장에 상장된 코인만 선택
target_coins = []
for idx in real_ticker_list:
    if idx in upbit_coins:
        target_coins.append(idx)

for ticker in real_ticker_list:
    # OHLCV 데이터 가져오기
    df = pyupbit.get_ohlcv(ticker, interval='day', count=20)  # 최근 20일 데이터 가져오기

    # 데이터가 없거나 'close' 열이 없는 경우 처리
    if df is None or 'close' not in df.columns:
        print(f"종목 {ticker}에 대한 데이터가 부족하거나 없습니다.")
    else:
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
