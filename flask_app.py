# ============================================================
# flask_app.py
# AstroLogue Flask 서버 — Streamlit 버전(app.py)과 별개로 운영
# 토스페이먼츠 결제 연동 포함
# ============================================================

import os
import json
import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from dotenv import load_dotenv

from core.astro import build_chart
from core.ai_report import generate_fortune_report

# --- [1. 환경 변수 로드] ---
# 프로젝트 루트의 .env 파일에서 API 키 등을 읽어온다.
# .env 파일 예시:
#   OPENAI_API_KEY=sk-...
#   TOSS_CLIENT_KEY=test_ck_...
#   TOSS_SECRET_KEY=test_sk_...
#   FLASK_SECRET_KEY=임의의_랜덤_문자열
load_dotenv()

OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY")
TOSS_CLIENT_KEY  = os.getenv("TOSS_CLIENT_KEY")   # 토스페이먼츠 클라이언트 키
TOSS_SECRET_KEY  = os.getenv("TOSS_SECRET_KEY")   # 토스페이먼츠 시크릿 키 (서버 전용)
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-in-production")

# 토스페이먼츠 결제 승인 API 엔드포인트
TOSS_CONFIRM_URL = "https://api.tosspayments.com/v1/payments/confirm"

# 리포트 1건당 결제 금액 (원 단위)
REPORT_PRICE = 3900


# --- [2. Flask 앱 초기화] ---
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY  # session 사용을 위한 시크릿 키


# ============================================================
# [3. 페이지 라우트]
# ============================================================

@app.route("/")
def index():
    """
    메인 홈 화면.
    카테고리 선택 버튼 + 출생 정보 입력 폼을 렌더링한다.
    """
    return render_template("index.html", toss_client_key=TOSS_CLIENT_KEY)


# ============================================================
# [4. API 라우트 — 차트 계산]
# ============================================================

@app.route("/api/chart", methods=["POST"])
def api_chart():
    """
    출생 정보를 받아 차트 계산 결과를 JSON으로 반환한다.
    결제 전 '미리보기(태양/달/상승궁)' 데이터를 제공하는 데 사용한다.

    Request Body (JSON):
        {
            "name":   "홍길동",
            "year":   1996,
            "month":  9,
            "day":    2,
            "hour":   22,
            "minute": 0,
            "city":   "Seoul"
        }

    Response (JSON):
        성공: { "sun": "처녀자리", "moon": "양자리", "ascendant": "황소자리",
                "planets_list": [...], "chart_info_str": "Sun:Virgo in ..." }
        실패: { "error": "오류 메시지" }
    """
    data = request.get_json(force=True)

    # 필수 필드 검증
    required = ["name", "year", "month", "day", "hour", "minute", "city"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"필수 항목 누락: {field}"}), 400

    result = build_chart(
        name=str(data["name"]),
        year=int(data["year"]),
        month=int(data["month"]),
        day=int(data["day"]),
        hour=int(data["hour"]),
        minute=int(data["minute"]),
        city=str(data["city"]),
    )

    if result.get("error"):
        return jsonify({"error": result["error"]}), 400

    # 세션에 차트 정보 임시 저장 (결제 성공 후 AI 호출에 사용)
    session["chart_info_str"] = result["chart_info_str"]
    session["user_name"] = data["name"]

    return jsonify(result)


# ============================================================
# [5. API 라우트 — AI 리포트 생성]
# ============================================================

@app.route("/api/fortune", methods=["POST"])
def api_fortune():
    """
    결제 확인이 완료된 후 AI 리포트를 생성하여 반환한다.
    직접 호출하지 말고 /pay/success 콜백에서 내부적으로 사용하는 것을 권장한다.

    Request Body (JSON):
        {
            "user_name":  "홍길동",
            "chart_info": "Sun:Virgo in Fifth_House, ..."
        }

    Response (JSON):
        성공: { "report": "### 1. [핵심 기질 및 성향] ..." }
        실패: { "error": "오류 메시지" }
    """
    data = request.get_json(force=True)
    user_name  = data.get("user_name")
    chart_info = data.get("chart_info")

    if not user_name or not chart_info:
        return jsonify({"error": "user_name 또는 chart_info 누락"}), 400

    report = generate_fortune_report(user_name, chart_info, OPENAI_API_KEY)
    return jsonify({"report": report})


