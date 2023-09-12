# 타 블로거의 RSI 실시간 값 조회하는 코드 (분석해보자)

import requests
from ast import literal_eval
import time
import datetime
import numpy as np
import pandas as pd
import operator
import threading
import websockets
import asyncio
import json
import math
import unicodedata
from wcwidth import wcswidth
from multiprocessing import Process

def fmt(x, w, align='r'):  
    x = str(x) 
    l = wcswidth(x) 
    s = w-l
    if s <= 0: 
        return x 
    if align == 'l': 
        return x + ' '*s 
    if align == 'c': 
        sl = s//2 
        sr = s - sl 
        return ' '*sl + x + ' '*sr 
    return ' '*s + x

#RSI계산 함수
def rsi_calculate(l, n, sample_number): #l = price_list, n = rsi_number
    
    diff=[]
    au=[]
    ad=[]
    
    if len(l) != sample_number: #url call error
        return -1 
    for i in range(len(l)-1):
        diff.append(l[i+1]-l[i]) #price difference
    
    au = pd.Series(diff) #list to series
    ad = pd.Series(diff)

    au[au<0] = 0 #remove ad
    ad[ad>0] = 0 #remove au

    _gain = au.ewm(com = n, min_periods = sample_number -1).mean() #Exponentially weighted average
    _loss = ad.abs().ewm(com = n, min_periods = sample_number -1).mean()
    RS = _gain/_loss

    rsi = 100-(100 / (1+RS.iloc[-1]))
    
    return rsi, _gain.iloc[-1], _loss.iloc[-1]

#마켓코드조회
def market_code():

    url = "https://api.upbit.com/v1/market/all"
    querystring = {"isDetails":"false"}
    response = requests.request("GET", url, params=querystring)

    #코인이름 - 마켓코드 매핑
    r_str = response.text
    r_str = r_str.lstrip('[') #첫 문자 제거
    r_str = r_str.rstrip(']') #마지막 문자 제거
    r_list = r_str.split("}") #str를 }기준으로 쪼개어 리스트로 변환

    name_to_code = {}
    code_list = []

    for i in range(len(r_list)-1):
        r_list[i] += "}"
        if i!=0:
            r_list[i] = r_list[i].lstrip(',')
        r_dict = literal_eval(r_list[i]) #element to dict
        if r_dict["market"][0]=='K': #원화거래 상품만 추출
            temp_dict = {r_dict["market"]:r_dict["korean_name"]}
            code_list.append(r_dict["market"]) #코드 리스트
            name_to_code.update(temp_dict) #코인이름 - 코드 매핑(딕셔너리)
    return code_list, name_to_code

def RSI_analysis_RESTAPI(code_list, name_to_code, time_unit, unit, rsi_number, target_up, target_down,rsi_sample, option): #1분 RSI 분석

    start = time.time()

    url = "https://api.upbit.com/v1/candles/"+time_unit+"/"+str(unit) # 1, 3, 5, 10, 15, 30, 60, 240
    
    coin_to_price = {}
    rsi_list = []
    sample = rsi_sample
    request_limit_per_second = -10
    request_count = 0
    request_time_list = np.array([])
    
    data_dict = {}
    
    for i in range(len(code_list)):
        data_dict[code_list[i]] = [[0 for col in range(sample)],0,0,0,0,0,0,0] #currentprice_list, rsi_signal_count , ttm, price, ori_gain, ori_loss, _gain, _loss 

    #코인별 시간별 가격 
    for i in range(len(code_list)):
        querystring = {"market":code_list[i],"count":str(sample)} #캔들 갯수
        if (request_count<request_limit_per_second): #max api 요청수, 분당 600, 초당 10회
            request_count+=1 #요청수 1회 증가
        else:
            request_time_sum = np.sum(request_time_list[request_limit_per_second:])
            if (request_time_sum >= 1):
                pass
            else:
                time.sleep(1-request_time_sum)

        times = time.time() #요청 시작 시간
        response = requests.request("GET", url, params=querystring)
        time.sleep(1)
        request_time_list = np.append(request_time_list, time.time()-times) #요청 끝 시간
        
        last_time = datetime.datetime.now()
        
        r_str = response.text
        r_str = r_str.lstrip('[') #첫 문자 제거
        r_str = r_str.rstrip(']') #마지막 문 제거
        r_list = r_str.split("}") #str를 }기준으로 쪼개어 리스트로 변환
        

        date_to_price = {}
        price_list = []

        for j in range(len(r_list)-1):
            r_list[j] += "}"
            if j!=0:
                r_list[j] = r_list[j].lstrip(',')
            r_dict = literal_eval(r_list[j]) #stinrg to dict 
            temp_dict = {r_dict["candle_date_time_kst"]:r_dict["trade_price"]}
            date_to_price.update(temp_dict) #시간-가격 매핑
            price_list.append(r_dict["trade_price"]) #가격 리스트
        price_list.reverse() #order : past -> now 
        temp_dict = {code_list[i]:date_to_price}
        coin_to_price.update(temp_dict) #코인-시간-가격 매핑
        data_dict[code_list[i]][0] = price_list

    return data_dict, last_time

