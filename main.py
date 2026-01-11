import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 설정 정보 (기존 정보를 그대로 입력하세요)
GOOGLE_API_KEY = "1-0-rK8a0_GEK4zXUcNmvkb0pnXIK4To2SnzW2rErglo"
SHEET_ID = "AIzaSyDzAf_DzzOZ98q4_j0TQGZ24deRTMmJ19Y"

# 2. 모델 및 데이터 주소 설정
# 사장님 계정에서 확인된 최신 모델명을 사용합니다.
MODEL_NAME = "gemini-3-flash-preview"
genai.configure(api_key=GOOGLE_API_KEY)
SHEET_URL = f"https://docs.google.com/spreadsheets/d/AIzaSyDzAf_DzzOZ98q4_j0TQGZ24deRTMmJ19Y/gviz/tq?tqx=out:csv"

st.set_page_config(page_title="광안리 와인곳간 AI 소믈리에", page_icon="🍷")
st.title("🍷 AI 소믈리에 추천 서비스")
st.markdown("---")

query = st.text_input("와인에 대해 무엇이든 물어보세요!", placeholder="예: 5만원대 선물용 레드와인 추천해줘")

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
1. 반드시 재고가 1개 이상인 와인만 추천할 것.
2. 와인 이름, 가격을 언급하며 어울리는 음식과 맛을 3줄 내외로 친절하게 설명해줘."""

            response = model.generate_content(prompt)
            
            st.success("✨ AI 소믈리에의 추천 결과")
            st.write(response.text)
            
        except Exception as e:
            # 오류 발생 시 구체적인 원인 출력
            st.error(f"오류가 발생했습니다: {e}")

st.markdown("---")
st.caption("실시간 매장 재고 데이터를 기반으로 답변합니다.")
