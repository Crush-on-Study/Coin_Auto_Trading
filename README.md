## 기획 의도

흔들리는 것은, 차트가 아닌 개미의 투심이다...!
<br> 저는 2020년 3월, 대학교 3학년 때부터 주식과 코인 투자를 해왔습니다. 

## 기술 스택

<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/mysql-4479A1?style=for-the-badge&logo=mysql&logoColor=white"> <img src="https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white"> <img src="https://img.shields.io/badge/amazonaws-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white"> <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white">


## 1차 수익률
KRW-BTC : +7.03%

## 구현 중인 전략
- 당일 거래량 상위 5~10종목 사이 중 유의종목을 제외한 나머지 Ticker의 RSI 보조지표를 참고 후 매수
- 매도 전략 : 수수료 0.05%를 포함하여 수익률 2.05% 이상을 기록할 시, 전량 매도  (현재 오버나잇은 고려 X)
- 스탑 로스 : 수수료 0.05%를 포함하여 수익률 -1.95%가 넘어갈 시, 전량 손절
  
- 볼린저 밴드 조회 기능 추가!
  - RSI 매수조건과 동시에 볼린저 밴드의 하단 근처에 도달 시, 보유 원화 잔고 100% 매수
  - 그 외에는 보유 원화 잔고의 70% 매수

- 분할 매수 & 분할 매도는 추후 연구하여 고려 예정
- 현, 백테스팅 결과 10종목 중 9종목에서 수익 달성 (6개월 간 10~20%)
  - 나머지 1종목은 유의종목으로 지정된 '던프로토콜' 상황. HTML Pasing 사용하여 유의종목 판단하는 코드 작성 중
