# ============================================================
# core/ai_report.py
# OpenAI API 호출 및 운세 리포트 생성 로직
# 출처: pages/01fortune2026.py 의 프롬프트 및 API 호출부 추출
# ============================================================

from openai import OpenAI


def build_prompt(user_name: str, chart_info: str) -> str:
    """
    사용자명과 차트 요약 정보를 받아 GPT-4o에 전달할 프롬프트 문자열을 반환한다.
    기존 Streamlit 버전의 프롬프트를 그대로 유지한다.

    Args:
        user_name:  사용자 이름
        chart_info: build_chart()가 반환한 chart_info_str
                    (예: "Sun:Virgo in Fifth_House, Moon:Aries in ...")

    Returns:
        완성된 프롬프트 문자열
    """
    return f"""
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


def generate_fortune_report(user_name: str, chart_info: str, api_key: str) -> str:
    """
    사용자명과 차트 정보를 바탕으로 GPT-4o를 호출해 운세 리포트를 생성한다.
    반환값은 순수 Markdown 문자열이며, UI 렌더링 로직을 포함하지 않는다.

    Args:
        user_name:  사용자 이름
        chart_info: build_chart()가 반환한 chart_info_str
        api_key:    OpenAI API 키 (환경변수에서 주입)

    Returns:
        GPT-4o가 생성한 Markdown 형식의 리포트 문자열.
        오류 발생 시 오류 메시지 문자열 반환.
    """
    try:
        client = OpenAI(api_key=api_key)
        prompt = build_prompt(user_name, chart_info)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "너는 구조적 데이터 분석과 점성술을 구조적으로 해독하는 전문 알고리즘이야."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"리포트 생성 중 오류 발생: {str(e)}"
