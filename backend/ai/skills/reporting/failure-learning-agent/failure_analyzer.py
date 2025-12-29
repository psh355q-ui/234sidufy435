"""
Failure Learning Agent

틀린 AI 판단을 자동으로 분석하고, 근본 원인을 찾아내어 시스템 개선을 제안하는 Agent

Core Functions:
- analyze_failure(): 특정 해석의 실패 분석
- batch_analyze_failures(): 기간 내 모든 실패 일괄 분석
- get_top_recurring_failures(): 반복적 실패 패턴 조회
- track_fix_effectiveness(): 수정 효과 추적
- suggest_system_improvements(): 시스템 개선 제안
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import anthropic

from backend.database.repository import (
    NewsInterpretationRepository,
    NewsMarketReactionRepository,
    FailureAnalysisRepository,
    MacroContextRepository
)
from backend.database.models import NewsInterpretation, NewsMarketReaction, FailureAnalysis

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FailureAnalyzer:
    """Failure Learning Agent - AI 실패 학습 시스템"""

    # Failure type definitions
    FAILURE_TYPES = [
        "DIRECTION_MISMATCH",
        "MAGNITUDE_ERROR",
        "OVERCONFIDENCE",
        "CONTEXT_MISREAD",
        "SENTIMENT_FLIP",
        "PRICED_IN",
        "DELAYED_REACTION"
    ]

    # Severity levels
    SEVERITY_LEVELS = ["CRITICAL", "MAJOR", "MINOR"]

    def __init__(self, db: Session):
        """
        Initialize Failure Analyzer

        Args:
            db: SQLAlchemy session
        """
        self.db = db
        self.interpretation_repo = NewsInterpretationRepository(db)
        self.reaction_repo = NewsMarketReactionRepository(db)
        self.failure_repo = FailureAnalysisRepository(db)
        self.macro_repo = MacroContextRepository(db)

        # Claude client for RCA
        self.claude_client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    def analyze_failure(
        self, interpretation_id: int, trigger: str = "DAILY_NIA_LOW"
    ) -> Dict[str, Any]:
        """
        특정 해석의 실패 분석

        Args:
            interpretation_id: 분석할 해석 ID
            trigger: "DAILY_NIA_LOW" | "OVERCONFIDENCE" | "MANUAL"

        Returns:
            {
                "failure_id": 123,
                "failure_type": "DIRECTION_MISMATCH",
                "severity": "MAJOR",
                "root_cause": "...",
                "lesson_learned": "...",
                "recommended_fix": "...",
                "similar_failures": [45, 67, 89],
                "pattern_detected": True
            }
        """
        logger.info(f"🔍 Analyzing failure for interpretation {interpretation_id} (trigger: {trigger})")

        # 1. Get interpretation and reaction
        interpretation = self.interpretation_repo.get_by_id(interpretation_id)
        if not interpretation:
            raise ValueError(f"Interpretation {interpretation_id} not found")

        reaction = self.reaction_repo.get_by_interpretation_id(interpretation_id)
        if not reaction or not reaction.verified_at:
            raise ValueError(f"Reaction for interpretation {interpretation_id} not verified yet")

        if reaction.interpretation_correct:
            logger.warning(f"⚠️ Interpretation {interpretation_id} was actually correct, skipping analysis")
            return {"error": "Interpretation was correct"}

        # 2. Collect context
        context = self._collect_context(interpretation, reaction)

        # 3. Classify failure type
        failure_type = self._classify_failure_type(interpretation, reaction)

        # 4. Find similar failures
        similar_failures = self._find_similar_failures(interpretation, failure_type)

        # 5. Determine severity
        severity = self._determine_severity(interpretation, reaction, similar_failures)

        # 6. Run RCA with Claude
        rca_result = self._run_claude_rca(interpretation, reaction, context, similar_failures)

        # 7. Save to database
        failure_data = {
            "interpretation_id": interpretation_id,
            "decision_link_id": None,  # TODO: Link if exists
            "ticker": interpretation.ticker,
            "failure_type": failure_type,
            "severity": severity,
            "expected_outcome": f"{interpretation.headline_bias} {interpretation.expected_impact}",
            "actual_outcome": f"{reaction.actual_price_change_1d:+.2f}%",
            "root_cause": rca_result["root_cause"],
            "lesson_learned": rca_result["lesson_learned"],
            "recommended_fix": rca_result["recommended_fix"],
            "fix_applied": False,
            "rag_context_updated": False,
            "analyzed_by": "FailureAnalyzer",
            "analyzed_at": datetime.now()
        }

        failure = self.failure_repo.create(failure_data)

        logger.info(
            f"✅ Failure analysis complete: {failure_type} ({severity})\n"
            f"   Root cause: {rca_result['root_cause'][:100]}..."
        )

        return {
            "failure_id": failure.id,
            "failure_type": failure_type,
            "severity": severity,
            "root_cause": rca_result["root_cause"],
            "lesson_learned": rca_result["lesson_learned"],
            "recommended_fix": rca_result["recommended_fix"],
            "similar_failures": [f.id for f in similar_failures],
            "pattern_detected": len(similar_failures) >= 3,
            "fix_type": rca_result.get("fix_type", "UNKNOWN"),
            "confidence": rca_result.get("confidence", 80)
        }

    def batch_analyze_failures(
        self, start_date: datetime, end_date: datetime, min_severity: str = "MAJOR"
    ) -> Dict[str, Any]:
        """
        기간 내 모든 실패 일괄 분석

        Args:
            start_date, end_date: 분석 기간
            min_severity: 최소 심각도 ("CRITICAL" | "MAJOR" | "MINOR")

        Returns:
            {
                "total_analyzed": 25,
                "by_type": {...},
                "critical_patterns": [...]
            }
        """
        logger.info(f"📊 Batch analyzing failures from {start_date} to {end_date}")

        # Get all interpretations in date range
        interpretations = self.interpretation_repo.get_by_date_range(start_date, end_date)

        analyzed_count = 0
        by_type = {}
        patterns = []

        for interpretation in interpretations:
            reaction = self.reaction_repo.get_by_interpretation_id(interpretation.id)

            # Skip if not verified or was correct
            if not reaction or not reaction.verified_at or reaction.interpretation_correct:
                continue

            # Check if already analyzed
            existing = self.failure_repo.get_by_interpretation_id(interpretation.id)
            if existing:
                continue

            # Analyze
            try:
                result = self.analyze_failure(interpretation.id, trigger="BATCH")

                # Count by type
                by_type[result["failure_type"]] = by_type.get(result["failure_type"], 0) + 1

                # Track patterns
                if result["pattern_detected"]:
                    patterns.append({
                        "failure_id": result["failure_id"],
                        "type": result["failure_type"],
                        "occurrences": len(result["similar_failures"]) + 1
                    })

                analyzed_count += 1

            except Exception as e:
                logger.error(f"❌ Failed to analyze interpretation {interpretation.id}: {e}")

        logger.info(f"✅ Batch analysis complete: {analyzed_count} failures analyzed")

        return {
            "total_analyzed": analyzed_count,
            "by_type": by_type,
            "critical_patterns": patterns
        }

    def get_top_recurring_failures(self, limit: int = 10) -> List[Dict]:
        """
        반복적 실패 패턴 조회

        Returns:
            [
                {
                    "pattern": "Geopolitical risk overestimation",
                    "count": 12,
                    "avg_nia_impact": -8.5,
                    "fix_applied": True,
                    "fix_effective": True,
                    "nia_improvement": 16.0
                },
                ...
            ]
        """
        logger.info(f"🔍 Getting top {limit} recurring failure patterns")

        # Group by failure_type and root_cause
        failures = self.failure_repo.get_by_date_range(
            datetime.now() - timedelta(days=365),
            datetime.now()
        )

        # Count patterns
        pattern_counts = {}

        for failure in failures:
            key = f"{failure.failure_type}_{failure.root_cause[:50]}"

            if key not in pattern_counts:
                pattern_counts[key] = {
                    "pattern": failure.root_cause,
                    "type": failure.failure_type,
                    "count": 0,
                    "failures": [],
                    "fix_applied": False,
                    "fix_effective": None
                }

            pattern_counts[key]["count"] += 1
            pattern_counts[key]["failures"].append(failure)

            if failure.fix_applied:
                pattern_counts[key]["fix_applied"] = True
                pattern_counts[key]["fix_effective"] = failure.fix_effective

        # Sort by count
        sorted_patterns = sorted(
            pattern_counts.values(),
            key=lambda x: x["count"],
            reverse=True
        )

        return sorted_patterns[:limit]

    def track_fix_effectiveness(
        self, failure_id: int, before_nia: float, after_nia: float
    ) -> bool:
        """
        수정 효과 추적

        Args:
            failure_id: 실패 분석 ID
            before_nia: 수정 전 NIA
            after_nia: 수정 후 NIA

        Returns:
            bool: Fix가 효과적이었는지 (NIA 개선 3%p 이상)
        """
        logger.info(f"📈 Tracking fix effectiveness for failure {failure_id}")

        failure = self.failure_repo.get_by_id(failure_id)
        if not failure:
            raise ValueError(f"Failure {failure_id} not found")

        improvement = after_nia - before_nia
        effective = improvement >= 3.0  # 3%p 이상 개선

        # Update failure record
        self.failure_repo.mark_fix_effective(failure, effective)

        logger.info(
            f"{'✅' if effective else '❌'} Fix effectiveness: "
            f"{before_nia:.1f}% → {after_nia:.1f}% ({improvement:+.1f}%p)"
        )

        return effective

    def suggest_system_improvements(self) -> Dict[str, Any]:
        """
        Annual Report용 시스템 개선 제안 종합

        Returns:
            {
                "completed_improvements": [...],
                "pending_improvements": [...],
                "rejected_improvements": [...]
            }
        """
        logger.info("📋 Suggesting system improvements")

        # Get all failures from this year
        year_start = datetime(datetime.now().year, 1, 1)
        failures = self.failure_repo.get_by_date_range(year_start, datetime.now())

        completed = []
        pending = []
        rejected = []

        for failure in failures:
            if failure.fix_applied and failure.fix_effective is not None:
                if failure.fix_effective:
                    completed.append({
                        "date": failure.updated_at.strftime("%Y-%m-%d") if failure.updated_at else "N/A",
                        "improvement": failure.fix_description or failure.recommended_fix,
                        "impact": "Positive"  # TODO: Calculate actual NIA impact
                    })
                else:
                    rejected.append({
                        "improvement": failure.fix_description or failure.recommended_fix,
                        "reason": "테스트 결과 NIA 개선 없음"
                    })
            elif not failure.fix_applied and failure.severity in ["CRITICAL", "MAJOR"]:
                pending.append({
                    "priority": failure.severity,
                    "improvement": failure.recommended_fix,
                    "justification": failure.root_cause,
                    "failure_count": 1  # TODO: Count similar failures
                })

        return {
            "completed_improvements": completed[:10],
            "pending_improvements": sorted(pending, key=lambda x: x["priority"], reverse=True)[:10],
            "rejected_improvements": rejected[:5]
        }

    # ========== Private Helper Methods ==========

    def _collect_context(
        self, interpretation: NewsInterpretation, reaction: NewsMarketReaction
    ) -> Dict:
        """Collect full context for RCA"""

        macro_context = interpretation.macro_context

        return {
            "ticker": interpretation.ticker,
            "headline": interpretation.news_article.headline if interpretation.news_article else "N/A",
            "content": interpretation.news_article.content if interpretation.news_article else "N/A",
            "headline_bias": interpretation.headline_bias,
            "expected_impact": interpretation.expected_impact,
            "time_horizon": interpretation.time_horizon,
            "confidence": interpretation.confidence,
            "reasoning": interpretation.reasoning,
            "price_at_news": reaction.price_at_news,
            "actual_change_1h": reaction.actual_price_change_1h,
            "actual_change_1d": reaction.actual_price_change_1d,
            "actual_change_3d": reaction.actual_price_change_3d,
            "macro_context": {
                "regime": macro_context.regime if macro_context else "N/A",
                "fed_stance": macro_context.fed_stance if macro_context else "N/A",
                "vix_level": macro_context.vix_level if macro_context else "N/A",
                "vix_category": macro_context.vix_category if macro_context else "N/A",
                "market_sentiment": macro_context.market_sentiment if macro_context else "N/A",
                "dominant_narrative": macro_context.dominant_narrative if macro_context else "N/A"
            }
        }

    def _classify_failure_type(
        self, interpretation: NewsInterpretation, reaction: NewsMarketReaction
    ) -> str:
        """Classify failure type based on patterns"""

        bias = interpretation.headline_bias
        actual_change = reaction.actual_price_change_1d or 0

        # Direction mismatch
        if bias == "BULLISH" and actual_change < -1.0:
            return "DIRECTION_MISMATCH"
        if bias == "BEARISH" and actual_change > 1.0:
            return "DIRECTION_MISMATCH"

        # Magnitude error
        if interpretation.expected_impact == "HIGH" and abs(actual_change) < 2.0:
            return "MAGNITUDE_ERROR"
        if interpretation.expected_impact == "LOW" and abs(actual_change) > 5.0:
            return "MAGNITUDE_ERROR"

        # Overconfidence
        if interpretation.confidence >= 80 and not reaction.interpretation_correct:
            return "OVERCONFIDENCE"

        # Sentiment flip (1h vs 1d)
        if reaction.actual_price_change_1h and reaction.actual_price_change_1d:
            if abs(reaction.actual_price_change_1h) > 1 and abs(reaction.actual_price_change_1d) > 1:
                if (reaction.actual_price_change_1h > 0) != (reaction.actual_price_change_1d > 0):
                    return "SENTIMENT_FLIP"

        return "DIRECTION_MISMATCH"  # Default

    def _find_similar_failures(
        self, interpretation: NewsInterpretation, failure_type: str
    ) -> List[FailureAnalysis]:
        """Find similar past failures"""

        # Get failures of same type for same ticker
        failures = self.failure_repo.get_by_ticker(interpretation.ticker, limit=50)

        similar = [
            f for f in failures
            if f.failure_type == failure_type
        ]

        return similar[:10]

    def _determine_severity(
        self,
        interpretation: NewsInterpretation,
        reaction: NewsMarketReaction,
        similar_failures: List[FailureAnalysis]
    ) -> str:
        """Determine severity based on impact and pattern"""

        # Pattern check (recurring failure)
        if len(similar_failures) >= 3:
            return "CRITICAL"

        # High impact prediction but failed
        if interpretation.expected_impact == "HIGH" and abs(reaction.actual_price_change_1d or 0) < 2.0:
            return "CRITICAL"

        # Overconfidence
        if interpretation.confidence >= 80:
            return "MAJOR"

        # Large actual movement
        if abs(reaction.actual_price_change_1d or 0) >= 5.0:
            return "MAJOR"

        return "MINOR"

    def _run_claude_rca(
        self,
        interpretation: NewsInterpretation,
        reaction: NewsMarketReaction,
        context: Dict,
        similar_failures: List[FailureAnalysis]
    ) -> Dict:
        """Run Root Cause Analysis with Claude API"""

        # Build similar failures summary
        similar_summary = ""
        if similar_failures:
            similar_summary = "\n".join([
                f"- {f.root_cause[:100]}" for f in similar_failures[:3]
            ])
        else:
            similar_summary = "없음 (처음 발생한 실패)"

        prompt = f"""당신은 AI 트레이딩 시스템의 실패 분석 전문가입니다.

