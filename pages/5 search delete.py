import streamlit as st
import requests
from datetime import datetime
from utils import set_page_config, load_secrets, is_activity_code_duplicate, save_to_notion
import sys
import json

# 페이지 설정 - 아이콘과 제목 설정
set_page_config("교사용 프롬프트 관리 도구", "🧑‍🏫", "#E6E6FA")

# secrets.toml 파일 로드
secrets = load_secrets()
if not secrets:
    st.stop()

# Notion API 설정
NOTION_API_KEY = secrets["notion"]["api_key"]
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
NOTION_PAGE_URL = "https://api.notion.com/v1/pages"

# 페이지 유형에 따른 데이터베이스 ID 선택
def get_database_id(page_type):
    if page_type == "text":
        return secrets["notion"]["database_id_text"]
    elif page_type == "vision":
        return secrets["notion"]["database_id_vision"]
    elif page_type == "image":
        return secrets["notion"]["database_id_image"]
    elif page_type == "chatbot":
        return secrets["notion"]["database_id_chatbot"]
    else:
        return None

# 비밀번호를 사용하여 프롬프트 검색
def search_prompt_by_password(page_type, password):
    database_id = get_database_id(page_type)
    if not database_id:
        st.error("⚠️ 유효하지 않은 페이지 유형입니다.")
        return []

    query_url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = NOTION_HEADERS
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
                    "property": "password",
                    "rich_text": {
                        "equals": password
                    }
                }
            ]
        }
    }
    with st.spinner('🔍 프롬프트를 검색하는 중입니다...'):
        response = requests.post(query_url, headers=headers, json=data)
        if response.status_code == 200:
            results = response.json().get("results", [])
            return results
        else:
            st.error(f"⚠️ Notion API 호출 실패: {response.status_code} - {response.text}")
            return []

# 활동 코드를 사용하여 프롬프트 삭제
def delete_prompt_by_activity_code(page_type, activity_code):
    database_id = get_database_id(page_type)
    if not database_id:
        st.error("⚠️ 유효하지 않은 페이지 유형입니다.")
        return False

    query_url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = NOTION_HEADERS
    data = {
        "filter": {
            "property": "activity_code",
            "rich_text": {
                "equals": activity_code
            }
        }
    }
    with st.spinner('🗑️ 프롬프트를 삭제하는 중입니다...'):
        response = requests.post(query_url, headers=headers, json=data)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                for result in results:
                    page_id = result["id"]
                    try:
                        archive_data = {"archived": True}
                        delete_response = requests.patch(f"{NOTION_PAGE_URL}/{page_id}", headers=headers, json=archive_data)
                        if delete_response.status_code == 200:
                            st.success(f"🎉 활동 코드 '{activity_code}'에 해당하는 프롬프트가 삭제되었습니다.")
                        else:
                            st.error(f"❌ 활동 코드 '{activity_code}'에 해당하는 프롬프트 삭제 중 오류가 발생했습니다. 상태 코드: {delete_response.status_code} - {delete_response.text}")
                            return False
                    except Exception as e:
                        st.error(f"❌ 활동 코드 '{activity_code}'에 해당하는 프롬프트 삭제 중 예외가 발생했습니다: {str(e)}")
                        return False
                return True
            else:
                st.warning("⚠️ 해당 활동 코드에 대한 프롬프트를 찾을 수 없습니다.")
                return False
        else:
            st.error(f"⚠️ Notion API 호출 실패: {response.status_code} - {response.text}")
            return False

