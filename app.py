import streamlit as st
import yfinance as ticker_data
import pandas as pd
import numpy as np
import requests

# ==========================================
# 텔레그램 설정 (본인의 정보로 변경)
# ==========================================
TELEGRAM_TOKEN = "여기에_BOT_TOKEN_입력"
TELEGRAM_CHAT_ID = "여기에_CHAT_ID_입력"

# 페이지 설정
st.set_page_config(page_title="쭈니형 거래량·수급 통합 스크리너", page_icon="📈", layout="wide")

st.title("📈 쭈니형 거래량 유입 종목 포착 스크리너")
st.caption("전일 대비 및 20일 평균 대비 거래량이 10% 이상 동시 증가한 수급 종목을 포착합니다.")

# 모니터링 대상 주요 종목
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

def send_telegram_message(message):
    """텔레그램 메시지 전송 함수"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, json=payload)
        return res.status_code == 200
    except Exception as e:
        return False

@st.cache_data(ttl=300)
def fetch_screened_stocks():
    results = []
    
    for symbol, name in STOCK_LIST.items():
        try:
            stock = ticker_data.Ticker(symbol)
            df = stock.history(period="1mo")
            
            if len(df) < 20:
                continue
                
            curr_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            price_change_pct = ((curr_price - prev_price) / prev_price) * 100
            
            curr_vol = df['Volume'].iloc[-1]
            prev_vol = df['Volume'].iloc[-2]
            avg_vol_20 = df['Volume'].iloc[-20:-1].mean()
            
            # 거래량 변화율 계산
            vol_increase_vs_prev = ((curr_vol - prev_vol) / prev_vol) * 100 if prev_vol > 0 else 0
            vol_increase_vs_avg = ((curr_vol - avg_vol_20) / avg_vol_20) * 100 if avg_vol_20 > 0 else 0
            
            # [조건 수정] 전일 대비 10% 이상 증가 AND 20일 평균 대비 10% 이상 증가
            if vol_increase_vs_prev >= 10 and vol_increase_vs_avg >= 10:
                trading_value_100m = (curr_price * curr_vol) / 100000000
                
                ma20 = df['Close'].iloc[-20:].mean()
                above_ma20 = curr_price >= ma20
                
                score = 30
                
                if vol_increase_vs_prev >= 100:
                    score += 30
                elif vol_increase_vs_prev >= 50:
                    score += 20
                elif vol_increase_vs_prev >= 20:
                    score += 10
                    
                if trading_value_100m >= 500:
                    score += 20
                elif trading_value_100m >= 100:
                    score += 10
                    
                if price_change_pct > 0:
                    score += 10
                    
                if above_ma20:
                    score += 10
                    
                results.append({
                    '종목명': name,
                    '종목코드': symbol.split('.')[0],
                    '현재가(원)': f"{int(curr_price):,}",
                    '등락률(%)': round(price_change_pct, 2),
                    '전일대비 거래량': f"+{round(vol_increase_vs_prev, 1)}%",
                    '20일평균대비 거래량': f"+{round(vol_increase_vs_avg, 1)}%",
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
with st.spinner("거래량 유입 종목 검증 중..."):
    df_result = fetch_screened_stocks()

if not df_result.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("포착된 종목 수", f"{len(df_result)}개")
    col2.metric("수급 1위 종목", df_result.iloc[0]['종목명'])
    col3.metric("1위 종합점수", f"{df_result.iloc[0]['포착 점수']}점")
    
    # 텔레그램 전송 버튼
    if st.button("📲 포착된 종목 리스트 텔레그램으로 받기"):
        msg_lines = ["🚨 *[거래량 유입 종목 포착]*\n"]
        for idx, row in df_result.head(10).iterrows():
            msg_lines.append(
                f"• *{row['종목명']}* ({row['종목코드']})\n"
                f"  - 현재가: {row['현재가(원)']}원 ({row['등락률(%)']}%)\n"
                f"  - 전일대비 거래량: {row['전일대비 거래량']} | 대금: {row['거래대금(억)']}\n"
                f"  - 포착점수: *{row['포착 점수']}점*\n"
            )
        
        full_msg = "\n".join(msg_lines)
        if send_telegram_message(full_msg):
            st.success("✅ 텔레그램 메시지가 성공적으로 전송되었습니다!")
        else:
            st.error("❌ 전송 실패! 텔레그램 토큰 및 Chat ID를 확인해주세요.")

    st.markdown("---")
    st.subheader("📋 실시간 거래량 유입 종목 순위 (점수순)")
    st.dataframe(df_result, use_container_width=True)
else:
    st.info("현재 전일 및 20일 평균 대비 거래량이 10% 이상 유입된 종목이 없습니다.")
