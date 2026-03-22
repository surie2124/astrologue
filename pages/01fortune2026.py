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
    
    /* 테이블 디자인 고도화 */
    .stTable {
        background-color: #161B22 !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid #2C3E50 !important;
    }
    thead tr th {
        background-color: #1F2937 !important;
        color: #A0C4FF !important;
        font-weight: 700 !important;
        text-align: center !important;
    }
    tbody tr td {
        color: #E0E0E0 !important;
        border-bottom: 1px solid #2C3E50 !important;
        text-align: center !important;
    }

    /* 사이드바 화살표(손잡이) 살리기 */
    button[data-testid="stSidebarCollapsedControl"] {
        visibility: visible !important;
        color: white !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [3. 보안 및 데이터 매핑] ---
MY_OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
geolocator = Nominatim(user_agent="astrologue_global_app")
tf = TimezoneFinder()

SIGN_MAP = {
    "Aries": "양자리", "Taurus": "황소자리", "Gemini": "쌍둥이자리", "Cancer": "게자리",
    "Leo": "사자자리", "Virgo": "처녀자리", "Libra": "천칭자리", "Scorpio": "전갈자리",
    "Sagittarius": "사수자리", "Capricorn": "염소자리", "Aquarius": "물병자리", "Pisces": "물고기자리"
}
PLANET_MAP = {
    "Sun": "태양", "Moon": "달", "Mercury": "수성", "Venus": "금성", "Mars": "화성",
    "Jupiter": "목성", "Saturn": "토성", "Uranus": "천왕성", "Neptune": "해왕성", "Pluto": "명왕성"
}

def get_global_location(city_name):
    try:
        location = geolocator.geocode(city_name)
        if location:
            return location.latitude, location.longitude, tf.timezone_at(lng=location.longitude, lat=location.latitude)
        return None, None, None
    except: return None, None, None

# --- [4. UI 레이아웃] ---
st.title("🪐 2026년 총운 해독")
st.write("새로운 시대의 시작점에서, 당신의 1년 궤적을 데이터로 예견합니다.")

with st.sidebar:
    st.header("✨ 서문")
    st.markdown("당신이 태어난 순간의 별의 배치는 당신의 영혼이 선택한 이번 생의 지도입니다.")

st.subheader("📝 당신의 기록을 남겨주세요")
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
    st.info("정확한 도시명을 영문으로 입력해 주세요.")
    if city_input:
        if st.button("📍 위치 확인"):
            lat_c, lng_c, tz_c = get_global_location(city_input)
            if lat_c: st.success(f"확인됨: {city_input}")
            else: st.error("도시를 찾을 수 없습니다.")

st.divider()

# --- [5. 분석 로직 (데이터 + 6가지 프롬프트)] ---
if st.button("✨ 2026년 대운 해독하기"):
    if not city_input or not user_name:
        st.warning("정보를 모두 입력해 주세요.")
    else:
        with st.spinner("🔮 우주의 데이터를 수집하여 차트를 해독하고 있습니다..."):
            lat, lng, tz_str = get_global_location(city_input)
            try:
                # 1. 차트 데이터 생성
                user = AstrologicalSubjectFactory.from_birth_data(
                    user_name, birth_date.year, birth_date.month, birth_date.day,
                    int(birth_hour), int(birth_min), lng=lng, lat=lat, tz_str=tz_str, online=False
                )

                # 2. [시각화] 출생 차트 데이터 표
                st.markdown("### ⭐ 나의 출생 차트 데이터")
                p_list = []
                for p in [user.sun, user.moon, user.mercury, user.venus, user.mars, user.jupiter, user.saturn, user.uranus, user.neptune, user.pluto]:
                    p_list.append({
                        "행성": PLANET_MAP.get(p.name, p.name),
                        "별자리": SIGN_MAP.get(p.sign, p.sign) + (" (역행)" if p.retrograde else ""),
                        "도수": f"{p.position:.1f}°",
                        "하우스": f"{p.house}H"
                    })
                p_list.append({"행성": "상승궁(ASC)", "별자리": SIGN_MAP.get(user.first_house.sign, user.first_house.sign), "도수": f"{user.first_house.position:.1f}°", "하우스": "1H"})
                st.table(pd.DataFrame(p_list))

                with st.expander("🏠 하우스 및 아스펙트 상세 보기"):
                    h_col1, h_col2 = st.columns(2)
                    with h_col1:
                        st.markdown("**[12 하우스]**")
                        h_list = [{"하우스": f"{i}H", "별자리": SIGN_MAP.get(getattr(user, f'house{i}').sign, getattr(user, f'house{i}').sign)} for i in range(1, 13)]
                        st.table(pd.DataFrame(h_list))
                    with h_col2:
                        st.markdown("**[주요 아스펙트]**")
                        a_list = [{"행성 1": PLANET_MAP.get(a.p1_name, a.p1_name), "유형": a.aspect_name, "행성 2": PLANET_MAP.get(a.p2_name, a.p2_name)} for a in user.aspects[:8]]
                        st.table(pd.DataFrame(a_list))

                st.divider()

                # 3. [AI 분석] 6가지 항목 포함 프롬프트
                chart_summary = f"""
                [Natal Chart] 
                User: {user_name}, Sun: {user.sun.sign} in {user.sun.house}H, 
                Moon: {user.moon.sign} in {user.moon.house}H, Asc: {user.first_house.sign}, 
                Saturn: {user.saturn.sign}, Jupiter: {user.jupiter.sign}
                """
                
                client = OpenAI(api_key=MY_OPENAI_API_KEY)
                
                # 정수님이 요청하신 6가지 항목을 정밀하게 반영한 프롬프트
                fortune_prompt = f"""
                아래 사용자의 네이탈 차트 데이터를 기반으로 '2026년 전체 운세'를 정밀하게 분석해.
                데이터: {chart_summary}

                너는 냉철한 데이터 분석가이자 신비로운 점성술사야. 모든 답변은 '반말'로, 하지만 아주 격조 있고 신비로운 문체로 작성해.

                반드시 다음 6가지 항목을 포함할 것:

                ### 1. [타고난 기질과 성향 분석]
                - 성격, 대인관계 방식, 의사결정 패턴을 차트 기반으로 설명해.

                ### 2. [2026년 전체 흐름 및 12개월 키워드]
                - 2026년의 에너지 흐름을 요약하고, 아래 포맷으로 1월~12월 키워드를 '표(Table)' 형태로 작성해.
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
                    max_tokens=3500
                )

                st.success(f"✅ {user_name}님의 2026년 문장이 완성되었습니다.")
                st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"해독 중 오류 발생: {e}")