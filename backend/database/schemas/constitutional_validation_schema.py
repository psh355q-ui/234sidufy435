"""
Constitutional Validation Database Schema

Tracks all constitutional validation results for War Room debates

Tables:
- constitutional_validations: Main validation records
- constitutional_violations: Specific violation details

Author: ai-trading-system
Date: 2025-12-27
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.database.models import Base


class ConstitutionalValidation(Base):
    """
    Constitutional validation record

    Each War Room debate generates one validation record
    """
    __tablename__ = "constitutional_validations"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Debate reference
    debate_id = Column(String(100), nullable=True, index=True)  # Optional debate tracking ID
    article_id = Column(Integer, ForeignKey("news_articles.id"), nullable=True, index=True)

    # Signal details
    ticker = Column(String(20), nullable=False, index=True)
    action = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Float, nullable=False)

    # Validation result
    is_constitutional = Column(Boolean, nullable=False, index=True)
    validation_timestamp = Column(DateTime, nullable=False, default=datetime.now, index=True)

    # Violation summary
    violation_count = Column(Integer, default=0)
    violation_severity = Column(String(20), nullable=True)  # CRITICAL, HIGH, MODERATE, LOW, NONE

    # Market context (simplified)
    market_regime = Column(String(20), nullable=True)  # RISK_ON, RISK_OFF, NEUTRAL
    portfolio_state = Column(JSON, nullable=True)  # Snapshot of portfolio at validation time

    # Metadata
    debate_duration_ms = Column(Float, nullable=True)
    model_votes = Column(JSON, nullable=True)  # {"claude": "BUY", "gemini": "SELL", ...}

    # Relationships
    violations = relationship("ConstitutionalViolation", back_populates="validation", cascade="all, delete-orphan")
    article = relationship("NewsArticle", backref="constitutional_validations")

    def __repr__(self):
        status = "✅ PASS" if self.is_constitutional else "❌ FAIL"
        return f"<ConstitutionalValidation({self.ticker} {self.action} {self.confidence:.0%} {status})>"


class ConstitutionalViolation(Base):
    """
    Specific constitutional violation

    Each validation can have multiple violations
    """
    __tablename__ = "constitutional_violations"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Parent validation
    validation_id = Column(Integer, ForeignKey("constitutional_validations.id"), nullable=False, index=True)

    # Violation details
    article_number = Column(String(20), nullable=False, index=True)  # e.g., "Article 1.1"
    article_title = Column(String(200), nullable=False)
    violation_type = Column(String(50), nullable=False, index=True)  # e.g., "position_size_exceeded"
    severity = Column(String(20), nullable=False)  # CRITICAL, HIGH, MODERATE, LOW

    # Violation specifics
    description = Column(Text, nullable=False)
    expected_value = Column(String(100), nullable=True)
    actual_value = Column(String(100), nullable=True)

    # Remediation (if auto-fixed)
    was_auto_fixed = Column(Boolean, default=False)
    fix_description = Column(Text, nullable=True)

    # Timestamp
    detected_at = Column(DateTime, nullable=False, default=datetime.now)

    # Relationship
    validation = relationship("ConstitutionalValidation", back_populates="violations")

    def __repr__(self):
        return f"<ConstitutionalViolation({self.article_number} {self.violation_type} {self.severity})>"


# Migration SQL (for reference)
CREATE_TABLES_SQL = """
-- Constitutional validations table
CREATE TABLE IF NOT EXISTS constitutional_validations (
    id SERIAL PRIMARY KEY,
    debate_id VARCHAR(100),
    article_id INTEGER REFERENCES news_articles(id),
    ticker VARCHAR(20) NOT NULL,
    action VARCHAR(10) NOT NULL,
    confidence FLOAT NOT NULL,
    is_constitutional BOOLEAN NOT NULL,
    validation_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    violation_count INTEGER DEFAULT 0,
    violation_severity VARCHAR(20),
    market_regime VARCHAR(20),
    portfolio_state JSONB,
    debate_duration_ms FLOAT,
    model_votes JSONB
);

CREATE INDEX idx_const_val_ticker ON constitutional_validations(ticker);
CREATE INDEX idx_const_val_is_constitutional ON constitutional_validations(is_constitutional);
CREATE INDEX idx_const_val_timestamp ON constitutional_validations(validation_timestamp);
CREATE INDEX idx_const_val_debate_id ON constitutional_validations(debate_id);

