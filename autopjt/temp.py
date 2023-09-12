# 비동기 처리 방식
import jwt
import uuid
import websocket
import json
import login
import time
import asyncio
import aiohttp
from balance import check_balance
from datetime import timedelta, datetime
import logging
from logging.handlers import RotatingFileHandler
import ta
import pandas as pd

log_filename = 'app.log'
max_log_size_bytes = 10 * 1024 * 1024  # 10 MB (최대 파일 크기)

# 로그 핸들러 생성
log_handler = RotatingFileHandler(log_filename, maxBytes=max_log_size_bytes, backupCount=5)  # 최대 5개의 백업 파일 유지

# 로그 포매터 설정
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)

# 로거에 핸들러 추가
logger = logging.getLogger(__name__)
logger.addHandler(log_handler)

# 로그 레벨 설정
logger.setLevel(logging.INFO)

# 로그 메시지 기록
logger.debug('Debug 메시지')
logger.info('Info 메시지')
logger.warning('Warning 메시지')
logger.error('Error 메시지')
logger.critical('Critical 메시지')

# Upbit API 요청 함수
async def upbit_api_request(url, headers=None, params=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            data = await response.json()
            return data

# WebSocket 메시지 처리 함수
def on_message(ws, message):
    data = json.loads(message)
    if "type" in data and data["type"] == "ticker" and "content" in data:
        coin = data["content"]["code"]
        timestamp = data["content"]["tradeDate"]
        trade_price = data["content"]["tradePrice"]
        print(f"코인: {coin}, 시간: {timestamp}, 가격: {trade_price}")

def on_connect(ws):
    print("connected!")

def on_error(ws, err):
    print(err)

def on_close(ws, close_status_code, close_msg):
    print(f"연결이 종료되었습니다. 코드: {close_status_code}, 메시지: {close_msg}")
    num_reconnect_attempts = 0  # 재시도 횟수 초기화
    while num_reconnect_attempts < 3:  # 최대 3번 재시도
        try:
            print("재연결 시도 중...")
            ws.run_forever()
            print("재연결 성공!")
            break
        except Exception as e:
            print(f"재연결 실패. 에러: {e}")
            # 백오프 전략 적용: 재연결 간격을 지수적으로 증가
            time.sleep(2 ** num_reconnect_attempts)
            num_reconnect_attempts += 1
    else:
        print("연속 실패로 프로그램 종료.")
        exit(1)  # 3번 연속 실패 후 프로그램 종료

payload = {
    'access_key': login.id,
    'nonce': str(uuid.uuid4()),
}

jwt_token = jwt.encode(payload, login.pw)
authorization_token = 'Bearer {}'.format(jwt_token)
headers = {"Authorization": authorization_token}

websocket.enableTrace(True)  # 디버그 트레이스 모드 활성화

# WebSocket 연결 및 실행 코드 추가
ws_app = websocket.WebSocketApp("wss://api.upbit.com/websocket/v1",
                                header=headers,
                                on_message=on_message,
                                on_open=on_connect,
                                on_error=on_error,
                                on_close=on_close)

ws_app.run_forever()

# 거래대금 상위 5종목의 실시간 가격 조회
async def fetch_top_5_volume_coins():
    while True:
        # Upbit API를 통해 거래대금이 가장 큰 코인 상위 5종목 조회
        url = "https://api.upbit.com/v1/market/all"
        markets = await upbit_api_request(url, headers)

        if not markets:
            print("거래 정보를 가져올 수 없습니다.")
            await asyncio.sleep(1)
            continue

        market_ids = [market["market"] for market in markets]
        url = f"https://api.upbit.com/v1/ticker?markets={','.join(market_ids)}"
        tickers = await upbit_api_request(url, headers)

        if not tickers:
            print("티커 정보를 가져올 수 없습니다.")
            await asyncio.sleep(1)
            continue

        # 거래대금 상위 5개 코인 추출 및 가격 출력
        sorted_tickers = sorted(tickers, key=lambda x: x["acc_trade_price_24h"], reverse=True)
        top_5_tickers = sorted_tickers[:5]
        for ticker in top_5_tickers:
            coin_name = ticker['market']
            trade_price = ticker['trade_price']
            print(f"{coin_name}의 현재 가격: {trade_price} KRW")

        await asyncio.sleep(1)  # 1초마다 실행
        
# 잔고 조회 및 수익률 조회 함수
async def fetch_and_print_balance():
    while True:
        await asyncio.sleep(1)  # 1초마다 실행
        print("현재 보유 자산 정보:")
        check_balance()  # 잔고 조회 함수 호출


# RSI를 1분 간격으로 업데이트하는 함수
async def update_rsi():
    while True:
        # 거래대금 상위 5개 코인 정보 가져오기
        url = "https://api.upbit.com/v1/market/all"
        markets = await upbit_api_request(url, headers)

        if not markets:
            print("거래 정보를 가져올 수 없습니다.")
            await asyncio.sleep(60)  # 60초(1분) 대기 후 다시 시도
            continue

        market_ids = [market["market"] for market in markets]
        url = f"https://api.upbit.com/v1/ticker?markets={','.join(market_ids)}"
        tickers = await upbit_api_request(url, headers)

        if not tickers:
            print("티커 정보를 가져올 수 없습니다.")
            await asyncio.sleep(60)  # 60초(1분) 대기 후 다시 시도
            continue

        # 거래대금 상위 5개 코인 추출
        sorted_tickers = sorted(tickers, key=lambda x: x["acc_trade_price_24h"], reverse=True)
        top_5_tickers = sorted_tickers[:5]

        # 각 코인에 대한 RSI 계산 및 출력
        for ticker in top_5_tickers:
            coin_name = ticker['market']

            # 코인에 대한 1분 봉 데이터 가져오기
            url = f"https://api.upbit.com/v1/candles/minutes/1"
            params = {"market": coin_name, "count": 14}  # 14개의 최근 봉 데이터를 가져옴 (1분 봉)
            candle_data = await upbit_api_request(url, headers, params)


            if not candle_data:
                print(f"{coin_name}의 1일 봉 데이터를 가져올 수 없습니다.")
                continue

            # 봉 데이터를 DataFrame으로 변환
            df = pd.DataFrame(candle_data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.set_index("timestamp", inplace=True)

            # RSI 계산
            df["rsi"] = ta.momentum.RSIIndicator(df["trade_price"]).rsi()

            # 최근 RSI 값 가져오기
            recent_rsi = df.iloc[-1]["rsi"]

            # 코인의 현재 가격 가져오기
            trade_price = ticker['trade_price']

            # 결과 출력
            print(f"{coin_name}의 현재 가격: {trade_price} KRW, 1일 봉 RSI: {recent_rsi:.2f}")

        await asyncio.sleep(30)  # 30초 대기


async def main():
    # 비동기 작업을 병렬로 실행
    tasks = [
        fetch_top_5_volume_coins(),
        update_rsi(),  # RSI 업데이트 함수 추가
        fetch_and_print_balance(),  # 잔고 조회 함수 추가
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
