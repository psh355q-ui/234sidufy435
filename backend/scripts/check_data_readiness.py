"""
check_data_readiness.py - 실거래 준비 상태 확인

📊 Data Sources:
    - PostgreSQL: agent_vote_tracking, price_tracking, ai_debate_sessions

🔗 External Dependencies:
    - sqlalchemy: DB 연결
    - pandas: 데이터 분석
    - tabulate: 테이블 출력

📤 Output:
    - 에이전트별 투표 통계
    - 합의 성과 통계
    - War Room 세션 통계
    - 실거래 준비 상태 판단

🔄 Called By:
    - Manual execution: python backend/scripts/check_data_readiness.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from backend.database.repository import get_sync_session
import pandas as pd
from datetime import datetime


def check_agent_votes():
    """
    에이전트별 투표 데이터 확인

    Data Source: PostgreSQL agent_vote_tracking table

    Returns:
        tuple: (DataFrame, ready_count) - 투표 통계, 준비된 에이전트 수
    """
    db = get_sync_session()

    try:
        query = text("""
            SELECT
                agent_name,
                COUNT(*) as total_votes,
                COUNT(*) FILTER (WHERE status = 'EVALUATED') as evaluated,
                ROUND(AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END)::numeric, 3) as accuracy,
                ROUND(AVG(vote_confidence)::numeric, 3) as avg_confidence
            FROM agent_vote_tracking
            WHERE status = 'EVALUATED'
            GROUP BY agent_name
            ORDER BY total_votes DESC
        """)

        result = db.execute(query).fetchall()

        if not result:
            print("\n⚠️ agent_vote_tracking 테이블에 데이터가 없습니다!")
            print("📝 War Room 토론을 실행하여 데이터를 생성하세요.")
            return None, 0

        df = pd.DataFrame(result, columns=['agent', 'total', 'evaluated', 'accuracy', 'avg_confidence'])

        print("\n" + "="*80)
        print("📊 에이전트별 투표 현황")
        print("="*80)
        print(df.to_string(index=False))

        ready_count = len(df[df['total'] >= 20])
        print(f"\n✅ 가중치 계산 가능 에이전트: {ready_count}/8")
        print(f"   (최소 20개 평가 완료 투표 필요)")

        if ready_count < 8:
            missing = 8 - ready_count
            print(f"\n⚠️ {missing}개 에이전트가 아직 데이터 부족")
            print(f"   권장: 1-2주 데이터 축적 후 재확인")

        return df, ready_count

    except Exception as e:
        print(f"\n❌ 에이전트 투표 확인 실패: {e}")
        import traceback
        traceback.print_exc()
        return None, 0
    finally:
        db.close()


def check_consensus_performance():
    """
    합의 성과 확인

    Data Source: PostgreSQL price_tracking table

    Returns:
        DataFrame: 합의 성과 통계
    """
    db = get_sync_session()

    try:
        query = text("""
            SELECT
                consensus_action,
                COUNT(*) as count,
                ROUND(AVG(return_pct)::numeric, 4) as avg_return,
                ROUND(AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END)::numeric, 3) as accuracy,
                ROUND(AVG(consensus_confidence)::numeric, 3) as avg_confidence
            FROM price_tracking
            WHERE status = 'EVALUATED'
            GROUP BY consensus_action
            ORDER BY count DESC
        """)

        result = db.execute(query).fetchall()

        if not result:
            print("\n⚠️ price_tracking 테이블에 평가 완료된 데이터가 없습니다!")
            print("📝 24시간 후 자동 평가를 기다리세요.")
            return None

        df = pd.DataFrame(result, columns=['action', 'count', 'avg_return', 'accuracy', 'avg_confidence'])

        print("\n" + "="*80)
        print("📈 합의 성과 통계")
        print("="*80)
        print(df.to_string(index=False))

        total_count = df['count'].sum()
        total_accuracy = (df['count'] * df['accuracy']).sum() / total_count if total_count > 0 else 0

        print(f"\n📊 전체 통계:")
        print(f"   총 평가: {total_count}개")
        print(f"   전체 정확도: {total_accuracy:.1%}")

        if total_count >= 50:
            print(f"\n✅ 충분한 합의 데이터 ({total_count}개 >= 50개)")
        else:
            print(f"\n⚠️ 합의 데이터 부족 ({total_count}개 < 50개)")

        return df

    except Exception as e:
        print(f"\n❌ 합의 성과 확인 실패: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()


def check_debate_sessions():
    """
    토론 세션 확인

    Data Source: PostgreSQL ai_debate_sessions table

    Returns:
        bool: 실거래 준비 상태
    """
    db = get_sync_session()

    try:
        # 전체 통계
        query = text("""
            SELECT
                COUNT(*) as total,
                COUNT(DISTINCT ticker) as tickers,
                ROUND(AVG(CASE WHEN constitutional_valid THEN 1.0 ELSE 0.0 END)::numeric, 3) as pass_rate,
                COUNT(*) FILTER (WHERE signal_id IS NOT NULL) as signals
            FROM ai_debate_sessions
        """)

        result = db.execute(query).fetchone()

        print("\n" + "="*80)
        print("🏛️ War Room 토론 통계")
        print("="*80)
        print(f"총 세션 수: {result[0]}")
        print(f"고유 종목 수: {result[1]}")
        print(f"Constitutional 통과율: {result[2]:.1%}")
        print(f"시그널 생성: {result[3]}")

        # 종목별 통계
        ticker_query = text("""
            SELECT
                ticker,
                COUNT(*) as count,
                ROUND(AVG(CASE WHEN constitutional_valid THEN 1.0 ELSE 0.0 END)::numeric, 3) as pass_rate
            FROM ai_debate_sessions
            GROUP BY ticker
            ORDER BY count DESC
            LIMIT 10
        """)

        ticker_result = db.execute(ticker_query).fetchall()

        if ticker_result:
            ticker_df = pd.DataFrame(ticker_result, columns=['ticker', 'sessions', 'pass_rate'])
            print("\n📋 종목별 세션 (Top 10):")
            print(ticker_df.to_string(index=False))

        # 최근 7일 활동
        recent_query = text("""
            SELECT
                DATE(created_at) as date,
                COUNT(*) as sessions
            FROM ai_debate_sessions
            WHERE created_at >= NOW() - INTERVAL '7 days'
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)

        recent_result = db.execute(recent_query).fetchall()

        if recent_result:
            recent_df = pd.DataFrame(recent_result, columns=['date', 'sessions'])
            print("\n📅 최근 7일 활동:")
            print(recent_df.to_string(index=False))

        # 실거래 준비 상태 판단
        ready = (
            result[0] >= 50 and  # 최소 50개 세션
            result[1] >= 5 and   # 최소 5개 종목
            result[2] >= 0.90    # 90% 이상 통과
        )

        print("\n" + "="*80)
        print("🎯 실거래 준비 상태 평가")
        print("="*80)

        # 조건별 체크
        conditions = [
            ("총 세션 >= 50개", result[0] >= 50, f"{result[0]}/50"),
            ("고유 종목 >= 5개", result[1] >= 5, f"{result[1]}/5"),
            ("Constitutional 통과율 >= 90%", result[2] >= 0.90, f"{result[2]:.1%}/90%"),
        ]

        for name, passed, value in conditions:
            status = "✅" if passed else "❌"
            print(f"{status} {name}: {value}")

        print("\n" + "="*80)
        if ready:
            print("✅ 모의 거래 테스트 준비 완료!")
            print("\n다음 단계:")
            print("  1. python backend/scripts/run_paper_trading.py")
            print("  2. 1주일 모의 거래 성과 모니터링")
            print("  3. 승률 >= 60% 확인 후 실거래 전환")
        else:
            print("⚠️ 데이터 축적 필요")
            print("\n다음 단계:")
            print("  1. War Room 자동 실행 스케줄러 설정")
            print("     python backend/automation/war_room_scheduler.py")
            print("  2. 24시간 자동 평가 시스템 가동")
            print("     python backend/automation/price_tracking_scheduler.py")
            print("  3. 1-2주 후 재확인")
        print("="*80)

        return ready

    except Exception as e:
        print(f"\n❌ 토론 세션 확인 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    """실거래 준비 상태 점검 메인 함수"""
    print("\n" + "="*80)
    print("🚀 AI Trading System - 실거래 준비 상태 점검")
    print("="*80)
    print(f"점검 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. 에이전트 투표 확인
    agent_df, ready_agents = check_agent_votes()

    # 2. 합의 성과 확인
    consensus_df = check_consensus_performance()

    # 3. 토론 세션 확인
    ready = check_debate_sessions()

    # 최종 요약
    print("\n" + "="*80)
    print("📋 최종 요약")
    print("="*80)

    if agent_df is not None:
        print(f"✅ 에이전트 투표 데이터: {len(agent_df)}개 에이전트")
        print(f"   가중치 계산 가능: {ready_agents}/8")
    else:
        print("❌ 에이전트 투표 데이터: 없음")

    if consensus_df is not None:
        total = consensus_df['count'].sum()
        print(f"✅ 합의 성과 데이터: {total}개 평가 완료")
    else:
        print("❌ 합의 성과 데이터: 없음")

    print(f"\n{'✅' if ready else '⚠️'} 전체 준비 상태: {'준비 완료' if ready else '데이터 축적 필요'}")

    if not ready:
        print("\n💡 권장 조치:")
        print("  1. War Room에서 다양한 종목 토론 (NVDA, GOOGL, AAPL, MSFT, TSLA)")
        print("  2. 매일 오전/오후 토론 실행 (스케줄러 활용)")
        print("  3. 24시간 후 자동 평가 대기")
        print("  4. 1-2주 후 재점검")

    print("="*80 + "\n")


if __name__ == "__main__":
    main()