-- Constitutional violations table
CREATE TABLE IF NOT EXISTS constitutional_violations (
    id SERIAL PRIMARY KEY,
    validation_id INTEGER NOT NULL REFERENCES constitutional_validations(id) ON DELETE CASCADE,
    article_number VARCHAR(20) NOT NULL,
    article_title VARCHAR(200) NOT NULL,
    violation_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    expected_value VARCHAR(100),
    actual_value VARCHAR(100),
    was_auto_fixed BOOLEAN DEFAULT FALSE,
    fix_description TEXT,
    detected_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_const_vio_validation_id ON constitutional_violations(validation_id);
CREATE INDEX idx_const_vio_article_number ON constitutional_violations(article_number);
CREATE INDEX idx_const_vio_type ON constitutional_violations(violation_type);
"""


# =============================================================================
# Repository
# =============================================================================

class ConstitutionalValidationRepository:
    """Repository for constitutional validation data"""

    def __init__(self, session):
        self.session = session

    def create_validation(
        self,
        ticker: str,
        action: str,
        confidence: float,
        is_constitutional: bool,
        violations: list = None,
        debate_id: str = None,
        article_id: int = None,
        market_regime: str = None,
        portfolio_state: dict = None,
        debate_duration_ms: float = None,
        model_votes: dict = None
    ) -> ConstitutionalValidation:
        """
        Create validation record

        Args:
            ticker: Stock ticker
            action: BUY, SELL, HOLD
            confidence: Confidence score (0.0-1.0)
            is_constitutional: Pass/fail
            violations: List of violation dicts
            debate_id: Optional debate tracking ID
            article_id: Optional news article ID
            market_regime: Market regime at time of validation
            portfolio_state: Portfolio snapshot
            debate_duration_ms: Debate duration
            model_votes: AI model votes

        Returns:
            ConstitutionalValidation object
        """
        # Determine severity
        violation_severity = "NONE"
        if violations:
            severities = [v.get("severity", "LOW") for v in violations]
            if "CRITICAL" in severities:
                violation_severity = "CRITICAL"
            elif "HIGH" in severities:
                violation_severity = "HIGH"
            elif "MODERATE" in severities:
                violation_severity = "MODERATE"
            else:
                violation_severity = "LOW"

        # Create validation
        validation = ConstitutionalValidation(
            debate_id=debate_id,
            article_id=article_id,
            ticker=ticker,
            action=action,
            confidence=confidence,
            is_constitutional=is_constitutional,
            violation_count=len(violations) if violations else 0,
            violation_severity=violation_severity,
            market_regime=market_regime,
            portfolio_state=portfolio_state,
            debate_duration_ms=debate_duration_ms,
            model_votes=model_votes
        )

        self.session.add(validation)
        self.session.flush()  # Get ID

        # Create violation records
        if violations:
            for vio in violations:
                violation = ConstitutionalViolation(
                    validation_id=validation.id,
                    article_number=vio.get("article_number", "Unknown"),
                    article_title=vio.get("article_title", "Unknown Article"),
                    violation_type=vio.get("violation_type", "unknown"),
                    severity=vio.get("severity", "LOW"),
                    description=vio.get("description", ""),
                    expected_value=vio.get("expected_value"),
                    actual_value=vio.get("actual_value"),
                    was_auto_fixed=vio.get("was_auto_fixed", False),
                    fix_description=vio.get("fix_description")
                )
                self.session.add(violation)

        self.session.commit()
        return validation

    def get_validation_by_id(self, validation_id: int) -> ConstitutionalValidation:
        """Get validation by ID"""
        return self.session.query(ConstitutionalValidation).filter_by(id=validation_id).first()

    def get_recent_validations(self, limit: int = 100) -> list:
        """Get recent validations"""
        return (
            self.session.query(ConstitutionalValidation)
            .order_by(ConstitutionalValidation.validation_timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_validations_by_ticker(self, ticker: str, limit: int = 50) -> list:
        """Get validations for specific ticker"""
        return (
            self.session.query(ConstitutionalValidation)
            .filter_by(ticker=ticker)
            .order_by(ConstitutionalValidation.validation_timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_violation_stats(self, days: int = 7) -> dict:
        """
        Get violation statistics

        Args:
            days: Number of days to analyze

        Returns:
            Stats dict
        """
        from sqlalchemy import func

        cutoff = datetime.now() - timedelta(days=days)

        # Total validations
        total = (
            self.session.query(func.count(ConstitutionalValidation.id))
            .filter(ConstitutionalValidation.validation_timestamp >= cutoff)
            .scalar()
        )

        # Failed validations
        failed = (
            self.session.query(func.count(ConstitutionalValidation.id))
            .filter(
                ConstitutionalValidation.validation_timestamp >= cutoff,
                ConstitutionalValidation.is_constitutional == False
            )
            .scalar()
        )

        # Violation counts by type
        violation_counts = (
            self.session.query(
                ConstitutionalViolation.violation_type,
                func.count(ConstitutionalViolation.id)
            )
            .join(ConstitutionalValidation)
            .filter(ConstitutionalValidation.validation_timestamp >= cutoff)
            .group_by(ConstitutionalViolation.violation_type)
            .all()
        )

        return {
            "period_days": days,
            "total_validations": total,
            "failed_validations": failed,
            "pass_rate": f"{((total - failed) / total * 100):.1f}%" if total > 0 else "N/A",
            "violation_types": dict(violation_counts)
        }