def upload_new_prompt(page_type, activity_code, prompt, email, password, adjectives=None, student_view=None):
    database_id = get_database_id(page_type)
    if not database_id:
        st.error("⚠️ 유효하지 않은 페이지 유형입니다.")
        return False

    # 기본 속성 설정
    properties = {
        "activity_code": {"rich_text": [{"text": {"content": activity_code}}]},
        "prompt": {"rich_text": [{"text": {"content": prompt}}]},
        "email": {"rich_text": [{"text": {"content": email}}]},
        "password": {"rich_text": [{"text": {"content": password}}]},
        "date": {"rich_text": [{"text": {"content": datetime.now().isoformat()}}]},
        "page": {"rich_text": [{"text": {"content": page_type}}]}
    }

    # page_type이 'image'인 경우
    if page_type == "image" and adjectives is not None:
        if isinstance(adjectives, str):
            adjectives_json = adjectives
        elif isinstance(adjectives, list):
            adjectives_json = json.dumps(adjectives, ensure_ascii=False)
        else:
            adjectives_json = '[]'
        properties["adjectives"] = {"rich_text": [{"text": {"content": adjectives_json}}]}

    # page_type이 'chatbot'인 경우
    if page_type == "chatbot" and student_view:
        properties["student_view"] = {"rich_text": [{"text": {"content": student_view}}]}

    # page_type이 'vision' 또는 'text'인 경우에 student_view 추가
    if page_type in ["vision", "text"] and student_view is not None:
        properties["student_view"] = {"rich_text": [{"text": {"content": student_view}}]}

    data = {"parent": {"database_id": database_id}, "properties": properties}

    with st.spinner('💾 새로운 프롬프트를 업로드하는 중입니다...'):
        response = requests.post(f"{NOTION_PAGE_URL}", headers=NOTION_HEADERS, json=data)
        if response.status_code == 200:
            st.success(f"🎉 새로운 프롬프트가 성공적으로 업로드되었습니다. 활동 코드: '{activity_code}'")
            return True
        else:
            st.error(f"❌ 프롬프트 업로드에 실패했습니다. 상태 코드: {response.status_code} - {response.text}")
            return False

def update_prompt(page_type, activity_code, new_prompt, email, password, adjectives=None, student_view=None):
    # 기존 프롬프트 삭제
    delete_success = delete_prompt_by_activity_code(page_type, activity_code)
    if not delete_success:
        return False

    # 새로운 프롬프트 업로드
    upload_success = upload_new_prompt(page_type, activity_code, new_prompt, email, password, adjectives, student_view)
    return upload_success

