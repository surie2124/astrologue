import streamlit as st
from kerykeion import AstrologicalSubjectFactory
from openai import OpenAI
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import datetime

# --- [1. 서비스 브랜드 및 보안 설정] ---
BRAND_KOR = "별들의 언어"
BRAND_ENG = "AstroLogue"

# 개발자용 API 키 (실제 배포 시에는 환경변수나 st.secrets 사용 권장)
MY_OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# 도구 초기화
geolocator = Nominatim(user_agent="astrologue_global_app")
tf = TimezoneFinder()

# --- [2. 헬퍼 함수 정의] ---

def get_global_location(city_name):
    try:
        location = geolocator.geocode(city_name)
        if location:
            lat, lng = location.latitude, location.longitude
            tz_str = tf.timezone_at(lng=lng, lat=lat)
            return lat, lng, tz_str
        return None, None, None
    except Exception:
        return None, None, None

def format_deg(pos_float):
    deg = int(pos_float)
    mins = int(round((pos_float - deg) * 60))
    if mins == 60: deg += 1; mins = 0
    return f"{deg}°{mins:02d}'"

# --- [3. 웹 UI 레이아웃 구성] ---

st.title(f"🪐 {BRAND_KOR}")
st.write(f"**{BRAND_ENG}:** 당신이 태어난 순간, 별들이 속삭인 운명의 언어를 해독합니다.")

with st.sidebar:
    st.header("✨우주에 새겨진 당신의 서사")
    st.markdown(f"""
    당신이 태어난 순간, 우주는 하나의 문장을 완성했다. 
    **{BRAND_KOR}**({BRAND_ENG})는 그 문장을 해독해, 
    천체의 정밀한 움직임과 점성술의 질서를 통해 당신의 삶에 흐르는 패턴을 구조적으로 해석한다. 
    
    단순한 운세가 아닌, 그 패턴을 기반으로 당신의 선택과 방향을 설계하는 가장 **정밀한 알고리즘**을 제안한다.
    """)
    st.divider()
    st.caption(f"© 2026 {BRAND_ENG} Project. All rights reserved.")

st.subheader("📝 당신의 기록을 남겨주세요")
col1, col2 = st.columns(2)

with col1:
    user_name = st.text_input("성함 (Name)", placeholder="Park")
    birth_date = st.date_input("출생 날짜 (Birth Date)", min_value=datetime.date(1950, 1, 1), value=datetime.date(1996, 1, 1))
    
    unknown_time = st.checkbox("시간을 모릅니다 (Unknown Time)")
    if unknown_time:
        birth_hour, birth_min = 12, 0
        st.caption("💡 시간을 모를 경우 정오(12:00) 기준으로 분석을 진행합니다.")
    else:
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            birth_hour = st.number_input("시 (Hour)", min_value=0, max_value=23, value=22, step=1)
        with t_col2:
            birth_min = st.number_input("분 (Minute)", min_value=0, max_value=59, value=0, step=1)

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

# --- [4. 분석 실행 버튼 및 로직] ---

