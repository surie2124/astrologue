import streamlit as st

# --- [1. 서비스 브랜드 및 페이지 설정] ---
BRAND_KOR = "별들의 언어"
BRAND_ENG = "AstroLogue"

st.set_page_config(
    page_title=f"{BRAND_KOR} ({BRAND_ENG})", 
    page_icon="🪐", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- [2. 모든 내비게이션 요소를 다 잡는 핵폭탄 CSS] ---
st.markdown("""
    <style>
    /* 상단/하단 기본 요소 제거 */
    header, footer, #MainMenu {visibility: hidden !important;}
    
    /* 1. 전체 배경 */
    .stApp {
        background-color: #0B0E14 !important;
    }
    
    /* 2. 사이드바 본체 배경 */
    section[data-testid="stSidebar"] {
        background-color: #0D1117 !important;
        border-right: 1px solid #1F2937 !important;
    }

    /* 3. [문제의 탭 부분] 모든 내비게이션 관련 배경을 투명/남색으로 강제 */
    div[data-testid="stSidebarNav"], 
    div[data-testid="stSidebarNav"] ul,
    div[data-testid="stSidebarNav"] li,
    div[data-testid="stSidebarNavItems"] {
        background-color: transparent !important;
    }

    /* 4. [글자색 강제] app, career 텍스트를 무조건 흰색으로 */
    div[data-testid="stSidebarNav"] span,
    div[data-testid="stSidebarNav"] a,
    .st-emotion-cache-17l3639, /* 버전별로 다를 수 있는 클래스명 대비 */
    .st-emotion-cache-6q9sum { 
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }

    /* 5. [호버/선택 효과] 마우스 올리거나 선택했을 때 */
    div[data-testid="stSidebarNav"] a:hover {
        background-color: rgba(160, 196, 255, 0.1) !important;
    }
    
    div[data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: rgba(160, 196, 255, 0.2) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stSidebarNav"] a[aria-current="page"] span {
        color: #A0C4FF !important; /* 선택된 탭은 하늘색 포인트 */
    }

    /* 6. 사이드바 일반 텍스트 (서사 부분) */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2 {
        color: #FFFFFF !important;
    }

    /* 7. 메인 화면 버튼 및 디자인 (기존 유지) */
    h3 {
        color: #A0C4FF !important;
        text-align: center;
        text-shadow: 0 0 10px rgba(160, 196, 255, 0.3);
    }

    .stButton>button {
        width: 100% !important;
        min-height: 140px !important; 
        background: linear-gradient(145deg, #161B22, #0D1117) !important;
        color: #FFFFFF !important;
        border-radius: 20px !important;
        border: 1px solid #2C3E50 !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        white-space: pre-line !important;
        transition: all 0.4s ease !important;
    }

    .stButton>button:hover {
        border-color: #A0C4FF !important;
        transform: translateY(-5px) !important;
        box-shadow: 0 10px 30px rgba(160, 196, 255, 0.25) !important;
    }

    .footer-text {
        color: #FFFFFF !important;
        font-size: 0.9em;
        opacity: 0.7;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [3. 메인 화면 구성] ---
st.image("assets/main_hero&text.png", use_container_width=True)
st.subheader("🌙 해독할 운명의 카테고리를 선택하세요")

if st.button("🪐 2026년 총운\n새로운 시대의 시작, 당신의 1년 해독"):
    st.switch_page("pages/01.fortune2026.py")
    
if st.button("💼 **직업·재물운**\n나의 성공 궤적과 부의 그릇 분석"):
    st.switch_page("pages/02.career.py")

if st.button("💖 **연애·재회운**\n숨겨진 인연과 사랑의 타이밍"):
    st.toast("현재 우주의 신호를 수신 중입니다.")

st.markdown("<br><br><center><p class='footer-text'>별들이 당신에게 전하는 문장은 여전히 쓰여지고 있습니다.</p></center>", unsafe_allow_html=True)

# --- [4. 사이드바 구성] ---
with st.sidebar:
    st.header("✨ 우주에 새겨진 당신의 서사")
    st.markdown(f"""
    당신이 태어난 순간, 우주는 하나의 문장을 완성했다. 
    **{BRAND_KOR}**({BRAND_ENG})는 그 문장을 해독해 당신의 삶에 흐르는 패턴을 구조적으로 해석한다. 
    
    단순한 운세가 아닌, 그 패턴을 기반으로 당신의 선택과 방향을 설계하는 가장 **정밀한 알고리즘**을 제안한다.
    """)
    st.divider()
    st.caption(f"© 2026 {BRAND_ENG} Project. All rights reserved.")