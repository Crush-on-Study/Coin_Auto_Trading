# 비동기 처리 방식 연구 중
import jwt
import uuid
import websocket
import json
import login
import requests
import time
import asyncio
import aiohttp
from balance import check_balance
import logging

# 종료를 위한 플래그
exit_flag = False

# 로그 설정
logging.basicConfig(filename='app.log', level=logging.INFO)

# 로그 메시지 기록
logging.debug('Debug 메시지')
logging.info('Info 메시지')
logging.warning('Warning 메시지')
logging.error('Error 메시지')
logging.critical('Critical 메시지')

# Upbit API 요청 함수
async def upbit_api_request(url, headers):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data

# WebSocket 및 관련 함수
def on_message(ws, message):
    data = json.loads(message)
    if "type" in data:
        if data["type"] == "ticker" and "content" in data:
            coin = data["content"]["code"]
            timestamp = data["content"]["tradeDate"]
            trade_price = data["content"]["tradePrice"]
            print(f"코인: {coin}, 시간: {timestamp}, 가격: {trade_price}")

def on_connect(ws):
    print("connected!")
    # 업비트 보유 자산 정보 조회

def on_error(ws, err):
    print(err)

def on_close(ws, close_status_code, close_msg):
    print(f"연결이 종료되었습니다. 코드: {close_status_code}, 메시지: {close_msg}")
    while True:
        try:
            print("재연결 시도 중...")
            ws.run_forever()
            print("재연결 성공!")
            break
        except Exception as e:
            print(f"재연결 실패. 에러: {e}")
            time.sleep(5)  # 재연결을 시도하기 전에 잠시 대기

def keyboard_input():
    global exit_flag
    while True:
        user_input = input("프로그램을 종료하려면 'q'를 누르세요: ")
        if user_input.strip().lower() == 'q':
            exit_flag = True
            ws_app.close()  # 웹소켓 연결 종료
            break

payload = {
    'access_key': login.id,
    'nonce': str(uuid.uuid4()),
}

jwt_token = jwt.encode(payload, login.pw)
authorization_token = 'Bearer {}'.format(jwt_token)
headers = {"Authorization": authorization_token}

websocket.enableTrace(True)  # 디버그 트레이스 모드 활성화

ws_app = websocket.WebSocketApp("wss://api.upbit.com/websocket/v1",
                                header=headers,
                                on_message=on_message,
                                on_open=on_connect,
                                on_error=on_error,
                                on_close=on_close)
ws_app.run_forever()

async def fetch_and_print_balance():
    while True:
        await asyncio.sleep(1)  # 1초마다 실행
        print("현재 보유 자산 정보:")
        check_balance()  # 잔고 조회 함수 호출

async def main():
    # 비동기 작업을 병렬로 실행
    tasks = [
        fetch_and_print_balance(),
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

