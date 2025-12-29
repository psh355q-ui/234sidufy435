"""
Macro Context Updater

매일 09:00 KST에 실행되어 거시 경제 상황 스냅샷을 생성합니다.

데이터 소스:
- VIX Index (Fear & Greed)
- S&P 500 Trend
- Fed Stance (recent FOMC minutes)
- News Sentiment
- Geopolitical Events

생성되는 데이터:
- macro_context_snapshots 테이블에 일별 snapshot 저장
"""

from datetime import datetime, date
from typing import Dict, Optional
import anthropic
import os

from backend.database.repository import MacroContextRepository, get_sync_session
from backend.database.models import MacroContextSnapshot


class MacroContextUpdater:
    """거시 경제 컨텍스트 일일 업데이트"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def update_daily_snapshot(self) -> MacroContextSnapshot:
        """
        매일 09:00 KST 실행

        Returns:
            MacroContextSnapshot: 생성된 스냅샷
        """
        print(f"[MacroContextUpdater] Starting daily update for {date.today()}")

        # 1. 시장 데이터 수집
        market_data = self._collect_market_data()

        # 2. AI 분석으로 dominant narrative 생성
        narrative = self._generate_dominant_narrative(market_data)

        # 3. 각 필드 결정
        snapshot_data = {
            "snapshot_date": date.today(),
            "regime": self._determine_regime(market_data),
            "fed_stance": self._analyze_fed_stance(market_data),
            "vix_level": market_data.get("vix_level", 15.0),
            "vix_category": self._categorize_vix(market_data.get("vix_level", 15.0)),
            "sector_rotation": self._detect_sector_rotation(market_data),
            "dominant_narrative": narrative,
            "geopolitical_risk": self._assess_geopolitical_risk(market_data),
            "earnings_season": self._is_earnings_season(),
            "market_sentiment": self._determine_market_sentiment(market_data),
            "sp500_trend": self._analyze_sp500_trend(market_data)
        }

        # 4. DB 저장
        with get_sync_session() as session:
            repo = MacroContextRepository(session)

            # 기존 오늘 날짜 스냅샷이 있으면 업데이트 (중복 방지)
            existing = repo.get_by_date(date.today())
            if existing:
                print(f"[MacroContextUpdater] Updating existing snapshot for {date.today()}")
                for key, value in snapshot_data.items():
                    if key != "snapshot_date":  # snapshot_date는 unique이므로 제외
                        setattr(existing, key, value)
                existing.updated_at = datetime.now()
                session.commit()
                session.refresh(existing)
                snapshot = existing
            else:
                print(f"[MacroContextUpdater] Creating new snapshot for {date.today()}")
                snapshot = repo.create(snapshot_data)

        print(f"[MacroContextUpdater] ✅ Snapshot saved: regime={snapshot.regime}, fed={snapshot.fed_stance}")
        return snapshot

    def _collect_market_data(self) -> Dict:
        """
        시장 데이터 수집

        실제 구현 시:
        - Yahoo Finance API (VIX, S&P 500)
        - FRED API (Fed rates)
        - NewsAPI (sentiment)

        현재는 Mock 데이터 반환
        """
        # TODO: 실제 API 연동
        return {
            "vix_level": 15.5,
            "sp500_change_1d": 0.5,
            "sp500_change_5d": 2.1,
            "sp500_change_20d": 5.3,
            "fed_rate": 5.25,
            "news_sentiment_avg": 0.3,  # -1 ~ +1
            "sector_performance": {
                "TECH": 1.2,
                "HEALTHCARE": -0.3,
                "FINANCE": 0.8,
                "ENERGY": -1.5
            },
            "geopolitical_events": [
                "Middle East tensions",
                "China-Taiwan relations"
            ]
        }

    def _generate_dominant_narrative(self, market_data: Dict) -> str:
        """
        Claude API로 dominant narrative 생성

        Args:
            market_data: 시장 데이터

        Returns:
            str: AI가 생성한 지배적 서사 (100-200자)
        """
        prompt = f"""
