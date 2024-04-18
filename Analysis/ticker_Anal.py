# 단순 수익률 계산 및 시각화를 통한 자산 추이 변동을 확인하기 위한 간단한 프로그램
import pandas as pd
import requests
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
import matplotlib.pyplot as plt

# 이 함수는 업비트 API에서 실시간 호가 정보를 가져옴.
# API 키가 필요 없으므로 headers는 생략.
def get_current_price_from_upbit(ticker):
    # 업비트 시세 정보를 조회하는 URL
    url = f"https://api.upbit.com/v1/ticker?markets={ticker}"
    response = requests.get(url)
    data = response.json()
    
    # 현재 가격을 반환.
    return data[0]['trade_price'] if data else None

# 이 함수는 엑셀 파일에서 데이터를 읽고, 현재 가격 정보를 추가하여 수익률과 현재 수익금을 계산.
def calculate_return_and_profit(file_path):
    df = pd.read_excel(file_path, engine='openpyxl')
    
    # 현재 가격, 수익률, 현재 수익금을 저장할 빈 리스트를 생성
    current_prices = []
    return_rates = []
    current_profits = []
    profit_changes = []
    
    # 각 티커에 대해 반복하며 현재 가격을 조회하고 수익률을 계산
    for i, row in df.iterrows():
        # API에서 티커의 현재 가격을 가져옴
        current_price = get_current_price_from_upbit('KRW-' + row['Ticker'])
        # 현재 가격을 리스트에 추가.
        current_prices.append(current_price)
        # 수익률을 계산하여 리스트에 추가.
        return_rate = ((current_price - row['Avg_BUY']) / row['Avg_BUY']) * 100
        return_rates.append(return_rate)
        # 현재 수익금을 계산하여 리스트에 추가.
        current_profit = row['Total'] * (1 + return_rate / 100)
        current_profits.append(current_profit)
        # 현재 변동금액을 계산하여 리스트에 추가.
        profit_change = (current_price - row['Avg_BUY']) * row['Amount']
        profit_changes.append(profit_change)
    
    # 현재 가격, 수익률, 현재 수익금을 데이터프레임에 추가.
    df['Current_Price'] = current_prices
    df['Return_Rate'] = return_rates
    df['Current_Profit'] = current_profits
    df['Profit_Change'] = profit_changes
    
    # 합계를 계산하여 맨 아래에 추가.
    summary = pd.DataFrame({
        'Ticker': ['Total'],
        'Avg_BUY': [None],
        'Amount': [None],
        'Total': [df['Total'].sum()],
        'Current_Price': [None],
        'Return_Rate': [None],
        'Current_Profit': [df['Current_Profit'].sum()],
        'Profit_Change': [df['Profit_Change'].sum()]
    })
    df_final = pd.concat([df, summary], ignore_index=True)
    
    # 결과를 새로운 엑셀 파일에 저장.
    new_file_path = file_path.replace('.xlsx', '_updated_with_totals.xlsx')
    df_final.to_excel(new_file_path, index=False)
    
    return new_file_path

def save_and_insert_chart_with_values(df, excel_file_path):
    # 'Total' 행 제외 (nan으로 뜨는데 순서 잘못 지켜서 걍 없앰 ㅋ)
    df_plot = df[df['Ticker'] != 'Total']

    # 막대 그래프
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(df_plot['Ticker'], df_plot['Profit_Change'], color='skyblue')
    
    # 막대에 텍스트(수익률) 추가
    for bar, return_rate in zip(bars, df_plot['Return_Rate']):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, f'{return_rate:.2f}%', 
                va='bottom' if yval < 0 else 'top', ha='center', color='black', fontsize=8)
    
    plt.xlabel('Ticker')
    plt.ylabel('Profit Change')
    plt.title('Profit Change by Ticker with Return Rate')
    plt.axhline(0, color='grey', linewidth=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # 그래프 PNG 파일로 저장
    chart_image_path = 'profit_change_chart.png'
    plt.savefig(chart_image_path)
    plt.close() 
    
    # 엑셀 파일에 이미지 삽입
    wb = load_workbook(excel_file_path)
    ws = wb.active
    img = Image(chart_image_path)
    ws.add_image(img, 'A10')
    wb.save(excel_file_path)
    wb.close()

# 함수 호출 부분.
if __name__ == '__main__':
    file_path = r'경로 기입'
    updated_file_path = calculate_return_and_profit(file_path)

    # 업데이트된 파일에서 데이터를 읽어옵니다.
    df_updated = pd.read_excel(updated_file_path, engine='openpyxl')
    # 시각화 함수를 호출합니다.
    save_and_insert_chart_with_values(df_updated, updated_file_path)