def update_prompt_form(selected_result, activity_code, current_prompt, current_email):
    with st.form(key="update_form"):
        new_prompt = st.text_area("새 프롬프트를 입력하세요:", current_prompt, key="new_prompt")
        new_email = st.text_input("새 이메일을 입력하세요:", current_email, key="new_email")

        if st.session_state.page_type == "image":
            # Notion에서 가져온 JSON 문자열
            current_adjectives_json = selected_result['properties'].get('adjectives', {}).get('rich_text', [])
            if current_adjectives_json:
                current_adjectives_json = current_adjectives_json[0].get('text', {}).get('content', '')
                try:
                    # JSON 문자열을 리스트로 변환
                    current_adjectives_list = json.loads(current_adjectives_json)
                    # 리스트를 쉼표로 구분된 문자열로 변환하여 표시
                    current_adjectives_str = ', '.join(current_adjectives_list)
                except json.JSONDecodeError:
                    # 파싱 실패 시 원본 문자열 사용
                    current_adjectives_str = current_adjectives_json
            else:
                current_adjectives_str = ''
            # 사용자에게 형용사 입력란 표시
            new_adjectives_str = st.text_area("새 형용사를 입력하세요 (쉼표로 구분):", current_adjectives_str, key="new_adjectives")
        elif st.session_state.page_type == "chatbot":
            # 이제 'student_view'를 사용합니다.
            rich_text_list = selected_result['properties'].get('student_view', {}).get('rich_text', [])
            if rich_text_list:
                current_student_view = rich_text_list[0].get('text', {}).get('content', '')
            else:
                current_student_view = ''
            new_student_view = st.text_area("새 학생용 보기 텍스트를 입력하세요:", current_student_view, key="new_student_view")
        elif st.session_state.page_type in ["vision", "text"]:
            # Safely get the student_view property
            rich_text_list = selected_result['properties'].get('student_view', {}).get('rich_text', [])
            if rich_text_list:
                current_student_view = rich_text_list[0].get('text', {}).get('content', '')
            else:
                current_student_view = ''
            new_student_view = st.text_area("새 학생용 보기 텍스트를 입력하세요:", current_student_view, key="new_student_view")

        submitted = st.form_submit_button("프롬프트 업데이트")

        if submitted:
            with st.spinner('🔄 프롬프트를 업데이트하는 중입니다...'):
                if st.session_state.page_type == "image":
                    # 사용자 입력을 리스트로 변환
                    new_adjectives_list = [adj.strip() for adj in new_adjectives_str.split(',') if adj.strip()]
                    # 리스트를 JSON 문자열로 변환
                    new_adjectives_json = json.dumps(new_adjectives_list, ensure_ascii=False)
                    update_success = update_prompt(
                        st.session_state.page_type,
                        activity_code,
                        new_prompt,
                        new_email,
                        st.session_state.password,
                        adjectives=new_adjectives_json
                    )
                elif st.session_state.page_type == "chatbot":
                    update_success = update_prompt(
                        st.session_state.page_type,
                        activity_code,
                        new_prompt,
                        new_email,
                        st.session_state.password,
                        student_view=new_student_view  # 변경된 부분
                    )
                elif st.session_state.page_type in ["vision", "text"]:
                    update_success = update_prompt(
                        st.session_state.page_type,
                        activity_code,
                        new_prompt,
                        new_email,
                        st.session_state.password,
                        student_view=new_student_view
                    )
                else:
                    update_success = update_prompt(
                        st.session_state.page_type,
                        activity_code,
                        new_prompt,
                        new_email,
                        st.session_state.password
                    )

                if update_success:
                    st.session_state.current_step = 5  # 업데이트 성공 시 다음 단계로 이동
                    st.rerun()
                else:
                    st.error("❌ 업데이트에 실패했습니다.")

# 초기화: 세션 상태에 현재 단계가 없을 경우 1로 설정
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# 교사용 인터페이스
st.title("🛠️ 교사용 프롬프트 관리 도구")

st.markdown("""
이 도구를 사용하여 저장된 프롬프트를 검색하고 삭제, 수정할 수 있습니다.
""")

