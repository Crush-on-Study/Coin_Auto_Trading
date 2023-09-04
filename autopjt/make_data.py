import pyupbit
import pandas as pd
from datetime import datetime, timedelta

# coin_list 가져오기
from get_top_5_volume import coin_list

# 데이터 수집 기간 설정 (과거 90일)
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

# 데이터 수집 및 저장
for ticker in coin_list:
    df = pyupbit.get_ohlcv(ticker, interval='day', to=end_date)
    df.to_csv(f'{ticker}_historical_price_data.csv')  # CSV 파일로 저장
    print(f'{ticker} 데이터 수집 및 저장 완료')

print("모든 데이터 수집 및 저장 완료")
