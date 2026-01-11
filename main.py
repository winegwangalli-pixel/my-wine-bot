import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. 보안 설정: API 키를 금고(Secrets)에서 안전하게 가져옵니다.
try:
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error("API 키 설정에 문제가 있습니다. Streamlit Secrets 설정을 확인해주세요.")
    st.stop()

# 2. 구글 시트 데이터 로드
SHEET_ID = "1-0-rK8a0_GEK4zXUcNmvkb0pnXIK4To2SnzW2rErglo"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data
def load_data():
    # 시트에서 상단 4개 열(상품명, 주종, 공급가, 재고)을 읽어옵니다.
    df = pd.read_csv(SHEET_URL)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다. 구글 시트 공유 설정을 확인해주세요: {e}")
    st.stop()

# 3. 모델 설정
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# 4. 앱 UI 구성
st.title("🍷 우리 매장 AI 소믈리에")
st.write("찾으시는 와인이나 어울리는 안주를 물어보세요!")

query = st.text_input("질문을 입력하세요 (예: 3만원대 레드와인 추천해줘)", "")

if query:
    with st.spinner("재고를 확인하고 추천 리스트를 만들고 있습니다..."):
        # 재고 데이터를 텍스트로 변환
        inventory_str = df.to_string(index=False)
        
        # 사장님이 원하신 정돈된 답변 구성
        prompt = f"""너는 와인 매장의 전문 소믈리에야. 아래 [매장 재고 데이터]를 바탕으로 질문에 답해줘.
            
[매장 재고 데이터]
{inventory_str}

[고객 질문]
{query}

[답변 규칙]
1. 답변 시작 시 고객의 질문 상황에 공감하는 문장을 한 줄 넣을 것.
2. 반드시 재고가 있는 와인 중 가장 적합한 **Top 3**를 선정할 것.
3. 각 와인마다 아래 4가지 항목을 반드시 포함할 것:

✨ **AI 소믈리에의 엄선 추천 Top 3**

1️⃣ **와인명** (가격)
- **✅ 추천 이유**: (질문에 이 와인이 왜 적합한지 설명)
- **👅 맛 / 특징**: (당도, 산도, 바디감 등 핵심 맛 설명)
- **👤 이런 분께 추천**: (추천 대상 타겟팅)
- **🧀 추천 안주**: (구체적인 메뉴 제안)

2️⃣ **와인명** (가격)
- (위와 동일한 4가지 항목 적용)

3️⃣ **와인명** (가격)
- (위와 동일한 4가지 항목 적용)

마지막에 "매장에 진열된 실제 병의 라벨을 직접 확인해 보세요! 도움이 필요하시면 직원을 불러주세요 🍷"라고 마무리할 것."""

        response = model.generate_content(prompt)
        st.markdown(response.text)
