"""
Daily Briefing Router
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, Dict
from datetime import date

from backend.services.daily_briefing_service import DailyBriefingService
from backend.ai.skills.common.logging_decorator import log_endpoint

router = APIRouter(prefix="/api/briefing", tags=["Daily Briefing"])

# Singleton service
_service = None

def get_service():
    global _service
    if _service is None:
        _service = DailyBriefingService()
    return _service

@router.get("/latest")
@log_endpoint("briefing", "read")
async def get_latest_briefing():
    """Get the latest daily briefing"""
    service = get_service()
    briefing = await service.get_latest_briefing()
    
    if not briefing:
        # If none exists, try generating one for today?
        # Or return 404
        return {"content": "No briefing available yet. generating...", "date": str(date.today())}
    
    return {
        "id": briefing.id,
        "date": briefing.date,
        "content": briefing.content,
        "metrics": briefing.metrics,
        "updated_at": briefing.updated_at
    }

@router.post("/generate")
@log_endpoint("briefing", "generate")
async def generate_briefing(background_tasks: BackgroundTasks):
    """Trigger generation of daily briefing"""
    service = get_service()
    
    # Run in background to avoid timeout
    # But for MVP testing, wait? 
    # Let's await it for immediate feedback in this version
    result = await service.generate_briefing()
    return result
