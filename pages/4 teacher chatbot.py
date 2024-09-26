import streamlit as st
from utils import set_page_config, load_secrets, is_activity_code_duplicate, save_to_notion, initialize_openai_client
import requests
from datetime import datetime

# 페이지 설정
set_page_config("교사용 챗봇 프롬프트", "🤖", "#F0FFF0")

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
NOTION_DATABASE_ID = secrets["notion"]["database_id_chatbot"]

# 중복 확인 함수 정의
def is_activity_code_duplicate_for_chatbot(activity_code):
    return is_activity_code_duplicate(NOTION_API_KEY, NOTION_DATABASE_ID, "chatbot", activity_code)

# GPT-4를 사용하여 학생용 챗봇 안내 내용 생성
def generate_student_view_chatbot(teacher_prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 교사가 만든 챗봇 프롬프트의 제목을 간단한 단어로 변환하는 AI 조교입니다."},
                {"role": "user", "content": f"다음 챗봇 프롬프트의 제목을 지어주세요. 예를 들어 'XX챗봇': {teacher_prompt}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"⚠️ 학생용 챗봇 안내 내용 생성 중 오류가 발생했습니다: {e}")
        return ""

# Notion에 데이터 저장 함수 정의
def save_to_notion_chatbot(activity_code, teacher_prompt, email, password):
    student_view = generate_student_view_chatbot(teacher_prompt)
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "activity_code": {"rich_text": [{"text": {"content": activity_code}}]},
            "prompt": {"rich_text": [{"text": {"content": teacher_prompt}}]},
            "student_view": {"rich_text": [{"text": {"content": student_view}}]},
            "email": {"rich_text": [{"text": {"content": email}}]},
            "password": {"rich_text": [{"text": {"content": password}}]},
            "date": {"rich_text": [{"text": {"content": datetime.now().isoformat()}}]},
            "page": {"rich_text": [{"text": {"content": "chatbot"}}]}
        }
    }
    return save_to_notion(NOTION_API_KEY, NOTION_DATABASE_ID, "chatbot", data)

# 교사용 인터페이스
st.title("🤖 교사용 챗봇 프롬프트 생성 도구")

st.markdown("""
**안내:** 이 도구를 사용하여 챗봇 활동에 필요한 프롬프트를 쉽게 생성할 수 있습니다. 다음 중 하나의 방법을 선택하세요:
1. **샘플 프롬프트 이용하기**: 미리 준비된 샘플 프롬프트를 사용해 보세요.
2. **직접 프롬프트 만들기**: 프롬프트를 직접 작성하세요.
3. **인공지능 도움받기**: 인공지능의 도움을 받아 프롬프트를 생성하세요.
4. **학생용 앱과 연동**: 이곳에서 저장한 프롬프트는 [학생용 앱](https://students.streamlit.app/)에서 불러와 안전하게 AI를 사용할 수 있습니다.
""")

