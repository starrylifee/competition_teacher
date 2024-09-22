import streamlit as st

# 페이지 설정 - 아이콘과 제목 설정
st.set_page_config(
    page_title="교사용 교육 도구 홈",  # 브라우저 탭에 표시될 제목
    page_icon="🧑‍🏫",  # 브라우저 탭에 표시될 아이콘 (이모지 또는 이미지 파일 경로)
)

# Streamlit의 기본 메뉴와 푸터 숨기기
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden; }
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# 홈 화면 제목
st.title("안전하게 경험하는 인공지능 첫걸음")
st.info("대상학년: 초등학교 1~6학년")

# 소개 문구
st.markdown("""
## 🛠️ 교사용 교육 도구 모음
이 페이지에서는 교육 활동을 지원하는 다양한 AI 및 이미지 기반 도구를 사용할 수 있습니다. 각 도구는 교사들이 쉽게 교육용 프롬프트를 생성하고 학생들에게 안전하게 적용할 수 있도록 설계되었습니다.
""")

# 강조 문구
st.markdown("""
**이곳에서 저장한 프롬프트는 [학생용 앱](https://students.streamlit.app/)에서 불러와 안전하게 AI를 사용할 수 있습니다.**
""")

# 도구 링크 및 설명
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <h4>1. 교사용 이미지분석 프롬프트 생성 도구</h4>
        <a href="https://prompt-input.streamlit.app/teacher_vision" target="_blank" style="text-decoration: none;">
            <span style="font-size: 100px;">🖼️</span>
            <div style="text-align: center; font-size: 20px;">클릭하세요</div>
        </a>
        <p>이 도구를 사용하여 이미지분석 API를 활용한 교육용 프롬프트를 쉽게 생성할 수 있습니다. Vision API를 활용해 프롬프트를 생성하고 저장하세요.</p>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <h4>2. 교사용 텍스트 프롬프트 생성 도구</h4>
        <a href="https://prompt-input.streamlit.app/teacher_text" target="_blank" style="text-decoration: none;">
            <span style="font-size: 100px;">📝</span>
            <div style="text-align: center; font-size: 20px;">클릭하세요</div>
        </a>
        <p>이 도구를 사용하여 교육 활동에 필요한 텍스트 프롬프트를 쉽게 생성할 수 있습니다. AI가 텍스트 프롬프트를 생성하고, 이를 수정하여 저장하세요.</p>
        """,
        unsafe_allow_html=True
    )

with col1:
    st.markdown(
        """
        <h4>3. 교사용 이미지 생성 프롬프트 도구</h4>
        <a href="https://prompt-input.streamlit.app/teacher_image" target="_blank" style="text-decoration: none;">
            <span style="font-size: 100px;">🖌️</span>
            <div style="text-align: center; font-size: 20px;">클릭하세요</div>
        </a>
        <p>이 도구를 사용하여 교육 활동에 필요한 이미지 생성 프롬프트를 직접 입력하고 저장할 수 있습니다. 학생들이 사용할 이미지를 손쉽게 생성하세요.</p>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <h4>4. 교사용 챗봇 프롬프트 생성 도구</h4>
        <a href="https://prompt-input.streamlit.app/teacher_chatbot" target="_blank" style="text-decoration: none;">
            <span style="font-size: 100px;">🤖</span>
            <div style="text-align: center; font-size: 20px;">클릭하세요</div>
        </a>
        <p>이 도구를 사용하여 교육 활동에 필요한 맞춤형 챗봇을 만들 수 있습니다. 학생들이 사용할 챗봇을 손쉽게 생성하세요.</p>
        """,
        unsafe_allow_html=True
    )

with col1:
    st.markdown(
        """
        <h4>5. 교사용 프롬프트 관리 도구</h4>
        <a href="https://prompt-input.streamlit.app/search_delete" target="_blank" style="text-decoration: none;">
            <span style="font-size: 100px;">🛠️</span>
            <div style="text-align: center; font-size: 20px;">클릭하세요</div>
        </a>
        <p>이 도구를 사용하여 저장된 프롬프트를 검색하고 삭제할 수 있습니다. 비밀번호나 활동 코드를 사용하여 프롬프트를 관리하세요.</p>
        """,
        unsafe_allow_html=True
    )