# ============================================================
# [6. 토스페이먼츠 결제 라우트]
# ============================================================

@app.route("/pay/request", methods=["POST"])
def pay_request():
    """
    결제창 요청 처리.
    프론트엔드에서 토스페이먼츠 JS SDK를 통해 결제창을 열기 전에
    서버 측 주문 정보를 세션에 저장한다.

    Request Body (JSON):
        {
            "order_id":   "order_20260101_abc123",  (클라이언트가 생성)
            "order_name": "AstroLogue 2026 총운 리포트"
        }

    Response (JSON):
        { "ok": true, "amount": 3900, "order_id": "...", "order_name": "..." }
    """
    data = request.get_json(force=True)
    order_id   = data.get("order_id")
    order_name = data.get("order_name", "AstroLogue 운세 리포트")

    if not order_id:
        return jsonify({"error": "order_id 누락"}), 400

    # 주문 정보 세션에 저장 (콜백에서 검증에 사용)
    session["order_id"]   = order_id
    session["order_name"] = order_name

    return jsonify({
        "ok": True,
        "amount": REPORT_PRICE,
        "order_id": order_id,
        "order_name": order_name,
    })


@app.route("/pay/success")
def pay_success():
    """
    토스페이먼츠 결제 성공 콜백.
    토스페이먼츠가 리다이렉트하는 URL로, 쿼리 파라미터로 결제 정보가 전달된다.

    Query Params (토스페이먼츠 자동 전달):
        paymentKey: 결제 고유 키
        orderId:    주문 ID
        amount:     결제 금액

    처리 순서:
        1. 금액 검증 (세션 금액 vs 콜백 금액)
        2. 토스페이먼츠 서버에 결제 최종 승인 요청
        3. 승인 성공 시 AI 리포트 생성
        4. 리포트 결과 페이지 렌더링
    """
    payment_key = request.args.get("paymentKey")
    order_id    = request.args.get("orderId")
    amount      = request.args.get("amount", 0, type=int)

    # --- 금액 검증 ---
    if amount != REPORT_PRICE:
        return render_template(
            "index.html",
            toss_client_key=TOSS_CLIENT_KEY,
            error="결제 금액이 일치하지 않습니다."
        )

    # --- 토스페이먼츠 결제 승인 요청 ---
    confirm_response = requests.post(
        TOSS_CONFIRM_URL,
        json={
            "paymentKey": payment_key,
            "orderId":    order_id,
            "amount":     amount,
        },
        auth=(TOSS_SECRET_KEY, ""),  # Basic Auth: secret_key를 username으로 사용
        headers={"Content-Type": "application/json"},
    )

    if confirm_response.status_code != 200:
        error_body = confirm_response.json()
        return render_template(
            "index.html",
            toss_client_key=TOSS_CLIENT_KEY,
            error=f"결제 승인 실패: {error_body.get('message', '알 수 없는 오류')}"
        )

    # --- 결제 승인 성공 → AI 리포트 생성 ---
    user_name  = session.get("user_name", "고객")
    chart_info = session.get("chart_info_str", "")

    report_md = generate_fortune_report(user_name, chart_info, OPENAI_API_KEY)

    # TODO: 결제 내역 및 리포트를 DB에 저장하는 로직 추가 예정

    return render_template(
        "report.html",
        user_name=user_name,
        report=report_md,
    )


@app.route("/pay/fail")
def pay_fail():
    """
    토스페이먼츠 결제 실패/취소 콜백.

    Query Params (토스페이먼츠 자동 전달):
        code:    오류 코드
        message: 오류 메시지
    """
    code    = request.args.get("code", "UNKNOWN")
    message = request.args.get("message", "결제에 실패했습니다.")

    return render_template(
        "index.html",
        toss_client_key=TOSS_CLIENT_KEY,
        error=f"결제 실패 ({code}): {message}"
    )


# ============================================================
# [7. 앱 실행]
# ============================================================

if __name__ == "__main__":
    # 개발 서버 실행
    # 프로덕션 환경에서는 gunicorn 등 WSGI 서버를 사용할 것
    app.run(debug=True, port=5000)
