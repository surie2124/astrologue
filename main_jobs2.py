from kerykeion import AstrologicalSubjectFactory
from openai import OpenAI

# 1. OpenAI API 키 세팅 (여기에 새로 발급받은 키를 넣어주세요)
client = OpenAI(api_key="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")

# 2. 차트 생성
user = AstrologicalSubjectFactory.from_birth_data(
    "Jungsoo Park", 1996, 9, 2, 22, 0, 
    lng=126.9780, lat=37.5665, tz_str="Asia/Seoul", 
    online=False
)

def format_deg(pos_float):
    deg = int(pos_float)
    mins = int(round((pos_float - deg) * 60))
    if mins == 60:
        deg += 1
        mins = 0
    return f"{deg}°{mins:02d}'"

# 3. 추출된 데이터를 하나의 텍스트(문자열)로 묶기
chart_data_text = "=== Planet positions ===\n"
planets = [
    ("Sun", user.sun), ("Moon", user.moon), ("Mercury", user.mercury),
    ("Venus", user.venus), ("Mars", user.mars), ("Jupiter", user.jupiter),
    ("Saturn", user.saturn), ("Uranus", user.uranus), ("Neptune", user.neptune),
    ("Pluto", user.pluto)
]
if hasattr(user, 'node'): planets.append(("North Node", user.node))
elif hasattr(user, 'true_node'): planets.append(("North Node", user.true_node))
if hasattr(user, 'chiron'): planets.append(("Chiron", user.chiron))

for name, p in planets:
    retro = ", Retrograde" if getattr(p, 'retrograde', False) else ""
    chart_data_text += f"{name} in {p.sign.capitalize()} {format_deg(p.position)}{retro}, in {p.house}\n"

chart_data_text += "\n=== House positions ===\n"
houses = [
    ("1st House", user.first_house), ("2nd House", user.second_house),
    ("3rd House", user.third_house), ("4th House", user.fourth_house),
    ("5th House", user.fifth_house), ("6th House", user.sixth_house),
    ("7th House", user.seventh_house), ("8th House", user.eighth_house),
    ("9th House", user.ninth_house), ("10th House", user.tenth_house),
    ("11th House", user.eleventh_house), ("12th House", user.twelfth_house)
]
for name, h in houses:
    chart_data_text += f"{name} in {h.sign.capitalize()} {format_deg(h.position)}\n"

chart_data_text += "\n=== Planet aspects ===\n"
aspect_types = {0: "Conjunction", 60: "Sextile", 90: "Square", 120: "Trine", 180: "Opposition"}
aspect_planets = planets[:10]
for i in range(len(aspect_planets)):
    for j in range(i + 1, len(aspect_planets)):
        p1_name, p1 = aspect_planets[i]
        p2_name, p2 = aspect_planets[j]
        diff = abs(p1.abs_pos - p2.abs_pos)
        if diff > 180: diff = 360 - diff
        for target_angle, aspect_name in aspect_types.items():
            orb = abs(diff - target_angle)
            if orb <= 8:
                chart_data_text += f"{p1_name} {aspect_name} {p2_name} (Orb: {int(orb)}°{int(round((orb - int(orb)) * 60)):02d}')\n"

# 4. [직업/재물운] 서비스 최적화 프롬프트 (버전 3.1)
prompt = f"""
아래는 사용자의 초정밀 점성술 네이탈 차트 데이터야.
{chart_data_text}

너는 '데이터 사이언스와 고전 점성술'을 결합한 세계 최고의 커리어 컨설턴트야. 
아래 [작성 가이드]를 반드시 지켜서 분석 리포트를 작성해.

[작성 가이드]:
1. 절대 "네이탈 차트 언급"이나 "가이드" 같은 내 지시어를 제목으로 쓰지 마. 
2. 모든 항목은 고객이 바로 읽는 '최종 리포트' 형태여야 함.
3. 점성술 용어는 '🪐 당신의 하늘에 새겨진 별들의 언어'라는 항목에서만 아주 짧게 언급하고, 나머지는 철저히 비즈니스 언어로 풀이할 것.
4. 말투는 예리하고 자신감 넘치는 '반말'을 유지하되, 품격 있는 문장을 사용할 것.

### 1. [운명의 궤적: 연령대별 커리어 타임라인]
- 사용자가 '대기만성형'인지 '초년발복형'인지 먼저 정의하고 시작할 것.
- 사용자의 생년월일 및 나이 데이터를 고려하여, 아래 포맷을 엄격히 지켜서 최소 10개 연령대 구간으로 작성해줘. 초반/후반 처럼 두루뭉술한 단어 금지. 네이탈 차트 기반으로, 명확히 숫자를 언급하라.
- 1번 문항의 비중을 전체의 60% 이상으로 아주 길고 상세하게 가져갈 것.

[타임라인 작성 포맷 예시] (반드시 이 형태를 유지할 것)
🔴 25-30세: [핵심 사건 한 줄 요약]
- 🪐 당신의 하늘에 새겨진 별들의 언어: (해당 시기에 영향을 주는 행성과 별자리 배치를 한 문장으로 요약)
- 💼 비즈니스 현실: (이 시기에 겪게 될 구체적인 직업적 사건과 재무적 변화)
- 🧠 심리적 변화: (사용자가 느낄 감정적 파동과 내면의 성장)
- 💡 별들의 나침반: (이 구간을 돌파하기 위한 가장 날카로운 조언)

### 2. [당신을 압도적 성공으로 이끌 필살기 Top 3]
- 뻔한 소리(마케팅, 기획 등) 금지. 예를 들어, '데이터를 기반으로 한 B2B 전략 기획', '리스크를 통제하는 재무 관리', '대중의 결핍을 파고드는 콘텐츠 브랜딩'처럼 아주 뾰족하고 구체적인 산업군/직무 3가지를 꼽아.
- 차트 데이터의 어떤 요소 때문에 내가 이 분야에서 남들을 압살할 수 있는지 구체적으로 설명해.

### 3. [재물 그릇의 크기와 치명적인 리스크]
- 내 차트에 나타난 '재물 그릇'의 형태를 현실적인 언어로 정의해줘. (예: 월급을 모아 태산을 만드는 타입, 한 방의 투자/사업으로 퀀텀 점프하는 타입, 타인의 자본을 굴리는 타입 등)
- 내가 살면서 절대 건드리면 안 되는 '재무적 뇌관(파산 리스크)'을 하나만 콕 집어서 경고해. (예: 친한 사람과의 동업, 감정에 휩쓸린 과소비, 하이리스크 주식 단타 등)
- 내 성향을 바탕으로 '돈이 새는 치명적인 단점'을 직설적으로 비판하고, 통장 잔고를 지키기 위해 무조건 지켜야 할 단 하나의 철칙을 제시해.
"""

# 서비스 컨셉에 맞는 문구로 변경
print("✨ 당신이 태어난 순간의 천체 좌표를 분석하여 운명의 궤적을 해독하고 있습니다. 잠시만 기다려 주세요...\n")

# 5. API 호출 (설정 동일)
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system", 
            "content": "너는 냉철한 데이터 분석가이자 신비로운 점성술사야. 고객에게 뜬구름 잡는 소리가 아닌, 삶의 전략이 되는 리포트를 제공해."
        },
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=3500 
)

print(response.choices[0].message.content)