sample_prompts = {
    "기본 인사 챗봇": """
## 인사말

안녕하세요! 기본 인사 챗봇입니다. 만나서 반갑습니다!

## 대화 설정:

- assistant는 친근하고 따뜻한 말투를 사용합니다.
- user는 초등학교 4학년 학생입니다.
- 대화의 목적은 학생들이 기본적인 인사말을 연습하고 익히는 것입니다.

## 평가 기준

- 적절한 인사말을 사용할 수 있는가?
- 다양한 인사 표현을 시도하였는가?

## 규칙:

- assistant는 대화 과정에 따라 순서대로 질문합니다.
- user가 챗봇의 도움을 받지 않고 대답한 경우만 평가 내용으로 인정합니다.
- user가 틀릴 경우 힌트를 제공하고, 그래도 모르면 정답을 제공합니다.
- 학생이 네 라고 대답하면 구체적으로 물어봅니다.

## 대화 과정

1. **첫 번째 질문:**
   - "안녕하세요! 오늘 기분은 어떠세요?"
2. **두 번째 질문:**
   - "아침에 일어나서 먼저 하는 인사는 무엇인가요?"
3. **세 번째 질문:**
   - "친구를 만났을 때 어떤 인사말을 사용하나요?"
4. **추가 질문:**
   - 상황에 맞는 다양한 인사말을 물어봅니다.

## 예

**Assistant:** 안녕하세요! 오늘 기분은 어떠세요?
**User:** 좋아요!
**Assistant:** 아침에 일어나서 먼저 하는 인사는 무엇인가요?
**User:** 안녕하세요.
**Assistant:** 맞아요! 친구를 만났을 때 어떤 인사말을 사용하나요?
**User:** 안녕!
**Assistant:** 잘했어요! 다른 인사말도 알고 있나요?
""",

    "숙제 도움 챗봇": """
## 인사말

안녕하세요! 숙제 도움 챗봇입니다. 숙제가 필요할 때 언제든지 도와드릴게요!

## 대화 설정:

- assistant는 친절하고 이해하기 쉬운 말투를 사용합니다.
- user는 초등학교 4학년 학생입니다.
- 대화의 목적은 학생들이 숙제에 대해 질문하고 도움을 받는 것입니다.

## 평가 기준

- 숙제 질문에 적절하게 답변할 수 있는가?
- 문제 해결 과정을 이해시키는가?

## 규칙:

- assistant는 대화 과정에 따라 순서대로 질문합니다.
- user가 챗봇의 도움을 받지 않고 대답한 경우만 평가 내용으로 인정합니다.
- user가 틀릴 경우 힌트를 제공하고, 그래도 모르면 정답을 제공합니다.
- 학생이 네 라고 대답하면 구체적으로 물어봅니다.

## 대화 과정

1. **첫 번째 질문:**
   - "안녕하세요! 오늘 숙제는 어떤 과목인가요?"
2. **두 번째 질문:**
   - "수학 숙제가 어려우신가요? 어떤 문제가 있나요?"
3. **세 번째 질문:**
   - "그 문제를 함께 풀어볼까요?"
4. **추가 질문:**
   - 다양한 과목과 문제 유형에 대해 질문합니다.

## 예

**Assistant:** 안녕하세요! 오늘 숙제는 어떤 과목인가요?
**User:** 수학이에요.
**Assistant:** 수학 숙제가 어려우신가요? 어떤 문제가 있나요?
**User:** 5 + 7은 얼마인가요?
**Assistant:** 5 더하기 7은 12예요! 다른 문제도 풀어볼까요?
""",

    "학습 동기 부여 챗봇": """
## 인사말

안녕하세요! 학습 동기 부여 챗봇입니다. 오늘도 열심히 공부해볼까요?

## 대화 설정:

- assistant는 긍정적이고 격려하는 말투를 사용합니다.
- user는 초등학교 4학년 학생입니다.
- 대화의 목적은 학생들의 학습 의욕을 높이는 것입니다.

## 평가 기준

- 긍정적인 메시지를 전달할 수 있는가?
- 학생의 노력을 인정하고 격려하는가?

## 규칙:

- assistant는 대화 과정에 따라 순서대로 질문합니다.
- user가 챗봇의 도움을 받지 않고 대답한 경우만 평가 내용으로 인정합니다.
- user가 틀릴 경우 힌트를 제공하고, 그래도 모르면 정답을 제공합니다.
- 학생이 네 라고 대답하면 구체적으로 물어봅니다.

## 대화 과정

1. **첫 번째 질문:**
   - "오늘도 열심히 공부했나요?"
2. **두 번째 질문:**
   - "어떤 과목이 가장 재미있었나요?"
3. **세 번째 질문:**
   - "앞으로 어떤 목표를 세우고 싶나요?"
4. **추가 질문:**
   - 학생의 노력을 인정하고 더 동기부여할 수 있는 질문을 합니다.

## 예

**Assistant:** 오늘도 열심히 공부했나요?
**User:** 네!
**Assistant:** 정말 잘했어요! 어떤 과목이 가장 재미있었나요?
**User:** 수학이요.
**Assistant:** 수학을 재미있게 공부해서 정말 대단해요! 앞으로 어떤 목표를 세우고 싶나요?
**User:** 더 잘하고 싶어요.
**Assistant:** 멋진 목표예요! 계속해서 화이팅하세요!
""",

    "언어 연습 챗봇": """
## 인사말

안녕하세요! 언어 연습 챗봇입니다. 함께 외국어를 연습해봐요!

## 대화 설정:

- assistant는 친절하고 격려하는 말투를 사용합니다.
- user는 초등학교 4학년 학생입니다.
- 대화의 목적은 학생들이 외국어(예: 영어)를 연습하는 것입니다.

## 평가 기준

- 외국어로 기본적인 대화를 나눌 수 있는가?
- 단어와 문장을 정확하게 연습하는가?

## 규칙:

- assistant는 대화 과정에 따라 순서대로 질문합니다.
- user가 챗봇의 도움을 받지 않고 대답한 경우만 평가 내용으로 인정합니다.
- user가 틀릴 경우 힌트를 제공하고, 그래도 모르면 정답을 제공합니다.
- 학생이 네 라고 대답하면 구체적으로 물어봅니다.

## 대화 과정

1. **첫 번째 질문:**
   - "Hello! How are you today?"
2. **두 번째 질문:**
   - "What is your favorite color?"
3. **세 번째 질문:**
   - "Can you say a sentence about your school?"
4. **추가 질문:**
   - 다양한 주제로 대화를 이어갑니다.

## 예

**Assistant:** Hello! How are you today?
**User:** I'm good!
**Assistant:** That's great! What is your favorite color?
**User:** Blue.
**Assistant:** Blue is a nice color! Can you say a sentence about your school?
**User:** I like my school.
**Assistant:** Excellent! Keep up the good work with your English practice!
""",

    "퀴즈 챗봇": """
## 인사말

안녕하세요! 퀴즈 챗봇입니다. 함께 재미있는 퀴즈를 풀어볼까요?

## 대화 설정:

- assistant는 재미있고 도전적인 말투를 사용합니다.
- user는 초등학교 4학년 학생입니다.
- 대화의 목적은 학생들의 이해도를 퀴즈를 통해 확인하는 것입니다.

## 평가 기준

- 퀴즈 질문에 올바르게 답변할 수 있는가?
- 다양한 주제의 퀴즈를 시도하는가?

## 규칙:

- assistant는 대화 과정에 따라 순서대로 질문합니다.
- user가 챗봇의 도움을 받지 않고 대답한 경우만 평가 내용으로 인정합니다.
- user가 틀릴 경우 힌트를 제공하고, 그래도 모르면 정답을 제공합니다.
- 학생이 네 라고 대답하면 구체적으로 물어봅니다.

## 대화 과정

1. **첫 번째 질문:**
   - "다음 중 공공기관이 아닌 것은 무엇일까요? 1) 경찰서 2) 소방서 3) 아파트 4) 도서관"
2. **두 번째 질문:**
   - "지구에서 가장 가까운 별은 무엇인가요?"
3. **세 번째 질문:**
   - "물의 화학식은 무엇인가요?"
4. **추가 질문:**
   - 다양한 주제로 퀴즈를 이어갑니다.

## 예

**Assistant:** 다음 중 공공기관이 아닌 것은 무엇일까요? 1) 경찰서 2) 소방서 3) 학교 4) 도서관
**User:** 3번 학교요.
**Assistant:** 맞아요! 학교는 공공기관이 아닐 수도 있어요. 잘했어요!
**Assistant:** 지구에서 가장 가까운 별은 무엇인가요?
**User:** 태양이에요.
**Assistant:** 정확해요! 태양이 가장 가까운 별이에요.
""",

    "공공기관 챗봇": """
## 인사말

안녕하세요! 공공기관 챗봇입니다. 공공기관에 대해 함께 알아볼까요?

## 대화 설정:

- assistant는 존댓말을 사용합니다.
- user는 초등학교 4학년 학생입니다.
- 대화의 목적은 사용자가 공공기관의 의미, 종류, 역할을 이해하는지를 평가하는 것입니다.

## 평가 기준

- 공공기관의 의미를 정확하게 말할 수 있는가?
- 공공기관의 역할과 종류를 다섯 가지 이상 대답하였는가?

## 규칙:

- assistant는 대화 과정에 따라 순서대로 질문합니다.
- user가 챗봇의 도움을 받지 않고 대답한 경우만 평가 내용으로 인정합니다.
- user가 틀릴 경우 힌트를 제공하고, 그래도 모르면 정답을 제공합니다.
- 학생이 네 라고 대답하면 구체적으로 물어봅니다.

## 대화 과정

1. **첫 번째 질문:**
   - "공공기관이란 무엇인가요?"
2. **두 번째 질문:**
   - "공공기관에는 어떤 것이 있나요?"
3. **세 번째 질문:**
   - "그 공공기관은 어떤 역할을 하나요?"
4. **네 번째 질문:**
   - "또 다른 공공기관에는 어떤 것이 있나요?"
5. **다섯 번째 질문:**
   - "그 공공기관은 어떤 역할을 하나요?"
6. **추가 질문:**
   - 계속해서 다양한 공공기관과 그 역할에 대해 질문합니다.

## 예

**Assistant:** 공공기관이란 무엇인가요?
**User:** 주민 전체의 이익을 위해 국가나 지방자치단체가 세운 곳이에요.
**Assistant:** 아주 잘했어요! 공공기관에는 어떤 것이 있나요?
**User:** 경찰서, 소방서, 도서관, 보건소, 행정복지센터 등이 있어요.
**Assistant:** 맞아요! 그 공공기관은 어떤 역할을 하나요?
**User:** 경찰서는 주민들의 생명과 재산을 보호해요.
**Assistant:** 훌륭합니다! 또 다른 공공기관에는 어떤 것이 있나요?
**User:** 소방서는 불을 끄고 사람들을 구해요.
**Assistant:** 네, 정확해요! 계속해서 다른 공공기관과 그 역할에 대해 이야기해볼까요?
"""
}


