@echo off
chcp 65001 >nul
title AI Trading System - 데이터베이스 마이그레이션

echo ================================================================================
echo 🗄️  AI Trading System - 데이터베이스 마이그레이션
echo ================================================================================
echo.

:: 작업 디렉토리로 이동
cd /d "D:\code\ai-trading-system"

echo 작업 디렉토리: %CD%
echo.

echo ⚠️  주의: Constitutional Validation 테이블을 생성합니다.
echo.
echo 필요한 테이블:
echo   - constitutional_validations
echo   - constitutional_violations
echo.

echo ================================================================================
echo 마이그레이션 실행
echo ================================================================================
echo.

:: 마이그레이션 파일 존재 확인
if not exist "backend\database\migrations\add_constitutional_validation_tables.sql" (
    echo ❌ 마이그레이션 파일을 찾을 수 없습니다.
    echo 경로: backend\database\migrations\add_constitutional_validation_tables.sql
    echo.
    pause
    exit /b 1
)

echo [방법 1] 로컬 PostgreSQL 시도...
echo.

:: 방법 1: 로컬 psql
psql --version >nul 2>&1
if not errorlevel 1 (
    echo PostgreSQL 버전:
    psql --version
    echo.
    echo 데이터베이스: ai_trading
    echo 사용자: postgres
    echo.

    psql -U postgres -d ai_trading -f "backend\database\migrations\add_constitutional_validation_tables.sql"

    if not errorlevel 1 (
        goto SUCCESS
    )

    echo [방법 1] 실패 - 다른 방법 시도...
    echo.
)

:: 방법 2: Docker exec
echo [방법 2] Docker PostgreSQL 시도...
echo.

docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker와 PostgreSQL 모두 사용할 수 없습니다.
    echo.
    echo 💡 해결 방법:
    echo    1. PostgreSQL 설치 또는 Docker 설치
    echo    2. psql을 PATH에 추가
    echo    3. Docker PostgreSQL 컨테이너 실행
    echo.
    pause
    exit /b 1
)

:: Docker 컨테이너 확인
docker ps --format "{{.Names}}" | findstr postgres >nul 2>&1
if errorlevel 1 (
    echo ❌ 실행 중인 PostgreSQL Docker 컨테이너를 찾을 수 없습니다.
    echo.
    echo 💡 Docker 컨테이너 시작:
    echo    docker start ai-trading-postgres-prod
    echo.
    pause
    exit /b 1
)

echo Docker 컨테이너 발견
echo.

:: Docker exec으로 마이그레이션 실행
type "backend\database\migrations\add_constitutional_validation_tables.sql" | docker exec -i ai-trading-postgres-prod psql -U postgres -d ai_trading

if errorlevel 1 (
    echo.
    echo ❌ 마이그레이션 실패
    echo.
    echo 💡 문제 해결:
    echo    1. Docker 컨테이너가 실행 중인지 확인: docker ps
    echo    2. 데이터베이스 존재 확인: docker exec ai-trading-postgres-prod psql -U postgres -l
    echo    3. 로그 확인: docker logs ai-trading-postgres-prod
    echo.
    pause
    exit /b 1
)

:SUCCESS
echo.
echo ================================================================================
echo ✅ 마이그레이션 완료
echo ================================================================================
echo.
echo 생성된 테이블:
echo   ✅ constitutional_validations
echo   ✅ constitutional_violations
echo.
echo 다음 단계:
echo   1. "2_데이터수집_테스트.bat"로 시스템 테스트 (5분)
echo   2. "3_데이터수집_시작.bat"로 실제 수집 시작 (14일)
echo.

pause
