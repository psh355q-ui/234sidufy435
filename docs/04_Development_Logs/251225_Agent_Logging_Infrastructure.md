# Agent Logging Infrastructure Implementation

**날짜**: 2025-12-25  
**Phase**: 1 & 1.5 (Infrastructure + Integration)  
**상태**: ✅ Complete  
**Commit**: 1e28b89

---

## 📋 개요

Self-Improving Agent System의 기반이 되는 **Agent Logging Infrastructure**를 구축했습니다. 모든 agent의 실행, 에러, 성능을 표준화된 포맷으로 기록하여 Debugging Agent가 분석할 수 있도록 했습니다.

---

## 🎯 목표

1. ✅ 표준화된 로그 스키마 정의
2. ✅ 재사용 가능한 Logger 유틸리티 구현
3. ✅ 실제 agent 2개에 통합 및 검증
4. ✅ Privacy 보호 (gitignore 적용)
5. ✅ Debugging Agent 개발 준비

---

## 🏗️ 구현 내용

### 1. 로그 스키마 정의

> [!IMPORTANT]
> Pydantic 기반 스키마로 타입 안정성과 유효성 검증 보장

**파일**: [log_schema.py](file:///d:/code/ai-trading-system/backend/ai/skills/common/log_schema.py)

```python
class ExecutionLog(BaseModel):
    """Agent 실행 추적"""
    timestamp: datetime
    agent: str  # "category/agent-name"
    task_id: str
    status: ExecutionStatus  # SUCCESS, FAILED, PARTIAL
    duration_ms: int
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]]

class ErrorLog(BaseModel):
    """에러 캡처"""
    timestamp: datetime
    agent: str
    task_id: str
    error: Dict[str, Any]  # type, message, stack, context
    impact: ErrorImpact  # LOW, MEDIUM, HIGH, CRITICAL
    recovery_attempted: bool

class PerformanceLog(BaseModel):
    """성능 모니터링"""
    timestamp: datetime
    agent: str
    metrics: Dict[str, float]  # cpu, memory, api_calls, etc.
```

**특징:**
- JSON Lines (.jsonl) 포맷으로 저장
- 일별 로그 파일 자동 생성
- 스트리밍 로그 처리 최적화

---

### 2. AgentLogger 유틸리티

**파일**: [agent_logger.py](file:///d:/code/ai-trading-system/backend/ai/skills/common/agent_logger.py)

```python
logger = AgentLogger("agent-name", "category")

# 실행 로그
logger.log_execution(ExecutionLog(...))

# 에러 로그
logger.log_error(ErrorLog(...))

# 최근 로그 읽기
executions = logger.read_recent_executions(days=1)
errors = logger.read_recent_errors(days=7)
```

**기능:**
- 자동 디렉토리 생성
- Thread-safe 로그 작성
- 효율적인 JSONL 파싱
- Metadata 관리

---

### 3. 디렉토리 구조

```
backend/ai/skills/
├── common/
│   ├── log_schema.py          # Pydantic schemas
│   ├── agent_logger.py        # Logger utility
│   ├── __init__.py
│   ├── README.md              # 전체 문서
│   ├── test_logging.py        # 테스트 스크립트
│   └── generate_logs.py       # API 테스트
│
└── logs/                       # ⚠️ Gitignored
    ├── .gitkeep
    ├── system/
    │   └── signal-consolidation/
    │       ├── execution-2025-12-25.jsonl (7+ logs)
    │       ├── errors-2025-12-25.jsonl (1 log)
    │       ├── performance-2025-12-25.jsonl (1 log)
    │       └── metadata.json
    └── war-room/
        └── war-room-debate/
            └── errors-2025-12-25.jsonl (1+ logs)
```

---

### 4. Agent 통합

#### 4.1 signal-consolidation-router

**파일**: [signal_consolidation_router.py:L20-L40](file:///d:/code/ai-trading-system/backend/api/signal_consolidation_router.py#L20-L40)

```python
# Imports
from backend.ai.skills.common.agent_logger import AgentLogger
from backend.ai.skills.common.log_schema import ExecutionLog, ErrorLog

# Initialize
agent_logger = AgentLogger("signal-consolidation", "system")
```

**통합 방법:**
1. Start time & task ID 추적
2. Success 시 execution log
3. Error 시 error log with stack trace

**결과**: 7+ execution logs, 1 error log 생성

---

#### 4.2 war-room-router

**파일**: [war_room_router.py:L42-L56](file:///d:/code/ai-trading-system/backend/api/war_room_router.py#L42-L56)

> [!TIP]
> 복잡한 endpoint는 기존 try-except 구조를 활용하여 최소 변경으로 통합

```python
# 기존 try-except 활용
try:
    start_time = datetime.now()
    task_id = f"war-room-{ticker}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # ... existing logic ...
    
    # Success logging before return
    agent_logger.log_execution(ExecutionLog(...))
    return response

except Exception as e:
    # Error logging in existing except block
    agent_logger.log_error(ErrorLog(...))
    raise
```

**결과**: 1+ error logs 생성 (API 호출 테스트)

---

## 📊 생성된 로그 데이터

### Execution Log 예시

```json
{
  "timestamp": "2025-12-25T18:19:57",
  "agent": "system/signal-consolidation",
  "task_id": "consolidate-20251225-181957",
  "status": "SUCCESS",
  "duration_ms": 1200,
  "input": {"ticker": "AAPL", "hours": 24, "limit": 10},
  "output": {"total_count": 7, "sources": ["war_room", "deep_reasoning"]}
}
```

### Error Log 예시

```json
{
  "timestamp": "2025-12-25T18:30:00",
  "agent": "war-room/war-room-debate",
  "task_id": "war-room-AAPL-20251225-183000",
  "error": {
    "type": "TypeError",
    "message": "missing required positional argument for AIDebateSession",
    "stack": "Traceback...",
    "context": {"ticker": "AAPL", "execute_trade": false}
  },
  "impact": "CRITICAL",
  "recovery_attempted": false
}
```

---

## 🔒 Privacy & Security

### Gitignore 설정

**파일**: [.gitignore:L139-L147](file:///d:/code/ai-trading-system/.gitignore#L139-L147)

```gitignore
# Agent Skills Logs (runtime data only)
backend/ai/skills/logs/**/*.jsonl
backend/ai/skills/logs/**/*.json
!backend/ai/skills/logs/**/.gitkeep
```

> [!WARNING]
> 로그 파일은 개인 실행 데이터, API 응답, 에러 컨텍스트 등 민감한 정보 포함 가능

**보호 내용:**
- 실행 로그 (input/output data)
- 에러 로그 (stack traces, context)
- Metadata (성능 baseline)

**Git에 포함:**
- 디렉토리 구조 (.gitkeep)
- 코드 및 유틸리티
- 문서

---

## ✅ 검증 & 테스트

### 1. 단위 테스트

**스크립트**: [test_logging.py](file:///d:/code/ai-trading-system/backend/ai/skills/common/test_logging.py)

```bash
$ python backend/ai/skills/common/test_logging.py

✅ Execution log generated (3개)
✅ Error log generated (1개)
✅ Performance log generated (1개)
✅ Metadata saved and retrieved
```

### 2. API 통합 테스트

**스크립트**: [generate_logs.py](file:///d:/code/ai-trading-system/backend/ai/skills/common/generate_logs.py)

```bash
$ python backend/ai/skills/common/generate_logs.py

✅ GET /api/consolidated-signals (200)
✅ GET /api/consolidated-signals/stats (200)
⚠️  POST /api/war-room/debate (500 - error logged)
```

### 3. 로그 파일 검증

```bash
# 로그 개수 확인
$ cat backend/ai/skills/logs/system/signal-consolidation/execution-*.jsonl | wc -l
7

# 로그 파싱 테스트
$ cat execution-2025-12-25.jsonl | jq '.duration_ms'
800
1000
1200
```

---

## 📚 문서화

### README.md

**파일**: [backend/ai/skills/common/README.md](file:///d:/code/ai-trading-system/backend/ai/skills/common/README.md)

**포함 내용:**
- 📂 Directory structure
- 🚀 Usage examples (import, create logger, log events)
- 📋 Log schemas (ExecutionLog, ErrorLog, PerformanceLog)
- 🎯 Integration example (full code sample)
- 📊 Log file format (JSON Lines)
- 🔍 Querying logs (jq, Python)
- ⚠️ Important notes

---

## 🎯 성과 요약

| 항목 | 상태 | 결과 |
|------|------|------|
| Log Infrastructure | ✅ | Schemas, Logger, Directory |
| signal-consolidation | ✅ | 7+ execution, 1 error, 1 perf |
| war-room-debate | ✅ | 1+ error logs |
| Gitignore | ✅ | Privacy protected |
| Documentation | ✅ | Complete README |
| Testing | ✅ | Unit + Integration |

**총 로그 데이터:**
- 2개 categories (system, war-room)
- 2개 agents
- 9+ logs (diverse types)

---

## 🚀 다음 단계: Phase 2

### Debugging Agent Skill 개발

```
backend/ai/skills/system/debugging-agent/
├── SKILL.md                    # Agent definition
├── scripts/
│   ├── log_reader.py           # Read JSONL logs
│   ├── pattern_detector.py     # Detect patterns
│   │   - Recurring errors (3+ in 24h)
│   │   - Performance degradation (2x baseline)
│   │   - High error rates (>5%)
│   └── improvement_proposer.py # Generate proposals
│       - Root cause analysis
│       - Solution suggestions
│       - Confidence scoring (5 metrics)
└── docs/
    └── PROPOSAL_FORMAT.md
```

**예상 시간**: 4-6시간

---

## 📦 Git Commits

1. **e943b87**: "feat: Add Agent Logging Infrastructure (Phase 1)"
   - Log schemas, AgentLogger, gitignore, tests

2. **2e31001**: "feat: Add logging to signal-consolidation agent + Test verification"
   - signal-consolidation integration, test scripts

3. **1681edd**: "feat: Agent logging infrastructure with signal-consolidation integration"
   - generate_logs.py script

4. **4474d44**: "feat: Agent Logging Infrastructure Phase 1 Complete"
   - Final Phase 1 commit with full documentation

5. **1e28b89**: "feat: Add logging to War Room debate endpoint" ← **Latest**
   - War Room integration, Phase 1.5 complete

---

**작성일**: 2025-12-25  
**Version**: 1.0  
**Status**: Phase 1 & 1.5 Complete ✅
