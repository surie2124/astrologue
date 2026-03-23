import streamlit as st
from kerykeion import AstrologicalSubjectFactory
from openai import OpenAI
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import datetime
import pandas as pd

# --- [1. 설정 및 브랜드] ---
BRAND_KOR = "별들의 언어"
BRAND_ENG = "AstroLogue"

st.set_page_config(page_title=f"{BRAND_KOR}", page_icon="🪐", layout="centered", initial_sidebar_state="collapsed")

# --- [2. 화이트 테마 및 버튼 커스텀 CSS] ---
st.markdown("""
    <style>
    /* 상단 및 불필요 요소 제거 */
    [data-testid="stStatusWidget"], .stDeployButton, [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
    header { background-color: rgba(0,0,0,0) !important; }
    footer { visibility: hidden !important; }

    /* 배경 및 기본 텍스트 */
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, div, label, .stMarkdown { color: #1A1A1A !important; }

    /* -------------------------------------------
       [버튼 디자인 커스텀]
    ------------------------------------------- */
    .stButton>button {
        width: 100% !important;
        /* 기본 상태: 회색 계열 */
        background-color: #F3F4F6 !important; 
        /* 텍스트: 검정 */
        color: #1A1A1A !important; 
        /* 라운드 테두리 */
        border-radius: 12px !important; 
        border: 1px solid #D1D5DB !important;
        padding: 10px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }

    /* 호버 상태: 푸른 계열 + 검정 텍스트 유지 */
    .stButton>button:hover {
        background-color: #BFDBFE !important; /* 연한 블루 (검정 글씨 가독성 확보) */
        color: #000000 !important; 
        border-color: #3B82F6 !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2) !important;
        transform: translateY(-1px) !important;
    }

    /* 대시보드 메트릭 */
    [data-testid="stMetricValue"] { color: #1E3A8A !important; font-weight: 800 !important; }
    [data-testid="stMetricLabel"] { color: #4B5563 !important; }

    /* 사이드바 */
    [data-testid="stSidebar"] { background-color: #F9FAFB !important; }
    </style>
    """, unsafe_allow_html=True)

# --- [3. 헬퍼 로직] ---
MY_OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
geolocator = Nominatim(user_agent="astrologue_global_app")
tf = TimezoneFinder()

SIGN_MAP = {
    "Aries": "양자리", "Ari": "양자리", "Taurus": "황소자리", "Tau": "황소자리", "Gemini": "쌍둥이자리", "Gem": "쌍둥이자리",
    "Cancer": "게자리", "Can": "게자리", "Leo": "사자자리", "Virgo": "처녀자리", "Vir": "처녀자리", "Libra": "천칭자리", "Lib": "천칭자리",
    "Scorpio": "전갈자리", "Sco": "전갈자리", "Sagittarius": "사수자리", "Sag": "사수자리", "Capricorn": "염소자리", "Cap": "염소자리",
    "Aquarius": "물병자리", "Aqu": "물병자리", "Pisces": "물고기자리", "Pis": "물고기자리"
}
PLANET_MAP = { "Sun": "태양", "Moon": "달", "Mercury": "수성", "Venus": "금성", "Mars": "화성", "Jupiter": "목성", "Saturn": "토성", "Uranus": "천왕성", "Neptune": "해왕성", "Pluto": "명왕성" }

def clean_house(house_str):
    """'Fifth_House' 등을 '5'로 변환"""
    import re
    nums = {"First": "1", "Second": "2", "Third": "3", "Fourth": "4", "Fifth": "5", "Sixth": "6", 
            "Seventh": "7", "Eighth": "8", "Ninth": "9", "Tenth": "10", "Eleventh": "11", "Twelfth": "12"}
    for k, v in nums.items():
        if k in str(house_str): return v
    return str(house_str)

def get_location(city):
    try:
        loc = geolocator.geocode(city)
        if loc: return loc.latitude, loc.longitude, tf.timezone_at(lng=loc.longitude, lat=loc.latitude)
        return None, None, None
    except: return None, None, None


# --- [4. UI 레이아웃] ---
st.title("🪐 2026년 총운 해독")
st.write("당신의 출생 정보를 바탕으로 2026년의 천체 궤도를 시뮬레이션합니다.")

col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input("성함 (Name)", placeholder="Park")
    birth_date = st.date_input("출생 날짜", value=datetime.date(1996, 1, 1))
    unknown_time = st.checkbox("시간을 모릅니다")
    t_col1, t_col2 = st.columns(2)
    with t_col1: birth_hour = st.number_input("시", 0, 23, 22)
    with t_col2: birth_min = st.number_input("분", 0, 59, 0)
with col2:
    city_input = st.text_input("출생 도시 (City)", placeholder="Seoul")
    st.info("한글 또는 영문으로 입력해 주세요. (예: 서울, Seoul, New York)")

