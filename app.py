import streamlit as st

# --- [1. 서비스 브랜드 및 페이지 설정] ---
BRAND_KOR = "별들의 언어"
BRAND_ENG = "AstroLogue"

st.set_page_config(
    page_title=f"{BRAND_KOR} ({BRAND_ENG})", 
    page_icon="🪐", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- [2. UI 정밀 타격 및 다크 디자인 CSS] ---
st.markdown("""
    <style>
    /* 1. 우측 상단의 요란한 요소들(깃허브, 배포 버튼, 상태 표시)만 숨김 */
    [data-testid="stStatusWidget"], .stDeployButton, [data-testid="stToolbar"] {
        visibility: hidden !important;
        display: none !important;
    }

    /* 2. 왼쪽 상단 사이드바 화살표(손잡이)는 강제로 '보이게' 설정 */
    header {
        background-color: rgba(0,0,0,0) !important; /* 헤더 배경은 투명하게 */
    }
    
    button[data-testid="stSidebarCollapsedControl"] {
        visibility: visible !important;
        color: #FFFFFF !important;
        background-color: rgba(255, 255, 255, 0.15) !important; /* 버튼이 잘 보이도록 살짝 강조 */
        border-radius: 8px !important;
        left: 10px !important;
    }

    /* 3. 전체 앱 배경 및 텍스트 기본 설정 */
    .stApp {
        background-color: #0B0E14 !important;
    }
    
    /* 4. [중요] 카테고리 안내 문구 및 일반 텍스트 흰색 */
    h3, p, span, div, .footer-text {
        color: #FFFFFF !important;
    }

    /* 5. 버튼 디자인: 좌우로 길고 묵직한 스타일 유지 */
    .stButton {
        width: 100%;
    }
    
    .stButton>button {
        width: 100% !important;
        min-height: 120px !important; 
        background: linear-gradient(145deg, #161B22, #0D1117) !important;
        color: #FFFFFF !important; /* 텍스트 흰색 */
        border-radius: 20px !important;
        border: 1px solid #2C3E50 !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        white-space: pre-line !important;
        margin-top: 15px !important;
        transition: all 0.4s ease !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5) !important;
    }

    /* 버튼 호버 시 화이트-블루 광채 효과 */
    .stButton>button:hover {
        border-color: #A0C4FF !important;
        color: #FFFFFF !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 30px rgba(160, 196, 255, 0.2) !important;
        background: #1C2230 !important;
    }

    /* 6. 사이드바 내부 디자인 (남색 배경 + 흰색 글씨) */
    [data-testid="stSidebar"] {
        background-color: #0D1117 !important;
        border-right: 1px solid #1F2937 !important;
    }
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] h2 {
        color: #FFFFFF !important;
    }

    /* 푸터 및 메뉴 숨김 */
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    </style>
    """, unsafe_allow_html=True)

# --- [3. 메인 화면 구성] ---
st.image("assets/main_hero&text.png", use_container_width=True)
st.subheader("🌙 해독할 운명의 카테고리를 선택하세요")

if st.button("🪐 2026년 총운\n새로운 시대의 시작, 당신의 1년 해독"):
    st.switch_page("pages/01fortune2026.py")
    
if st.button("💼 **직업·재물운**\n나의 성공 궤적과 부의 그릇 분석"):
    st.switch_page("pages/02career.py")

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