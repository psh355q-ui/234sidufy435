---
description: 안전한 DB 스키마 변경을 위한 자동화 워크플로우. 영향도 분석 및 마이그레이션 생성을 지원합니다.
---

# DB Schema Change Workflow

데이터베이스 스키마 변경을 안전하고 체계적으로 수행하기 위한 워크플로우입니다.

## 트리거 (Trigger)
- 명령어: `/db-schema-change`
- 키워드: "DB 변경", "스키마 변경", "컬럼 추가"

## Workflow Steps

### 1. 변경 사항 파악
사용자로부터 변경 대상과 내용을 입력받습니다.
- 대상 테이블: (예: `trading_signals`)
- 변경 내용: (예: `executed_at` 컬럼 인덱스 추가)

### 2. 영향도 자동 분석
해당 테이블이나 컬럼이 사용되는 코드를 검색하여 사용자에게 리포트합니다.

```powershell
Write-Host "🔍 영향도 분석 중..."
# 예시: grep -r "trading_signals" backend/
# 실제 구현 시 ripgrep(rg) 또는 findstr 사용 권장
```

### 3. models.py 수정 가이드
`backend/database/models.py` 파일의 해당 모델 클래스를 찾아 보여주고, 수정을 제안하거나 직접 수행합니다.

### 4. 마이그레이션 생성
Alembic을 사용하여 마이그레이션 파일을 생성합니다.

```powershell
# 가상 환경 활성화 필요 시 추가
alembic revision --autogenerate -m "auto_generated_migration"
```

### 5. 테스트 및 적용
로컬 DB에 적용하여 문제가 없는지 확인합니다.

```powershell
alembic upgrade head
```

### 6. 문서 업데이트
변경 사항을 `docs/database/CHANGELOG.md`에 기록할 것을 제안합니다.

---

## 사용 예시

**User**: "/db-schema-change users 테이블에 phone_number 컬럼 추가해줘"

**Antigravity**:
1. `users` 테이블 사용처 분석
2. `models.py`의 `User` 클래스에 `phone_number = Column(String(20), nullable=True)` 추가
3. `alembic revision --autogenerate -m "add_phone_number_to_users"` 실행
4. `alembic upgrade head` 실행
5. 완료 보고