if city_input:
        if st.button("📍 위치 확인"):
            lat_c, lng_c, tz_c = get_global_location(city_input)
            if lat_c:
                st.success(f"확인됨: {city_input} (위도: {lat_c:.2f}, 경도: {lng_c:.2f})")
            else:
                st.error("도시를 찾을 수 없습니다. 정확한 지명인지 확인해 주세요.")

st.divider()

# --- [5. 실행 로직] ---
if st.button("✨ 2026년 대운 해독하기"):
    if not city_input or not user_name:
        st.warning("정보를 입력해 주세요.")
    else:
        with st.spinner("🔮 우주의 데이터를 수집하여 차트를 해독하고 있습니다..."):
            lat, lng, tz = get_location(city_input)
            try:
                user = AstrologicalSubjectFactory.from_birth_data(
                    user_name, birth_date.year, birth_date.month, birth_date.day,
                    int(birth_hour), int(birth_min), lng=lng, lat=lat, tz_str=tz, online=False
                )

                # [A. 대시보드형 데이터 요약]
                st.markdown("### 🧬 핵심 정체성 데이터")
                m1, m2, m3 = st.columns(3)
                m1.metric("태양 (의지)", SIGN_MAP.get(user.sun.sign, user.sun.sign))
                m2.metric("달 (정서)", SIGN_MAP.get(user.moon.sign, user.moon.sign))
                m3.metric("상승궁 (사회적 자아)", SIGN_MAP.get(user.first_house.sign, user.first_house.sign))

                with st.expander("📝 전체 천체 배치 상세 표 확인"):
                    p_list = []
                    for p in [user.sun, user.moon, user.mercury, user.venus, user.mars, user.jupiter, user.saturn]:
                        p_list.append({
                            "천체": PLANET_MAP.get(p.name, p.name),
                            "별자리": SIGN_MAP.get(p.sign, p.sign) + (" (역행)" if p.retrograde else ""),
                            "하우스": clean_house(p.house) + "H"
                        })
                    st.table(pd.DataFrame(p_list))

                st.divider()

                # [B. 전략적 AI 분석]
                chart_info = f"Sun:{user.sun.sign} in {user.sun.house}, Moon:{user.moon.sign} in {user.moon.house}, Asc:{user.first_house.sign}"
                
                client = OpenAI(api_key=MY_OPENAI_API_KEY)
                
                # 분석 톤을 정수님의 배경(OM/전략/데이터)에 맞게 튜닝
                prompt = f"""
                당신은 점성술 데이터를 기반으로 개인의 연간 비즈니스/라이프 전략을 수립하는 'Strategic Astrologer'야. 
                사용자({user_name})의 차트({chart_info})를 분석하여 2026년 전략 리포트를 작성해.

                분석 가이드라인:
                    1. 절대 "네이탈 차트 언급"이나 "가이드" 같은 내 지시어를 제목이나 텍스트로 쓰지 마. 
                    2. 모든 항목은 고객이 바로 읽는 '최종 리포트' 형태여야 함.
                    3. 점성술 용어는 오직 지정된 항목에서만 아주 짧게 언급하고, 나머지는 고객이 이해하기 쉬운 언어로 풀이할 것.
                    4. 말투는 예리하고 자신감 넘치는 '반말'을 유지하되, 품격 있는 문장을 사용할 것.
                    5. 전체 분량은 최소 2,500자 이상으로 아주 길고 심도 있게 작성할 것.
                    6. '2. 12개월 궤적' 섹션은 반드시 아래 Markdown Table 포맷을 정확히 지켜서 작성해.
                   | 월 | 총운 | 재물 | 연애 | 건강 |
                   |---|---|---|---|---|

                포함 항목:
                ### 1. [핵심 기질 및 성향] : 성격, 대인관계 방식, 의사결정 패턴을 차트 기반으로 설명해. 현 리포트에서 가장 중요하므로, 전체 분량의 30-40% 차지할 것.
                ### 2. [2026년 12개월 궤적] : 연간 흐름을 데이터 테이블로 정리. 현 리포트에서 가장 중요하므로, 전체 분량의 30-40% 차지할 것.
                ### 3. [커리어 변곡점] 직업적 성공이나 변곡점이 올 시기를 집어줘
                ### 4. [관계의 역학] : 대인관계에서의 리스크 관리와 협력 패턴.
                ### 5. [올해의 연애 흐름] : 2026년의 애정운 흐름과 본인이 주의해야 할 심리적 패턴을 분석해. 2번 항목과 결과값 톤앤매너가 일치해야 한다.
                ### 6. [2026년 나를 위한 별들의 조언] : 마지막으로 사용자가 2026년을 관통하며 가슴에 새겨야 할 '단 한 문장'의 문장을 제시하며 마쳐.
                """

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "너는 구조적 데이터 분석과 점성술을 구조적으로 해독하는 전문 알고리즘이야."},
                              {"role": "user", "content": prompt}],
                    temperature=0.8
                )
                
                st.success(f"✅ {user_name}님의 2026년 운명이 해독되었습니다.")
                st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"해독 중 오류 발생: {e}. 데이터 구조를 확인 중입니다.")