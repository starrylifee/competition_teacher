import streamlit as st
from utils import set_page_config, load_secrets, is_activity_code_duplicate, save_to_notion, initialize_openai_client
import requests
from datetime import datetime

# 페이지 설정
set_page_config("교사용 교육 도구 텍스트", "🧑‍🏫", "#FFFACD")

# secrets 로드
secrets = load_secrets()
if not secrets:
    st.stop()

# OpenAI 클라이언트 초기화
client = initialize_openai_client(secrets)
if not client:
    st.stop()

# Notion API 설정
NOTION_API_KEY = secrets["notion"]["api_key"]
NOTION_DATABASE_ID = secrets["notion"]["database_id_text"]

# 중복 확인 함수 정의
def is_activity_code_duplicate_for_text(activity_code):
    return is_activity_code_duplicate(NOTION_API_KEY, NOTION_DATABASE_ID, "text", activity_code)

# GPT-4를 사용하여 학생용 안내 내용 생성
def generate_student_view(teacher_prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 수업용 프롬프트를 학생들이 필요한 내용으로 변환하는 AI 조교입니다."},
                {"role": "user", "content": f"다음 수업용 프롬프트를 학생들이 할 미션으로 아주 간단하게 변환해주세요: {teacher_prompt}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"⚠️ 학생용 안내 내용 생성 중 오류가 발생했습니다: {e}")
        return ""

# Notion에 데이터 저장 함수 정의
def save_to_notion_data(activity_code, teacher_prompt, email, password):
    student_view = generate_student_view(teacher_prompt)
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "activity_code": {"rich_text": [{"text": {"content": activity_code}}]},
            "prompt": {"rich_text": [{"text": {"content": teacher_prompt}}]},
            "student_view": {"rich_text": [{"text": {"content": student_view}}]},
            "email": {"rich_text": [{"text": {"content": email}}]},
            "password": {"rich_text": [{"text": {"content": password}}]},
            "date": {"rich_text": [{"text": {"content": datetime.now().isoformat()}}]},
            "page": {"rich_text": [{"text": {"content": "text"}}]}
        }
    }
    return save_to_notion(NOTION_API_KEY, NOTION_DATABASE_ID, "text", data)

# 교사용 인터페이스
st.title("🎓 교사용 프롬프트 생성 도구")

st.markdown("""
**안내:** 이 도구를 사용하여 교육 활동에 필요한 프롬프트를 쉽게 생성할 수 있습니다. 다음 중 하나의 방법을 선택하세요:
1. **샘플 프롬프트 이용하기**: 미리 준비된 샘플 프롬프트를 사용해 보세요.
2. **직접 프롬프트 만들기**: 프롬프트를 직접 작성하세요.
3. **인공지능 도움받기**: 인공지능의 도움을 받아 프롬프트를 생성하세요.
4. **학생용 앱과 연동**: 이곳에서 저장한 프롬프트는 [학생용 앱](https://students.streamlit.app/)에서 불러와 안전하게 AI를 사용할 수 있습니다.
""")

# 샘플 프롬프트 목록
sample_prompts = {
    "사회시간 - 백과사전 글 쉽게 설명하기": "네이버 백과사전에서 가져온 글을 초등학교 3학년이 이해할 수 있도록 쉽게 설명해 주세요.",
    "국어시간 - 시 번역하기": "어려운 시를 읽고, 초등학생이 이해하기 쉬운 풀어서 설명해 주세요.",
    "친구에게 줄 상장 만들기": "친구에게 줄 상장을 만들고 싶어요. 친구와의 즐거웠던 추억을 넣어 상장 제목과 내용을 만들어 주세요.",
    "모둠활동 - 이야기 이어쓰기": "모둠에서 짧은 글을 지었습니다. 이 이후의 대화를 상상해서 이어서 적어 주세요.",
    "과학시간 - 어려운 개념 쉽게 설명하기": "오늘 배운 과학 개념을 초등학생이 이해할 수 있게 쉽게 설명해 주세요.",
    "역사시간 - 역사적 사건 요약하기": "역사 교과서에서 본 복잡한 사건을 초등학교 4학년이 이해할 수 있도록 간단히 요약해 주세요.",
    "음악시간 - 노래 가사 쉽게 풀어쓰기": "어려운 노래 가사를 초등학생이 이해할 수 있게 쉽게 풀어서 설명해 주세요.",
    "미술시간 - 작품 설명": "유명한 미술 작품에 대해 읽고, 초등학교 3학년이 이해할 수 있게 간단히 설명해 주세요.",
    "수학시간 - 문제 풀이 설명": "어려운 수학 문제의 풀이 과정을 초등학생이 이해할 수 있도록 쉽게 설명해 주세요.",
    "도덕시간 - 윤리적 상황 설명": "복잡한 윤리적 상황을 간단하게 풀어서 초등학생이 이해할 수 있도록 설명해 주세요."
}

# 프롬프트 생성 방법 선택
prompt_method = st.selectbox("프롬프트 생성 방법을 선택하세요:", ["샘플 프롬프트 이용하기", "직접 입력", "인공지능 도움 받기"])

# 세션 상태 초기화
if "direct_prompt" not in st.session_state:
    st.session_state.direct_prompt = ""
if "ai_prompt" not in st.session_state:
    st.session_state.ai_prompt = ""
if "final_prompt" not in st.session_state:
    st.session_state.final_prompt = ""

