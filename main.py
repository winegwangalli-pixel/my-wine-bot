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

# --- 4. 메인 UI 구성 (모바일 가시성 최적화) ---
st.set_page_config(page_title="와인곳간 AI 소믈리에", layout="centered")

st.title("🍷 와인곳간 AI 수석 소믈리에")
st.info("취향을 선택하시면 최적의 와인을 추천해 드립니다.")

# [가격 선택] 메인 화면에 크게 배치
st.subheader("1. 예산 범위를 골라주세요")
price_option = st.selectbox(
    "💵 가격대 선택",
    ["전체 가격대", "가성비 데일리 (3만원 이하)", "부담 없는 선물/모임 (3~7만원)", "특별한 날의 주인공 (7~15만원)", "프리미엄 콜렉션 (15만원 이상)"],
    label_visibility="collapsed"
)

st.markdown("---")

# [맛 선택] 메인 화면에 크게 배치
st.subheader("2. 선호하는 맛을 알려주세요")
auto_recommend = st.toggle("⭐ 상관없음 (소믈리에 베스트 추천)", value=False)

if auto_recommend:
    st.success("✨ 전문가가 검증한 가장 대중적인 와인들로 엄선해 드릴게요!")
    body = sweet = acidity = tannin = "상관없음(베스트 추천)"
else:
    # 모바일에서 보기 편하게 슬라이더 배치
    body = st.select_slider("⚖️ 바디감 (무게감)", options=["매우 가벼움", "가벼움", "중간", "약간 무거움", "매우 진함"])
    sweet = st.select_slider("🍭 당도 (달콤함)", options=["매우 드라이", "드라이", "중간", "약간 달콤", "매우 달콤"])
    acidity = st.select_slider("🍋 산도 (새콤함)", options=["낮음", "약간 낮음", "중간", "약간 높음", "매우 높음"])
    tannin = st.select_slider("🪵 타닌 (떫은맛)", options=["거의 없음", "부드러움", "중간", "약간 강함", "강함"])

st.markdown("---")

# [추가 질문]
st.subheader("3. 더 구체적인 요청이 있으신가요?")
query = st.text_input("💬 (예: 캠핑 가서 고기랑 먹을 와인)", placeholder="자유롭게 적어주세요.")

# 추천 버튼을 크게 만듦
if st.button("🍷 나만의 와인 추천받기", use_container_width=True):
    with st.spinner("사장님의 취향에 딱 맞는 와인을 찾고 있습니다..."):
        inventory_sample = df.head(100).to_string(index=False)
        preference_info = "대중적 인기 와인" if auto_recommend else f"바디:{body}, 당도:{sweet}, 산도:{acidity}, 타닌:{tannin}"

        prompt = f"""너는 20년 경력의 친절한 마스터 소믈리에야. 초보자도 이해하기 쉬운 언어로 우리 매장 재고에서 3가지를 추천해줘.
[매장 재고 데이터]
{inventory_sample}
[고객 조건] 가격대:{price_option}, 취향:{preference_info}, 요청:{query}

✨ **마스터 소믈리에의 맞춤 추천 Top 3**
1️⃣ **와인명** (가격)
- **✅ 선정 이유**: (가장 먼저 설명)
- **🍷 초보자용 맛 표현**: (쉬운 단어로 친절하게)
- **👤 이런 분께 추천**: (상황이나 성향)
- **🍽️ 함께하면 맛있는 음식**: (구체적 메뉴)

마지막엔 "궁금하신 점은 직원을 불러주세요! 🍷"로 마무리해줘."""

        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
