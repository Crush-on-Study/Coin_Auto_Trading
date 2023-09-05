import pyupbit
import os
import pandas as pd
from datetime import datetime, timedelta

# real_ticker_list 가져오기
from get_top_5_volume import real_ticker_list

# real_ticker_list 수정
real_ticker_list = ['KRW-' + ticker.split('-')[0] for ticker in real_ticker_list]

# 업비트 KRW 시장의 코인 목록 가져오기
upbit_coins = pyupbit.get_tickers(fiat="KRW")

# 현재 날짜 문자열 생성
today_date = datetime.now().strftime('%Y-%m-%d')

# 데이터 수집 기간 설정 (과거 90일)
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

# csv_folder 폴더 경로 (AUTOPJT 폴더 안에 있는 경우)
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_folder = os.path.join(script_dir, 'csv_folder')

# real_ticker_list에 포함된 코인 중 업비트 KRW 시장에 상장된 코인만 선택
target_coins = []
for idx in real_ticker_list:
    if idx in upbit_coins:
        target_coins.append(idx)

# target_coins 리스트에 담긴 코인들의 ohlcv 정보 가져오기
ohlcv_data = {}
for coin in target_coins:
    try:
        df = pyupbit.get_ohlcv(coin, interval='day', to=end_date)
        ohlcv_data[coin] = df
        print(f'{coin} 데이터 수집 완료')
    except Exception as e:
        print(f'오류 발생: {e}')

# ohlcv 데이터를 파일로 저장
for coin, df in ohlcv_data.items():
    try:
        # 'timestamp' 열을 추가하여 열 순서를 조정
        df['timestamp'] = df.index
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        
        file_name = f'{today_date} {coin.split("-")[1]}.csv'
        file_path = os.path.join(csv_folder, file_name)
        df.to_csv(file_path)
        print(f'{coin} 데이터 저장 완료')
    except Exception as e:
        print(f'오류 발생: {e}')

print("모든 데이터 수집 및 저장 완료")
