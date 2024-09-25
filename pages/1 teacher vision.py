import streamlit as st
from utils import set_page_config, load_secrets, is_activity_code_duplicate, save_to_notion, initialize_openai_client
import requests
from datetime import datetime

# 페이지 설정
set_page_config("교사용 교육 도구 비전", "🧑‍🏫", "#E0FFFF")

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
NOTION_DATABASE_ID = secrets["notion"]["database_id_vision"]

# 중복 확인 함수 정의
def is_activity_code_duplicate_for_text(activity_code):
    return is_activity_code_duplicate(NOTION_API_KEY, NOTION_DATABASE_ID, "vision", activity_code)

# GPT-4를 사용하여 학생용 안내 내용 생성
def generate_student_view(teacher_prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 교사가 만든 vision 프롬프트의 제목을 간단한 단어로 변환하는 AI 조교입니다."},
                {"role": "user", "content": f"다음 vision 프롬프트의 제목을 지어주고, 이 프롬프트와 인공지능 모델을 이용하기 위해 학생이 입력해야할 이미지를 말해주세요.: {teacher_prompt}"}
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
            "page": {"rich_text": [{"text": {"content": "vision"}}]}
        }
    }
    return save_to_notion(NOTION_API_KEY, NOTION_DATABASE_ID, "vision", data)

# 교사용 인터페이스
st.title("📸 교사용 이미지 분석 프롬프트 생성 도구")

st.markdown("""
**안내:** 이 도구를 사용하여 이미지 분석 API를 활용한 교육용 프롬프트를 쉽게 생성할 수 있습니다. 다음 중 하나의 방법을 선택하세요:
1. **샘플 프롬프트 이용하기**: 미리 준비된 샘플 프롬프트를 사용해 보세요.
2. **직접 프롬프트 만들기**: 프롬프트를 직접 작성하세요.
3. **인공지능 도움받기**: 인공지능의 도움을 받아 프롬프트를 생성하세요.
4. **학생용 앱과 연동**: 이곳에서 저장한 프롬프트는 [학생용 앱](https://students.streamlit.app/)에서 불러와 안전하게 AI를 사용할 수 있습니다.
""")

