from kerykeion import AstrologicalSubjectFactory

# 1. 차트 생성 (네 진짜 생일: 1996년 9월 2일 22시 00분)
user = AstrologicalSubjectFactory.from_birth_data(
    "Jungsoo Park", 1996, 9, 2, 22, 0, 
    lng=126.9780, lat=37.5665, tz_str="Asia/Seoul", 
    online=False
)

# 2. 도수 변환 헬퍼 함수 (소수점을 00°00' 형태로 예쁘게 변환)
def format_deg(pos_float):
    deg = int(pos_float)
    mins = int(round((pos_float - deg) * 60))
    if mins == 60:
        deg += 1
        mins = 0
    return f"{deg}°{mins:02d}'"

# ==========================================
# [1] Planet positions (행성 위치 추출)
# ==========================================
print("Planet positions:")
# 주요 10대 행성 리스트
planets = [
    ("Sun", user.sun), ("Moon", user.moon), ("Mercury", user.mercury),
    ("Venus", user.venus), ("Mars", user.mars), ("Jupiter", user.jupiter),
    ("Saturn", user.saturn), ("Uranus", user.uranus), ("Neptune", user.neptune),
    ("Pluto", user.pluto)
]

# 에러 방지: Node와 Chiron은 존재할 때만 리스트에 안전하게 추가 (v5 업데이트 반영)
if hasattr(user, 'node'):
    planets.append(("North Node", user.node))
elif hasattr(user, 'true_node'):
    planets.append(("North Node", user.true_node))
    
if hasattr(user, 'chiron'):
    planets.append(("Chiron", user.chiron))

for name, p in planets:
    sign = p.sign.capitalize() # 별자리 이름
    pos = format_deg(p.position) # 해당 별자리 내의 도수/분
    house = p.house
    retro = ", Retrograde" if getattr(p, 'retrograde', False) else ""
    print(f"{name} in {sign} {pos}{retro}, in {house}")

# ==========================================
# [2] House positions (하우스 위치 추출)
# ==========================================
print("\nHouse positions:")
houses = [
    ("1st House", user.first_house), ("2nd House", user.second_house),
    ("3rd House", user.third_house), ("4th House", user.fourth_house),
    ("5th House", user.fifth_house), ("6th House", user.sixth_house),
    ("7th House", user.seventh_house), ("8th House", user.eighth_house),
    ("9th House", user.ninth_house), ("10th House", user.tenth_house),
    ("11th House", user.eleventh_house), ("12th House", user.twelfth_house)
]

for name, h in houses:
    sign = h.sign.capitalize()
    pos = format_deg(h.position)
    print(f"{name} in {sign} {pos}")

# ==========================================
# [3] Planet aspects (행성 간 각도 및 허용 오차 계산)
# ==========================================
print("\nPlanet aspects:")
aspect_types = {0: "Conjunction", 60: "Sextile", 90: "Square", 120: "Trine", 180: "Opposition"}
aspect_planets = planets[:10] # 주요 10대 행성끼리만 각도 계산 (Node, Chiron 제외)

for i in range(len(aspect_planets)):
    for j in range(i + 1, len(aspect_planets)):
        p1_name, p1 = aspect_planets[i]
        p2_name, p2 = aspect_planets[j]
        
        # 두 행성 간의 절대 각도(360도 기준) 차이 계산
        diff = abs(p1.abs_pos - p2.abs_pos)
        if diff > 180:
            diff = 360 - diff
            
        # 메이저 애스펙트 및 오차(Orb) 확인
        for target_angle, aspect_name in aspect_types.items():
            orb = abs(diff - target_angle)
            if orb <= 8:  # 허용 오차(Orb)를 8도 이내로 설정
                orb_deg = int(orb)
                orb_min = int(round((orb - orb_deg) * 60))
                print(f"{p1_name} {aspect_name} {p2_name} (Orb: {orb_deg}°{orb_min:02d}')")