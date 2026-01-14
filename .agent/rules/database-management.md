---
description: DB 스키마 변경 시 준수해야 할 필수 절차와 안전 수칙.
---

# Database Management Rules

데이터 무결성 유지와 안정적인 서비스를 위해 모든 데이터베이스 변경은 다음 규칙을 따라야 합니다.

## 1. 필수 절차 (Mandatory Procedure)

DB 스키마를 변경(테이블 생성, 컬럼 추가/수정/삭제)할 때는 반드시 다음 단계를 거쳐야 합니다.

### Step 1: 영향도 분석 (Impact Analysis)
변경하려는 테이블이나 컬럼이 코드의 어느 부분에서 사용되는지 확인합니다.
```bash
grep -r "table_name" backend/
grep -r "column_name" backend/
```

### Step 2: 마이그레이션 생성 (Use Migrations)
`models.py`를 직접 수정하고 끝내지 말고, 반드시 Alembic을 통해 마이그레이션 파일을 생성해야 합니다.
```bash
# models.py 수정 후
alembic revision --autogenerate -m "description_of_change"
```

### Step 3: 로컬 테스트 (Local Test)
마이그레이션을 로컬 DB에 적용하고, 롤백이 가능한지 확인합니다.
```bash
alembic upgrade head
# 테스트 실행
alembic downgrade -1
alembic upgrade head
```

### Step 4: 문서화 (Documentation)
- `docs/database/CHANGELOG.md` (없으면 생성)에 변경 사항을 기록합니다.
- `docs/architecture/structure-map.md`의 ERD가 업데이트되었는지 확인합니다 (자동화 예정).

## 2. 금지 사항 (Prohibited Actions)

- ❌ **Direct SQL Execution**: 운영 DB(`production`)에서 `ALTER TABLE`, `DROP TABLE` 등의 DDL을 직접 실행하지 마십시오.
- ❌ **Ignoring Foreign Keys**: 외래 키 제약 조건을 무시하거나 강제로 끄지 마십시오.
- ❌ **Migration Bypass**: 마이그레이션 파일 없이 코드만 배포하지 마십시오.

## 3. 명명 규칙 (Naming Conventions)

- **Tables**: `snake_case`, 복수형 (e.g., `trading_signals`, `users`)
- **Columns**: `snake_case` (e.g., `created_at`, `user_id`)
- **Indexes**: `idx_tablename_columnname` (e.g., `idx_orders_created_at`)
- **Constraints**: `fk_tablename_referencetable` (e.g., `fk_orders_users`)

## 4. Workflow

Antigravity는 안전한 DB 변경을 돕기 위해 `/db-schema-change` 워크플로우를 제공합니다.

```
/db-schema-change
```