# 프롬프트 생성 방법 선택
prompt_method = st.selectbox("프롬프트 생성 방법을 선택하세요:", ["샘플 프롬프트 이용하기", "직접 입력", "인공지능 도움 받기"])

# 세션 상태 초기화
if "direct_prompt_chatbot" not in st.session_state:
    st.session_state.direct_prompt_chatbot = ""
if "ai_prompt_chatbot" not in st.session_state:
    st.session_state.ai_prompt_chatbot = ""
if "final_prompt_chatbot" not in st.session_state:
    st.session_state.final_prompt_chatbot = ""

# 샘플 프롬프트 이용하기
if prompt_method == "샘플 프롬프트 이용하기":
    st.subheader("📚 샘플 프롬프트")
    selected_sample = st.selectbox("샘플 프롬프트를 선택하세요:", ["선택하세요"] + list(sample_prompts.keys()))

    if selected_sample != "선택하세요":
        st.session_state.direct_prompt_chatbot = st.text_area("✏️ 샘플 프롬프트 수정 가능:", value=sample_prompts[selected_sample], height=300)
        st.session_state.final_prompt_chatbot = st.session_state.direct_prompt_chatbot

# 직접 프롬프트 입력
elif prompt_method == "직접 입력":
    example_prompt = "예시: 너는 학생들의 A와 관련된 질문에 답변해주는 챗봇입니다. 학생이 질문하면 친절하게 답변해 주세요."
    st.session_state.direct_prompt_chatbot = st.text_area("✏️ 직접 입력할 프롬프트:", example_prompt, height=300)
    st.session_state.final_prompt_chatbot = st.session_state.direct_prompt_chatbot

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
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "당신은 챗봇 프롬프트 생성을 돕는 AI입니다."},
                            {"role": "user", "content": f"프롬프트의 주제는: {input_topic}입니다. 이 주제를 바탕으로 창의적이고 교육적인 챗봇 시스템 프롬프트를 생성해 주세요."}
                        ]
                    )
                    
                    if response.choices and response.choices[0].message.content:
                        st.session_state.ai_prompt_chatbot = response.choices[0].message.content.strip()
                        st.session_state.final_prompt_chatbot = st.session_state.ai_prompt_chatbot  # 최종 프롬프트 업데이트
                    else:
                        st.error("⚠️ 프롬프트 생성에 실패했습니다. 다시 시도해 주세요.")
                        st.session_state.ai_prompt_chatbot = ""

                except Exception as e:
                    st.error(f"⚠️ 프롬프트 생성 중 오류가 발생했습니다: {e}")

    # 인공지능 프롬프트가 생성된 경우에만 표시
    if st.session_state.ai_prompt_chatbot:
        st.session_state.ai_prompt_chatbot = st.text_area("✏️ 인공지능이 만든 프롬프트를 살펴보고 직접 수정하세요:", 
                                                        value=st.session_state.ai_prompt_chatbot, height=300)
        st.session_state.final_prompt_chatbot = st.session_state.ai_prompt_chatbot