# 단계별 UI 구성
if st.session_state.current_step == 1:
    st.header("1. 분석/생성 유형 선택")
    page_type = st.selectbox("분석/생성 유형을 선택하세요:", ["vision", "text", "image", "chatbot"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("다음", key="next_step1"):
            st.session_state.page_type = page_type
            st.session_state.current_step = 2
    with col2:
        st.write("")  # 빈 공간

elif st.session_state.current_step == 2:
    st.header("2. 비밀번호 입력 및 프롬프트 검색")
    password = st.text_input("🔒 비밀번호를 입력하세요:", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전", key="previous_step2"):
            st.session_state.current_step = 1
    with col2:
        if st.button("다음", key="next_step2"):
            if password:
                st.session_state.password = password
                results = search_prompt_by_password(st.session_state.page_type, password)
                if results:
                    st.session_state.search_results = results
                    st.session_state.current_step = 3
                else:
                    st.warning("⚠️ 해당 비밀번호에 대한 프롬프트를 찾을 수 없습니다.")
            else:
                st.error("⚠️ 비밀번호를 입력하세요.")

elif st.session_state.current_step == 3:
    st.header("3. 삭제 또는 수정 선택")
    st.subheader("검색 결과:")

    if st.session_state.search_results:
        # 검색된 프롬프트를 테이블로 생성
        data = []
        for idx, res in enumerate(st.session_state.search_results):
            activity_code = res['properties']['activity_code']['rich_text'][0]['text']['content']
            prompt = res['properties']['prompt']['rich_text'][0]['text']['content']

            if st.session_state.page_type == "image":
                adjectives_rich_text = res['properties'].get('adjectives', {}).get('rich_text', [])
                if adjectives_rich_text:
                    adjectives = adjectives_rich_text[0].get('text', {}).get('content', '')
                else:
                    adjectives = ''
                data.append({"번호": idx + 1, "활동 코드": activity_code, "프롬프트": prompt, "형용사": adjectives})
            elif st.session_state.page_type == "chatbot":
                rich_text_list = res['properties'].get('student_view', {}).get('rich_text', [])
                if rich_text_list:
                    student_view = rich_text_list[0].get('text', {}).get('content', '')
                else:
                    student_view = ''
                data.append({"번호": idx + 1, "활동 코드": activity_code, "프롬프트": prompt, "학생용 보기": student_view})
            elif st.session_state.page_type in ["vision", "text"]:
                rich_text_list = res['properties'].get('student_view', {}).get('rich_text', [])
                if rich_text_list:
                    student_view = rich_text_list[0].get('text', {}).get('content', '')
                else:
                    student_view = ''
                data.append({"번호": idx + 1, "활동 코드": activity_code, "프롬프트": prompt, "학생용 보기": student_view})
            else:
                data.append({"번호": idx + 1, "활동 코드": activity_code, "프롬프트": prompt})

        st.table(data)

        # 삭제 또는 수정할 프롬프트 선택
        st.markdown("### 삭제 또는 수정할 프롬프트를 선택하세요:")
        prompt_options = [
            f"{item['번호']}. 활동 코드: {item['활동 코드']} | 프롬프트: {item['프롬프트']}" for item in data
        ]
        selected_prompt = st.selectbox("선택:", prompt_options, key="select_prompt_action")

        if selected_prompt:
            selected_index = int(selected_prompt.split('.')[0]) - 1
            selected_result = st.session_state.search_results[selected_index]
            selected_activity_code = selected_result['properties']['activity_code']['rich_text'][0]['text']['content']
            current_prompt = selected_result['properties']['prompt']['rich_text'][0]['text']['content']
            current_email = selected_result['properties']['email']['rich_text'][0]['text']['content']

            # 삭제 및 수정 버튼
            col1, col2 = st.columns(2)
            with col1:
                if st.button("삭제", key=f"delete_{selected_activity_code}"):
                    delete_success = delete_prompt_by_activity_code(st.session_state.page_type, selected_activity_code)
                    if delete_success:
                        st.session_state.current_step = 1
                        st.rerun()
            with col2:
                if st.button("수정", key=f"modify_{selected_activity_code}"):
                    st.session_state.selected_activity_code = selected_activity_code
                    st.session_state.current_step = 4  # 수정 단계로 이동
    else:
        st.warning("⚠️ 검색된 프롬프트가 없습니다.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("이전", key="previous_step3_no_results"):
                st.session_state.current_step = 2

elif st.session_state.current_step == 4:
    st.header("4. 프롬프트 수정")
    activity_code = st.session_state.get('selected_activity_code', None)
    if not activity_code:
        st.error("❌ 수정할 활동 코드를 찾을 수 없습니다.")
        st.session_state.current_step = 1
    else:
        selected_result = next(res for res in st.session_state.search_results if res['properties']['activity_code']['rich_text'][0]['text']['content'] == activity_code)
        current_prompt = selected_result['properties']['prompt']['rich_text'][0]['text']['content']
        current_email = selected_result['properties']['email']['rich_text'][0]['text']['content']

        # 프롬프트 수정 폼 호출
        update_prompt_form(selected_result, activity_code, current_prompt, current_email)

elif st.session_state.current_step == 5:
    st.success("🎉 프롬프트가 성공적으로 수정되었습니다!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("처음으로", key="reset"):
            st.session_state.current_step = 1
            st.rerun()
    with col2:
        st.write("")  # 빈 공간
