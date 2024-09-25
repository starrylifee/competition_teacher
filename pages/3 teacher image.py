import streamlit as st
from utils import set_page_config, load_secrets, is_activity_code_duplicate, save_to_notion, initialize_openai_client
import requests
import json
from datetime import datetime

# 페이지 설정
set_page_config("교사용 교육 도구 이미지", "🧑‍🏫", "#FFEBEE")

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
NOTION_DATABASE_ID = secrets["notion"]["database_id_image"]

# 중복 확인 함수 정의
def is_activity_code_duplicate_for_image(activity_code):
    return is_activity_code_duplicate(NOTION_API_KEY, NOTION_DATABASE_ID, "image", activity_code)

# Notion에 데이터 저장 함수 정의
def save_to_notion_data(activity_code, input_topic, email, password, adjectives_json):
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "activity_code": {
                "rich_text": [{"text": {"content": activity_code}}]
            },
            "prompt": {
                "rich_text": [{"text": {"content": input_topic}}]
            },
            "email": {
                "rich_text": [{"text": {"content": email}}]
            },
            "password": {
                "rich_text": [{"text": {"content": password}}]
            },
            "adjectives": {
                "rich_text": [{"text": {"content": adjectives_json}}]
            },
            "date": {
                "rich_text": [{"text": {"content": datetime.now().isoformat()}}]
            },
            "page": {
                "rich_text": [{"text": {"content": "image"}}]
            }
        }
    }
    return save_to_notion(NOTION_API_KEY, NOTION_DATABASE_ID, "image", data)

# 교사용 인터페이스
st.title("🎨 교사용 이미지 생성 프롬프트 도구")

st.markdown("""
**안내:** 이 도구를 사용하여 교육 활동에 필요한 이미지 생성 프롬프트를 입력하고 저장할 수 있습니다. 아래의 단계를 따라 입력해 주세요.
1. **활동 코드**: 학생들이 입력할 고유 코드를 설정합니다.
2. **이미지 대상**: 생성하고자 하는 이미지의 대상을 간단하게 입력합니다.
3. **형용사 모드 선택**: 기본 형용사 또는 커스텀 꾸미는 말을 입력하세요.
4. **프롬프트 저장**: 입력한 프롬프트를 저장하여 서버에 추가합니다.
5. **학생용 앱과 연동**: 이곳에서 저장한 프롬프트는 [학생용 앱](https://students.streamlit.app/)에서 불러와 안전하게 AI를 사용할 수 있습니다.
""")

# 교사가 주제를 선택하거나 직접 입력
sample_topics_with_intentions = {
    "2학년 과학시간 - 숲 속의 동물": "숲 속에 사는 다양한 동물들의 모습을 설명하는 이미지를 생성하고자 하는 의도.",
    "2학년 체육시간 - 공원에서의 놀이": "공원에서 다양한 놀이 활동을 하는 모습을 생성하여, 학생들이 체육 활동의 재미를 느낄 수 있게 하고자 하는 의도.",
    "3학년 미술시간 - 문화 축제 장면": "문화 축제의 장면을 통해 학생들이 다양한 문화를 이해하도록 돕고자 하는 의도.",
    "3학년 사회시간 - 바닷가 풍경": "바닷가의 모습을 설명하고, 지리적 특성을 학생들에게 알려주는 이미지를 생성하고자 하는 의도.",
    "4학년 사회시간 - 자연재해 현장": "자연재해가 발생한 현장을 설명하는 이미지를 통해, 그 영향과 대비 방법을 설명하고자 하는 의도.",
    "4학년 역사시간 - 역사적인 건축물": "역사적인 건축물의 사진을 생성하여, 그 건축물의 의미와 건축 양식을 설명하고자 하는 의도.",
    "5학년 과학시간 - 과학 실험 장면": "과학 실험을 하는 장면을 시각화하여, 실험의 과정을 설명하고자 하는 의도.",
    "5학년 도덕시간 - 우리 주변에서 공중도덕을 어기는 모습": "공중도덕을 어기는 다양한 사례를 통해, 학생들에게 공중도덕의 중요성을 인식시키고자 하는 의도.",
    "5학년 사회시간 - 다양한 직업 사람들": "다양한 직업을 가진 사람들의 모습을 설명하는 이미지를 생성하고자 하는 의도.",
    "6학년 과학시간 - 우주 탐험": "우주 탐험을 설명하는 이미지를 생성하고, 우주에 대한 지식을 쉽게 설명하고자 하는 의도.",
    "6학년 역사시간 - 고대 유적지": "고대 유적지를 설명하는 이미지를 생성하고자 하는 의도."
}

