"""
AI Learning Module

Phase 25: Self-Learning + Hallucination Prevention

Modules:
- hallucination_detector: 3-gate validation system
- statistical_validators: Statistical significance testing
- walk_forward_validator: Out-of-sample validation
- agent_weight_manager: Automatic weight adjustment based on performance

Author: AI Trading System
Date: 2025-12-23
"""

from .agent_weight_manager import (
    AgentWeightManager,
    calculate_weights,
    get_low_performers
)

# Phase 25.1: Hallucination Prevention Infrastructure
from .hallucination_detector import HallucinationDetector
from .statistical_validators import StatisticalValidators
from .walk_forward_validator import WalkForwardValidator

# Phase 25.2: Agent-Specific Learning Systems
from .news_agent_learning import NewsAgentLearning
from .trader_agent_learning import TraderAgentLearning
from .risk_agent_learning import RiskAgentLearning
from .remaining_agents_learning import (
    MacroAgentLearning,
    InstitutionalAgentLearning,
    AnalystAgentLearning
)

# Phase 25.3: Central Orchestration
from .learning_orchestrator import LearningOrchestrator
from .daily_learning_scheduler import DailyLearningScheduler

__all__ = [
    # Phase 25.4 (existing)
    "AgentWeightManager",
    "calculate_weights",
    "get_low_performers",
    # Phase 25.1 (infrastructure)
    "HallucinationDetector",
    "StatisticalValidators",
    "WalkForwardValidator",
    # Phase 25.2 (agent learning)
    "NewsAgentLearning",
    "TraderAgentLearning",
    "RiskAgentLearning",
    "MacroAgentLearning",
    "InstitutionalAgentLearning",
    "AnalystAgentLearning",
    # Phase 25.3 (orchestration)
    "LearningOrchestrator",
    "DailyLearningScheduler",
]

