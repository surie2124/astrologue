import streamlit as st
from kerykeion import AstrologicalSubjectFactory
from openai import OpenAI
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import datetime
import pandas as pd

# --- [1. 서비스 브랜드 및 페이지 설정] ---
BRAND_KOR = "별들의 언어"
BRAND_ENG = "AstroLogue"

st.set_page_config(
    page_title=f"2026년 총운 - {BRAND_ENG}", 
    page_icon="🪐", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- [2. 통합 다크 디자인 & 테이블 CSS] ---
st.markdown("""
    <style>
    [data-testid="stStatusWidget"], .stDeployButton, [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
    header { background-color: rgba(0,0,0,0) !important; }
    footer { visibility: hidden !important; }
    .stApp { background-color: #0B0E14 !important; }
    h1, h2, h3, p, span, div, label, .stMarkdown { color: #FFFFFF !important; }
    
    .stTable {
        background-color: #161B22 !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid #2C3E50 !important;
    }
    thead tr th { background-color: #1F2937 !important; color: #A0C4FF !important; text-align: center !important; }
    tbody tr td { color: #E0E0E0 !important; border-bottom: 1px solid #2C3E50 !important; text-align: center !important; }

    button[data-testid="stSidebarCollapsedControl"] {
        visibility: visible !important;
        color: white !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [3. 데이터 매핑 설정 (약어 대응 추가)] ---
MY_OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
geolocator = Nominatim(user_agent="astrologue_global_app")
tf = TimezoneFinder()

# 약어와 풀네임을 모두 지원하도록 보강
SIGN_MAP = {
    "Aries": "양자리", "Ari": "양자리", "Taurus": "황소자리", "Tau": "황소자리",
    "Gemini": "쌍둥이자리", "Gem": "쌍둥이자리", "Cancer": "게자리", "Can": "게자리",
    "Leo": "사자자리", "Virgo": "처녀자리", "Vir": "처녀자리", "Libra": "천칭자리", "Lib": "천칭자리",
    "Scorpio": "전갈자리", "Sco": "전갈자리", "Sagittarius": "사수자리", "Sag": "사수자리",
    "Capricorn": "염소자리", "Cap": "염소자리", "Aquarius": "물병자리", "Aqu": "물병자리", "Pisces": "물고기자리", "Pis": "물고기자리"
}
PLANET_MAP = {
    "Sun": "태양", "Moon": "달", "Mercury": "수성", "Venus": "금성", "Mars": "화성",
    "Jupiter": "목성", "Saturn": "토성", "Uranus": "천왕성", "Neptune": "해왕성", "Pluto": "명왕성"
}
HOUSE_ATTRS = ["first_house", "second_house", "third_house", "fourth_house", "fifth_house", "sixth_house", 
               "seventh_house", "eighth_house", "ninth_house", "tenth_house", "eleventh_house", "twelfth_house"]

def get_global_location(city_name):
    try:
        location = geolocator.geocode(city_name)
        if location: return location.latitude, location.longitude, tf.timezone_at(lng=location.longitude, lat=location.latitude)
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
    st.info("한글 또는 영문으로 입력하세요.")

st.divider()

# --- [5. 메인 분석 로직 (오류 유발 요소 제거)] ---
if st.button("✨ 2026년 대운 해독하기"):
    if not city_input or not user_name:
        st.warning("정보를 모두 입력해 주세요.")
    else:
        with st.spinner("🔮 우주의 데이터를 시뮬레이션하고 있습니다..."):
            lat, lng, tz_str = get_global_location(city_input)
            try:
                user = AstrologicalSubjectFactory.from_birth_data(
                    user_name, birth_date.year, birth_date.month, birth_date.day,
                    int(birth_hour), int(birth_min), lng=lng, lat=lat, tz_str=tz_str, online=False
                )

                # 1. 시각화: 행성 데이터 (깔끔한 한글 변환)
                st.markdown("### ⭐ 나의 출생 차트 데이터")
                p_list = []
                for p in [user.sun, user.moon, user.mercury, user.venus, user.mars, user.jupiter, user.saturn, user.uranus, user.neptune, user.pluto]:
                    p_list.append({
                        "행성": PLANET_MAP.get(p.name, p.name),
                        "별자리": SIGN_MAP.get(p.sign, p.sign) + (" (역행)" if p.retrograde else ""),
                        "도수": f"{p.position:.1f}°",
                        "하우스": f"{p.house}H" # house_name 대신 숫자로 표시
                    })
                p_list.append({"행성": "상승궁(ASC)", "별자리": SIGN_MAP.get(user.first_house.sign, user.first_house.sign), "도수": f"{user.first_house.position:.1f}°", "하우스": "1H"})
                st.table(pd.DataFrame(p_list))

                # 2. 하우스 정보 (아스펙트 제거하여 안전성 확보)
                with st.expander("🏠 12 하우스 상세 정보"):
                    h_list = []
                    for i, attr in enumerate(HOUSE_ATTRS, 1):
                        house_obj = getattr(user, attr)
                        h_list.append({"하우스": f"{i}H", "영역": f"{i}번 방", "별자리": SIGN_MAP.get(house_obj.sign, house_obj.sign)})
                    st.table(pd.DataFrame(h_list))

                st.divider()

                # 3. AI 분석 실행 (요청하신 6가지 항목)
                chart_summary = f"Sun:{user.sun.sign}, Moon:{user.moon.sign}, Asc:{user.first_house.sign}, Saturn:{user.saturn.sign}"
                client = OpenAI(api_key=MY_OPENAI_API_KEY)
                
                fortune_prompt = f"""
                아래 사용자의 네이탈 데이터 {chart_summary}를 기반으로 2026년 운세를 분석해.
                1.기질분석 2.12개월 키워드표 3.커리어 4.연애 5.금전 6.조언 순서로 반말로 격조있게 써줘.
                """

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "너는 AstroLogue 점성술 알고리즘이야."}, {"role": "user", "content": fortune_prompt}],
                    temperature=0.7, max_tokens=3500
                )

                st.success(f"✅ {user_name}님의 운명이 해독되었습니다.")
                st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"해독 중 오류 발생: {e}. 라이브러리 호환성 문제입니다.")