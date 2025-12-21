"""
Base Agent Class for Agent Skills

All skill-based agents inherit from this class.
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

from backend.ai.skills.skill_loader import get_skill_loader

logger = logging.getLogger(__name__)


class BaseSkillAgent(ABC):
    """
    Base class for all Agent Skills
    
    Subclasses must implement:
        - execute(): Main agent logic
    """
    
    def __init__(self, category: str, agent_name: str):
        """
        Initialize agent with skill
        
        Args:
            category: Skill category
            agent_name: Agent name
        """
        self.category = category
        self.agent_name = agent_name
        
        # Load skill
        loader = get_skill_loader()
        self.skill = loader.load_skill(category, agent_name)
        
        # Extract skill components
        self.metadata = self.skill["metadata"]
        self.instructions = self.skill["instructions"]
        self.tools = self.skill.get("tools", [])
        
        logger.info(f"Initialized {category}/{agent_name} v{self.metadata.get('metadata', {}).get('version', '1.0')}")
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main logic
        
        Args:
            context: Execution context with input data
        
        Returns:
            Agent's analysis result
        """
        pass
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt (instructions) for this agent
        
        Returns:
            Full instruction text from SKILL.md
        """
        return self.instructions
    
    def get_user_prompt(self, context: Dict[str, Any]) -> str:
        """
        Generate user prompt for LLM based on context
        
        Args:
            context: Execution context
        
        Returns:
            Formatted user prompt
        """
        # Default implementation - can be overridden
        task_desc = context.get('task_description', 'Analyze the provided data')
        input_data = context.get('input_data', {})
        
        return f"""
## Current Task
{task_desc}

## Input Data
{self._format_input_data(input_data)}

Please provide your analysis following the format and guidelines specified in your role description.
"""
    
    def _format_input_data(self, data: Any) -> str:
        """
        Format input data for prompt
        
        Args:
            data: Input data (dict, list, str, etc.)
        
        Returns:
            Formatted string
        """
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                lines.append(f"**{key}**: {value}")
            return "\n".join(lines)
        elif isinstance(data, list):
            return "\n".join(f"- {item}" for item in data)
        else:
            return str(data)
    
    def get_metadata_field(self, field: str, default: Any = None) -> Any:
        """
        Get a specific metadata field
        
        Args:
            field: Field name
            default: Default value if not found
        
        Returns:
            Field value or default
        """
        return self.metadata.get(field, default)
    
    def get_name(self) -> str:
        """Get agent's name from metadata"""
        return self.metadata.get("name", self.agent_name)
    
    def get_description(self) -> str:
        """Get agent's description from metadata"""
        return self.metadata.get("description", "")
    
    def get_version(self) -> str:
        """Get agent's version"""
        return self.metadata.get("metadata", {}).get("version", "1.0")
    
    def get_role(self) -> str:
        """Get agent's role (from agent_role metadata)"""
        return self.metadata.get("metadata", {}).get("agent_role", "analyst")
    
    def supports_tool(self, tool_name: str) -> bool:
        """
        Check if agent supports a specific tool
        
        Args:
            tool_name: Tool name
        
        Returns:
            True if tool is in allowed-tools list
        """
        return tool_name in self.tools
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} category={self.category} name={self.agent_name}>"


class AnalysisSkillAgent(BaseSkillAgent):
    """
    Base class for analysis agents
    
    Provides common functionality for agents that analyze
    tickers, news, or market data.
    """
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Default execute implementation for analysis agents
        
        Args:
            context: Must contain 'ticker' or 'news_id' or 'data'
        
        Returns:
            Analysis result
        """
        # This is a default implementation
        # Subclasses should override for specific logic
        ticker = context.get('ticker')
        news_id = context.get('news_id')
        
        if ticker:
            return await self.analyze_ticker(ticker, context)
        elif news_id:
            return await self.analyze_news(news_id, context)
        else:
            raise ValueError("Context must contain 'ticker' or 'news_id'")
    
    async def analyze_ticker(self, ticker: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a ticker
        
        Args:
            ticker: Stock ticker
            context: Additional context
        
        Returns:
            Analysis result
        """
        raise NotImplementedError("Subclass must implement analyze_ticker()")
    
    async def analyze_news(self, news_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a news article
        
        Args:
            news_id: News article ID
            context: Additional context
        
        Returns:
            Analysis result
        """
        raise NotImplementedError("Subclass must implement analyze_news()")


class DebateSkillAgent(BaseSkillAgent):
    """
    Base class for War Room debate agents
    
    Provides vote structure for debate participation.
    """
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute debate agent
        
        Args:
            context: Debate context (ticker, market_data, news, etc.)
        
        Returns:
            Vote with action, confidence, reasoning
        """
        return await self.vote(context)
    
    async def vote(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cast a vote in the debate
        
        Args:
            context: Debate context
        
        Returns:
            {
                "agent": agent_name,
                "action": "BUY|SELL|HOLD",
                "confidence": 0.0-1.0,
                "reasoning": "...",
                "risk_factors": [...],
                "timestamp": ...
            }
        """
        raise NotImplementedError("Subclass must implement vote()")
