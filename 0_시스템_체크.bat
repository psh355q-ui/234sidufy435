@echo off
chcp 65001 >nul
title AI Trading System - 시스템 체크

echo ================================================================================
echo 🔍 AI Trading System - 시스템 환경 체크
echo ================================================================================
echo.

cd /d "D:\code\ai-trading-system"

echo 📁 작업 디렉토리: %CD%
echo.

echo ================================================================================
echo [1/5] Python 확인
echo ================================================================================
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않거나 PATH에 없습니다.
    echo.
) else (
    python --version
    echo ✅ Python 정상
)
echo.

echo ================================================================================
echo [2/5] PostgreSQL 확인
echo ================================================================================
psql --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  로컬 PostgreSQL이 PATH에 없습니다 (Docker 사용 중일 수 있음)
) else (
    psql --version
    echo ✅ PostgreSQL 정상
)
echo.

echo ================================================================================
echo [3/5] Docker 확인
echo ================================================================================
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker가 설치되어 있지 않습니다
) else (
    docker --version

    :: Docker 컨테이너 확인
    docker ps --format "{{.Names}}" | findstr postgres >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  PostgreSQL Docker 컨테이너가 실행 중이 아닙니다
        echo     시작 명령: docker start ai-trading-postgres
    ) else (
        echo ✅ Docker PostgreSQL 컨테이너 실행 중
    )
)
echo.

echo ================================================================================
echo [4/5] 필수 파일 확인
echo ================================================================================

set ALL_OK=1

if not exist "scripts\start_data_accumulation.py" (
    echo ❌ scripts\start_data_accumulation.py 없음
    set ALL_OK=0
) else (
    echo ✅ scripts\start_data_accumulation.py
)

if not exist "scripts\monitor_accumulation.py" (
    echo ❌ scripts\monitor_accumulation.py 없음
    set ALL_OK=0
) else (
    echo ✅ scripts\monitor_accumulation.py
)

if not exist "backend\orchestration\data_accumulation_orchestrator.py" (
    echo ❌ backend\orchestration\data_accumulation_orchestrator.py 없음
    set ALL_OK=0
) else (
    echo ✅ backend\orchestration\data_accumulation_orchestrator.py
)

if not exist "backend\database\migrations\add_constitutional_validation_tables.sql" (
    echo ❌ backend\database\migrations\add_constitutional_validation_tables.sql 없음
    set ALL_OK=0
) else (
    echo ✅ backend\database\migrations\add_constitutional_validation_tables.sql
)
echo.

echo ================================================================================
echo [5/5] Python 패키지 확인
echo ================================================================================
python -c "import sqlalchemy; print('✅ sqlalchemy:', sqlalchemy.__version__)" 2>nul || echo ❌ sqlalchemy 미설치
python -c "import aiohttp; print('✅ aiohttp:', aiohttp.__version__)" 2>nul || echo ❌ aiohttp 미설치
python -c "import bs4; print('✅ beautifulsoup4:', bs4.__version__)" 2>nul || echo ❌ beautifulsoup4 미설치
python -c "import feedparser; print('✅ feedparser:', feedparser.__version__)" 2>nul || echo ❌ feedparser 미설치
echo.

echo ================================================================================
echo 요약
echo ================================================================================
if %ALL_OK%==1 (
    echo.
    echo ✅ 모든 필수 파일이 존재합니다.
    echo.
    echo 💡 다음 단계:
    echo    1. "1_DB_마이그레이션.bat" - 데이터베이스 테이블 생성 (최초 1회)
    echo    2. "2_데이터수집_테스트.bat" - 5분 테스트
    echo    3. "3_데이터수집_시작.bat" - 실제 데이터 수집 시작
    echo.
) else (
    echo.
    echo ❌ 일부 파일이 없습니다. 프로젝트 구조를 확인하세요.
    echo.
)

pause