현재 시장 상황을 분석하여 지배적 서사(Dominant Narrative)를 한 문장으로 요약해주세요.

시장 데이터:
- VIX: {market_data.get('vix_level', 'N/A')}
- S&P 500 (1일): {market_data.get('sp500_change_1d', 'N/A')}%
- S&P 500 (5일): {market_data.get('sp500_change_5d', 'N/A')}%
- S&P 500 (20일): {market_data.get('sp500_change_20d', 'N/A')}%
- Fed Rate: {market_data.get('fed_rate', 'N/A')}%
- 뉴스 감성: {market_data.get('news_sentiment_avg', 'N/A')}
- 지정학적 이슈: {market_data.get('geopolitical_events', [])}

요구사항:
- 100-200자 이내
- 투자자 관점에서 서술
- 핵심 동인(driver) 명시

예시: "기술주 강세 속 Fed 매파 발언에도 불구하고 연말 랠리 기대감으로 시장 상승세 지속"
"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=200,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            narrative = message.content[0].text.strip()
            print(f"[MacroContextUpdater] Generated narrative: {narrative[:50]}...")
            return narrative

        except Exception as e:
            print(f"[MacroContextUpdater] ⚠️ Claude API error: {e}")
            # Fallback
            return "시장 데이터 기반 자동 생성 실패 - 수동 검토 필요"

    def _determine_regime(self, market_data: Dict) -> str:
        """
        시장 체제 결정

        Returns:
            'RISK_ON' | 'RISK_OFF' | 'TRANSITION' | 'UNKNOWN'
        """
        vix = market_data.get("vix_level", 15.0)
        sp500_trend = market_data.get("sp500_change_5d", 0)

        if vix < 15 and sp500_trend > 1:
            return "RISK_ON"
        elif vix > 25 and sp500_trend < -1:
            return "RISK_OFF"
        elif vix >= 15 and vix <= 25 and abs(sp500_trend) < 1:
            return "TRANSITION"
        else:
            return "UNKNOWN"

    def _analyze_fed_stance(self, market_data: Dict) -> str:
        """
        Fed 스탠스 분석

        실제 구현 시: FOMC minutes, Fed speeches 분석

        Returns:
            'HAWKISH' | 'DOVISH' | 'NEUTRAL'
        """
        # TODO: 실제 Fed 발언 분석
        fed_rate = market_data.get("fed_rate", 5.25)

        if fed_rate > 5.0:
            return "HAWKISH"
        elif fed_rate < 3.0:
            return "DOVISH"
        else:
            return "NEUTRAL"

    def _categorize_vix(self, vix_level: float) -> str:
        """
        VIX 범주화

        Returns:
            'LOW' | 'NORMAL' | 'ELEVATED' | 'HIGH' | 'EXTREME'
        """
        if vix_level < 12:
            return "LOW"
        elif vix_level < 20:
            return "NORMAL"
        elif vix_level < 30:
            return "ELEVATED"
        elif vix_level < 40:
            return "HIGH"
        else:
            return "EXTREME"

    def _detect_sector_rotation(self, market_data: Dict) -> Optional[str]:
        """
        섹터 로테이션 감지

        Returns:
            str: 로테이션 방향 (예: "TECH_TO_DEFENSIVE")
        """
        sector_perf = market_data.get("sector_performance", {})

        if not sector_perf:
            return None

        # 가장 강한 섹터와 가장 약한 섹터
        sorted_sectors = sorted(sector_perf.items(), key=lambda x: x[1], reverse=True)
        strongest = sorted_sectors[0][0]
        weakest = sorted_sectors[-1][0]

        return f"{weakest}_TO_{strongest}"

    def _assess_geopolitical_risk(self, market_data: Dict) -> str:
        """
        지정학적 리스크 평가

        Returns:
            'HIGH' | 'MEDIUM' | 'LOW'
        """
        events = market_data.get("geopolitical_events", [])

        # 고위험 키워드
        high_risk_keywords = ["war", "invasion", "nuclear", "embargo"]
        medium_risk_keywords = ["tensions", "sanctions", "dispute"]

        for event in events:
            event_lower = event.lower()
            if any(keyword in event_lower for keyword in high_risk_keywords):
                return "HIGH"

        for event in events:
            event_lower = event.lower()
            if any(keyword in event_lower for keyword in medium_risk_keywords):
                return "MEDIUM"

        return "LOW"

    def _is_earnings_season(self) -> bool:
        """
        실적 시즌 여부

        실적 시즌: 1월 중순~2월 중순, 4월 중순~5월 중순,
                  7월 중순~8월 중순, 10월 중순~11월 중순
        """
        today = date.today()
        month = today.month
        day = today.day

        earnings_months = [1, 2, 4, 5, 7, 8, 10, 11]

        if month in earnings_months:
            # 중순~말 (15일~월말)
            if month in [1, 4, 7, 10] and day >= 15:
                return True
            # 초순~중순 (1일~15일)
            if month in [2, 5, 8, 11] and day <= 15:
                return True

        return False

    def _determine_market_sentiment(self, market_data: Dict) -> str:
        """
        시장 센티먼트 결정

        Returns:
            'EXTREME_FEAR' | 'FEAR' | 'NEUTRAL' | 'GREED' | 'EXTREME_GREED'
        """
        vix = market_data.get("vix_level", 15.0)
        news_sentiment = market_data.get("news_sentiment_avg", 0)

        # VIX 기반 (역관계)
        if vix < 12:
            vix_sentiment = 2  # Greed
        elif vix < 20:
            vix_sentiment = 1
        elif vix < 30:
            vix_sentiment = 0
        elif vix < 40:
            vix_sentiment = -1
        else:
            vix_sentiment = -2  # Fear

        # 뉴스 감성 (-1 ~ +1)
        if news_sentiment > 0.5:
            news_sent_score = 2
        elif news_sentiment > 0.2:
            news_sent_score = 1
        elif news_sentiment > -0.2:
            news_sent_score = 0
        elif news_sentiment > -0.5:
            news_sent_score = -1
        else:
            news_sent_score = -2

        # 종합 점수
        total_score = (vix_sentiment + news_sent_score) / 2

        if total_score > 1.5:
            return "EXTREME_GREED"
        elif total_score > 0.5:
            return "GREED"
        elif total_score > -0.5:
            return "NEUTRAL"
        elif total_score > -1.5:
            return "FEAR"
        else:
            return "EXTREME_FEAR"

    def _analyze_sp500_trend(self, market_data: Dict) -> str:
        """
        S&P 500 트렌드 분석

        Returns:
            'STRONG_UPTREND' | 'UPTREND' | 'SIDEWAYS' | 'DOWNTREND' | 'STRONG_DOWNTREND'
        """
        change_20d = market_data.get("sp500_change_20d", 0)

        if change_20d > 5:
            return "STRONG_UPTREND"
        elif change_20d > 2:
            return "UPTREND"
        elif change_20d > -2:
            return "SIDEWAYS"
        elif change_20d > -5:
            return "DOWNTREND"
        else:
            return "STRONG_DOWNTREND"


# 스크립트 직접 실행 시
if __name__ == "__main__":
    updater = MacroContextUpdater()
    snapshot = updater.update_daily_snapshot()

    print("\n" + "="*60)
    print("✅ Macro Context Snapshot Created")
    print("="*60)
    print(f"Date: {snapshot.snapshot_date}")
    print(f"Regime: {snapshot.regime}")
    print(f"Fed Stance: {snapshot.fed_stance}")
    print(f"VIX: {snapshot.vix_level} ({snapshot.vix_category})")
    print(f"Market Sentiment: {snapshot.market_sentiment}")
    print(f"S&P 500 Trend: {snapshot.sp500_trend}")
    print(f"Geopolitical Risk: {snapshot.geopolitical_risk}")
    print(f"Earnings Season: {snapshot.earnings_season}")
    print(f"\nNarrative: {snapshot.dominant_narrative}")
    print("="*60)
