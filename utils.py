import streamlit as st
import requests
from datetime import datetime
import pathlib
import toml
from openai import OpenAI

# 공통 설정 함수
def set_page_config(title, icon, background_color):
    st.set_page_config(
        page_title=title,
        page_icon=icon,
    )

    # 배경색 변경을 위한 CSS
    page_bg_css = f"""
    <style>
        .stApp {{
            background-color: {background_color};
        }}
    </style>
    """
    
    # 기본 메뉴와 푸터 숨기기
    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        <script>
        document.addEventListener("DOMContentLoaded", function() {
            var mainMenu = document.getElementById('MainMenu');
            if (mainMenu) {{
                mainMenu.style.display = 'none';
            }}
            var footer = document.getElementsByTagName('footer')[0];
            if (footer) {{
                footer.style.display = 'none';
            }}
            var header = document.getElementsByTagName('header')[0];
            if (header) {{
                header.style.display = 'none';
            }}
        });
        </script>
    """
    
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    st.markdown(page_bg_css, unsafe_allow_html=True)

# secrets 로드 함수
def load_secrets():
    # 현재 작업 디렉토리를 기준으로 .streamlit/secrets.toml 경로 설정
    secrets_path = pathlib.Path.cwd() / ".streamlit" / "secrets.toml"    
    try:
        with open(secrets_path, "r", encoding="utf-8") as f:
            secrets = toml.load(f)
        return secrets
    except Exception as e:
        st.error(f"⚠️ secrets.toml 파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

# Notion 중복 확인 함수
def is_activity_code_duplicate(notion_api_key, database_id, page_type, activity_code):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "filter": {
            "and": [
                {
                    "property": "page",
                    "rich_text": {
                        "equals": page_type
                    }
                },
                {
                    "property": "activity_code",
                    "rich_text": {
                        "equals": activity_code
                    }
                }
            ]
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            results = response.json().get("results")
            return len(results) > 0
        else:
            st.error(f"⚠️ Notion API 호출 실패: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"⚠️ Notion API 호출 중 오류가 발생했습니다: {e}")
        return False

# Notion 데이터 저장 함수
def save_to_notion(notion_api_key, database_id, page_type, data):
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    try:
        response = requests.post(f"https://api.notion.com/v1/pages", headers=headers, json=data)
        if response.status_code != 200:
            st.error(f"❌ Notion API 요청이 실패했습니다. 상태 코드: {response.status_code}")
            st.error(f"오류 메시지: {response.text}")
        return response.status_code == 200
    except Exception as e:
        st.error(f"❌ Notion 데이터 저장 중 오류가 발생했습니다: {e}")
        return False

# OpenAI 클라이언트 초기화 함수
def initialize_openai_client(secrets, index=0):
    try:
        client = OpenAI(api_key=secrets["api"]["keys"][index])
        return client
    except Exception as e:
        st.error(f"⚠️ OpenAI 클라이언트를 초기화하는 중 오류가 발생했습니다: {e}")
        return None