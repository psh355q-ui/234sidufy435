"""
Report Orchestrator Agent

AI 판단의 정확도를 측정하고, 리포트에 accountability 섹션을 생성하는 전문 Agent

Core Functions:
- calculate_news_interpretation_accuracy(): NIA 계산
- generate_weekly_accountability_section(): Weekly 리포트용 섹션
- generate_annual_accountability_report(): Annual 리포트용 섹션
- enhance_daily_report_with_accountability(): Daily 리포트 강화
"""

from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from backend.database.repository import (
    NewsInterpretationRepository,
    NewsMarketReactionRepository,
    NewsDecisionLinkRepository,
    NewsNarrativeRepository,
    FailureAnalysisRepository
)


class ReportOrchestrator:
    """Report Orchestrator Agent - AI 판단 책임 추적"""

    def __init__(self, db: Session):
        """
        Initialize Report Orchestrator

        Args:
            db: SQLAlchemy session
        """
        self.interpretation_repo = NewsInterpretationRepository(db)
        self.reaction_repo = NewsMarketReactionRepository(db)
        self.link_repo = NewsDecisionLinkRepository(db)
        self.narrative_repo = NewsNarrativeRepository(db)
        self.failure_repo = FailureAnalysisRepository(db)
        self.db = db

    def calculate_news_interpretation_accuracy(
        self, timeframe: str = "daily"
    ) -> Dict[str, Any]:
        """
        NIA (News Interpretation Accuracy) 계산

        Args:
            timeframe: "daily" | "weekly" | "annual"

        Returns:
            {
                "overall_accuracy": 0.75,
                "by_impact": {"HIGH": 0.85, "MEDIUM": 0.72, "LOW": 0.68},
                "by_type": {"EARNINGS": 0.85, "MACRO": 0.72, "GEOPOLITICS": 0.45},
                "best_call": {...},
                "worst_call": {...}
            }
        """
        # 1. Determine date range
        start_date, end_date = self._get_date_range(timeframe)

        # 2. Get verified interpretations
        interpretations = self.interpretation_repo.get_by_date_range(start_date, end_date)

        # 3. Filter only verified ones (with market reaction)
        verified_data = []
        for interp in interpretations:
            reaction = self.reaction_repo.get_by_interpretation_id(interp.id)
            if reaction and reaction.verified_at:
                verified_data.append({
                    "interpretation": interp,
                    "reaction": reaction
                })

        if not verified_data:
            return {
                "overall_accuracy": 0.0,
                "by_impact": {},
                "by_type": {},
                "best_call": None,
                "worst_call": None,
                "total_verified": 0
            }

        # 4. Calculate overall accuracy
        correct_count = sum(1 for item in verified_data if item["reaction"].interpretation_correct)
        overall_accuracy = correct_count / len(verified_data)

        # 5. Calculate by impact
        by_impact = self._calculate_by_impact(verified_data)

        # 6. Calculate by type (inferred from news context)
        by_type = self._calculate_by_type(verified_data)

        # 7. Find best and worst calls
        best_call = self._find_best_call(verified_data)
        worst_call = self._find_worst_call(verified_data)

        return {
            "overall_accuracy": round(overall_accuracy, 2),
            "by_impact": by_impact,
            "by_type": by_type,
            "best_call": best_call,
            "worst_call": worst_call,
            "total_verified": len(verified_data)
        }

    def generate_weekly_accountability_section(self) -> Dict[str, Any]:
        """
        Weekly Report용 AI 판단 진화 로그 생성

        Returns:
            {
                "nia_score": 75,
                "improvement": "+5%p",
                "best_judgment": {...},
                "worst_judgment": {...},
                "lesson_learned": "..."
            }
        """
        # 1. Calculate current week NIA
        current_week = self.calculate_news_interpretation_accuracy("weekly")
        nia_score = int(current_week["overall_accuracy"] * 100)

        # 2. Calculate previous week NIA for comparison
        prev_week_start = datetime.now() - timedelta(days=14)
        prev_week_end = datetime.now() - timedelta(days=7)
        prev_week_interps = self.interpretation_repo.get_by_date_range(prev_week_start, prev_week_end)

        prev_week_verified = []
        for interp in prev_week_interps:
            reaction = self.reaction_repo.get_by_interpretation_id(interp.id)
            if reaction and reaction.verified_at:
                prev_week_verified.append(reaction)

        if prev_week_verified:
            prev_correct = sum(1 for r in prev_week_verified if r.interpretation_correct)
            prev_nia = int((prev_correct / len(prev_week_verified)) * 100)
            improvement = f"+{nia_score - prev_nia}%p" if nia_score >= prev_nia else f"{nia_score - prev_nia}%p"
        else:
            improvement = "N/A"

        # 3. Format best/worst judgments
        best_judgment = self._format_judgment(current_week["best_call"]) if current_week["best_call"] else None
        worst_judgment = self._format_judgment(current_week["worst_call"]) if current_week["worst_call"] else None

        # 4. Extract lesson learned from worst judgment
        lesson_learned = self._extract_lesson(current_week["worst_call"]) if current_week["worst_call"] else "이번 주 실패 사례 없음"

        return {
            "nia_score": nia_score,
            "improvement": improvement,
            "best_judgment": best_judgment,
            "worst_judgment": worst_judgment,
            "lesson_learned": lesson_learned
        }

    def generate_annual_accountability_report(self) -> Dict[str, Any]:
        """
        Annual Report용 전체 accountability 리포트 생성

        Returns:
            {
                "nia_overall": 68,
                "by_type": {...},
                "top_3_failures": [...],
                "system_improvements": [...]
            }
        """
        # 1. Calculate annual NIA
        annual_nia = self.calculate_news_interpretation_accuracy("annual")
        nia_overall = int(annual_nia["overall_accuracy"] * 100)

        # 2. By type breakdown
        by_type = {k: int(v * 100) for k, v in annual_nia["by_type"].items()}

        # 3. Get top 3 failures
        year_start = datetime(datetime.now().year, 1, 1)
        year_end = datetime.now()
        failures = self.failure_repo.get_by_date_range(year_start, year_end)

        # Sort by severity and get top 3
        top_failures = sorted(failures, key=lambda f: self._severity_score(f.severity), reverse=True)[:3]
        top_3_failures = [
            {
                "description": f.root_cause,
                "lesson": f.lesson_learned,
                "fix": f.recommended_fix
            }
            for f in top_failures
        ]

        # 4. Get system improvements (failures that were fixed and effective)
        improvements = [
            {
                "date": f.updated_at.strftime("%Y-%m-%d") if f.updated_at else "N/A",
                "improvement": f.fix_description,
                "before_nia": "N/A",  # TODO: Calculate before/after from historical data
                "after_nia": "N/A"
            }
            for f in failures
            if f.fix_applied and f.fix_effective
        ]

        return {
            "nia_overall": nia_overall,
            "by_type": by_type,
            "top_3_failures": top_3_failures,
            "system_improvements": improvements
        }

    def enhance_daily_report_with_accountability(self, report_data: Dict) -> Dict:
        """
        Daily Report에 정확도 삽입

        Args:
            report_data: 기존 리포트 데이터

        Returns:
            정확도가 강화된 리포트 데이터
        """
        # Calculate today's NIA
        daily_nia = self.calculate_news_interpretation_accuracy("daily")
        accuracy_percentage = int(daily_nia["overall_accuracy"] * 100)

        # Enhance narratives if they exist
        if "narratives" in report_data:
            for narrative in report_data["narratives"]:
                if "interpretation_id" in narrative:
                    # Add accuracy to narrative text
                    narrative["text"] = f"{narrative['text']} (해석 정확도: {accuracy_percentage}%)"

        # Add overall accuracy section
        report_data["accountability"] = {
            "accuracy_percentage": accuracy_percentage,
            "total_verified": daily_nia["total_verified"]
        }

        return report_data

    # ========== Private Helper Methods ==========

    def _get_date_range(self, timeframe: str) -> tuple:
        """
        Get date range for timeframe

        Returns:
            (start_date, end_date)
        """
        now = datetime.now()

        if timeframe == "daily":
            start_date = datetime(now.year, now.month, now.day, 0, 0, 0)
            end_date = now
        elif timeframe == "weekly":
            start_date = now - timedelta(days=7)
            end_date = now
        elif timeframe == "annual":
            start_date = datetime(now.year, 1, 1, 0, 0, 0)
            end_date = now
        else:
            raise ValueError(f"Invalid timeframe: {timeframe}")

        return start_date, end_date

    def _calculate_by_impact(self, verified_data: List[Dict]) -> Dict[str, float]:
        """
        Calculate accuracy by expected impact

        Returns:
            {"HIGH": 0.85, "MEDIUM": 0.72, "LOW": 0.68}
        """
        by_impact = {}

        for impact_level in ["HIGH", "MEDIUM", "LOW"]:
            filtered = [
                item for item in verified_data
                if item["interpretation"].expected_impact == impact_level
            ]

            if filtered:
                correct = sum(1 for item in filtered if item["reaction"].interpretation_correct)
                by_impact[impact_level] = round(correct / len(filtered), 2)

        return by_impact

    def _calculate_by_type(self, verified_data: List[Dict]) -> Dict[str, float]:
        """
        Calculate accuracy by news type (EARNINGS, MACRO, GEOPOLITICS)

        Note: News type is inferred from reasoning or news content
        """
        by_type = {}

        for news_type in ["EARNINGS", "MACRO", "GEOPOLITICS"]:
            filtered = [
                item for item in verified_data
                if news_type.lower() in item["interpretation"].reasoning.lower()
            ]

            if filtered:
                correct = sum(1 for item in filtered if item["reaction"].interpretation_correct)
                by_type[news_type] = round(correct / len(filtered), 2)

        return by_type

    def _find_best_call(self, verified_data: List[Dict]) -> Optional[Dict]:
        """
        Find best call (correct + highest magnitude)
        """
        correct_calls = [
            item for item in verified_data
            if item["reaction"].interpretation_correct
        ]

        if not correct_calls:
            return None

        # Sort by actual price change magnitude
        best = max(correct_calls, key=lambda x: abs(x["reaction"].actual_price_change_1d or 0))

        return self._format_call(best)

    def _find_worst_call(self, verified_data: List[Dict]) -> Optional[Dict]:
        """
        Find worst call (incorrect + highest confidence)
        """
        incorrect_calls = [
            item for item in verified_data
            if not item["reaction"].interpretation_correct
        ]

        if not incorrect_calls:
            return None

        # Sort by confidence (high confidence but wrong = worst)
        worst = max(incorrect_calls, key=lambda x: x["interpretation"].confidence)

        return self._format_call(worst)

    def _format_call(self, item: Dict) -> Dict:
        """
        Format interpretation + reaction as call summary
        """
        interp = item["interpretation"]
        reaction = item["reaction"]

        return {
            "interpretation_id": interp.id,
            "ticker": interp.ticker,
            "headline": interp.news_article.headline if interp.news_article else "N/A",
            "bias": interp.headline_bias,
            "actual_change": round(reaction.actual_price_change_1d or 0, 2),
            "correct": reaction.interpretation_correct,
            "confidence": interp.confidence
        }

    def _format_judgment(self, call: Optional[Dict]) -> Optional[str]:
        """
        Format call as human-readable judgment
        """
        if not call:
            return None

        return (
            f"{call['ticker']} {call['headline']} → "
            f"{call['bias']} 예측 → "
            f"실제 {call['actual_change']:+.1f}% "
            f"(정확도: {100 if call['correct'] else 0}%)"
        )

    def _extract_lesson(self, call: Optional[Dict]) -> str:
        """
        Extract lesson learned from worst call
        """
        if not call:
            return "실패 사례 없음"

        # Get failure analysis if exists
        failures = self.failure_repo.get_by_interpretation_id(call["interpretation_id"])

        if failures:
            return failures[0].lesson_learned

        # Generic lesson based on bias mismatch
        if call["bias"] == "BULLISH" and call["actual_change"] < 0:
            return "상승 예측 실패 - 시장 역풍(headwind) 요인 재검토 필요"
        elif call["bias"] == "BEARISH" and call["actual_change"] > 0:
            return "하락 예측 실패 - 숏커버 또는 저점 매수세 고려 필요"
        else:
            return "방향성 예측 실패 - 뉴스 임팩트 과대평가 가능성"

    def _severity_score(self, severity: str) -> int:
        """
        Convert severity to numeric score for sorting
        """
        severity_map = {
            "CRITICAL": 3,
            "MAJOR": 2,
            "MINOR": 1
        }
        return severity_map.get(severity, 0)

    def _check_interpretation_accuracy(
        self, headline_bias: str, actual_price_change: float
    ) -> bool:
        """
        Check if interpretation was correct

        Args:
            headline_bias: "BULLISH" | "BEARISH" | "NEUTRAL"
            actual_price_change: 실제 가격 변화율 (%)

        Returns:
            bool: 정확 여부
        """
        if headline_bias == "BULLISH":
            return actual_price_change > 1.0
        elif headline_bias == "BEARISH":
            return actual_price_change < -1.0
        else:  # NEUTRAL
            return -1.0 <= actual_price_change <= 1.0


