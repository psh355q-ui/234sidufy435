"""
Agent Logger Utility

Provides logging functionality for all agent skills.

Usage:
    from backend.ai.skills.common.agent_logger import AgentLogger
    
    logger = AgentLogger("signal-generator-agent", "system")
    logger.log_execution(ExecutionLog(...))
    logger.log_error(ErrorLog(...))
"""

from pathlib import Path
from datetime import datetime
from typing import Optional
import json

try:
    from backend.ai.skills.common.log_schema import (
        ExecutionLog,
        ErrorLog,
        PerformanceLog,
        AgentMetadata
    )
except ModuleNotFoundError:
    from log_schema import (
        ExecutionLog,
        ErrorLog,
        PerformanceLog,
        AgentMetadata
    )


class AgentLogger:
    """
    Logger for agent skills
    
    Writes logs to:
    - backend/ai/skills/logs/{category}/{agent-name}/execution-YYYY-MM-DD.jsonl
    - backend/ai/skills/logs/{category}/{agent-name}/errors-YYYY-MM-DD.jsonl
    - backend/ai/skills/logs/{category}/{agent-name}/performance-YYYY-MM-DD.jsonl
    - backend/ai/skills/logs/{category}/{agent-name}/metadata.json
    """
    
    def __init__(self, agent_name: str, category: str):
        """
        Initialize logger
        
        Args:
            agent_name: Agent name (e.g., "signal-generator-agent")
            category: Category (analysis, system, war-room, video-production)
        """
        self.agent_name = agent_name
        self.category = category
        self.agent_full_name = f"{category}/{agent_name}"
        
        # Log directory
        self.log_dir = Path(__file__).parent.parent / "logs" / category / agent_name
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_execution(self, log: ExecutionLog):
        """Log agent execution"""
        date = datetime.now().date()
        log_file = self.log_dir / f"execution-{date}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log.to_jsonl() + '\n')
    
    def log_error(self, log: ErrorLog):
        """Log error/exception"""
        date = datetime.now().date()
        log_file = self.log_dir / f"errors-{date}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log.to_jsonl() + '\n')
    
    def log_performance(self, log: PerformanceLog):
        """Log performance metrics"""
        date = datetime.now().date()
        log_file = self.log_dir / f"performance-{date}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log.to_jsonl() + '\n')
    
    def update_metadata(self, metadata: AgentMetadata):
        """Update agent metadata"""
        metadata_file = self.log_dir / "metadata.json"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata.model_dump(), f, indent=2, default=str)
    
    def get_metadata(self) -> Optional[AgentMetadata]:
        """Get agent metadata"""
        metadata_file = self.log_dir / "metadata.json"
        
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return AgentMetadata(**data)
    
    def read_recent_executions(self, days: int = 1) -> list:
        """
        Read recent execution logs
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of execution log dicts
        """
        logs = []
        
        for i in range(days):
            date = datetime.now().date()
            if i > 0:
                from datetime import timedelta
                date = date - timedelta(days=i)
            
            log_file = self.log_dir / f"execution-{date}.jsonl"
            
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            logs.append(json.loads(line))
        
        return logs
    
    def read_recent_errors(self, days: int = 1) -> list:
        """
        Read recent error logs
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of error log dicts
        """
        logs = []
        
        for i in range(days):
            date = datetime.now().date()
            if i > 0:
                from datetime import timedelta
                date = date - timedelta(days=i)
            
            log_file = self.log_dir / f"errors-{date}.jsonl"
            
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            logs.append(json.loads(line))
        
        return logs


# Example usage
if __name__ == "__main__":
    try:
        from backend.ai.skills.common.log_schema import ExecutionStatus, ErrorImpact
    except ModuleNotFoundError:
        from log_schema import ExecutionStatus, ErrorImpact
    
    # Create logger
    logger = AgentLogger("signal-generator-agent", "system")
    
    # Log execution
    exec_log = ExecutionLog(
        timestamp=datetime.now(),
        agent="system/signal-generator-agent",
        task_id="task-test-001",
        status=ExecutionStatus.SUCCESS,
        duration_ms=1200,
        input={"ticker": "AAPL"},
        output={"action": "BUY", "confidence": 0.85}
    )
    logger.log_execution(exec_log)
    print("✅ Execution logged")
    
    # Log error
    error_log = ErrorLog(
        timestamp=datetime.now(),
        agent="system/signal-generator-agent",
        task_id="task-test-002",
        error={
            "type": "ValueError",
            "message": "Invalid ticker",
            "stack": "..."
        },
        impact=ErrorImpact.LOW,
        recovery_attempted=False
    )
    logger.log_error(error_log)
    print("✅ Error logged")
    
    # Update metadata
    metadata = AgentMetadata(
        agent_name="signal-generator-agent",
        category="system",
        version="1.0",
        dependencies=["war-room", "analysis"],
        performance_baseline={
            "avg_execution_time_ms": 1000,
            "success_rate": 0.95
        },
        last_updated=datetime.now()
    )
    logger.update_metadata(metadata)
    print("✅ Metadata updated")
    
    # Read logs
    executions = logger.read_recent_executions(days=1)
    print(f"\n✅ Read {len(executions)} execution logs")
    
    errors = logger.read_recent_errors(days=1)
    print(f"✅ Read {len(errors)} error logs")