# 주제 선택 방식 선택
input_method = st.radio("🖼️ 이미지 대상을 선택하거나 직접 입력하세요:", ["샘플 주제 선택", "직접 입력"], key="input_method")

if input_method == "샘플 주제 선택":
    input_topic = st.selectbox("🖼️ 이미지 주제를 선택하세요:", list(sample_topics_with_intentions.keys()))
    input_topic_cleaned = input_topic.split(" - ")[1]  # 선택한 주제에서 과목 부분 제외하고 주제만 저장

    # 선택한 주제에 대한 설명을 st.info로 표시
    st.info(sample_topics_with_intentions[input_topic])
else:
    input_topic_cleaned = st.text_input("🖼️ 생성하고자 하는 이미지의 대상을 간단하게 입력하세요 (예: '곰', '나무', '산'): ", "").strip()


# 형용사 입력 방식 선택
mode = st.radio(
    "📝 형용사 입력 방식 선택",
    ("기본 형용사 사용", "커스텀 꾸미는 말 입력"),
    key="adjective_mode"  # 고유한 key 추가
)

if mode == "기본 형용사 사용":
    st.markdown("**기본 형용사 목록:**")
    # 기본 형용사 리스트
    default_adjectives = [
        "몽환적인", "현실적인", "우아한", "고요한", "활기찬", 
        "긴장감 있는", "로맨틱한", "공포스러운", "신비로운", "평화로운",
        "미니멀한", "복잡한", "빈티지한", "모던한", "고전적인", 
        "미래적인", "자연주의적인", "기하학적인", "추상적인", "대담한",
        "매끄러운", "거친", "부드러운", "뾰족한", "질감이 느껴지는", 
        "광택 있는", "매트한", "무광의",
        "즐거운", "슬픈", "분노한", "평온한", "감동적인", 
        "따뜻한", "외로운", "흥미로운", "짜릿한", "사려 깊은"
    ]
    adjectives_json = json.dumps(default_adjectives, ensure_ascii=False)  # 기본 형용사를 JSON으로 변환
    st.write(", ".join(default_adjectives))
else:
    # 커스텀 형용사 입력
    custom_adjectives = st.text_input("✏️ 사용하고자 하는 형용사를 쉼표(,)로 구분하여 입력하세요:", "").strip()
    if custom_adjectives:
        adjectives_json = json.dumps([adj.strip() for adj in custom_adjectives.split(',')], ensure_ascii=False)  # 쉼표로 나눈 형용사를 JSON으로 변환
    else:
        adjectives_json = "[]"

# 활동 코드 입력 (형용사 선택 후에 위치)
activity_code = st.text_input("🔑 활동 코드 입력", value=st.session_state.get('activity_code', '')).strip()

if is_activity_code_duplicate_for_image(activity_code):
    st.error("⚠️ 이미 사용된 코드입니다. 다른 코드를 입력해주세요.")
    activity_code = ""  # 중복된 경우 초기화
else:
    st.session_state['activity_code'] = activity_code

# Email 및 Password 입력 (활동 코드가 이메일 위로 이동됨)
email = st.text_input("📧 Email (선택사항)", value=st.session_state.get('email', '')).strip()
password = st.text_input("🔒 Password (선택사항)", value=st.session_state.get('password', ''), type="password").strip()

# 프롬프트 저장
if st.button("💾 프롬프트 저장") and activity_code:
    if input_topic_cleaned:
        if password and password.isnumeric():
            st.error("⚠️ 비밀번호는 숫자만 입력할 수 없습니다.")
        else:
            with st.spinner('💾 데이터를 저장하는 중입니다...'):
                if save_to_notion_data(activity_code, input_topic_cleaned, email, password, adjectives_json):
                    st.success(f"🎉 프롬프트가 성공적으로 저장되었습니다.\n\n"
                               f"**활동 코드:** {activity_code}\n"
                               f"**이미지 대상:** {input_topic_cleaned}\n"
                               f"**형용사:** {adjectives_json}\n"
                               f"**이메일:** {email}\n"
                               f"**비밀번호:** {'[입력됨]' if password else '[입력되지 않음]'}")
                else:
                    st.error("❌ 프롬프트 저장 중 오류가 발생했습니다.")
    else:
        st.error("⚠️ 이미지 대상을 입력하세요.")