if st.button("✨ 별들의 언어 해독하기"):
    if not city_input:
        st.warning("분석을 위해 태어난 도시를 입력해 주세요.")
    else:
        with st.spinner("🔮 당신의 하늘에 새겨진 비밀을 해독하고 있습니다..."):
            lat, lng, tz_str = get_global_location(city_input)
            
            if not lat:
                st.error("입력하신 도시를 찾을 수 없습니다.")
            else:
                try:
                    # B. Kerykeion 차트 계산
                    user = AstrologicalSubjectFactory.from_birth_data(
                        user_name, birth_date.year, birth_date.month, birth_date.day,
                        int(birth_hour), int(birth_min), 
                        lng=lng, lat=lat, tz_str=tz_str, online=False
                    )

                    time_info = "정확한 출생 시간" if not unknown_time else "추정 시간(정오)"
                    
                    # C. 데이터 추출
                    chart_data_text = "=== Planet positions ===\n"
                    planets_list = [
                        ("Sun", user.sun), ("Moon", user.moon), ("Mercury", user.mercury),
                        ("Venus", user.venus), ("Mars", user.mars), ("Jupiter", user.jupiter),
                        ("Saturn", user.saturn), ("Uranus", user.uranus), ("Neptune", user.neptune),
                        ("Pluto", user.pluto)
                    ]
                    if hasattr(user, 'node'): planets_list.append(("North Node", user.node))
                    if hasattr(user, 'chiron'): planets_list.append(("Chiron", user.chiron))

                    for name, p in planets_list:
                        retro = ", Retrograde" if getattr(p, 'retrograde', False) else ""
                        chart_data_text += f"{name} in {p.sign.capitalize()} {format_deg(p.position)}{retro}, in {p.house}\n"

                    chart_data_text += "\n=== House positions ===\n"
                    houses_list = [
                        ("1st House", user.first_house), ("2nd House", user.second_house),
                        ("3rd House", user.third_house), ("4th House", user.fourth_house),
                        ("5th House", user.fifth_house), ("6th House", user.sixth_house),
                        ("7th House", user.seventh_house), ("8th House", user.eighth_house),
                        ("9th House", user.ninth_house), ("10th House", user.tenth_house),
                        ("11th House", user.eleventh_house), ("12th House", user.twelfth_house)
                    ]
                    for name, h in houses_list:
                        chart_data_text += f"{name} in {h.sign.capitalize()} {format_deg(h.position)}\n"

                    chart_data_text += "\n=== Planet aspects ===\n"
                    aspect_types = {0: "Conjunction", 60: "Sextile", 90: "Square", 120: "Trine", 180: "Opposition"}
                    primary_planets = planets_list[:10]
                    for i in range(len(primary_planets)):
                        for j in range(i + 1, len(primary_planets)):
                            p1_name, p1 = primary_planets[i]; p2_name, p2 = primary_planets[j]
                            diff = abs(p1.abs_pos - p2.abs_pos)
                            if diff > 180: diff = 360 - diff
                            for target_angle, aspect_name in aspect_types.items():
                                orb = abs(diff - target_angle)
                                if orb <= 8:
                                    chart_data_text += f"{p1_name} {aspect_name} {p2_name} (Orb: {int(orb)}°{int(round((orb - int(orb)) * 60)):02d}')\n"

                    # D. OpenAI 클라이언트 생성 및 프롬프트 설정
                    client = OpenAI(api_key=MY_OPENAI_API_KEY) # <--- 여기가 핵심 수정 포인트!
                    
                    final_prompt = f"""
                    사용자 정보: {user_name} ({time_info} 기반 분석)
                    {chart_data_text}

                    너는 '데이터 사이언스와 고전 점성술'을 결합한 세계 최고의 커리어 컨설턴트야. 
                    아래 [작성 가이드]를 반드시 지켜서 분석 리포트를 작성해.

                    [작성 가이드]:
                    1. 절대 "네이탈 차트 언급"이나 "가이드" 같은 내 지시어를 제목이나 텍스트로 쓰지 마. 
                    2. 모든 항목은 고객이 바로 읽는 '최종 리포트' 형태여야 함.
                    3. 점성술 용어는 오직 지정된 항목에서만 아주 짧게 언급하고, 나머지는 철저히 비즈니스 언어로 풀이할 것.
                    4. 말투는 예리하고 자신감 넘치는 '반말'을 유지하되, 품격 있는 문장을 사용할 것.
                    5. 전체 분량은 최소 2,500자 이상으로 아주 길고 심도 있게 작성할 것.

                    ### 1. [운명의 궤적: 연령대별 커리어 타임라인]
                    - 사용자가 '대기만성형'인지 '초년발복형'인지 먼저 정의하고 시작할 것.
                    - 사용자의 생년월일 및 나이 데이터를 고려하여, 아래 포맷을 엄격히 지켜서 최소 10개 연령대 구간으로 작성해줘. 초반/후반 처럼 두루뭉술한 단어 금지. 네이탈 차트 기반으로, 명확히 숫자를 언급하라.
                    - 1번 문항의 비중을 전체의 60% 이상으로 아주 길고 상세하게 가져갈 것.
                    - [타임라인 작성 포맷 예시] (반드시 이 형태를 유지할 것)
                    🔴 25-30세: [핵심 사건 한 줄 요약]
                    - 🪐 당신의 하늘에 새겨진 별들의 언어: (해당 시기에 영향을 주는 행성과 별자리 배치를 한 문장으로 요약)
                    - 💼 비즈니스 현실: (이 시기에 겪게 될 구체적인 직업적 사건과 재무적 변화)
                    - 🧠 심리적 변화: (사용자가 느낄 감정적 파동과 내면의 성장)
                    - 💡 별들의 도움말: (이 구간을 돌파하기 위한 가장 날카로운 조언)

                    ### 2. [당신을 압도적 성공으로 이끌 필살기 Top 3]
                    - 구체적인 직무/산업군 3가지 선정 및 차트 기반 분석.
                    - 뻔한 소리(마케팅, 기획 등) 금지. 예를 들어, '데이터를 기반으로 한 B2B 전략 기획', '리스크를 통제하는 재무 관리', '대중의 결핍을 파고드는 콘텐츠 브랜딩'처럼 아주 뾰족하고 구체적인 산업군/직무 3가지를 꼽아.
                    - 차트 데이터의 어떤 요소 때문에 내가 이 분야에서 남들을 압살할 수 있는지 구체적으로 설명해.

                    ### 3. [재물 그릇의 본질과 치명적인 리스크]
                    - 내 차트에 나타난 '재물 그릇'의 형태를 현실적인 언어로 정의해줘. (예: 월급을 모아 태산을 만드는 타입, 한 방의 투자/사업으로 퀀텀 점프하는 타입, 타인의 자본을 굴리는 타입 등)
                    - 내가 살면서 절대 건드리면 안 되는 '재무적 뇌관(파산 리스크)'을 하나만 콕 집어서 경고해. (예: 친한 사람과의 동업, 감정에 휩쓸린 과소비, 하이리스크 주식 단타 등)
                    - 내 성향을 바탕으로 '돈이 새는 치명적인 단점'을 직설적으로 비판하고, 통장 잔고를 지키기 위해 무조건 지켜야 할 단 하나의 철칙을 제시해.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "너는 냉철한 데이터 분석가이자 신비로운 점성술사야. 삶의 전략이 되는 리포트를 제공해."},
                            {"role": "user", "content": final_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=3500 
                    )

                    st.success("✅ 해독이 완료되었습니다. 당신의 성도를 펼칩니다.")
                    st.markdown("---")
                    st.markdown(response.choices[0].message.content)
                    st.markdown("---")
                    st.caption(f"📍 분석 데이터: {city_input} (위도: {lat:.2f}, 경도: {lng:.2f}) | 시간대: {tz_str}")

                except Exception as e:
                    st.error(f"데이터 해독 중 예기치 못한 오류가 발생했습니다: {e}")