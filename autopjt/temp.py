# 비동기 처리 방식 연구 중
import jwt,uuid
import websocket
import json
import requests
import time
import login, asyncio , aiohttp
from bs4 import BeautifulSoup


# Upbit API 요청 함수
async def upbit_api_request(url, headers):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data

# 상위 5종목 가져와라.
def fetch_top_5_volume_coins():
    url = "https://coinmarketcap.com/exchanges/upbit/"
    
    # 웹페이지에서 데이터 가져오기
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 상위 5종목 데이터를 추출합니다.
        top_5_coins = []
        table = soup.find("table", {"id": "exchange-markets"})
        rows = table.find("tbody").find_all("tr")
        for row in rows:
            columns = row.find_all("td")
            market_name = columns[1].text.strip()  # 거래소 이름
            base_currency = columns[3].text.strip()  # 기초 통화
            if base_currency == "KRW":
                coin_name = market_name.replace("KRW-", "")
                top_5_coins.append(coin_name)
                if len(top_5_coins) == 5:
                    break
        
        return top_5_coins
    else:
        print("CoinMarketCap 웹페이지에 접근할 수 없습니다.")
        return []


async def check_sell_conditions(coin_name):
    # Upbit API 엔드포인트
    endpoint = f"https://api.upbit.com/v1/accounts"
    
    # Upbit API 요청 헤더 설정
    payload = {
        'access_key': login.id,
        'nonce': str(uuid.uuid4()),
    }
    jwt_token = jwt.encode(payload, login.pw)
    authorization_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorization_token}
    
    # Upbit API 호출하여 보유 중인 코인 정보 가져오기
    data = await upbit_api_request(endpoint, headers)
    
    for item in data:
        if item["currency"] == coin_name:
            balance = float(item["balance"])
            avg_buy_price = float(item["avg_buy_price"])
            current_price = await get_current_coin_price(coin_name)
            
            if current_price is not None:
                profit_percentage = ((current_price - avg_buy_price) / avg_buy_price) * 100
                
                # 매도 조건 검사
                if profit_percentage >= 2.05 or profit_percentage <= -1.95:
                    # 시장가로 전량 매도
                    await sell_coin(coin_name, balance)
                    print(f"매도 조건 충족: {coin_name} 매도 완료")
            else:
                print(f"{coin_name} 코인 가격 정보를 가져올 수 없습니다.")
                
async def get_current_coin_price(coin_name):
    # Upbit API 엔드포인트
    endpoint = f"https://api.upbit.com/v1/ticker?markets=KRW-{coin_name}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as response:
            data = await response.json()
            if data:
                current_price = data[0]["trade_price"]
                return current_price
            return None

async def sell_coin(coin_name, amount):
    # 매도 코드를 여기에 추가하세요
    # 예: 실제 거래소 API를 사용하여 코인을 매도하는 코드
    pass


# 현재 코인 가격 조회
def get_current_coin_price(coin):
    ticker_url = f"https://api.upbit.com/v1/ticker?markets=KRW-{coin}"
    response = requests.get(ticker_url)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            current_price = data[0]["trade_price"]
            return current_price
    return None

# 현재 내 계좌 조회
def get_upbit_balance():
    payload = {
        'access_key': login.id,
        'nonce': str(uuid.uuid4()),
    }
    jwt_token = jwt.encode(payload, login.pw)
    authorization_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorization_token}
    
    response = requests.get("https://api.upbit.com/v1/accounts", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        for item in data:
            currency = item["currency"]
            balance = float(item["balance"])  # 문자열을 숫자로 변환
            avg_buy_price = float(item["avg_buy_price"])  # 문자열을 숫자로 변환
            
            if currency == "KRW":
                # KRW는 원화 잔고이므로 건너뜁니다.
                continue
            
            # 현재 코인의 가격 조회
            current_price = get_current_coin_price(currency)
            
            if current_price is not None:  # None이 아닐 때만 계산
                balance_krw = balance * avg_buy_price if currency != "KRW" else balance
                # 수익률 계산
                profit_percentage = ((current_price - avg_buy_price) / avg_buy_price) * 100
                # 계산 혹은 출력 로직 추가
                print(f"코인: {currency}, 수량: {balance}, 평균 매수 가격: {avg_buy_price}, 현재 가격: {current_price}, 현재 수익률: {profit_percentage:.2f}%")
            else:
                print(f"{currency} 코인 가격 정보를 가져올 수 없습니다.")
    else:
        print(f"에러 타입 {response.status_code} : 업비트 API 조회 실패")


def on_message(ws, message):
    # do something
    data = message.decode('utf-8')
    print(data)

def on_connect(ws):
    print("connected!")
    # 업비트 보유 자산 정보 조회
    get_upbit_balance()

def on_error(ws, err):
    print(err)

def on_close(ws, close_status_code, close_msg):
    print(f"연결이 종료되었습니다. 코드: {close_status_code}, 메시지: {close_msg}")
    
    # 연결이 끊겼을 때 다시 연결하기 위한 로직
    while True:
        try:
            print("재연결 시도 중...")
            ws.run_forever()
            print("재연결 성공!")
            break
        
        except Exception as e:
            print(f"재연결 실패. 에러: {e}")
            time.sleep(5)  # 재연결을 시도하기 전에 잠시 대기

payload = {
    'access_key': login.id,
    'nonce': str(uuid.uuid4()),
}

jwt_token = jwt.encode(payload, login.pw)
authorization_token = 'Bearer {}'.format(jwt_token)
headers = {"Authorization": authorization_token}

ws_app = websocket.WebSocketApp("wss://api.upbit.com/websocket/v1",
                                header=headers,
                                on_message=on_message,
                                on_open=on_connect,
                                on_error=on_error,
                                on_close=on_close)
ws_app.run_forever()

# main 함수에서 비동기 작업 시작
async def main():
    coins_to_check = fetch_top_5_volume_coins()  # 거래대금 상위 5종목 가져오기
    print("거래대금 상위 5종목:", coins_to_check)
    tasks = [check_sell_conditions(coin) for coin in coins_to_check]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