# 샘플 프롬프트 목록
sample_prompts = {
    "2학년 미술시간 - 사진 속 감정 분석": "사진 속 인물들의 감정을 분석하여 초등학생이 이해할 수 있도록 설명해 주세요.",
    "2학년 사회시간 - 풍경 사진 설명": "풍경 사진을 보고, 그 특징과 아름다움을 초등학생이 이해할 수 있도록 설명해 주세요.",
    "2학년 과학시간 - 동물 사진 설명": "동물 사진을 보고, 그 동물의 특성을 설명하고, 초등학생이 이해할 수 있도록 쉽게 풀어 설명해 주세요.",
    "2학년 미술시간 - 미술 작품 분석": "미술 작품 사진을 보고, 초등학생이 이해할 수 있도록 그 작품의 주요 특징을 설명해 주세요.",
    "3학년 과학시간 - 자연 현상 분석": "자연 현상의 사진을 보고, 그 현상이 무엇인지 설명하고 왜 그런 현상이 일어나는지 초등학생에게 설명해 주세요.",
    "3학년 사회시간 - 건축물 사진 설명": "건축물 사진을 보고, 그 건축물이 어떤 목적으로 만들어졌는지와 그 디자인의 특징을 설명해 주세요.",
    "3학년 과학시간 - 동물 행동 분석": "동물이 무엇을 하고 있는지 사진을 보고 설명하고, 그 행동이 왜 중요한지 설명해 주세요.",
    "3학년 사회시간 - 날씨 사진 설명": "날씨와 관련된 사진을 보고 그 날씨 상황을 설명하고, 초등학생이 이해할 수 있도록 그 영향도 설명해 주세요.",
    "4학년 과학시간 - 우주 사진 설명": "우주 사진을 보고, 그 사진에 나타난 행성, 별, 은하 등을 설명하고, 초등학생이 이해할 수 있도록 그 특징을 알려주세요.",
    "4학년 체육시간 - 스포츠 사진 분석": "스포츠 경기가 이루어지는 사진을 보고, 그 경기의 규칙과 진행 상황을 설명해 주세요.",
    "5학년 사회시간 - 사람의 표정 분석": "사람의 표정을 분석하여 그 사람이 어떤 감정을 느끼고 있을지 초등학생이 이해할 수 있도록 설명해 주세요.",
    "5학년 사회시간 - 교통수단 사진 설명": "교통수단의 사진을 보고, 그 교통수단이 어떻게 사용되는지와 왜 중요한지 설명해 주세요.",
    "5학년 과학시간 - 식물 사진 분석": "식물의 사진을 보고, 그 식물이 어떻게 자라는지와 그 식물의 특징을 설명해 주세요.",
    "6학년 사회시간 - 고대 유물 사진 설명": "고대 유물의 사진을 보고, 그 유물이 어떤 역사적 의미를 가지는지 설명해 주세요.",
    "6학년 역사시간 - 인물 사진 설명": "역사적 인물의 사진을 보고, 그 인물이 어떤 일을 했고 왜 중요한지 초등학생이 이해할 수 있도록 설명해 주세요.",
    "6학년 사회시간 - 풍경 사진의 계절 설명": "풍경 사진을 보고, 그 사진이 어떤 계절에 찍혔는지와 그 계절의 특징을 설명해 주세요.",
    "6학년 과학시간 - 기후 변화 사진 분석": "기후 변화의 징후를 보여주는 사진을 보고, 그 사진이 무엇을 나타내고 있는지 설명하고 기후 변화의 중요성을 설명해 주세요.",
    "6학년 역사시간 - 역사적 사건 사진 설명": "역사적인 사건이 담긴 사진을 보고, 그 사건이 무엇인지와 왜 중요한지 초등학생이 이해할 수 있도록 설명해 주세요.",
    "6학년 사회시간 - 문화 행사 사진 설명": "문화 행사의 사진을 보고, 그 행사가 어떤 목적으로 이루어졌고 그 의미가 무엇인지 설명해 주세요.",
    "6학년 과학시간 - 직업 사진 설명": "다양한 직업을 가진 사람들이 나오는 사진을 보고, 그 사람들이 어떤 일을 하고 있는지 설명해 주세요."
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
        st.session_state.direct_prompt = st.text_area("✏️ 샘플 프롬프트 수정 가능:", value=sample_prompts[selected_sample], height=300)
        st.session_state.final_prompt = st.session_state.direct_prompt

# 직접 프롬프트 입력
elif prompt_method == "직접 입력":
    example_prompt = "예시: 너는 A활동을 돕는 보조교사 입니다. 학생이 B사진을 입력하면, 인공지능이 B를 분석하여 C를 할 수 있도록 도움을 주세요."
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
                            {"role": "system", "content": "당신은 Vision API를 사용하여 교육 목적으로 시스템 프롬프트를 만드는 것을 돕는 AI입니다. 이미지의 시각적 요소를 분석하여 이에 기반한 프롬프트를 생성하세요."},
                            {"role": "user", "content": f"프롬프트의 주제는: {input_topic}입니다. 이 주제를 바탕으로 Vision API를 사용하여 창의적이고 교육적인 시스템 프롬프트를 생성해 주세요."}
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
                    st.session_state.ai_prompt = ""

    # 인공지능 프롬프트가 생성된 경우에만 표시
    if st.session_state.ai_prompt:
        st.session_state.ai_prompt = st.text_area("✏️ 인공지능이 만든 프롬프트를 살펴보고 직접 수정하세요:", 
                                                  value=st.session_state.ai_prompt, height=300)
        st.session_state.final_prompt = st.session_state.ai_prompt

# 활동 코드 입력
if st.session_state.final_prompt:
    st.subheader("🔑 활동 코드 설정")
    activity_code = st.text_input("활동 코드를 입력하세요", value=st.session_state.get('activity_code', '')).strip()

    # 숫자만 입력된 경우에도 허용하도록 변경
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

