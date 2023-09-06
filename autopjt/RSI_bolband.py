import pyupbit
import ta
import login
import requests

webhook_url = 'My_Slack_webhook'

# get_top_5_volume.py에서 이미 구한 coin_list를 가져옴
from get_top_5_volume import real_ticker_list

upbit = pyupbit.Upbit(login.id, login.pw)  # login.py에서 API 키 정보 가져오기

# real_ticker_list 수정
real_ticker_list = ['KRW-' + coin.split('-')[0] for coin in real_ticker_list]

# 업비트 KRW 시장의 코인 목록 가져오기
upbit_coins = pyupbit.get_tickers(fiat="KRW")

# real_ticker_list에 포함된 코인 중 업비트 KRW 시장에 상장된 코인만 선택
target_coins = []
for coin in real_ticker_list:
    if coin in upbit_coins:
        target_coins.append(coin)
        
# Slack에 메시지 보내기
def send_slack_message(message):
    payload = {
        'text': message,
    }
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print('Slack에 메시지를 성공적으로 보냈습니다.')
        else:
            print('Slack에 메시지 보내기 실패:', response.status_code, response.text)
    except Exception as e:
        print('Slack에 메시지 보내기 오류:', str(e))

# RSI 값이 포함된 코인의 개수를 저장할 변수
count_rsi_condition = 0

# 매수 함수 정의
def execute_market_buy_order(coin, amount_to_buy_per_coin):
    try:
        upbit.buy_market_order(coin, amount_to_buy_per_coin)
        print(f"{coin} 시장가 매수 주문이 실행되었습니다. 매수량: {amount_to_buy_per_coin}")
        # 매수 주문이 성공했을 때 메시지 보내기
        send_slack_message(f'{coin} 시장가 매수 주문이 실행되었습니다.')
    except Exception as e:
        print(f"시장가 매수 주문 실행 중 오류 발생: {e}")

# 매도 함수 정의
def execute_market_sell_order_with_profit(coin, buy_price):    
    try:
        # 현재 코인의 가격 조회
        orderbook = pyupbit.get_orderbook(ticker=coin)
        # print(orderbook[0])        
        current_price = orderbook['orderbook_units'][0]['ask_price']
        
        # 수익률 계산
        profit_percentage = ((current_price - buy_price) / buy_price) * 100
        
        print("현재 가격:", current_price)
        print("수익률:", profit_percentage)

        if profit_percentage >= 2.05:  # 수익률이 2.05% 이상이면 매도 주문 실행
            upbit.sell_market_order(coin, upbit.get_balance(coin))  # 보유 중인 모든 코인 매도
            print(f"{coin} 시장가 매도 주문이 실행되었습니다. 수익률: {profit_percentage:.2f}%")
            # 매도 주문이 성공했을 때 메시지 보내기
            send_slack_message(f'{coin} 시장가 매도 주문이 실행되었습니다. 수익률: {profit_percentage:.2f}%')
        else:
            print("매도 타이밍이 아닙니다.")
    except Exception as e:
        print(f"시장가 매도 주문 실행 중 오류 발생: {e}")



# 메인 함수
def main():
    global count_rsi_condition  # count_rsi_condition 변수를 global로 선언
    count_rsi_condition = 0  # 초기화
    for coin in real_ticker_list:
        # OHLCV 데이터 가져오기
        df = pyupbit.get_ohlcv(coin, interval='day', count=20)  # 최근 20일 데이터 가져오기

        # 데이터가 없거나 'close' 열이 없는 경우 처리
        if df is None or 'close' not in df.columns:
            print(f"종목 {coin}에 대한 데이터가 부족하거나 없습니다.")
        else:
            # RSI 계산
            df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()

            # 볼린저 밴드 계산
            bollinger = ta.volatility.BollingerBands(df['close'])
            df['bollinger_mavg'] = bollinger.bollinger_mavg()
            df['bollinger_hband'] = bollinger.bollinger_hband()
            df['bollinger_lband'] = bollinger.bollinger_lband()

            # 조건에 맞으면 카운트 증가
            if 25 <= df.iloc[-1]['rsi'] <= 35:
                count_rsi_condition += 1

            # 결과 출력
            print(f"종목: {coin}")
            print(df[['rsi', 'bollinger_mavg', 'bollinger_hband', 'bollinger_lband']].tail())
            print("\n")

    # RSI 값이 25에서 35 사이에 있는 코인의 개수 출력
    print(f"RSI 값이 25에서 35 사이에 있는 코인의 개수: {count_rsi_condition}")

    # 조건에 맞는 코인이 있을 경우, 원화 잔고를 나눠서 매수
    if count_rsi_condition > 0:
        try:
            krw_balance = upbit.get_balance("KRW")  # 현재 원화 잔고 조회
            if krw_balance >= 5000: # 비트코인의 경우는 5000원부터 매매가 가능
                amount_to_buy_per_coin = krw_balance / count_rsi_condition
                for coin in real_ticker_list:
                    # 특정 조건에 따라 시장가 매수 주문 실행
                    # 예: RSI가 70 이상인 경우 KRW-BTC 시장에서 원화 잔고 전체를 시장가 주문으로 매수
                    if 25 <= df.iloc[-1]['rsi'] <= 35:
                        execute_market_buy_order(coin, amount_to_buy_per_coin)
            else:
                print("원화 잔고가 부족합니다.")
        except Exception as e:
            print(f"시장가 매수 주문 실행 중 오류 발생: {e}")

    # 매도 주문 실행 함수 호출
    for coin in real_ticker_list:
        # 현재 보유 중인 코인의 매수 가격 조회
        buy_price = upbit.get_avg_buy_price(coin)
        balance = upbit.get_balance(coin)  # 보유 중인 코인 수량 조회
        print('내 보유 코인과 현재 호가', coin, buy_price, balance)
        if buy_price:  # 매수 기록이 있는 코인만 처리
            execute_market_sell_order_with_profit(coin, buy_price)

# 메인 함수 호출
if __name__ == "__main__":
    main()
