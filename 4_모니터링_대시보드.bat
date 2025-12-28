@echo off
chcp 65001 >nul
title AI Trading System - 실시간 모니터링

echo ================================================================================
echo 📊 AI Trading System - 실시간 모니터링 대시보드
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
echo 대시보드 시작
echo ================================================================================
echo.
echo 화면 갱신 간격: 5초
echo 종료하려면 Ctrl+C를 누르세요
echo.
echo ⚠️  참고: "데이터수집_시작.bat"가 실행 중이어야 데이터를 볼 수 있습니다.
echo.
echo ================================================================================
echo.

:: 모니터링 대시보드 실행
python scripts/monitor_accumulation.py --refresh 5

pause