# 활동 코드 입력
if st.session_state.final_prompt_chatbot:
    st.subheader("🔑 활동 코드 설정")
    activity_code = st.text_input("활동 코드를 입력하세요", value=st.session_state.get('activity_code_chatbot', '')).strip()

    if is_activity_code_duplicate_for_chatbot(activity_code):
        st.error("⚠️ 이미 사용된 코드입니다. 다른 코드를 입력해주세요.")
        activity_code = ""  # 중복된 경우 초기화
    else:
        st.session_state['activity_code_chatbot'] = activity_code

    # Email 및 Password 입력
    email = st.text_input("📧 Email (선택사항) 학생의 생성결과물을 받아볼 수 있습니다.", value=st.session_state.get('email_chatbot', '')).strip()
    password = st.text_input("🔒 Password (선택사항) 저장한 프롬프트를 조회, 삭제할 수 있습니다.", value=st.session_state.get('password_chatbot', ''), type="password").strip()

    st.markdown("**[https://students.streamlit.app/](https://students.streamlit.app/)** 에서 학생들이 이 활동 코드를 입력하면 해당 프롬프트를 불러올 수 있습니다.")

# 서버 저장 버튼은 항상 표시되며, 입력 검증 후 동작
if st.button("💾 프롬프트를 서버에 저장"):
    if not st.session_state.final_prompt_chatbot.strip():
        st.error("⚠️ 프롬프트가 없습니다. 먼저 프롬프트를 생성하세요.")
    elif not activity_code:
        st.error("⚠️ 활동 코드를 입력하세요.")
    elif password and password.isnumeric():
        st.error("⚠️ 비밀번호는 숫자만 입력할 수 없습니다. 영문 또는 영문+숫자 조합을 사용하세요.")
    else:
        with st.spinner('💾 데이터를 저장하는 중입니다...'):
            student_view = generate_student_view_chatbot(st.session_state.final_prompt_chatbot)
            if save_to_notion_chatbot(activity_code, st.session_state.final_prompt_chatbot, email, password):
                st.success(f"🎉 프롬프트가 성공적으로 저장되었습니다. **저장된 값:**\n\n"
                           f"**활동 코드:** {activity_code}\n"
                           f"**프롬프트:** {st.session_state.final_prompt_chatbot}\n"
                           f"**학생용 안내:** {student_view}\n"
                           f"**이메일:** {email}\n"
                           f"**비밀번호:** {'[입력됨]' if password else '[입력되지 않음]'}")
            else:
                st.error("❌ 프롬프트 저장 중 오류가 발생했습니다.")