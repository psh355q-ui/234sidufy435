"""
tickers.py - 티커 자동완성 API

📊 Data Sources:
    - Static JSON File: backend/data/tickers.json
        - S&P 500 티커 목록
        - NASDAQ 100 티커 목록
        - Russell 2000 샘플
        - ETF 목록
        - 한글명 → 티커 매핑

🔗 External Dependencies:
    - fastapi: API 라우팅
    - json: JSON 파일 파싱
    - pathlib: 파일 경로 처리

📤 API Endpoints:
    - GET /api/tickers/autocomplete: 전체 티커 데이터
        Response: {version, tickers: {sp500[], nasdaq100[], etf[], korean_names{}}}
    - GET /api/tickers/version: 데이터 버전 정보

🔄 Called By:
    - frontend/src/components/TickerSearch.tsx
    - frontend/src/pages/Dashboard.tsx (search bar)

📝 Notes:
    - 데이터는 정적 JSON 파일 (업데이트 필요 시 수동)
    - 버전 형식: YYYY.MM.DD
    - 캐싱 전략: 프론트엔드에서 localStorage 사용 권장
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import json
import os
from pathlib import Path

router = APIRouter(prefix="/api/tickers", tags=["tickers"])

# Path to tickers JSON file
TICKERS_FILE = Path(__file__).parent.parent / "data" / "tickers.json"


@router.get("/autocomplete")
async def get_autocomplete_tickers():
    """
    Get ticker autocomplete data with version control
    
    Returns:
        - version: Data version (YYYY.MM.DD format)
        - last_updated: ISO timestamp
        - tickers: Dictionary containing ticker arrays and Korean name mappings
    """
    try:
        # Load ticker data from JSON file
        with open(TICKERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Add server timestamp
        data["server_time"] = datetime.utcnow().isoformat() + "Z"
        
        return data
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail=f"Ticker data file not found: {TICKERS_FILE}"
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON in ticker data file: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading ticker data: {str(e)}"
        )


@router.get("/version")
async def get_ticker_version():
    """
    Get current ticker data version (lightweight check)
    
    Returns:
        - version: Current data version
        - last_updated: Last update timestamp
    """
    try:
        with open(TICKERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return {
            "version": data.get("version"),
            "last_updated": data.get("last_updated"),
            "server_time": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading version: {str(e)}"
        )
