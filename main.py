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

# 2. 데이터 로드
SHEET_ID = "1-0-rK8a0_GEK4zXUcNmvkb0pnXIK4To2SnzW2rErglo"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data
def load_data():
    df = pd.read_csv(SHEET_URL)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 로드 실패: {e}")
    st.stop()

# 3. 모델 설정
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# --- 4. 사이드바: 5단계 정밀 취향 선택창 ---
st.sidebar.header("🎯 소믈리에의 맞춤 필터")

price_option = st.sidebar.selectbox(
    "💵 어느 정도 가격대를 생각하시나요?",
    ["전체 가격대", "가성비 데일리 (3만원 이하)", "부담 없는 선물/모임 (3~7만원)", "특별한 날의 주인공 (7~15만원)", "프리미엄 콜렉션 (15만원 이상)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("👅 선호하는 맛 (5단계)")

body = st.sidebar.select_slider("바디감 (무게감)", options=["매우 가벼움", "가벼움", "중간", "약간 무거움", "매우 진하고 무거움"])
sweet = st.sidebar.select_slider("당도 (달콤함)", options=["매우 드라이", "드라이", "중간", "약간 달콤함", "매우 달콤함"])
acidity = st.sidebar.select_slider("산도 (새콤함)", options=["낮음", "약간 낮음", "중간", "약간 높음", "매우 높음(생동감)"])
tannin = st.sidebar.select_slider("타닌 (떫은맛)", options=["거의 없음", "부드러움", "중간", "약간 강함", "강함"])

# --- 5. 메인 UI ---
st.title("🍷 와인곳간 AI 수석 소믈리에")
st.markdown("---")
st.write("사장님의 취향을 선택하시거나, 아래에 원하시는 느낌을 자유롭게 적어주세요.")

query = st.text_input("💬 추가 요청사항 (예: 캠핑 가서 고기랑 먹을 거예요)", "")

if st.button("전문 소믈리에의 추천 받기"):
    with st.spinner("사장님의 취향에 딱 맞는 와인을 찾고 있습니다..."):
        inventory_sample = df.head(100).to_string(index=False)
        
        prompt = f"""너는 20년 경력의 친절한 마스터 소믈리에야. 와인 초보자도 이해하기 쉬운 언어로 우리 매장 재고에서 3가지를 추천해줘.

[매장 재고 데이터]
{inventory_sample}

[고객의 정밀 선택 조건]
- 가격대: {price_option}
- 바디감: {body} / 당도: {sweet} / 산도: {acidity} / 타닌: {tannin}
- 고객 추가 요청: {query}

[답변 작성 규칙]
1. '추천 이유'를 가장 먼저 배치하여 고객의 선택 조건과 어떻게 맞는지 설명할 것.
2. '테이스팅 노트'는 와인 초보자도 바로 이해할 수 있는 쉬운 단어(예: 진한 포도잼 맛, 숲속의 젖은 흙 냄새, 상큼한 레몬 사탕 등)로 쓸 것.
3. '추천 고객' 항목을 추가하여 어떤 상황이나 성향의 분께 어울리는지 적을 것.
4. 어려운 전문 용어(탄닌, 테루아 등)를 쓸 때는 쉬운 설명을 덧붙이거나 일상적인 표현으로 대체할 것.

✨ **마스터 소믈리에의 맞춤 추천 Top 3**

1️⃣ **와인명** (가격)
- **✅ 선정 이유**: (고객님이 고르신 {price_option} 가격대와 {body} 취향에 왜 이 와인이 찰떡궁합인지 가장 먼저 설명)
- **🍷 초보자도 알기 쉬운 맛 표현**: (입안에서 느껴지는 맛을 과일, 디저트, 꽃 등에 비유하여 아주 친절하게 설명)
- **👤 이런 분께 추천드려요**: (이런 취향을 가진 분이나 이런 상황에 계신 분께 강력 추천)
- **🍽️ 함께하면 맛있는 음식**: (함께 먹으면 맛이 배가 되는 안주를 구체적인 메뉴로 추천)

(2, 3번 와인도 동일한 형식으로 작성)

마지막에 "필요한 와인이 있으시면 언제든 불러주세요! 🍷"라고 따뜻하게 마무리해줘."""

        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"응답 생성 중 오류가 발생했습니다: {e}")
