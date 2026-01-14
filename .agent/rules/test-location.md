---
description: 테스트 스크립트 및 임시 파일 생성 위치에 대한 엄격한 규칙.
---

# Test & Script Location Rules

프로젝트 루트 디렉토리의 오염을 방지하고 코드 관리를 체계화하기 위해, 테스트 및 임시 파일 생성 위치를 엄격히 제한합니다.

## 1. 파일 생성 위치 규칙 (Mandatory Location)

모든 **테스트 코드**, **임시 스크립트**, **검증용 파일**은 반드시 다음 경로 하위에 생성해야 합니다.

- **경로**: `tests/` (Project Root 하위)
- **권장 구조**:
  ```
  tests/
  ├── unit/            # 단위 테스트
  ├── integration/     # 통합 테스트
  ├── temp/            # 임시 스크립트 (나중에 지울 것)
  └── scripts/         # 유틸리티 성격의 일회성 스크립트
  ```

## 2. 금지 사항 (Prohibited Actions)

- ❌ **Root Pollution**: 프로젝트 루트(`D:\code\ai-trading-system\`)에 `temp.py`, `test.py`, `check_something.py` 등을 직접 생성하는 것을 **엄격히 금지**합니다.
- ❌ **Backend Pollution**: `backend/` 폴더 내부에 로직과 관계없는 테스트 파일을 섞지 마십시오.

## 3. 실행 가이드 (Execution Guide)

`tests/` 폴더에 있는 스크립트를 실행할 때는 프로젝트 루트에서 모듈 경로를 인식할 수 있도록 주의해야 합니다.

```powershell
# 올바른 실행 방법 (PYTHONPATH 설정)
$env:PYTHONPATH = "$PWD"; python tests/temp/my_test.py
```

또는 스크립트 상단에 다음 코드를 추가하세요:

```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

## 4. 예외 (Exceptions)

- 프로젝트 설정 파일 (`.env`, `docker-compose.yml` 등)
- 배포 및 실행 스크립트 (`start.bat` 등)
- 공식 문서 (`README.md` 등)
