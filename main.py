import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 설정 정보 (기존 정보를 그대로 입력하세요)
GOOGLE_API_KEY = st.secrets["AIzaSyAPNPzhuB7RajC8njNU30nwVBITqHuBu70"]
SHEET_ID = "1-0-rK8a0_GEK4zXUcNmvkb0pnXIK4To2SnzW2rErglo"

# 2. 모델 및 데이터 주소 설정
# 사장님 계정에서 확인된 최신 모델명을 사용합니다.
MODEL_NAME = "gemini-3-flash-preview"
genai.configure(api_key=GOOGLE_API_KEY)
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1-0-rK8a0_GEK4zXUcNmvkb0pnXIK4To2SnzW2rErglo/gviz/tq?tqx=out:csv"

st.set_page_config(page_title="광안리 와인곳간 AI 소믈리에", page_icon="🍷")
st.title("🍷 와인곳간 AI 소믈리에 ")
st.markdown("---")

query = st.text_input("와인에 대해 무엇이든 물어보세요! 자세히 물어봐주면 더 좋아요 :)", placeholder="예: 5만원대 선물용 레드와인 추천해줘")

if query:
    with st.spinner('재고를 분석하여 추천 리스트를 작성 중입니다...'):
        try:
            # 시트 읽기 (오류 방지를 위해 4번째 열까지만 읽음)
            df = pd.read_csv(SHEET_URL, usecols=[0, 1, 2, 3], on_bad_lines='skip')
            inventory_str = df.to_string(index=False)
            
            # 모델 호출
            model = genai.GenerativeModel(MODEL_NAME)
            
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
- **✅ 추천 이유**: (질문하신 상황에 이 와인이 왜 가장 적합한지 설명)
- **👅 맛 / 특징**: (당도, 산도, 바디감 등 핵심적인 맛 설명)
- **👤 이런 분께 추천**: (선물용, 와인 초보자, 묵직한 맛을 즐기는 분 등 타겟팅)
- **🧀 추천 안주**: (시트에 적힌 음식 외에도 잘 어울릴법한 구체적인 메뉴 제안)

2️⃣ **와인명** (가격)
- (위와 동일한 4가지 항목 적용)

3️⃣ **와인명** (가격)
- (위와 동일한 4가지 항목 적용)

마지막에 "원하시는 와인이 있으시면 직원에게 말씀해 주세요! 🍷"라고 친절하게 마무리할 것."""

            response = model.generate_content(prompt)
            
            st.success("✨ AI 소믈리에의 추천 결과")
            st.write(response.text)
            
        except Exception as e:
            # 오류 발생 시 구체적인 원인 출력
            st.error(f"오류가 발생했습니다: {e}")

st.markdown("---")
st.caption("실시간 매장 재고 데이터를 기반으로 답변합니다.")
