# ============================================================
# core/location.py
# 위치 관련 유틸리티 함수 모음
# 출처: pages/01fortune2026.py 에서 추출
# ============================================================

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

# 지오코더 및 타임존 파인더 초기화 (모듈 로드 시 1회만 실행)
_geolocator = Nominatim(user_agent="astrologue_global_app")
_tf = TimezoneFinder()


def get_location(city: str) -> tuple[float | None, float | None, str | None]:
    """
    도시명을 받아 (위도, 경도, 시간대 문자열)을 반환한다.
    도시를 찾지 못하거나 오류 발생 시 (None, None, None) 반환.

    Args:
        city: 한글 또는 영문 도시명 (예: "서울", "Seoul", "New York")

    Returns:
        (lat, lng, tz_str) 튜플
        예: (37.5665, 126.9780, "Asia/Seoul")
    """
    try:
        loc = _geolocator.geocode(city)
        if loc:
            lat = loc.latitude
            lng = loc.longitude
            tz_str = _tf.timezone_at(lng=lng, lat=lat)
            return lat, lng, tz_str
        return None, None, None
    except Exception:
        return None, None, None


def format_deg(pos_float: float) -> str:
    """
    kerykeion이 반환하는 소수점 도수(float)를 '00°00'' 형태 문자열로 변환한다.

    Args:
        pos_float: 소수점 도수 (예: 12.75)

    Returns:
        포맷된 문자열 (예: "12°45'")
    """
    deg = int(pos_float)
    mins = int(round((pos_float - deg) * 60))
    # 반올림으로 60분이 될 경우 도 단위로 올림 처리
    if mins == 60:
        deg += 1
        mins = 0
    return f"{deg}°{mins:02d}'"


def clean_house(house_str: str) -> str:
    """
    kerykeion이 반환하는 하우스 문자열(예: 'Fifth_House')을
    숫자 문자열(예: '5')로 변환한다.

    Args:
        house_str: kerykeion 하우스 속성 문자열

    Returns:
        숫자 문자열 (예: "5"), 매칭 실패 시 원본 문자열 반환
    """
    nums = {
        "First": "1", "Second": "2", "Third": "3", "Fourth": "4",
        "Fifth": "5", "Sixth": "6", "Seventh": "7", "Eighth": "8",
        "Ninth": "9", "Tenth": "10", "Eleventh": "11", "Twelfth": "12"
    }
    for k, v in nums.items():
        if k in str(house_str):
            return v
    return str(house_str)
