"""
Emergency Status API Router

Provides real-time emergency detection based on Constitution rules
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.repository import get_sync_session
from backend.constitution.constitution import Constitution
from datetime import datetime, timedelta
import logging

router = APIRouter(prefix="/emergency", tags=["Emergency Detection"])
logger = logging.getLogger(__name__)


def get_db():
    """Database session dependency"""
    db = get_sync_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/status")
async def get_emergency_status(db: Session = Depends(get_db)):
    """
    Check if emergency conditions are active (Constitution-based)
    
    Returns emergency status and Grounding search recommendation
    """
    try:
        constitution = Constitution()
        
        # TODO: Get real portfolio data
        # For now, use placeholder values
        daily_loss = 0.0  # -0.02 = -2%
        total_drawdown = 0.0  # -0.08 = -8%
        vix = 18.0  # Current VIX
        
        # Check Constitution circuit breaker
        should_trigger, reason = constitution.validate_circuit_breaker_trigger(
            daily_loss=daily_loss,
            total_drawdown=total_drawdown,
            vix=vix
        )
        
        # Get Grounding usage today
        today_count = await get_grounding_count_today(db)
        
        # Determine severity
        severity = "normal"
        if should_trigger:
            if abs(daily_loss) >= 0.05:  # 5%+ loss
                severity = "critical"
            elif vix >= 35:
                severity = "high"
            else:
                severity = "medium"
        
        return {
            "is_emergency": should_trigger,
            "severity": severity,
            "triggers": [reason] if should_trigger else [],
            "recommend_grounding": should_trigger and today_count < 1,
            "grounding_searches_today": today_count,
            "daily_limit": 10,
            "message": reason if should_trigger else "Market conditions normal",
            "last_checked": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking emergency status: {e}")
        return {
            "is_emergency": False,
            "severity": "normal",
            "triggers": [],
            "recommend_grounding": False,
            "grounding_searches_today": 0,
            "daily_limit": 10,
            "error": str(e)
        }


async def get_grounding_count_today(db: Session) -> int:
    """Get number of Grounding searches made today"""
    try:
        # TODO: Query actual grounding_search_log table
        # For now, return 0
        return 0
    except Exception:
        return 0


@router.post("/grounding/track")
async def track_grounding_search(
    ticker: str,
    results_count: int = 0,
    db: Session = Depends(get_db)
):
    """
    Track a Grounding API search for cost monitoring
    
    Args:
        ticker: Stock ticker searched
        results_count: Number of results returned
    """
    try:
        # TODO: Save to grounding_search_log table
        cost = 0.035  # $0.035 per search
        
        logger.info(f"Grounding search tracked: {ticker}, cost=${cost}")
        
        return {
            "success": True,
            "ticker": ticker,
            "cost_usd": cost,
            "results_count": results_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error tracking Grounding search: {e}")
        return {"success": False, "error": str(e)}
