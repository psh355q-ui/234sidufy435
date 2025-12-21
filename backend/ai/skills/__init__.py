"""
Agent Skills Package

Provides Agent Skills framework for AI Trading System.
"""

from .skill_loader import SkillLoader, get_skill_loader
from .base_agent import BaseSkillAgent, AnalysisSkillAgent, DebateSkillAgent

__all__ = [
    'SkillLoader',
    'get_skill_loader',
    'BaseSkillAgent',
    'AnalysisSkillAgent',
    'DebateSkillAgent',
]

__version__ = '1.0.0'
