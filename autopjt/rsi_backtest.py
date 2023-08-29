import RSI
import random
import balance
import login,pyupbit

upbit = pyupbit.Upbit(login.id,login.pw)

def random_num(length):
    strategy = []
    for _ in range(length):
        rsi = random.randint(20,85)
        strategy.append(rsi)
    
    return strategy

def rsi_backtest(strategy):
    initial_balance = balance.check_remaining_krw()
    initial_balance = float(initial_balance)
    # print('19번 코드',initial_balance)
    if initial_balance < 1000000:
        initial_balance = 1000000
    remaining_balance = initial_balance
    holdings = 0  # 보유한 코인의 수량

    for i in range(len(strategy)):
        rsi = strategy[i]  # 간단한 예제를 위해 RSI 값만 활용

        if rsi <= 30:  # RSI가 30 이하인 경우 매수
            buy_price = 100  # 임의의 매수 가격 설정
            buy_quantity = remaining_balance // buy_price  # 보유 가능한 수량 계산
            holdings += buy_quantity
            remaining_balance -= buy_price * buy_quantity
        
        elif rsi >= 70:  # RSI가 70 이상인 경우 매도
            sell_price = 150  # 임의의 매도 가격 설정
            remaining_balance += sell_price * holdings
            holdings = 0

    final_balance = remaining_balance + (holdings * sell_price)
    return final_balance

if __name__ == "__main__":
    strategy = random_num(20) # RSI 지수 20개 넣어보자
    print(f'Input된 임의의 RSI값들 : {strategy}')
    result = rsi_backtest(strategy)
    print(f'시뮬레이션 결과 : {result}')
