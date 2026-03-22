import streamlit as st
from kerykeion import AstrologicalSubjectFactory
from openai import OpenAI
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import datetime

# --- [1. 브랜드 및 보안 설정] ---
BRAND_KOR = "별들의 언어"
BRAND_ENG = "AstroLogue"
MY_OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# --- [2. 헬퍼 함수] ---
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

def format_deg(pos_float):
    deg = int(pos_float)
    mins = int(round((pos_float - deg) * 60))
    if mins == 60: deg += 1; mins = 0
    return f"{deg}°{mins:02d}'"

# --- [3. UI 레이아웃] ---
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

if st.button("✨ 2026년 대운 해독하기"):
    if not city_input:
        st.warning("도시를 입력해 주세요.")
    else:
        with st.spinner("🔮 2026년의 천체 궤도를 시뮬레이션하고 있습니다..."):
            lat, lng, tz_str = get_global_location(city_input)
            try:
                user = AstrologicalSubjectFactory.from_birth_data(
                    user_name, birth_date.year, birth_date.month, birth_date.day,
                    int(birth_hour), int(birth_min), lng=lng, lat=lat, tz_str=tz_str, online=False
                )

                # 데이터 추출 (Career 페이지와 동일 로직)
                chart_data = f"Name: {user_name}, Sun: {user.sun.sign}, Moon: {user.moon.sign}, ..." # 중략 (필요 데이터 구성)
                
                client = OpenAI(api_key=MY_OPENAI_API_KEY)
                
                fortune_prompt = f"""
                아래 사용자의 네이탈 차트 데이터를 기반으로 '2026년 전체 운세'를 분석해.
                데이터: {chart_data}

                너는 냉철한 데이터 분석가이자 신비로운 점성술사야. 다음 6가지 항목을 '반말'로, 품격 있게 작성해.

                ### 1. [타고난 기질과 성향 분석]
                - 이 사용자의 타고난 성격, 대인관계 방식, 의사결정 패턴을 데이터 기반으로 정밀 분석해.

                ### 2. [2026년 전체 흐름 및 12개월 키워드]
                - 2026년의 전반적인 에너지의 고저를 설명하고, 아래 포맷으로 1월~12월 키워드를 '표(Table)' 형태로 만들어.
                | 월 | 핵심 키워드 | 운의 강도 |
                |---|---|---|
                | 1월 | ... | ... | (12월까지)

                ### 3. [커리어 이슈 포인트 & 집중 시기]
                - 이직, 승진, 프로젝트 성공 등 직업적 변곡점과 가장 에너지가 강한 시기를 집어줘.

                ### 4. [연애 흐름과 반복되는 패턴]
                - 2026년에 만날 인연의 특징과 본인이 연애에서 반복하는 실수/패턴을 분석해.

                ### 5. [금전 관리 및 투자 타이밍]
                - 재물운의 흐름과 공격적으로 투자해야 할 시기 vs 지켜야 할 시기를 명확히 구분해.

                ### 6. [2026년 나를 위한 별들의 조언]
                - 마지막으로 이 사용자가 2026년을 승리로 이끌기 위해 가슴에 새겨야 할 단 한 문장을 제시해.
                """

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "너는 삶의 전략을 설계하는 점성술 알고리즘이야."},
                              {"role": "user", "content": fortune_prompt}],
                    temperature=0.7, max_tokens=3500
                )

                st.success("✅ 2026년의 문장이 완성되었습니다.")
                st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"해독 중 오류 발생: {e}")