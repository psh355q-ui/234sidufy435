@echo off
chcp 65001 >nul
title AI Trading System - 데이터 수집 시스템

echo ================================================================================
echo 🎯 AI Trading System - 데이터 수집 시스템
echo ================================================================================
echo.

:: 작업 디렉토리로 이동
cd /d "D:\code\ai-trading-system"

echo [1/4] 작업 디렉토리 확인...
echo 현재 위치: %CD%
echo.

:: logs 디렉토리 생성
if not exist "logs" (
    echo [2/4] logs 디렉토리 생성...
    mkdir logs
) else (
    echo [2/4] logs 디렉토리 확인 완료
)
echo.

:: Python 실행 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 오류: Python이 설치되어 있지 않거나 PATH에 등록되지 않았습니다.
    echo.
    echo 💡 해결 방법:
    echo    1. Python 3.11 이상 설치
    echo    2. 환경변수 PATH에 Python 추가
    echo    3. 또는 절대 경로로 실행: C:\Python311\python.exe
    echo.
    pause
    exit /b 1
)

echo [3/4] Python 버전 확인 완료
python --version
echo.

:: 스크립트 파일 존재 확인
if not exist "scripts\start_data_accumulation.py" (
    echo ❌ 오류: 데이터 수집 스크립트를 찾을 수 없습니다.
    echo 경로: scripts\start_data_accumulation.py
    echo.
    pause
    exit /b 1
)

echo [4/4] 스크립트 파일 확인 완료
echo.

echo ================================================================================
echo 🚀 데이터 수집 시작
echo ================================================================================
echo.
echo 실행 모드: 연속 수집 (14일, 100개 토론 목표)
echo 뉴스 체크 간격: 5분
echo.
echo ⚠️  중요 안내:
echo    1. 이 창을 닫지 마세요 (최소화는 가능합니다)
echo    2. 매일 백엔드 켤 때마다 실행하세요
echo    3. 중단하려면 Ctrl+C를 누르세요
echo    4. 목표 달성 시 자동으로 종료됩니다
echo.
echo 시작 시간: %date% %time%
echo ================================================================================
echo.

:: 데이터 수집 실행
python scripts\start_data_accumulation.py --days 14 --debates 100

:: 종료 코드 확인
if errorlevel 1 (
    echo.
    echo ❌ 오류 발생
    echo.
    echo 💡 문제 해결:
    echo    1. "6_로그_확인.bat"으로 에러 로그 확인
    echo    2. PostgreSQL/Docker가 실행 중인지 확인
    echo    3. 인터넷 연결 확인
    echo    4. Gemini API 키 확인 (.env 파일)
    echo.
) else (
    echo.
    echo ================================================================================
    echo ✅ 데이터 수집 정상 종료
    echo 종료 시간: %date% %time%
    echo ================================================================================
    echo.
)

:: 종료 전 로그 위치 안내
echo 📁 생성된 파일:
echo    - logs\data_accumulation.log
echo    - logs\constitutional_validations.jsonl
echo    - logs\accumulation_stats_*.json
echo.
echo 💡 다음 단계:
echo    - "4_모니터링_대시보드.bat"로 진행 상황 확인
echo    - "5_품질리포트_생성.bat"로 품질 분석
echo.

pause
