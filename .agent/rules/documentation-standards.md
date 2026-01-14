---
description: Documentation standards including filename conventions (YYMMDD_) and folder structure.
---

# Documentation Standards

문서의 체계적인 관리와 시간순 정렬을 위해 다음 표준을 준수해야 합니다.

## 1. 파일명 규칙 (Filename Convention)

모든 새 문서는 다음 형식을 따릅니다:

**Format**: `YYMMDD_Category_Description.md`

| 구성요소 | 설명 | 예시 | 비고 |
|----------|------|------|------|
| **YYMMDD** | 작성일 (년월일) | `260114` | 파일의 시간순 정렬 보장 |
| **Category** | 문서 유형 | `Implementation` | 아래 카테고리 참조 |
| **Description** | 문서 내용 (Snake Case) | `structure_map_automation` | 영문 소문자, 언더스코어 `_` 사용 |

### 카테고리 (Category)

| 카테고리 | 설명 |
|----------|------|
| `Implementation` | 기능 구현 완료 보고서 |
| `Planning` | 개발 계획, 설계 문서 |
| `Rules` | 규칙, 정책, 가이드라인 변경 |
| `Workflow` | 새로운 워크플로우 또는 프로세스 |
| `Guide` | 사용자 매뉴얼, 튜토리얼 |
| `Report` | 진행 상황 보고, 회고 |
| `Architecture` | 시스템 아키텍처, 구조 변경 |
| `Analysis` | 리서치, 분석 결과 |

### 예시

- `260114_Implementation_db_schema_agent.md`
- `260114_Planning_rag_system_v2.md`
- `260114_Rules_coding_conventions.md`

## 2. 폴더 구조 (Folder Structure)

문서는 `docs/` 디렉토리 내 적절한 하위 폴더에 위치해야 합니다.

```
docs/
├── architecture/        # 시스템 아키텍처 및 구조 관련
├── planning/            # 개발 계획, 스펙, 요구사항
├── progress/            # 일일/주간 보고서, 진행 상황
├── guides/              # 사용자 가이드, 개발자 가이드, 매뉴얼
├── features/            # 특정 기능에 대한 상세 설명
├── api/                 # API 문서
├── database/            # DB 스키마, 마이그레이션 로그
├── skills/              # AI Agent Skills 관련
└── archive/             # 오래되거나 더 이상 유효하지 않은 문서
```

## 3. 문서 작성 가이드

- **Header**: 문서 상단에 제목, 작성일, 작성자, 요약을 포함합니다.
- **Markdown**: 표준 Markdown 문법을 사용합니다.
- **Images**: 이미지는 `docs/images/` 폴더에 `YYMMDD_description.png` 형식으로 저장하고 참조합니다.
- **Links**: 관련 문서는 상대 경로로 링크합니다.

## 4. 자동화 도구

문서 생성 시 실수를 방지하기 위해 `.agent/scripts/create_doc.py` 스크립트(추후 구현 예정) 사용을 권장합니다.

```bash
# 예시:
python .agent/scripts/create_doc.py --category Implementation --desc structure_map_automation
```