# 샘플 프롬프트 이용하기
if prompt_method == "샘플 프롬프트 이용하기":
    st.subheader("📚 샘플 프롬프트")
    selected_sample = st.selectbox("샘플 프롬프트를 선택하세요:", ["선택하세요"] + list(sample_prompts.keys()))

    if selected_sample != "선택하세요":
        st.info(f"선택된 프롬프트: {sample_prompts[selected_sample]}")
        st.session_state.direct_prompt = st.text_area("✏️ 샘플 프롬프트 수정 가능:", value=sample_prompts[selected_sample], height=300)
        st.session_state.final_prompt = st.session_state.direct_prompt

# 직접 프롬프트 입력
elif prompt_method == "직접 입력":
    example_prompt = "예시: 너는 A활동을 돕는 보조교사 입니다. 학생이 B를 입력하면, 인공지능이 B를 분석하여 C를 할 수 있도록 도움을 주세요."
    st.session_state.direct_prompt = st.text_area("✏️ 직접 입력할 프롬프트:", example_prompt, height=300)
    st.session_state.final_prompt = st.session_state.direct_prompt

# 인공지능 도움 받기
elif prompt_method == "인공지능 도움 받기":
    input_topic = st.text_input("📚 프롬프트 주제 또는 키워드를 입력하세요:", "")

    if st.button("✨ 인공지능아 프롬프트를 만들어줘"):
        if input_topic.strip() == "":
            st.error("⚠️ 주제를 입력하세요.")
        else:
            with st.spinner('🧠 프롬프트를 생성 중입니다...'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",  # 적절한 GPT 모델을 선택
                        messages=[
                            {"role": "system", "content": "당신은 text generation api를 이용하여 교육 목적으로 시스템 프롬프트를 만드는 것을 돕는 AI입니다."},
                            {"role": "user", "content": f"프롬프트의 주제는: {input_topic}입니다. 이 주제를 바탕으로 Text Generation API를 사용하여 창의적이고 교육적인 시스템 프롬프트를 생성해 주세요."}
                        ]
                    )
                    
                    if response.choices and response.choices[0].message.content:
                        st.session_state.ai_prompt = response.choices[0].message.content.strip()
                        st.session_state.final_prompt = st.session_state.ai_prompt  # 최종 프롬프트 업데이트
                    else:
                        st.error("⚠️ 프롬프트 생성에 실패했습니다. 다시 시도해 주세요.")
                        st.session_state.ai_prompt = ""

                except Exception as e:
                    st.error(f"⚠️ 프롬프트 생성 중 오류가 발생했습니다: {e}")

    # 인공지능 프롬프트가 생성된 경우에만 표시
    if st.session_state.ai_prompt:
        st.session_state.ai_prompt = st.text_area("✏️ 인공지능이 만든 프롬프트를 살펴보고 직접 수정하세요:", 
                                                    value=st.session_state.ai_prompt, height=300)
        st.session_state.final_prompt = st.session_state.ai_prompt

# 활동 코드 입력
if st.session_state.final_prompt:
    st.subheader("🔑 활동 코드 설정")
    activity_code = st.text_input("활동 코드를 입력하세요", value=st.session_state.get('activity_code', '')).strip()

    if is_activity_code_duplicate_for_text(activity_code):
        st.error("⚠️ 이미 사용된 코드입니다. 다른 코드를 입력해주세요.")
        activity_code = ""  # 중복된 경우 초기화
    else:
        st.session_state['activity_code'] = activity_code

    # Email 및 Password 입력
    email = st.text_input("📧 Email (선택사항) 학생의 생성결과물을 받아볼 수 있습니다.", value=st.session_state.get('email', '')).strip()
    password = st.text_input("🔒 Password (선택사항) 저장한 프롬프트를 조회, 삭제할 수 있습니다.", value=st.session_state.get('password', ''), type="password").strip()

    st.markdown("**[https://students.streamlit.app/](https://students.streamlit.app/)** 에서 학생들이 이 활동 코드를 입력하면 해당 프롬프트를 불러올 수 있습니다.")

# 서버 저장 버튼은 항상 표시되며, 입력 검증 후 동작
if st.button("💾 프롬프트를 서버에 저장"):
    if not st.session_state.final_prompt.strip():
        st.error("⚠️ 프롬프트가 없습니다. 먼저 프롬프트를 생성하세요.")
    elif not activity_code:
        st.error("⚠️ 활동 코드를 입력하세요.")
    elif password and password.isnumeric():
        st.error("⚠️ 비밀번호는 숫자만 입력할 수 없습니다. 영문 또는 영문+숫자 조합을 사용하세요.")
    else:
        with st.spinner('💾 데이터를 저장하는 중입니다...'):
            student_view = generate_student_view(st.session_state.final_prompt)
            if save_to_notion_data(activity_code, st.session_state.final_prompt, email, password):
                st.success(f"🎉 프롬프트가 성공적으로 저장되었습니다. **저장된 값:**\n\n"
                           f"**활동 코드:** {activity_code}\n"
                           f"**프롬프트:** {st.session_state.final_prompt}\n"
                           f"**학생용 안내:** {student_view}\n"
                           f"**이메일:** {email}\n"
                           f"**비밀번호:** {'[입력됨]' if password else '[입력되지 않음]'}")
            else:
                st.error("❌ 프롬프트 저장 중 오류가 발생했습니다.")
