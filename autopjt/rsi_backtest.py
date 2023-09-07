import os
import pandas as pd
import ta
from datetime import datetime, timedelta

# 현재 스크립트 파일의 디렉터리 경로
script_dir = os.path.dirname(os.path.abspath(__file__))

# csv_folder 폴더 경로 (AUTOPJT 폴더 안에 있는 경우)
csv_folder = os.path.join(script_dir, 'csv_folder')

# 현재 날짜 구하기
today_date = datetime.now().strftime('%Y-%m-%d')

# RSI 전략 정의    
def rsi_strategy(data):
    # RSI 계산
    data['rsi'] = ta.momentum.RSIIndicator(data['close']).rsi()

    # 초기 자본금 및 포지션 설정
    initial_balance = 10000000  # 초기 자본금
    balance = initial_balance
    position = 0
    buy_price = None  # 구매 가격을 저장할 변수

    # 거래 로그 기록
    trade_log = []

    # 전략 적용
    for i, row in data.iterrows():
        if buy_price is not None and (row['close'] / buy_price - 1) >= 0.0205:
            # 수익률이 2.05% 이상이면 매도
            if position > 0:
                balance = position * row['close']
                position = 0
                trade_log.append(('sell', row['timestamp'], row['close']))
                buy_price = None  # 매도한 경우 구매 가격 초기화
                
            elif buy_price is not None and (row['close'] / buy_price - 1) <= -0.0195:
                # 손절 기능: 수익률이 -1.95% 이하이면 매도
                if position > 0:
                    balance = position * row['close']
                    position = 0
                    trade_log.append(('sell', row['timestamp'], row['close']))
                    buy_price = None  # 손절한 경우 구매 가격 초기화
                    
        elif 25 <= row['rsi'] <= 35:
            # RSI가 25 이상 35 이하일 때 매수
            if balance > 0:
                position = balance / row['close']
                balance = 0
                trade_log.append(('buy', row['timestamp'], row['close']))
                buy_price = row['close']  # 매수한 경우 구매 가격 저장

    # 최종 자본금 계산
    final_balance = balance if balance > 0 else position * data.iloc[-1]['close']
    
    return final_balance, trade_log

# CSV 폴더에서 파일 목록 가져오기
csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]

# 오늘과 다른 날짜의 파일을 삭제
for file_name in csv_files:
    # 파일 이름에서 날짜 추출
    file_date = file_name.split(' ')[0]
    
    if file_date != today_date:
        file_path = os.path.join(csv_folder, file_name)  # 파일 경로
        os.remove(file_path)
        print(f'{file_name} 파일을 삭제했습니다.')
    else:
        print(f'{file_name}은 오늘의 데이터입니다. 백테스팅을 실행합니다.')

# 파일별로 백테스팅 수행
for file_name in csv_files:
    # 파일 이름에서 날짜 추출
    file_date = file_name.split(' ')[0]
    
    if file_date == today_date:
        file_path = os.path.join(csv_folder, file_name)  # 파일 경로
        coin_name = file_name.split(' ')[1].split('.')[0]  # 코인 이름 추출
        # CSV 파일 불러오기
        try:
            df = pd.read_csv(file_path)

            # 컬럼 이름 변경
            df.rename(columns={"Unnamed: 0": "timestamp"}, inplace=True)

            # 백테스팅 수행
            result = rsi_strategy(df)
            
            if result is not None:
                final_balance, trade_log = result

            # 결과 출력
            print(f'{coin_name} 백테스팅 결과 - 최종 자본금: {final_balance}')
            print('거래 로그:')
            for action, timestamp, price in trade_log:
                print(f"{timestamp}: {action} at {price}")
            else:
                print(f'{coin_name} 데이터에 대한 백테스팅 결과가 없습니다.')
        except Exception as e:
            print(f'오류 발생: {e}')
