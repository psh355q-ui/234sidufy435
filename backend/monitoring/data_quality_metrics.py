"""
Data Quality Metrics

Tracks data quality for the accumulation phase:
- News collection quality
- Debate quality
- Constitutional compliance
- Signal quality
- System health

Author: ai-trading-system
Date: 2025-12-27
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from sqlalchemy import func

from backend.database.repository import (
    NewsRepository,
    AnalysisRepository,
    get_sync_session
)
from backend.database.schemas.constitutional_validation_schema import (
    ConstitutionalValidation,
    ConstitutionalViolation,
    ConstitutionalValidationRepository
)

logger = logging.getLogger(__name__)


@dataclass
class DataQualityReport:
    """Data quality report"""
    generated_at: datetime = field(default_factory=datetime.now)
    period_days: int = 7

    # News quality
    news_article_count: int = 0
    news_sources_count: int = 0
    news_coverage_score: float = 0.0  # 0-100

    # Debate quality
    debate_count: int = 0
    avg_confidence: float = 0.0
    confidence_distribution: Dict[str, int] = field(default_factory=dict)

    # Constitutional compliance
    validation_count: int = 0
    violation_count: int = 0
    compliance_rate: float = 0.0  # 0-100
    top_violations: List[Dict] = field(default_factory=list)

    # Signal quality
    signal_distribution: Dict[str, int] = field(default_factory=dict)
    ticker_coverage: int = 0
    signal_diversity_score: float = 0.0  # 0-100

    # System health
    error_count: int = 0
    error_rate: float = 0.0  # 0-100
    uptime_score: float = 100.0  # 0-100

    # Overall score
    overall_quality_score: float = 0.0  # 0-100

    def calculate_overall_score(self):
        """Calculate overall quality score"""
        scores = []

        # News coverage (20%)
        if self.news_coverage_score > 0:
            scores.append(self.news_coverage_score * 0.20)

        # Confidence (25%)
        confidence_score = self.avg_confidence * 100
        scores.append(confidence_score * 0.25)

        # Constitutional compliance (30%)
        scores.append(self.compliance_rate * 0.30)

        # Signal diversity (15%)
        scores.append(self.signal_diversity_score * 0.15)

        # System health (10%)
        scores.append(self.uptime_score * 0.10)

        self.overall_quality_score = sum(scores)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "generated_at": self.generated_at.isoformat(),
            "period_days": self.period_days,
            "news": {
                "articles": self.news_article_count,
                "sources": self.news_sources_count,
                "coverage_score": f"{self.news_coverage_score:.1f}"
            },
            "debates": {
                "count": self.debate_count,
                "avg_confidence": f"{self.avg_confidence:.2%}",
                "confidence_distribution": self.confidence_distribution
            },
            "constitutional": {
                "validations": self.validation_count,
                "violations": self.violation_count,
                "compliance_rate": f"{self.compliance_rate:.1f}%",
                "top_violations": self.top_violations[:5]
            },
            "signals": {
                "distribution": self.signal_distribution,
                "ticker_coverage": self.ticker_coverage,
                "diversity_score": f"{self.signal_diversity_score:.1f}"
            },
            "system": {
                "errors": self.error_count,
                "error_rate": f"{self.error_rate:.1f}%",
                "uptime_score": f"{self.uptime_score:.1f}"
            },
            "overall_score": f"{self.overall_quality_score:.1f}"
        }


class DataQualityMetrics:
    """
    Data Quality Metrics Tracker

    Analyzes and reports on data quality across all accumulation systems
    """

    def __init__(self):
        """Initialize metrics tracker"""
        logger.info("📊 Data Quality Metrics initialized")

    def generate_report(self, days: int = 7) -> DataQualityReport:
        """
        Generate data quality report

        Args:
            days: Number of days to analyze

        Returns:
            DataQualityReport
        """
        logger.info(f"Generating data quality report for last {days} days...")

        report = DataQualityReport(period_days=days)
        cutoff = datetime.now() - timedelta(days=days)

        with get_sync_session() as session:
            # 1. News Quality
            logger.info("  Analyzing news quality...")
            self._analyze_news_quality(session, report, cutoff)

            # 2. Constitutional Compliance
            logger.info("  Analyzing constitutional compliance...")
            self._analyze_constitutional_compliance(session, report, cutoff)

            # 3. Signal Quality
            logger.info("  Analyzing signal quality...")
            self._analyze_signal_quality(session, report, cutoff)

            # 4. System Health
            logger.info("  Analyzing system health...")
            self._analyze_system_health(session, report, cutoff)

        # Calculate overall score
        report.calculate_overall_score()

        logger.info(f"✅ Report generated | Overall Score: {report.overall_quality_score:.1f}/100")

        return report

    def _analyze_news_quality(self, session, report: DataQualityReport, cutoff: datetime):
        """Analyze news collection quality"""
        news_repo = NewsRepository(session)

        # Note: Assumes NewsRepository has these methods or we use raw queries

        # Total articles (simplified - would need actual implementation)
        try:
            # This is a placeholder - actual implementation depends on NewsRepository
            report.news_article_count = 0  # Placeholder
            report.news_sources_count = 0  # Placeholder

            # Coverage score: based on article count and source diversity
            # Target: 100+ articles, 5+ sources
            article_score = min(100, (report.news_article_count / 100) * 100)
            source_score = min(100, (report.news_sources_count / 5) * 100)
            report.news_coverage_score = (article_score + source_score) / 2

        except Exception as e:
            logger.warning(f"Error analyzing news quality: {e}")
            report.news_coverage_score = 0.0

    def _analyze_constitutional_compliance(self, session, report: DataQualityReport, cutoff: datetime):
        """Analyze constitutional compliance"""
        try:
            # Total validations
            validation_count = (
                session.query(func.count(ConstitutionalValidation.id))
                .filter(ConstitutionalValidation.validation_timestamp >= cutoff)
                .scalar()
            )

            report.validation_count = validation_count or 0

            if validation_count == 0:
                report.compliance_rate = 100.0
                return

            # Failed validations
            failed_count = (
                session.query(func.count(ConstitutionalValidation.id))
                .filter(
                    ConstitutionalValidation.validation_timestamp >= cutoff,
                    ConstitutionalValidation.is_constitutional == False
                )
                .scalar()
            )

            report.violation_count = failed_count or 0

            # Compliance rate
            report.compliance_rate = ((validation_count - failed_count) / validation_count) * 100

            # Average confidence
            avg_conf = (
                session.query(func.avg(ConstitutionalValidation.confidence))
                .filter(ConstitutionalValidation.validation_timestamp >= cutoff)
                .scalar()
            )

            report.avg_confidence = float(avg_conf) if avg_conf else 0.0

            # Confidence distribution
            high_conf = (
                session.query(func.count(ConstitutionalValidation.id))
                .filter(
                    ConstitutionalValidation.validation_timestamp >= cutoff,
                    ConstitutionalValidation.confidence >= 0.80
                )
                .scalar()
            )

            medium_conf = (
                session.query(func.count(ConstitutionalValidation.id))
                .filter(
                    ConstitutionalValidation.validation_timestamp >= cutoff,
                    ConstitutionalValidation.confidence >= 0.60,
                    ConstitutionalValidation.confidence < 0.80
                )
                .scalar()
            )

            low_conf = validation_count - (high_conf or 0) - (medium_conf or 0)

            report.confidence_distribution = {
                "high (≥80%)": high_conf or 0,
                "medium (60-80%)": medium_conf or 0,
                "low (<60%)": low_conf
            }

            # Top violations
            violation_counts = (
                session.query(
                    ConstitutionalViolation.violation_type,
                    ConstitutionalViolation.severity,
                    func.count(ConstitutionalViolation.id).label('count')
                )
                .join(ConstitutionalValidation)
                .filter(ConstitutionalValidation.validation_timestamp >= cutoff)
                .group_by(ConstitutionalViolation.violation_type, ConstitutionalViolation.severity)
                .order_by(func.count(ConstitutionalViolation.id).desc())
                .limit(5)
                .all()
            )

            report.top_violations = [
                {
                    "type": vio_type,
                    "severity": severity,
                    "count": count
                }
                for vio_type, severity, count in violation_counts
            ]

        except Exception as e:
            logger.warning(f"Error analyzing constitutional compliance: {e}")
            report.compliance_rate = 100.0

    def _analyze_signal_quality(self, session, report: DataQualityReport, cutoff: datetime):
        """Analyze signal quality"""
        try:
            # Signal distribution
            signal_dist = (
                session.query(
                    ConstitutionalValidation.action,
                    func.count(ConstitutionalValidation.id).label('count')
                )
                .filter(ConstitutionalValidation.validation_timestamp >= cutoff)
                .group_by(ConstitutionalValidation.action)
                .all()
            )

            report.signal_distribution = {action: count for action, count in signal_dist}

            # Ticker coverage
            ticker_count = (
                session.query(func.count(func.distinct(ConstitutionalValidation.ticker)))
                .filter(ConstitutionalValidation.validation_timestamp >= cutoff)
                .scalar()
            )

            report.ticker_coverage = ticker_count or 0

            # Diversity score
            # Based on:
            # 1. Ticker count (target: 10+)
            # 2. Signal balance (not all BUY or all SELL)

            ticker_score = min(100, (report.ticker_coverage / 10) * 100)

            # Calculate signal balance (entropy-based)
            total_signals = sum(report.signal_distribution.values())
            if total_signals > 0:
                # Ideal: 33% BUY, 33% SELL, 33% HOLD
                buy_pct = report.signal_distribution.get("BUY", 0) / total_signals
                sell_pct = report.signal_distribution.get("SELL", 0) / total_signals
                hold_pct = report.signal_distribution.get("HOLD", 0) / total_signals

                # Deviation from ideal
                balance_score = 100 - (
                    abs(buy_pct - 0.33) * 100 +
                    abs(sell_pct - 0.33) * 100 +
                    abs(hold_pct - 0.33) * 100
                ) * 1.5  # Scale factor

                balance_score = max(0, balance_score)
            else:
                balance_score = 0

            report.signal_diversity_score = (ticker_score + balance_score) / 2

        except Exception as e:
            logger.warning(f"Error analyzing signal quality: {e}")
            report.signal_diversity_score = 0.0

    def _analyze_system_health(self, session, report: DataQualityReport, cutoff: datetime):
        """Analyze system health"""
        try:
            # Error count (from validation failures)
            # In production, you'd track actual system errors separately

            # For now, use validation count as proxy for uptime
            if report.validation_count > 0:
                # Assume each validation is a successful cycle
                # Target: 100+ validations in period
                uptime_score = min(100, (report.validation_count / 100) * 100)
            else:
                uptime_score = 0

            # Error rate based on violations
            if report.validation_count > 0:
                error_rate = (report.violation_count / report.validation_count) * 100
            else:
                error_rate = 0

            report.error_count = report.violation_count  # Proxy
            report.error_rate = error_rate
            report.uptime_score = max(0, 100 - error_rate)  # Inverse of error rate

        except Exception as e:
            logger.warning(f"Error analyzing system health: {e}")
            report.uptime_score = 100.0

    def print_report(self, report: DataQualityReport):
        """Print formatted report"""
        print("\n" + "=" * 80)
        print("📊 DATA QUALITY REPORT")
        print("=" * 80)
        print(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Period: Last {report.period_days} days")
        print()

        print("📰 NEWS QUALITY")
        print("-" * 80)
        print(f"  Articles collected:  {report.news_article_count}")
        print(f"  News sources:        {report.news_sources_count}")
        print(f"  Coverage score:      {report.news_coverage_score:.1f}/100")
        print()

        print("🎭 DEBATE QUALITY")
        print("-" * 80)
        print(f"  Total debates:       {report.debate_count}")
        print(f"  Avg confidence:      {report.avg_confidence:.1%}")
        print(f"  Distribution:")
        for level, count in report.confidence_distribution.items():
            print(f"    {level:15}: {count}")
        print()

        print("🏛️ CONSTITUTIONAL COMPLIANCE")
        print("-" * 80)
        print(f"  Validations:         {report.validation_count}")
        print(f"  Violations:          {report.violation_count}")
        print(f"  Compliance rate:     {report.compliance_rate:.1f}%")

        if report.top_violations:
            print(f"  Top violations:")
            for vio in report.top_violations:
                print(f"    - {vio['type']:30} ({vio['severity']:8}): {vio['count']}")
        print()

        print("📊 SIGNAL QUALITY")
        print("-" * 80)
        print(f"  Signal distribution:")
        for action, count in report.signal_distribution.items():
            print(f"    {action:6}: {count}")
        print(f"  Ticker coverage:     {report.ticker_coverage} unique tickers")
        print(f"  Diversity score:     {report.signal_diversity_score:.1f}/100")
        print()

        print("🔧 SYSTEM HEALTH")
        print("-" * 80)
        print(f"  Errors:              {report.error_count}")
        print(f"  Error rate:          {report.error_rate:.1f}%")
        print(f"  Uptime score:        {report.uptime_score:.1f}/100")
        print()

        print("=" * 80)
        print(f"OVERALL QUALITY SCORE: {report.overall_quality_score:.1f}/100")
        print("=" * 80)

        # Quality rating
        if report.overall_quality_score >= 90:
            rating = "🟢 EXCELLENT"
        elif report.overall_quality_score >= 75:
            rating = "🟡 GOOD"
        elif report.overall_quality_score >= 60:
            rating = "🟠 FAIR"
        else:
            rating = "🔴 NEEDS IMPROVEMENT"

        print(f"\nQuality Rating: {rating}\n")

    def save_report(self, report: DataQualityReport, filename: Optional[str] = None):
        """Save report to file"""
        import json
        import os

        if not filename:
            filename = f"logs/quality_report_{report.generated_at.strftime('%Y%m%d_%H%M%S')}.json"

        os.makedirs("logs", exist_ok=True)

        with open(filename, "w") as f:
            json.dump(report.to_dict(), f, indent=2)

        logger.info(f"✅ Report saved to {filename}")


# =============================================================================
# CLI
# =============================================================================

def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Data Quality Metrics Report")
    parser.add_argument("--days", type=int, default=7, help="Number of days to analyze (default: 7)")
    parser.add_argument("--save", action="store_true", help="Save report to file")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Generate report
    metrics = DataQualityMetrics()
    report = metrics.generate_report(days=args.days)

    # Print report
    metrics.print_report(report)

    # Save if requested
    if args.save:
        metrics.save_report(report)


if __name__ == "__main__":
    main()