# ========== Standalone Usage ==========

if __name__ == "__main__":
    from backend.database.repository import get_sync_session

    with get_sync_session() as session:
        orchestrator = ReportOrchestrator(session)

        # Test NIA calculation
        print("="*60)
        print("📊 Testing NIA Calculation")
        print("="*60)

        daily_nia = orchestrator.calculate_news_interpretation_accuracy("daily")
        print(f"\nDaily NIA: {daily_nia['overall_accuracy'] * 100:.1f}%")
        print(f"Total Verified: {daily_nia['total_verified']}")
        print(f"By Impact: {daily_nia['by_impact']}")
        print(f"By Type: {daily_nia['by_type']}")

        if daily_nia["best_call"]:
            print(f"\n✅ Best Call: {daily_nia['best_call']['ticker']} - {daily_nia['best_call']['actual_change']:+.1f}%")

        if daily_nia["worst_call"]:
            print(f"\n❌ Worst Call: {daily_nia['worst_call']['ticker']} - {daily_nia['worst_call']['actual_change']:+.1f}%")

        # Test Weekly Section
        print("\n" + "="*60)
        print("📅 Testing Weekly Accountability Section")
        print("="*60)

        weekly = orchestrator.generate_weekly_accountability_section()
        print(f"\nNIA Score: {weekly['nia_score']}%")
        print(f"Improvement: {weekly['improvement']}")
        print(f"Best: {weekly['best_judgment']}")
        print(f"Worst: {weekly['worst_judgment']}")
        print(f"Lesson: {weekly['lesson_learned']}")

        print("\n" + "="*60)
