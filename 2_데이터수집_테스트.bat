@echo off
chcp 65001 >nul
title AI Trading System - 데이터 수집 테스트 (5분)

echo ================================================================================
echo 🧪 AI Trading System - 데이터 수집 테스트 모드
echo ================================================================================
echo.

:: 작업 디렉토리로 이동
cd /d "D:\code\ai-trading-system"

echo [1/3] 작업 디렉토리 확인...
echo 현재 위치: %CD%
echo.

:: logs 디렉토리 생성
if not exist "logs" (
    echo [2/3] logs 디렉토리 생성...
    mkdir logs
) else (
    echo [2/3] logs 디렉토리 확인 완료
)
echo.

:: Python 및 스크립트 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    pause
    exit /b 1
)

echo [3/3] Python 버전 확인 완료
python --version
echo.

echo ================================================================================
echo 🧪 테스트 모드 실행 (약 5분)
echo ================================================================================
echo.

python scripts\start_data_accumulation.py --test

if errorlevel 1 (
    echo.
    echo ❌ 테스트 실패 - "6_로그_확인.bat"으로 에러 확인
    pause
    exit /b 1
)

echo.
echo ✅ 테스트 완료! "3_데이터수집_시작.bat"를 실행하세요.
echo.
pause