아래 AI 해석이 틀렸습니다. 근본 원인을 분석해주세요.

## 해석 정보
- 종목: {context['ticker']}
- 뉴스 헤드라인: {context['headline']}
- AI 예측: {context['headline_bias']} (confidence: {context['confidence']}%)
- 예상 임팩트: {context['expected_impact']}
- Time horizon: {context['time_horizon']}
- AI 추론: {context['reasoning']}

## 거시 경제 컨텍스트 (해석 당시)
- Market regime: {context['macro_context']['regime']}
- Fed stance: {context['macro_context']['fed_stance']}
- VIX: {context['macro_context']['vix_level']} ({context['macro_context']['vix_category']})
- Market sentiment: {context['macro_context']['market_sentiment']}
- Dominant narrative: {context['macro_context']['dominant_narrative']}

## 실제 시장 반응
- 뉴스 발표 시점 가격: ${context['price_at_news']}
- 1시간 후: {context['actual_change_1h'] or 'N/A'}%
- 1일 후: {context['actual_change_1d'] or 'N/A'}%
- 3일 후: {context['actual_change_3d'] or 'N/A'}%

## 유사 과거 실패 사례
{similar_summary}

## 요청사항
다음 JSON 형식으로 응답해주세요:
{{
    "root_cause": "근본 원인 (1-2문장, 구체적으로)",
    "lesson_learned": "배운 교훈 (actionable, 다음부터 X를 Y로 변경)",
    "recommended_fix": "시스템 개선 제안 (구체적 구현 방법)",
    "fix_type": "PROMPT_UPDATE|CONTEXT_ADDITION|RAG_UPDATE|NEW_FEATURE",
    "pattern_type": "SYSTEMATIC|ONE_OFF",
    "confidence": 70
}}

