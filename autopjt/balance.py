import login
import pyupbit

def check_balance():
    upbit = pyupbit.Upbit(login.id, login.pw)
    my_account = upbit.get_balances()  # 내 잔고의 모든 코인 조회
    valid_markets = pyupbit.get_tickers()
    
    for coin_info in my_account:
        coin_balance = coin_info['balance']
        avg_buy_price = coin_info['avg_buy_price']
        unit_currency = coin_info['unit_currency']
        currency = coin_info['currency']
        
        if f'{unit_currency}-{currency}' in valid_markets:
            print(f"보유 코인: {currency}, 보유 수량: {coin_balance} {unit_currency}, 평균 매수가: {avg_buy_price} {unit_currency}")
            ticker = f"{unit_currency}-{currency}"
            current_price = pyupbit.get_current_price(ticker)            
            current_price = float(current_price)
            avg_buy_price = float(avg_buy_price)
            
            profit_rate = ((current_price-avg_buy_price) / avg_buy_price) * 100
            print(f"현재 가격: {current_price} {unit_currency}")
            print(f"수익률: {profit_rate:.2f}%")
            
        else:
            continue
        
def check_remaining_krw():
    upbit = pyupbit.Upbit(login.id, login.pw)
    my_account = upbit.get_balances()
    for coin_info in my_account:
        if coin_info.get('currency') == 'KRW':
            print(f"남은 원화 잔고: {coin_info['balance']} KRW")
            return coin_info['balance']
    
    return 0

if __name__ == "__main__":
    check_balance()
    result = check_remaining_krw()
