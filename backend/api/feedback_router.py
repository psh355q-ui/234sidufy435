from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import logging

# Ensure models are imported
from backend.database.models import UserFeedback
from backend.database.repository import get_sync_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["feedback"])

class FeedbackCreate(BaseModel):
    target_type: str  # 'report', 'signal', 'briefing'
    target_id: str
    feedback_type: str  # 'like', 'dislike'
    comment: Optional[str] = None

@router.post("/", status_code=201)
def create_feedback(
    feedback: FeedbackCreate
):
    """
    유저 피드백 저장
    """
    try:
        with get_sync_session() as db:
            new_feedback = UserFeedback(
                target_type=feedback.target_type,
                target_id=feedback.target_id,
                feedback_type=feedback.feedback_type,
                comment=feedback.comment
            )
            db.add(new_feedback)
            db.commit()
            db.refresh(new_feedback)
            
            logger.info(f"Feedback received: {feedback.target_type}/{feedback.target_id} -> {feedback.feedback_type}")
            return {"status": "success", "id": new_feedback.id}
        
    except Exception as e:
        logger.error(f"Failed to save feedback: {e}")
        # rollback handled by session context manager or engine usually, but manual safety:
        # db.rollback() # scoped_session handles context
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")

@router.get("/stats")
def get_feedback_stats():
    """
    간단한 피드백 통계 (Admin용)
    """
    try:
        with get_sync_session() as db:
            from sqlalchemy import func
            
            # Total
            total = db.query(func.count(UserFeedback.id)).scalar() or 0
            
            # Likes
            likes = db.query(func.count(UserFeedback.id)).filter(UserFeedback.feedback_type == 'like').scalar() or 0
            
            return {
                "total_feedback": total,
                "likes": likes,
                "dislikes": total - likes
            }
    except Exception as e:
        logger.error(f"Failed to fetch stats: {e}")
        return {"error": str(e)}

@router.get("/")
def get_feedbacks(limit: int = 20):
    """
    최신 피드백 조회
    """
    try:
        with get_sync_session() as db:
            from sqlalchemy import desc
            feedbacks = db.query(UserFeedback).order_by(desc(UserFeedback.created_at)).limit(limit).all()
            return feedbacks
    except Exception as e:
        logger.error(f"Failed to fetch feedbacks: {e}")
        raise HTTPException(status_code=500, detail=str(e))
