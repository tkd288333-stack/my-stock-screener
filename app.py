import streamlit as st
import yfinance as ticker_data
import pandas as pd
import numpy as np

# 페이지 설정
st.set_page_config(page_title="쭈니형 거래량·수급 통합 스크리너", page_icon="📈", layout="wide")

st.title("📈 쭈니형 거래량 10% 이상 유입 종목 포착 스크리너")
st.caption("20일 평균 대비 거래량이 10% 이상 유입된 수급 유망 종목을 포착하여 점수순으로 정렬합니다.")

# 모니터링 대상 주요 종목 확장 (코스피/코스닥 주요 우량 종목)
STOCK_LIST = {
    '005930.KS': '삼성전자',
    '000660.KS': 'SK하이닉스',
    '373220.KS': 'LG에너지솔루션',
    '207940.KS': '삼성바이오로직스',
    '005935.KS': '삼성전자우',
    '005380.KS': '현대차',
    '000270.KS': '기아',
    '068270.KS': '셀트리온',
    '105560.KS': 'KB금융',
    '055550.KS': '신한지주',
    '035420.KS': 'NAVER',
    '035720.KS': '카카오',
    '012330.KS': '현대모비스',
    '028260.KS': '삼성물산',
    '015760.KS': '한국전력',
    '032830.KS': '삼성생명',
    '010140.KS': '삼성중공업',
    '000810.KS': '삼성화재',
    '018260.KS': '삼성SDS',
    '030200.KS': 'KT',
    '017670.KS': 'SK텔레콤',
    '003550.KS': 'LG',
    '034730.KS': 'SK',
    '009150.KS': '삼성전기',
    '036570.KS': '엔씨소프트',
    '086520.KQ': '에코프로비엠',
    '091990.KQ': '셀트리온헬스케어',
    '247540.KQ': '에코프로',
    '066570.KS': 'LG전자'
}

@st.cache_data(ttl=300)
def fetch_screened_stocks():
    results = []
    
    for symbol, name in STOCK_LIST.items():
        try:
            stock = ticker_data.Ticker(symbol)
            df = stock.history(period="1mo")
            
            if len(df) < 20:
                continue
                
            # 최근 종가 및 거래량 정보
            curr_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            price_change_pct = ((curr_price - prev_price) / prev_price) * 100
            
            curr_vol = df['Volume'].iloc[-1]
            avg_vol_20 = df['Volume'].iloc[-20:-1].mean()
            
            # 20일 평균 대비 거래량 증가율 (%)
            vol_increase_pct = ((curr_vol - avg_vol_20) / avg_vol_20) * 100
            
            # 핵심 조건: 20일 평균 거래량 대비 10% 이상 증가
            if vol_increase_pct >= 10:
                # 거래대금 계산 (억 원 단위)
                trading_value_100m = (curr_price * curr_vol) / 100000000
                
                # 20일 이동평균선 위치
                ma20 = df['Close'].iloc[-20:].mean()
                above_ma20 = curr_price >= ma20
                
                # 점수 산정 로직 (100점 만점 기준)
                score = 30  # 1차 포착 기본점수
                
                # 가산점 1: 거래량 폭발력 (최대 30점)
                if vol_increase_pct >= 200:
                    score += 30
                elif vol_increase_pct >= 100:
                    score += 20
                elif vol_increase_pct >= 30:
                    score += 10
                    
                # 가산점 2: 거래대금 규모 (최대 20점)
                if trading_value_100m >= 500:
                    score += 20
                elif trading_value_100m >= 100:
                    score += 10
                    
                # 가산점 3: 당일 주가 상승 (양봉 유지) (최대 10점)
                if price_change_pct > 0:
                    score += 10
                    
                # 가산점 4: 20일선 위에 위치 (추세 양호) (최대 10점)
                if above_ma20:
                    score += 10
                    
                results.append({
                    '종목명': name,
                    '종목코드': symbol.split('.')[0],
                    '현재가(원)': f"{int(curr_price):,}",
                    '등락률(%)': round(price_change_pct, 2),
                    '거래량 증가율(%)': f"+{round(vol_increase_pct, 1)}%",
                    '거래대금(억)': f"{int(trading_value_100m):,}억",
                    '20일선 위': '✅' if above_ma20 else '❌',
                    '포착 점수': score
                })
        except Exception as e:
            continue
            
    res_df = pd.DataFrame(results)
    if not res_df.empty:
        res_df = res_df.sort_values(by='포착 점수', ascending=False).reset_index(drop=True)
    return res_df

# 데이터 수집 및 화면 표시
with st.spinner("거래량 10% 이상 유입 종목 분석 중..."):
    df_result = fetch_screened_stocks()

if not df_result.empty:
    # 요약 상단 지표
    col1, col2, col3 = st.columns(3)
    col1.metric("포착된 종목 수", f"{len(df_result)}개")
    col2.metric("수급 1위 종목", df_result.iloc[0]['종목명'])
    col3.metric("1위 종합점수", f"{df_result.iloc[0]['포착 점수']}점")
    
    st.markdown("---")
    st.subheader("📋 실시간 거래량 10% 이상 유입 종목 순위 (점수순)")
    st.dataframe(df_result, use_container_width=True)
else:
    st.info("현재 20일 평균 대비 거래량이 10% 이상 유입된 종목이 없습니다.")
