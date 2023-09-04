import pandas as pd
import ta

# coin_list 가져오기
from get_top_5_volume import coin_list

# 빈 데이터프레임 생성
combined_data = pd.DataFrame()

# 각 코인의 데이터를 읽어와서 하나의 데이터프레임에 추가
for ticker in coin_list:
    file_path = f'{ticker}_historical_price_data.csv'
    df = pd.read_csv(file_path)
    combined_data = pd.concat([combined_data, df], ignore_index=True)

# RSI 전략 정의
def rsi_strategy(data):
    # RSI 계산
    data['rsi'] = ta.momentum.RSIIndicator(data['close']).rsi()

    # RSI 신호 생성
    data['buy_signal'] = (data['rsi'] > 70)  # RSI가 70 이상일 때 매수 신호 생성
    data['sell_signal'] = (data['rsi'] < 30)  # RSI가 30 미만일 때 매도 신호 생성

    # 전략 적용
    position = 0  # 포지션 (0: 현금, 1: 보유)
    balance = 10000000  # 초기 자본금 1000만원을 디폴트로 지정.
    for i, row in data.iterrows():
        if row['buy_signal']:
            # 매수 조건 충족 시 구매
            position = balance / row['close']
            balance = 0
        elif row['sell_signal']:
            # 매도 조건 충족 시 판매
            balance = position * row['close']
            position = 0
    return balance

# 백테스팅 수행
final_balance = rsi_strategy(combined_data)

# 백테스팅 결과 출력
print(f"최종 자본금: {final_balance}")