분석 시 고려사항:
1. AI가 놓친 시장 맥락은 무엇인가?
2. 뉴스가 이미 priced-in 되었을 가능성은?
3. Sentiment flip (반대 방향 움직임)의 원인은?
4. Macro context와 뉴스 해석의 정합성은?
5. 과거 유사 실패와의 패턴은?
"""

        try:
            message = self.claude_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text.strip()

            # Parse JSON
            # Try to extract JSON from markdown code block if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            rca_result = json.loads(response_text)

            logger.info(f"✅ Claude RCA complete: {rca_result['root_cause'][:100]}...")

            return rca_result

        except Exception as e:
            logger.error(f"❌ Claude RCA failed: {e}", exc_info=True)

            # Fallback to simple analysis
            return {
                "root_cause": f"AI 예측 {context['headline_bias']} vs 실제 {context['actual_change_1d']:+.2f}% (분석 실패)",
                "lesson_learned": "Claude API 오류로 상세 분석 실패. 수동 검토 필요",
                "recommended_fix": "N/A",
                "fix_type": "UNKNOWN",
                "pattern_type": "ONE_OFF",
                "confidence": 50
            }


# ========== Standalone Usage ==========

if __name__ == "__main__":
    from backend.database.repository import get_sync_session

    with get_sync_session() as session:
        analyzer = FailureAnalyzer(session)

        print("="*60)
        print("🧪 Testing Failure Analyzer")
        print("="*60)

        # Example: Analyze a specific failure
        # analyzer.analyze_failure(interpretation_id=123, trigger="MANUAL")

        # Example: Get recurring patterns
        patterns = analyzer.get_top_recurring_failures(limit=5)
        print(f"\n📊 Top Recurring Failure Patterns: {len(patterns)}")

        for i, pattern in enumerate(patterns, 1):
            print(f"\n{i}. {pattern['type']} (count: {pattern['count']})")
            print(f"   Pattern: {pattern['pattern'][:100]}...")

        print("\n" + "="*60)
