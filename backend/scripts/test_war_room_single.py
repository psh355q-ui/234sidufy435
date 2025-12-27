"""
test_war_room_single.py - War Room 단일 토론 테스트

📊 Data Sources:
    - FastAPI: War Room API

🔗 External Dependencies:
    - requests: HTTP 요청

📤 Output:
    - War Room 토론 결과
    - DB 저장 확인

🔄 Called By:
    - Manual execution: python backend/scripts/test_war_room_single.py
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8001"

def test_war_room(ticker: str = "NVDA"):
    """
    War Room 단일 토론 테스트

    Args:
        ticker: 종목 코드 (기본값: NVDA)
    """
    print("="*80)
    print(f"🏛️ War Room 토론 테스트: {ticker}")
    print("="*80)
    print(f"시작 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # War Room 토론 실행
        print(f"📡 POST /api/war-room/debate")
        print(f"   Ticker: {ticker}\n")

        response = requests.post(
            f"{API_BASE}/api/war-room/debate",
            json={"ticker": ticker},
            timeout=300  # 5분 타임아웃
        )

        if response.status_code == 200:
            result = response.json()

            print("✅ 토론 성공!\n")
            print("="*80)
            print("📊 토론 결과")
            print("="*80)
            print(f"Session ID: {result['session_id']}")
            print(f"Ticker: {result['ticker']}")
            print(f"\n합의:")
            print(f"  Action: {result['consensus']['action']}")
            print(f"  Confidence: {result['consensus']['confidence']:.2%}")
            print(f"  Summary: {result['consensus'].get('summary', 'N/A')}")

            print(f"\nConstitutional 검증: {'✅ 통과' if result['constitutional_valid'] else '❌ 실패'}")

            if result.get('signal_id'):
                print(f"Signal ID: {result['signal_id']}")

            if result.get('order_id'):
                print(f"Order ID: {result['order_id']}")

            print(f"\n에이전트 투표 ({len(result['votes'])}개):")
            print("-"*80)
            for vote in result['votes']:
                print(f"  {vote['agent']:15} | {vote['action']:4} | {vote['confidence']:.1%} | {vote['reasoning'][:50]}...")

            print("="*80)

            # DB 확인
            print("\n🔍 DB 저장 확인...")
            check_db_saves(result['session_id'])

        else:
            print(f"❌ 토론 실패!")
            print(f"Status Code: {response.status_code}")
            print(f"Error: {response.text}")

    except requests.exceptions.Timeout:
        print("❌ 타임아웃 (5분 초과)")
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        import traceback
        traceback.print_exc()


def check_db_saves(session_id: int):
    """
    DB 저장 확인

    Args:
        session_id: War Room 세션 ID
    """
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    from sqlalchemy import text
    from backend.database.repository import get_sync_session

    db = get_sync_session()

    try:
        # ai_debate_sessions 확인
        session_check = text("""
            SELECT ticker, consensus_action, consensus_confidence, constitutional_valid
            FROM ai_debate_sessions
            WHERE id = :session_id
        """)

        session_result = db.execute(session_check, {"session_id": session_id}).fetchone()

        if session_result:
            print(f"  ✅ ai_debate_sessions: {session_result[0]} | {session_result[1]} | {session_result[2]:.2%} | {'Valid' if session_result[3] else 'Invalid'}")
        else:
            print(f"  ❌ ai_debate_sessions: 저장 안됨")

        # price_tracking 확인
        price_check = text("""
            SELECT ticker, initial_price, consensus_action, status
            FROM price_tracking
            WHERE session_id = :session_id
        """)

        price_result = db.execute(price_check, {"session_id": session_id}).fetchone()

        if price_result:
            print(f"  ✅ price_tracking: {price_result[0]} | ${price_result[1]:.2f} | {price_result[2]} | {price_result[3]}")
        else:
            print(f"  ⚠️ price_tracking: 저장 안됨 (KIS_ACCOUNT_NUMBER 미설정?)")

        # agent_vote_tracking 확인
        agent_check = text("""
            SELECT COUNT(*) FROM agent_vote_tracking
            WHERE session_id = :session_id
        """)

        agent_count = db.execute(agent_check, {"session_id": session_id}).scalar()

        if agent_count and agent_count > 0:
            print(f"  ✅ agent_vote_tracking: {agent_count}개 에이전트 투표 저장")
        else:
            print(f"  ⚠️ agent_vote_tracking: 저장 안됨")

    except Exception as e:
        print(f"  ❌ DB 확인 실패: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    ticker = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    test_war_room(ticker)
