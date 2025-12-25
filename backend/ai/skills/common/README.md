# Agent Skills Logging Infrastructure

**Created**: 2025-12-25  
**Purpose**: Centralized logging for all agent skills

---

## 📂 Structure

```
backend/ai/skills/
├── common/
│   ├── log_schema.py      # Pydantic schemas for logs
│   ├── agent_logger.py    # Logger utility
│   └── __init__.py
│
└── logs/                   # ⚠️  Gitignored - runtime only
    ├── analysis/
    │   └── {agent-name}/
    │       ├── execution-YYYY-MM-DD.jsonl
    │       ├── errors-YYYY-MM-DD.jsonl
    │       ├── performance-YYYY-MM-DD.jsonl
    │       └── metadata.json
    ├── system/
    ├── war-room/
    └── debugging-agent/
        └── proposals/
```

---

## 🚀 Usage

### 1. Import

```python
from backend.ai.skills.common.agent_logger import AgentLogger
from backend.ai.skills.common.log_schema import (
    ExecutionLog,
    ErrorLog,
    PerformanceLog,
    ExecutionStatus,
    ErrorImpact
)
```

### 2. Create Logger

```python
# Initialize logger for your agent
logger = AgentLogger("your-agent-name", "system")
```

### 3. Log Execution

```python
from datetime import datetime

exec_log = ExecutionLog(
    timestamp=datetime.now(),
    agent="system/your-agent-name",
    task_id="task-001",
    status=ExecutionStatus.SUCCESS,
    duration_ms=1200,
    input={"ticker": "AAPL"},
    output={"action": "BUY", "confidence": 0.85}
)

logger.log_execution(exec_log)
```

### 4. Log Errors

```python
import traceback

try:
    # Your code
    risky_operation()
except Exception as e:
    error_log = ErrorLog(
        timestamp=datetime.now(),
        agent="system/your-agent-name",
        task_id="task-001",
        error={
            "type": type(e).__name__,
            "message": str(e),
            "stack": traceback.format_exc(),
            "context": {"additional": "info"}
        },
        impact=ErrorImpact.CRITICAL,
        recovery_attempted=False
    )
    
    logger.log_error(error_log)
```

### 5. Log Performance

```python
import psutil
import os

perf_log = PerformanceLog(
    timestamp=datetime.now(),
    agent="system/your-agent-name",
    metrics={
        "cpu_percent": psutil.cpu_percent(),
        "memory_mb": psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024,
        "api_calls": 3,
        "db_queries": 5
    }
)

logger.log_performance(perf_log)
```

### 6. Read Logs

```python
# Read recent execution logs
executions = logger.read_recent_executions(days=1)
for log in executions:
    print(f"Task {log['task_id']}: {log['status']}")

# Read recent errors
errors = logger.read_recent_errors(days=7)
for log in errors:
    print(f"Error: {log['error']['type']} - {log['error']['message']}")
```

---

## 📋 Log Schemas

### ExecutionLog

```json
{
  "timestamp": "2025-12-25T18:00:00Z",
  "agent": "system/signal-generator-agent",
  "task_id": "task-001",
  "status": "SUCCESS",
  "duration_ms": 1200,
  "input": {"ticker": "AAPL"},
  "output": {"action": "BUY", "confidence": 0.85}
}
```

### ErrorLog

```json
{
  "timestamp": "2025-12-25T18:05:00Z",
  "agent": "analysis/deep-reasoning-agent",
  "task_id": "task-002",
  "error": {
    "type": "TimeoutError",
    "message": "Query timeout after 30s",
    "stack": "...",
    "context": {"table": "knowledge_graph"}
  },
  "impact": "CRITICAL",
  "recovery_attempted": false
}
```

### PerformanceLog

```json
{
  "timestamp": "2025-12-25T18:00:00Z",
  "agent": "war-room/trader-agent",
  "metrics": {
    "cpu_percent": 45.2,
    "memory_mb": 512,
    "api_calls": 3
  }
}
```

---

## 🎯 Integration Example

```python
# backend/ai/skills/system/signal-generator-agent/generator.py

from datetime import datetime
import traceback
from backend.ai.skills.common.agent_logger import AgentLogger
from backend.ai.skills.common.log_schema import *

# Initialize logger once
logger = AgentLogger("signal-generator-agent", "system")

async def generate_signal(input_data):
    start_time = datetime.now()
    task_id = f"task-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    try:
        # Your logic
        result = await process_signal(input_data)
        
        # Log success
        logger.log_execution(ExecutionLog(
            timestamp=datetime.now(),
            agent="system/signal-generator-agent",
            task_id=task_id,
            status=ExecutionStatus.SUCCESS,
            duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
            input=input_data,
            output=result
        ))
        
        return result
        
    except Exception as e:
        # Log error
        logger.log_error(ErrorLog(
            timestamp=datetime.now(),
            agent="system/signal-generator-agent",
            task_id=task_id,
            error={
                "type": type(e).__name__,
                "message": str(e),
                "stack": traceback.format_exc()
            },
            impact=ErrorImpact.CRITICAL,
            recovery_attempted=False
        ))
        
        raise
```

---

## 📊 Log File Format

**JSON Lines (.jsonl)**:
- Each line = 1 JSON object
- Easy to append
- Easy to parse line-by-line
- Works with standard tools (jq, grep)

**Example**:
```
{"timestamp":"2025-12-25T18:00:00Z","agent":"system/signal-generator-agent","task_id":"task-001","status":"SUCCESS","duration_ms":1200}
{"timestamp":"2025-12-25T18:01:00Z","agent":"system/signal-generator-agent","task_id":"task-002","status":"FAILED","duration_ms":5000}
```

---

## 🔍 Querying Logs

### Using jq

```bash
# Count errors by type
cat backend/ai/skills/logs/system/signal-generator-agent/errors-2025-12-25.jsonl | jq -r '.error.type' | sort | uniq -c

# Find slow executions (> 5s)
cat backend/ai/skills/logs/system/*/execution-2025-12-25.jsonl | jq 'select(.duration_ms > 5000)'
```

### Using Python

```python
import json
from pathlib import Path

def count_errors_by_type(agent_category, agent_name, days=1):
    """Count errors by type"""
    error_counts = {}
    
    log_dir = Path(f"backend/ai/skills/logs/{agent_category}/{agent_name}")
    
    for log_file in log_dir.glob("errors-*.jsonl"):
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    log = json.loads(line)
                    error_type = log['error']['type']
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1
    
    return error_counts
```

---

## ⚠️  Important Notes

1. **Gitignored**: `logs/` directory is in `.gitignore` - only code, not data
2. **Runtime Creation**: Log files created automatically on first use
3. **Daily Rotation**: New file per day (YYYY-MM-DD format)
4. **No Auto-Cleanup**: Old logs accumulate - consider cleanup script
5. **Thread-Safe**: Append operations are atomic

---

## 🚀 Next Steps

### Phase 1 ✅ COMPLETE
- [x] Log schemas (log_schema.py)
- [x] Logger utility (agent_logger.py)
- [x] Directory structure
- [x] Testing

### Phase 2: Debugging Agent
- [ ] Log analyzer
- [ ] Pattern detector
- [ ] Improvement proposer

### Phase 3: Integration
- [ ] Add logging to existing agents
- [ ] Dashboard for log viewing (optional)

---

**Created**: 2025-12-25  
**Version**: 1.0
