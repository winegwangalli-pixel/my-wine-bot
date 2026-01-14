import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. 보안 설정
try:
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error("API 키 설정에 문제가 있습니다. Streamlit Secrets를 확인해주세요.")
    st.stop()

# 2. 데이터 로드 및 전처리
SHEET_ID = "1-0-rK8a0_GEK4zXUcNmvkb0pnXIK4To2SnzW2rErglo"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # 가격 데이터 정제 (쉼표 제거 및 숫자 변환)
        if '가격' in df.columns:
            df['가격'] = pd.to_numeric(df['가격'].astype(str).str.replace(',', ''), errors='coerce')
        return df
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

df = load_data()

# 3. 모델 설정
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# --- 4. 메인 UI (다크 프리미엄 + 제목 크기 통일 버전) ---
st.set_page_config(page_title="와인곳간 AI 소믈리에", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&display=swap');
    
    /* 1. 배경을 깊이감 있는 검은색으로, 기본 글자를 흰색으로 고정 */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #0E1117 !important; /* 스트림릿 다크 기본 배경색 */
        color: #FFFFFF !important;
    }

    .header-container { text-align: center; padding: 30px 0px 10px 0px; }
    
    .main-title { 
        font-family: 'Nanum Myeongjo', serif !important; 
        font-size: 2.8rem !important; 
        font-weight: 800 !important; 
        color: #FFFFFF !important; 
        margin-bottom: 5px !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5) !important;
    }
    
    .sub-title { 
        font-family: 'Nanum Myeongjo', serif !important; 
        font-size: 1.1rem !important; 
        color: #FFFFFF !important; 
        opacity: 0.8;
        letter-spacing: 2px;
        margin-bottom: 20px !important;
    }

    /* 2. 모든 섹션 제목 스타일 (1.4rem 흰색 굵게 통일) */
    .unified-title {
        font-family: 'Nanum Myeongjo', serif !important;
        font-size: 1.4rem !important; 
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin-top: 35px !important;
        margin-bottom: 15px !important;
        display: block;
    }
    
    /* 3. 슬라이더 및 기타 요소 글자색 보정 */
    .stMarkdown, p, span, label {
        color: #FFFFFF !important;
    }
    
    /* 입력창 내부 텍스트 색상 보정 */
    input {
        color: #000000 !important; /* 입력하는 글자만 검은색 (흰 배경 입력창일 경우) */
    }

    .block-container { padding-top: 1.5rem !important; }
    </style>
    
    <div class='header-container'>
        <div class='main-title'>🍷 와인곳간 🍷</div>
        <div class='sub-title'>AI 수석 소믈리에</div>
    </div>
    """, unsafe_allow_html=True)
st.subheader("💵 가격대 선택")
price_option = st.selectbox(
    "가격대 선택창",
    ["전체 가격대", "가볍게 즐기는 데일리 (3만원 이하)", "실패 없는 미식 모임 (3~7만원)", "특별한 순간(7~15만원)", "프리미엄 (15만원 이상)"],
    label_visibility="collapsed"
)

st.subheader("👅 원하는 맛")
auto_recommend = st.toggle("⭐ 알아서 추천해주세요 (소믈리에 픽)", value=False)

if not auto_recommend:
    body = st.select_slider("⚖️ 바디감", options=["매우 가벼움", "가벼움", "중간", "약간 무거움", "매우 진함"], value="중간")
    sweet = st.select_slider("🍭 당도", options=["매우 드라이", "드라이", "중간", "약간 달콤", "매우 달콤"], value="중간")
    acidity = st.select_slider("🍋 산도", options=["낮음", "약간 낮음", "중간", "약간 높음", "매우 높음"], value="중간")
    tannin = st.select_slider("🪵 타닌", options=["거의 없음", "부드러움", "중간", "약간 강함", "강함"], value="중간")
else:
    st.info("💡 실패 없는 스테디셀러 위주로 큐레이팅을 시작합니다.")
    body = sweet = acidity = tannin = "상관없음"

st.subheader("✍️ 오늘의 취향")
st.markdown("""
    <div style='background-color: #F8F9FA; padding: 12px; border-radius: 8px; margin-top: -10px; margin-bottom: 10px; border: 1px solid #EEEEEE;'>
        <p style='font-size: 0.8rem; color: #444444; line-height: 1.6; margin: 0px; font-weight: 500;'>
            예) 방어랑 먹을 와인 / 오늘 조용히 혼술용<br>
            • 광안리 클램에서 라자냐랑 마실 와인 / 집들이 선물용<br>
            • 이탈리아 와인 도전 / 초보자가 먹을 부드러운 레드
        </p>
    </div>
    """, unsafe_allow_html=True)

query = st.text_input(
    "오늘의 취향 입력", 
    placeholder="자세히 적어주시면 더 추천 잘해드려요 :)", 
    label_visibility="collapsed"
)

# --- 5. 스마트 추천 로직 ---
if st.button("🍷 나만의 와인 추천받기", use_container_width=True):
    if df.empty:
        st.error("재고 데이터를 불러올 수 없습니다. 시트 공유 설정을 확인해주세요.")
    else:
        with st.spinner("500여 종의 와인 리스트에서 최고의 맛돌이 찾는 중..."):
            
            # 1차 필터링
            shuffled_df = df.sample(frac=1).reset_index(drop=True)
            filtered_df = pd.DataFrame()

            if "전체 가격대" in price_option:
                filtered_df = shuffled_df
            elif "3만원 이하" in price_option:
                filtered_df = shuffled_df[shuffled_df['가격'] <= 30000]
            elif "3~7만원" in price_option:
                filtered_df = shuffled_df[(shuffled_df['가격'] > 30000) & (shuffled_df['가격'] <= 70000)]
            elif "7~15만원" in price_option:
                filtered_df = shuffled_df[(shuffled_df['가격'] > 70000) & (shuffled_df['가격'] <= 150000)]
            elif "15만원 이상" in price_option:
                filtered_df = shuffled_df[shuffled_df['가격'] > 150000]

            # [보강] 필터링 결과가 없으면 전체 데이터에서 샘플링 (재고 없음 방지)
            is_fallback = False
            if filtered_df.empty:
                inventory_sample = shuffled_df.head(50).to_string(index=False)
                is_fallback = True
            else:
                inventory_sample = filtered_df.head(100).to_string(index=False)
            
            preference_info = "소믈리에 추천" if auto_recommend else f"바디:{body}, 당도:{sweet}, 산도:{acidity}, 타닌:{tannin}"

            # [보강] AI에게 "데이터가 부족해도 어떻게든 찾으라"고 명령
            fallback_msg = "단, 현재 선택하신 가격대에 딱 맞는 재고가 부족하다면, 전체 리스트에서 가장 유사한 느낌의 베스트 와인을 추천해줘." if is_fallback else ""

            prompt = f"""너는 20년 경력의 마스터 소믈리에야. 
            **[절대 규칙] 반드시 제공된 [매장 재고 데이터]에 있는 '상품명'과 '가격'만 사용해. 절대 없는 와인을 지어내지 마.**
            {fallback_msg}

            [매장 재고 데이터]
            {inventory_sample}

            [고객 조건] 가격대:{price_option}, 취향:{preference_info}, 요청:{query}

           [답변 가이드라인]
1. '선정 이유'를 감각적으로 먼저 설명할 것.
2. 테이스팅 노트는 '포도잼처럼 진한', '잘 익은 사과처럼 상큼한' 등 상상 가능한 언어를 쓸 것.
3. '추천 상황'을 넣어 고객의 질문에 대한 정답임을 보여줄 것.

✨ **당신을 위한 프라이빗 큐레이팅 Top 3**

1️⃣ **와인명** (가격)
- **✅ Curated for you**: (왜 이 와인이 오늘의 주인공인지 설명)
- **🍷 테이스팅 노트**: (초보자도 알기 쉬운 맛의 묘사)
- **👤 이런 순간에 추천**: (용도, 음식, 분위기 매칭)

(2, 3번 반복)

"오늘 추천드린 와인이 사장님의 특별한 시간을 완성해주길 바랍니다. 실물 확인은 직원을 불러주세요! 🍷"
"""

            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                if is_fallback:
                    st.caption("💡 선택하신 조건의 재고가 부족하여 소믈리에가 가장 유사한 와인으로 추천해 드렸습니다.")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
