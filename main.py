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
    df = pd.read_csv(SHEET_URL)
    # 데이터가 500개일 때 검색 효율을 위해 숫자로 변환 가능한 열은 변환 (예: 공급가)
    if '공급가' in df.columns:
        df['공급가'] = pd.to_numeric(df['공급가'], errors='coerce')
    return df

df = load_data()

# 3. 모델 설정
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# --- 4. 메인 UI (필터부) ---
st.set_page_config(page_title="와인곳간 AI 소믈리에", layout="centered")


st.subheader("📍 어떤 가격대를 찾으시나요?")
price_option = st.selectbox(
    "💵 가격대 선택",
    ["전체 가격대", "가볍게 즐기는 데일리 (3만원 이하)", "실패 없는 미식 모임 (3~7만원)", "특별한 날 (7~15만원)", "프리미엄 (15만원 이상)"]
)

st.subheader("👅 원하는 맛의 밸런스를 맞춰주세요")
auto_recommend = st.toggle("⭐ 알아서 추천해주세요 (소믈리에 픽)", value=False)

if auto_recommend:
    st.info("💡 실패 없는 스테디셀러 위주로 큐레이팅을 시작합니다.")
    body = sweet = acidity = tannin = "상관없음"
else:
    body = st.select_slider("⚖️ 바디감", options=["매우 가벼움", "가벼움", "중간", "약간 무거움", "매우 진함"], value="중간")
    sweet = st.select_slider("🍭 당도", options=["매우 드라이", "드라이", "중간", "약간 달콤", "매우 달콤"], value="중간")
    acidity = st.select_slider("🍋 산도", options=["낮음", "약간 낮음", "중간", "약간 높음", "매우 높음"], value="중간")
    tannin = st.select_slider("🪵 타닌", options=["거의 없음", "부드러움", "중간", "약간 강함", "강함"], value="중간")

st.subheader("✍️ 더 구체적인 취향이 있으신가요?")
query = st.text_input("💬 (예: 방어랑 먹을 와인, 오늘 조용히 혼술, 광안리 클램에서 버섯파스타랑 먹을와인, 와인을 잘모르는 친구에게 집들이 선물, 이탈리아 와인 도전해보고싶어 등)", placeholder="자유롭게 입력해주세요.")

# --- 5. 스마트 추천 로직 ---
if st.button("🍷 나만의 와인 추천받기", use_container_width=True):
    with st.spinner("500여 종의 와인 리스트에서 최고의 맛돌이 찾는중입니다..."):
        
        # [스마트 전략 1] 데이터 셔플링 (500개를 골고루 추천하기 위해)
        shuffled_df = df.sample(frac=1).reset_index(drop=True)
        
        # [스마트 전략 2] 가격대 1차 필터링 (AI의 부하를 줄여 답변 품질 상승)
        filtered_df = shuffled_df
        if "3만원 이하" in price_option:
            filtered_df = shuffled_df[shuffled_df['공급가'] <= 30000]
        elif "3~7만원" in price_option:
            filtered_df = shuffled_df[(shuffled_df['공급가'] > 30000) & (shuffled_df['공급가'] <= 70000)]
        elif "7~15만원" in price_option:
            filtered_df = shuffled_df[(shuffled_df['공급가'] > 70000) & (shuffled_df['공급가'] <= 150000)]
        elif "15만원 이상" in price_option:
            filtered_df = shuffled_df[shuffled_df['공급가'] > 150000]

        # 1차 필터링 후 최대 100개만 AI에게 전달 (ResourceExhausted 에러 방지)
        inventory_sample = filtered_df.head(100).to_string(index=False)
        
        preference_info = "소믈리에 추천" if auto_recommend else f"바디:{body}, 당도:{sweet}, 산도:{acidity}, 타닌:{tannin}"

        prompt = f"""너는 20년 경력의 마스터 소믈리에야. 와인 초보자도 이해하기 쉬운 언어로 우리 매장 재고에서 3가지를 엄선해줘.
        **[절대 규칙] 반드시 아래 [매장 재고 데이터]에 존재하는 와인 이름과 가격만 사용하여 답변해. 데이터에 없는 와인은 절대로 지어내지 마.**
[매장 재고 데이터]
{inventory_sample}

[고객 조건] 가격대:{price_option}, 취향:{preference_info}, 요청:{query}

[답변 규칙]
1. 선정 이유를 맨 처음에 배치할 것.
2. 테이스팅 노트는 초보자가 알기 쉽게 비유(포도잼, 레몬 사탕 등)를 쓸 것.
3. '추천 고객' 항목을 넣어 상황에 맞는 추천을 할 것.
4. 전문 서빙 팁은 제외할 것.

✨ **마스터 소믈리에의 맞춤 추천 Top 3**
(이하 1, 2, 3번 와인 형식 유지)
"""

        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"죄송합니다. 잠시 후 다시 시도해주세요. (오류: {e})")
