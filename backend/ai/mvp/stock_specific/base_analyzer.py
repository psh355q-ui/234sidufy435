
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseStockAnalyzer(ABC):
    """
    Abstract Base Class for Stock Specific Analyzers.
    Provides a standard interface for specialized analysis logic.
    """

    def __init__(self, symbol: str):
        self.symbol = symbol.upper()

    @abstractmethod
    def analyze_specifics(
        self,
        news_articles: Optional[list] = None,
        market_data: Optional[Dict[str, Any]] = None,
        event_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze stock-specific factors.
        
        Returns:
            Dict containing:
            - specific_risks: List[str]
            - specific_catalysts: List[str]
            - specific_metrics: Dict[str, Any] (e.g., Deliveries for Tesla)
            - score_adjustment: float (-2.0 to +2.0)
        """
        pass

    def get_prompt_addition(self) -> str:
        """
        Return text to be added to the LLM prompt.
        """
        return ""
