import streamlit as st
import pandas as pd
import google.generativeai as genai

# 사장님 정보 입력
GOOGLE_API_KEY = "AIzaSyDzAf_DzzOZ98q4_j0TQGZ24deRTMmJ19Y"
SHEET_ID = "1-0-rK8a0_GEK4zXUcNmvkb0pnXIK4To2SnzW2rErglo/edit?gid=0#gid=0"

# 설정 및 데이터 주소
genai.configure(api_key=GOOGLE_API_KEY)
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.set_page_config(page_title="AI 소믈리에", layout="centered")
st.title("🍷 우리매장 AI 소믈리에")

query = st.text_input("와인에 대해 궁금한 점을 물어보세요!", placeholder="예: 고기랑 어울리는 레드와인?")

if query:
    try:
        df = pd.read_csv(SHEET_URL)
        inventory_data = df.to_string(index=False)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"너는 소믈리에야. 아래 재고를 보고 친절하게 답해줘.\n재고:\n{inventory_data}\n질문: {query}"
        response = model.generate_content(prompt)
        st.success("AI 소믈리에의 추천")
        st.write(response.text)
    except Exception as e:
        st.error(f"오류가 발생했습니다. 시트 공유 설정을 확인해주세요: {e}")
