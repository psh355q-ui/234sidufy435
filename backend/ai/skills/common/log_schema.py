"""
Agent Logging Schema

Standard log formats for all agent skills in the AI Trading System.

Log Types:
1. ExecutionLog: Track each agent execution
2. ErrorLog: Capture errors and exceptions  
3. PerformanceLog: Monitor resource usage and metrics

Format: JSON Lines (.jsonl) - one JSON object per line
Storage: backend/ai/skills/logs/{category}/{agent-name}/
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ExecutionStatus(str, Enum):
    """Execution status types"""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    PARTIAL = "PARTIAL"


class ErrorImpact(str, Enum):
    """Error impact severity"""
    CRITICAL = "CRITICAL"  # System broken, immediate attention
    HIGH = "HIGH"          # Major feature broken
    MEDIUM = "MEDIUM"      # Degraded performance
    LOW = "LOW"            # Minor issue


class ExecutionLog(BaseModel):
    """
    Agent execution log
    
    Records each agent invocation with input, output, and timing.
    """
    timestamp: datetime = Field(description="Execution start time")
    agent: str = Field(description="Agent name in format: category/agent-name")
    task_id: str = Field(description="Unique task identifier")
    status: ExecutionStatus = Field(description="Execution outcome")
    duration_ms: int = Field(description="Execution time in milliseconds")
    input: Dict[str, Any] = Field(description="Input data to agent")
    output: Optional[Dict[str, Any]] = Field(default=None, description="Agent output")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    
    def to_jsonl(self) -> str:
        """Convert to JSON Lines format"""
        return self.model_dump_json(exclude_none=True)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorLog(BaseModel):
    """
    Error/exception log
    
    Captures errors with full context for debugging.
    """
    timestamp: datetime = Field(description="Error occurrence time")
    agent: str = Field(description="Agent name in format: category/agent-name")
    task_id: str = Field(description="Task ID where error occurred")
    error: Dict[str, Any] = Field(description="Error details (type, message, stack, context)")
    impact: ErrorImpact = Field(description="Error severity/impact")
    recovery_attempted: bool = Field(default=False, description="Was auto-recovery attempted?")
    recovery_successful: Optional[bool] = Field(default=None, description="Recovery outcome")
    related_errors: Optional[List[str]] = Field(default=None, description="Related error task_ids")
    
    def to_jsonl(self) -> str:
        """Convert to JSON Lines format"""
        return self.model_dump_json(exclude_none=True)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PerformanceLog(BaseModel):
    """
    Performance metrics log
    
    Tracks resource usage and performance indicators.
    """
    timestamp: datetime = Field(description="Metrics collection time")
    agent: str = Field(description="Agent name in format: category/agent-name")
    metrics: Dict[str, float] = Field(description="Performance metrics")
    # Common metrics:
    # - cpu_percent: CPU usage %
    # - memory_mb: Memory usage MB
    # - api_calls: Number of API calls
    # - db_queries: Number of DB queries
    # - avg_response_time_ms: Average response time
    
    def to_jsonl(self) -> str:
        """Convert to JSON Lines format"""
        return self.model_dump_json(exclude_none=True)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentMetadata(BaseModel):
    """
    Agent metadata
    
    Stores baseline performance and configuration for each agent.
    Saved as metadata.json in each agent's log directory.
    """
    agent_name: str
    category: str  # analysis, system, war-room, video-production
    version: str
    dependencies: List[str] = Field(default_factory=list)
    performance_baseline: Dict[str, float] = Field(
        description="Historical performance baselines",
        default_factory=dict
    )
    last_updated: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Example usage
if __name__ == "__main__":
    # Example ExecutionLog
    exec_log = ExecutionLog(
        timestamp=datetime.now(),
        agent="system/signal-generator-agent",
        task_id="task-20251225-001",
        status=ExecutionStatus.SUCCESS,
        duration_ms=1200,
        input={"ticker": "AAPL", "source": "war_room"},
        output={"action": "BUY", "confidence": 0.85}
    )
    print("ExecutionLog JSONL:")
    print(exec_log.to_jsonl())
    
    # Example ErrorLog
    error_log = ErrorLog(
        timestamp=datetime.now(),
        agent="analysis/deep-reasoning-agent",
        task_id="task-20251225-002",
        error={
            "type": "TimeoutError",
            "message": "Query timeout after 30s",
            "stack": "...",
            "context": {"table": "knowledge_graph", "query": "SELECT ..."}
        },
        impact=ErrorImpact.CRITICAL,
        recovery_attempted=False
    )
    print("\nErrorLog JSONL:")
    print(error_log.to_jsonl())
    
    # Example PerformanceLog
    perf_log = PerformanceLog(
        timestamp=datetime.now(),
        agent="war-room/trader-agent",
        metrics={
            "cpu_percent": 45.2,
            "memory_mb": 512,
            "api_calls": 3,
            "db_queries": 5,
            "avg_response_time_ms": 850
        }
    )
    print("\nPerformanceLog JSONL:")
    print(perf_log.to_jsonl())
