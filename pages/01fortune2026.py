import streamlit as st
from kerykeion import AstrologicalSubjectFactory
from openai import OpenAI
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import datetime

# --- [1. 서비스 브랜드 및 페이지 설정] ---
BRAND_KOR = "별들의 언어"
BRAND_ENG = "AstroLogue"

st.set_page_config(
    page_title=f"2026년 총운 - {BRAND_ENG}", 
    page_icon="🪐", 
    layout="centered",
    initial_sidebar_state="collapsed" # 모바일 배려: 처음엔 접어두기
)

# --- [2. 통합 다크 디자인 CSS] ---
st.markdown("""
    <style>
    /* 1. 상단 툴바(깃허브 등) 제거 및 사이드바 버튼 유지 */
    [data-testid="stStatusWidget"] { visibility: hidden !important; display: none !important; }
    header { background-color: rgba(0,0,0,0) !important; }
    footer { visibility: hidden !important; }
    
    /* 2. 전체 배경 및 텍스트 컬러 */
    .stApp { background-color: #0B0E14 !important; }
    h1, h2, h3, p, span, div, label, .stMarkdown { color: #FFFFFF !important; }
    
    /* 3. 입력창 디자인 커스텀 */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #161B22 !important;
        color: #FFFFFF !important;
        border: 1px solid #2C3E50 !important;
        border-radius: 10px !important;
    }
    
    /* 4. 버튼 디자인 (메인과 통일) */
    .stButton>button {
        width: 100% !important;
        background: linear-gradient(145deg, #161B22, #0D1117) !important;
        color: #A0C4FF !important;
        border-radius: 15px !important;
        border: 1px solid #2C3E50 !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        border-color: #A0C4FF !important;
        box-shadow: 0 0 15px rgba(160, 196, 255, 0.2) !important;
    }

    /* 5. 사이드바 디자인 (검정색 복구) */
    [data-testid="stSidebar"] {
        background-color: #0D1117 !important;
        border-right: 1px solid #1F2937 !important;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- [3. 보안 및 헬퍼 함수] ---
MY_OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
geolocator = Nominatim(user_agent="astrologue_global_app")
tf = TimezoneFinder()

def get_global_location(city_name):
    try:
        location = geolocator.geocode(city_name)
        if location:
            lat, lng = location.latitude, location.longitude
            tz_str = tf.timezone_at(lng=lng, lat=lat)
            return lat, lng, tz_str
        return None, None, None
    except: return None, None, None

# --- [4. UI 레이아웃] ---
st.title("🪐 2026년 총운 해독")
st.write("새로운 시대의 시작점에서, 당신의 1년 궤적을 데이터로 예견합니다.")

with st.sidebar:
    st.header("✨ 서문")
    st.markdown("당신이 태어난 순간의 성도와 2026년 현재의 별들이 부딪히며 만들어내는 '시간의 문장'을 읽어냅니다.")

st.subheader("📝 당신의 기록을 남겨주세요")
col1, col2 = st.columns(2)

with col1:
    user_name = st.text_input("성함 (Name)", placeholder="Park")
    birth_date = st.date_input("출생 날짜", min_value=datetime.date(1950, 1, 1), value=datetime.date(1996, 1, 1))
    unknown_time = st.checkbox("시간을 모릅니다")
    if unknown_time:
        birth_hour, birth_min = 12, 0
    else:
        t_col1, t_col2 = st.columns(2)
        with t_col1: birth_hour = st.number_input("시", 0, 23, 22)
        with t_col2: birth_min = st.number_input("분", 0, 59, 0)

with col2:
    city_input = st.text_input("출생 도시 (City)", placeholder="Seoul")
    st.info("정확한 도시명을 영문으로 입력해 주세요. (예: New York, London, Paris)")
    
    if city_input:
        if st.button("📍 위치 확인"):
            lat_check, lng_check, tz_check = get_global_location(city_input)
            if lat_check:
                st.success(f"확인됨: {city_input} (시간대: {tz_check})")
            else:
                st.error("도시를 찾을 수 없습니다. 영문 철자를 확인해 주세요.")

st.divider()

# --- [5. 분석 로직] ---
if st.button("✨ 2026년 대운 해독하기"):
    if not city_input or not user_name:
        st.warning("이름과 도시를 모두 입력해 주세요.")
    else:
        with st.spinner("🔮 2026년의 천체 궤도를 시뮬레이션하고 있습니다..."):
            lat, lng, tz_str = get_global_location(city_input)
            try:
                # 1. 네이탈 차트 생성
                user = AstrologicalSubjectFactory.from_birth_data(
                    user_name, birth_date.year, birth_date.month, birth_date.day,
                    int(birth_hour), int(birth_min), lng=lng, lat=lat, tz_str=tz_str, online=False
                )

                # 2. AI에게 전달할 데이터 정제
                chart_summary = f"""
                [User Profile]
                Name: {user_name}
                Sun Sign: {user.sun.sign} ({user.sun.element} element)
                Moon Sign: {user.moon.sign}
                Ascendant: {user.first_house.sign}
                Planets: Sun in {user.sun.house}th House, Moon in {user.moon.house}th House, 
                Saturn in {user.saturn.sign}, Jupiter in {user.jupiter.sign}
                """
                
                client = OpenAI(api_key=MY_OPENAI_API_KEY)
                
                fortune_prompt = f"""
                아래 사용자의 네이탈 차트 데이터를 기반으로 '2026년 전체 운세'를 정밀하게 분석해줘.
                데이터: {chart_summary}

                너는 데이터 사이언티스트의 냉철함과 고전 점성술사의 통찰력을 동시에 가진 'AstroLogue' 시스템이야.
                모든 답변은 '반말'로, 하지만 아주 격조 있고 신비로운 문체로 작성해.

                반드시 다음 6가지 항목을 포함할 것:

                ### 1. [타고난 기질과 성향 분석]
                - 성격, 대인관계 방식, 의사결정 패턴을 차트 기반으로 설명해.

                ### 2. [2026년 전체 흐름 및 12개월 키워드]
                - 2026년의 에너지 흐름을 요약하고, 1월부터 12월까지의 키워드를 아래 '표(Table)' 포맷으로 작성해.
                | 월 | 핵심 키워드 | 운의 강도(1-5) |
                |---|---|---|

                ### 3. [커리어 이슈 포인트 & 집중 시기]
                - 직업적 성공이나 변곡점이 올 시기를 집어줘.

                ### 4. [연애 흐름과 반복되는 패턴]
                - 2026년의 애정운 흐름과 본인이 주의해야 할 심리적 패턴을 분석해.

                ### 5. [금전 관리 및 투자 타이밍]
                - 재물운이 상승하는 시기와 수성 역행 등을 고려해 주의해야 할 시기를 구분해.

                ### 6. [2026년 나를 위한 별들의 조언]
                - 마지막으로 사용자가 2026년을 관통하며 가슴에 새겨야 할 '단 한 문장'의 문장을 제시하며 마쳐.
                """

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "너는 운명을 구조적으로 해독하는 AstroLogue 알고리즘이야."},
                        {"role": "user", "content": fortune_prompt}
                    ],
                    temperature=0.75,
                    max_tokens=3000
                )

                st.success("✅ 2026년의 문장이 완성되었습니다.")
                st.markdown("---")
                st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"해독 중 오류 발생: {e}. 입력하신 출생 정보를 다시 확인해 주세요.")