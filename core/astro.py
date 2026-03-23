# ============================================================
# core/astro.py
# 출생 차트 계산 핵심 로직
# 출처: pages/01fortune2026.py 의 AstrologicalSubjectFactory 호출부 추출
# ============================================================

from kerykeion import AstrologicalSubjectFactory
from core.location import get_location, format_deg, clean_house

# 영어 별자리명 → 한국어 매핑 테이블
SIGN_MAP: dict[str, str] = {
    "Aries": "양자리",       "Ari": "양자리",
    "Taurus": "황소자리",    "Tau": "황소자리",
    "Gemini": "쌍둥이자리", "Gem": "쌍둥이자리",
    "Cancer": "게자리",      "Can": "게자리",
    "Leo": "사자자리",
    "Virgo": "처녀자리",     "Vir": "처녀자리",
    "Libra": "천칭자리",     "Lib": "천칭자리",
    "Scorpio": "전갈자리",   "Sco": "전갈자리",
    "Sagittarius": "사수자리", "Sag": "사수자리",
    "Capricorn": "염소자리", "Cap": "염소자리",
    "Aquarius": "물병자리",  "Aqu": "물병자리",
    "Pisces": "물고기자리",  "Pis": "물고기자리",
}

# 영어 행성명 → 한국어 매핑 테이블
PLANET_MAP: dict[str, str] = {
    "Sun": "태양", "Moon": "달", "Mercury": "수성",
    "Venus": "금성", "Mars": "화성", "Jupiter": "목성",
    "Saturn": "토성", "Uranus": "천왕성", "Neptune": "해왕성",
    "Pluto": "명왕성",
}


def build_chart(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    city: str,
) -> dict:
    """
    사용자의 출생 정보를 받아 kerykeion으로 출생 차트를 계산하고
    Flask/AI 호출에 바로 사용할 수 있는 구조화된 딕셔너리를 반환한다.

    Args:
        name:   사용자 이름
        year:   출생 연도
        month:  출생 월
        day:    출생 일
        hour:   출생 시 (0~23)
        minute: 출생 분 (0~59)
        city:   출생 도시명 (한글/영문)

    Returns:
        {
            "sun":          태양 별자리 한국어 문자열,
            "moon":         달 별자리 한국어 문자열,
            "ascendant":    상승궁(1하우스) 별자리 한국어 문자열,
            "planets_list": 주요 7행성 정보 리스트 (테이블 렌더링용),
            "chart_info_str": AI 프롬프트에 넣을 요약 문자열,
            "error":        오류 발생 시 오류 메시지 문자열 (정상이면 None)
        }

    planets_list 각 원소 형태:
        {"천체": "태양", "별자리": "처녀자리", "하우스": "5H"}
    """
    # --- [1] 위치 정보 조회 ---
    lat, lng, tz = get_location(city)
    if lat is None:
        return {"error": f"도시를 찾을 수 없습니다: {city}"}

    try:
        # --- [2] kerykeion 출생 차트 계산 ---
        user = AstrologicalSubjectFactory.from_birth_data(
            name, year, month, day, hour, minute,
            lng=lng, lat=lat, tz_str=tz, online=False
        )

        # --- [3] 핵심 3요소 추출 (한국어 변환) ---
        sun_kor = SIGN_MAP.get(user.sun.sign, user.sun.sign)
        moon_kor = SIGN_MAP.get(user.moon.sign, user.moon.sign)
        asc_kor = SIGN_MAP.get(user.first_house.sign, user.first_house.sign)

        # --- [4] 주요 7행성 테이블 데이터 구성 ---
        core_planets = [
            user.sun, user.moon, user.mercury,
            user.venus, user.mars, user.jupiter, user.saturn
        ]
        planets_list = []
        for p in core_planets:
            planets_list.append({
                "천체": PLANET_MAP.get(p.name, p.name),
                "별자리": SIGN_MAP.get(p.sign, p.sign) + (" (역행)" if p.retrograde else ""),
                "하우스": clean_house(p.house) + "H",
            })

        # --- [5] AI 프롬프트용 요약 문자열 구성 ---
        chart_info_str = (
            f"Sun:{user.sun.sign} in {user.sun.house}, "
            f"Moon:{user.moon.sign} in {user.moon.house}, "
            f"Asc:{user.first_house.sign}"
        )

        return {
            "sun": sun_kor,
            "moon": moon_kor,
            "ascendant": asc_kor,
            "planets_list": planets_list,
            "chart_info_str": chart_info_str,
            "error": None,
        }

    except Exception as e:
        return {"error": f"차트 계산 중 오류 발생: {str(e)}"}
