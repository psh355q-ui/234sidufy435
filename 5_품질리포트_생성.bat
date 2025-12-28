@echo off
chcp 65001 >nul
title AI Trading System - 품질 리포트 생성

echo ================================================================================
echo 📊 AI Trading System - 품질 리포트 생성
echo ================================================================================
echo.

:: 작업 디렉토리로 이동
cd /d "D:\code\ai-trading-system"

echo 작업 디렉토리: %CD%
echo.

:: Python 실행 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 오류: Python이 설치되어 있지 않거나 PATH에 등록되지 않았습니다.
    echo.
    pause
    exit /b 1
)

echo Python 버전:
python --version
echo.

echo ================================================================================
echo 품질 리포트 생성 중...
echo ================================================================================
echo.
echo 분석 기간: 최근 7일
echo.

:: 품질 리포트 생성
python backend/monitoring/data_quality_metrics.py --days 7 --save

echo.
echo ================================================================================
echo 완료
echo ================================================================================
echo.
echo 📁 리포트 저장 위치: logs\quality_report_*.json
echo.

pause