async def RSI_get(code_list, name_to_code, data_dict, data, minute, rsi_number, rsi_sample, target_up, target_down, last_time):
    
    code = data['cd']
    ttm = data['ttm']
    
    if data_dict[code][4] == 0 and data_dict[code][5] == 0:
        rsi, data_dict[code][4], data_dict[code][5] = rsi_calculate(data_dict[code][0], rsi_number, rsi_sample) 
        data_dict[code][6] = data_dict[code][4]
        data_dict[code][7] = data_dict[code][5]
        if datetime.datetime.now().today().minute == last_time.today().minute:
            data_dict[code][0][-1] = data['tp']
            data_dict[code][2] = ttm
            return data_dict
            
    if (int(int(data_dict[code][2])/(minute*100)) != int(int(ttm)/(minute*100))):
        data_dict[code][0][-2] = data_dict[code][0][-1] 
        data_dict[code][4] = data_dict[code][6]
        data_dict[code][5] = data_dict[code][7]
            
    data_dict[code][0][-1] = data['tp']
            
    if int(int(data_dict[code][2])/20) != int(int(ttm)/20): #10초마다 rsi계산
        data_dict[code][2] = ttm #시간업데이트
                    
        if (data_dict[code][0][-1] - data_dict[code][0][-2]) > 0:
            data_dict[code][6] = (1-1/rsi_number) * data_dict[code][4] + 1/rsi_number * (data_dict[code][0][-1] - data_dict[code][0][-2])
            data_dict[code][7] = (1-1/rsi_number) * data_dict[code][5] + 1/rsi_number * 0
        else:
            data_dict[code][6] = (1-1/rsi_number) * data_dict[code][4] + 1/rsi_number * 0
            data_dict[code][7] = (1-1/rsi_number) * data_dict[code][5] + 1/rsi_number * -(data_dict[code][0][-1] - data_dict[code][0][-2])
                    	
        RS = data_dict[code][6] / data_dict[code][7]
                    	
        rsi = 100-(100 / (1+RS))
                
        if (rsi > target_up):
            data_dict[code][1] += 1
            print('%s' %fmt(name_to_code[code], 23, 'l'), "RSI:%d" %rsi, '  Today : %-6s'%data_dict[code][1], " " , time.strftime('%c', time.localtime(time.time())))
        elif (rsi < target_down):
            data_dict[code][1] -= 1
            print('%s' %fmt(name_to_code[code], 23, 'l'), "RSI:%d" %rsi, '  Today : %-6s'%data_dict[code][1], " " ,time.strftime('%c', time.localtime(time.time())))
    return data_dict


async def RSI_analysis_websocket(code_list, name_to_code, minute, rsi_number, target_up, target_down,rsi_sample, option):
    
    uri = "wss://api.upbit.com/websocket/v1"
    
    data_dict, last_time = RSI_analysis_RESTAPI(code_list, name_to_code, "minutes", minute,rsi_number, target_up, target_down, rsi_sample, option)
    
    async with websockets.connect(uri) as websocket:
            
        subscribe_fmt = [
            {"ticket":"test"},
            {"type": "ticker",
             "codes": code_list,
             "isOnlyRealtime":True
            },
            {"format":"SIMPLE"}
        ]
        subscribe_data = json.dumps(subscribe_fmt)
        await websocket.send(subscribe_data)
        
        while True:
            data = await websocket.recv()
            data = json.loads(data)
            data_dict = await RSI_get(code_list, name_to_code, data_dict, data, minute, rsi_number, rsi_sample, target_up, target_down, last_time)
            
def list_chuck(arr, n):
    return [arr[i: i + n] for i in range(0, len(arr), n)]
    
def mainprocess(code_list, name_to_code):
    
    rsi_number = 14
    minute = 1
    target_up = 70
    target_down = 40
    rsi_sample = 200
    option = "multi"
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(RSI_analysis_websocket(code_list, name_to_code, minute, rsi_number, target_up, target_down,rsi_sample, option))
    loop.close()
    
def main():
    
    
    print("#########Analysis Start##########\n")
    code_list, name_to_code = market_code()
   	
    divided_codelist = list_chuck(code_list, int(len(code_list)/4))
    
    code_list1 = divided_codelist[0]
    code_list2 = divided_codelist[1]
    code_list3 = divided_codelist[2]
    code_list4 = divided_codelist[3]

    for i in range(int(len(code_list)/4)*4, len(code_list)):
    	code_list4.append(code_list[i])
    	
    proc1 = Process(target = mainprocess, args = (code_list1, name_to_code))
    proc2 = Process(target = mainprocess, args = (code_list2, name_to_code))
    proc3 = Process(target = mainprocess, args = (code_list3, name_to_code))
    proc4 = Process(target = mainprocess, args = (code_list4, name_to_code))
    proc1.start()
    proc2.start()
    proc3.start()
    proc4.start()
    proc1.join()
    proc2.join()
    proc3.join()
    proc4.join()

    
main()

