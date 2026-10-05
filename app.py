
import streamlit as st
import pandas as pd

st.set_page_config(page_title="쭈니형 대형주 스크리너", layout="wide")

st.title("📈 쭈니형 대형주 전용 수급·차트·뉴스 통합 스크리너")
st.caption("시가총액 1조 이상 및 거래량이 풍부한 우량주 중에서 실시간 수급과 호재 뉴스가 터진 종목을 포착합니다.")

st.sidebar.header("⚙️ 검색 조건 설정")
min_score = st.sidebar.slider("최소 종합 점수 필터", 0, 100, 60)

data = [
    {
        "종목명": "SK하이닉스", "시가총액": "135조 원", "거래대금": "4,200억", "현재가": "185,000원", "등락률": "+4.1%", 
        "종합점수": 95, "체결강도": "145%", "외인순매수": "+1,200억", "기관순매수": "+650억",
        "최신뉴스": "[특징주] SK하이닉스, 대규모 자사주 매수 및 소각 발표에 강세", "포착키워드": "자사주, 소각, 대규모"
    },
    {
        "종목명": "삼성전자", "시가총액": "440조 원", "거래대금": "8,500억", "현재가": "74,500원", "등락률": "+2.3%", 
        "종합점수": 88, "체결강도": "128%", "외인순매수": "+850억", "기관순매수": "+320억",
        "최신뉴스": "삼성전자, 차세대 반도체 대규모 공급계약 체결 공시", "포착키워드": "공급계약, 대규모"
    },
    {
        "종목명": "삼성중공업", "시가총액": "8.5조 원", "거래대금": "850억", "현재가": "9,200원", "등락률": "+3.1%", 
        "종합점수": 82, "체결강도": "132%", "외인순매수": "+180억", "기관순매수": "+95억",
        "최신뉴스": "대형 카타르 LNG 운반선 추가 수주 계약 모멘텀", "포착키워드": "수주, 계약"
    }
]

df = pd.DataFrame(data)
filtered_df = df[df["종합점수"] >= min_score]

col1, col2, col3 = st.columns(3)
col1.metric("포착된 대형주", f"{len(filtered_df)}개")
col2.metric("1위 우량주", filtered_df.iloc[0]["종목명"] if not filtered_df.empty else "-")
col3.metric("1위 점수", f"{filtered_df.iloc[0]['종합점수']}점" if not filtered_df.empty else "0점")

st.markdown("---")
st.subheader("📋 실시간 포착 대형주 순위")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
