"""
NewsAgent Learning - Statistical Learning for News Source Credibility

This module implements self-learning for the NewsAgent with hallucination prevention.

Key Features:
- News source credibility tracking
- Sentiment prediction validation
- 4-Signal Consensus integration
- Statistical significance gates

Learning Process:
1. Track news source predictions vs actual market outcomes
2. Validate patterns with HallucinationDetector (3 gates)
3. Update source credibility scores only if statistically valid
4. Maintain temporal stability checks

Author: AI Trading System
Date: 2025-12-23
Phase: 25.2
"""

import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr

from backend.ai.learning.hallucination_detector import HallucinationDetector
from backend.ai.learning.statistical_validators import StatisticalValidators

logger = logging.getLogger(__name__)


class NewsAgentLearning:
    """
    Self-learning system for NewsAgent with hallucination prevention.
    
    Prevents:
    - Learning from lucky streaks (small sample)
    - Random correlations (p-value filtering)
    - Recent bias (temporal stability check)
    
    Example:
        learner = NewsAgentLearning()
        
        # After 30+ predictions
        success = learner.learn_source_credibility(
            source="TechCrunch",
            sentiment_predictions=[0.5, 0.7, 0.3, ...],  # 30+ predictions
            actual_returns=[0.02, 0.03, -0.01, ...]      # Actual outcomes
        )
        
        if success:
            credibility = learner.get_source_credibility("TechCrunch")
            print(f"TechCrunch credibility: {credibility:.2f}")
    """
    
    def __init__(
        self,
        min_sample_size: int = 30,
        min_p_value: float = 0.05,
        max_temporal_drift: float = 0.30
    ):
        """
        Initialize NewsAgent learning system.
        
        Args:
            min_sample_size: Minimum predictions before learning (default: 30)
            min_p_value: Maximum p-value for significance (default: 0.05)
            max_temporal_drift: Maximum correlation drift (default: 0.30)
        """
        self.detector = HallucinationDetector(
            min_sample_size=min_sample_size,
            min_p_value=min_p_value,
            max_temporal_drift=max_temporal_drift
        )
        
        # Source credibility scores (source -> correlation coefficient)
        self.source_credibility: Dict[str, float] = {}
        
        # Learning history (for debugging and monitoring)
        self.learning_history: List[Dict] = []
        
        # Default credibility for unknown sources
        self.default_credibility = 0.50
        
        logger.info(
            f"NewsAgentLearning initialized: "
            f"min_samples={min_sample_size}, "
            f"min_p={min_p_value}, "
            f"max_drift={max_temporal_drift}"
        )
    
    def learn_source_credibility(
        self,
        source: str,
        sentiment_predictions: List[float],
        actual_returns: List[float],
        verbose: bool = True
    ) -> Tuple[bool, str]:
        """
        Learn credibility of a news source from historical predictions.
        
        Args:
            source: News source name (e.g., "TechCrunch", "Reuters")
            sentiment_predictions: Sentiment scores predicted by this source
                                  (e.g., [0.7, 0.3, 0.8, ...] where 1.0 = very bullish)
            actual_returns: Actual stock returns that followed
                           (e.g., [0.02, -0.01, 0.03, ...])
            verbose: Whether to log detailed results
        
        Returns:
            Tuple of (success, reason)
            - success: True if learning was accepted
            - reason: Explanation of result
        
        Example:
            >>> learner = NewsAgentLearning()
            >>> # Collect 30+ predictions from TechCrunch
            >>> predictions = [0.5, 0.7, ...]  # 30+ sentiment scores
            >>> returns = [0.02, 0.03, ...]     # Actual returns
            >>> success, reason = learner.learn_source_credibility(
            ...     "TechCrunch", predictions, returns
            ... )
            >>> print(f"Learning result: {reason}")
        """
        if verbose:
            logger.info(f"🧠 Learning credibility for source: {source} ({len(sentiment_predictions)} samples)")
        
        # Validate pattern through 3 gates
        is_valid, reason = self.detector.validate_pattern(
            predictions=sentiment_predictions,
            outcomes=actual_returns,
            verbose=verbose
        )
        
        if not is_valid:
            # Pattern rejected - do NOT learn
            if verbose:
                logger.warning(f"❌ Learning REJECTED for {source}: {reason}")
            
            # Record rejection in history
            self.learning_history.append({
                "timestamp": datetime.now(),
                "source": source,
                "n_samples": len(sentiment_predictions),
                "action": "rejected",
                "reason": reason
            })
            
            return False, f"Learning rejected: {reason}"
        
        # Pattern validated - safe to learn!
        correlation, p_value = pearsonr(sentiment_predictions, actual_returns)
        
        # Update credibility score
        old_credibility = self.source_credibility.get(source, self.default_credibility)
        
        # Use correlation coefficient as credibility score
        # Range: -1.0 to 1.0, where:
        #   1.0 = perfect positive correlation
        #   0.0 = no correlation
        #  -1.0 = perfect negative correlation (contrarian indicator!)
        new_credibility = abs(correlation)  # Use absolute value (magnitude of predictiveness)
        
        self.source_credibility[source] = new_credibility
        
        # Record successful learning
        self.learning_history.append({
            "timestamp": datetime.now(),
            "source": source,
            "n_samples": len(sentiment_predictions),
            "action": "learned",
            "old_credibility": old_credibility,
            "new_credibility": new_credibility,
            "correlation": correlation,
            "p_value": p_value,
            "reason": reason
        })
        
        if verbose:
            logger.info(
                f"✅ Learning ACCEPTED for {source}: "
                f"Credibility {old_credibility:.2f} → {new_credibility:.2f} "
                f"(correlation={correlation:.2f}, p={p_value:.4f})"
            )
        
        return True, f"Credibility updated: {new_credibility:.2f}"
    
    def get_source_credibility(self, source: str) -> float:
        """
        Get current credibility score for a news source.
        
        Args:
            source: News source name
        
        Returns:
            Credibility score (0.0 to 1.0)
            Returns default (0.50) for unknown sources
        
        Example:
            >>> credibility = learner.get_source_credibility("TechCrunch")
            >>> print(f"TechCrunch credibility: {credibility:.0%}")
        """
        return self.source_credibility.get(source, self.default_credibility)
    
    def get_all_credibilities(self) -> Dict[str, float]:
        """Get credibility scores for all learned sources."""
        return self.source_credibility.copy()
    
    def learn_sentiment_adjustment(
        self,
        raw_sentiments: List[float],
        actual_returns: List[float],
        verbose: bool = True
    ) -> Tuple[bool, Optional[float]]:
        """
        Learn optimal sentiment scaling factor.
        
        Sometimes news sentiment scores might be consistently too high or too low.
        This method learns a calibration factor.
        
        Args:
            raw_sentiments: Raw sentiment scores from NLP
            actual_returns: Actual returns
            verbose: Log details
        
        Returns:
            Tuple of (success, scaling_factor)
        
        Example:
            >>> # If sentiment is always 0.7 but returns are 0.02 (much smaller)
            >>> success, factor = learner.learn_sentiment_adjustment(
            ...     raw_sentiments=[0.7, 0.8, 0.6, ...],
            ...     actual_returns=[0.02, 0.03, 0.01, ...]
            ... )
            >>> # factor might be ~0.03 (scale down sentiment)
        """
        if verbose:
            logger.info(f"🧠 Learning sentiment adjustment ({len(raw_sentiments)} samples)")
        
        # Validate pattern
        is_valid, reason = self.detector.validate_pattern(
            predictions=raw_sentiments,
            outcomes=actual_returns,
            verbose=verbose
        )
        
        if not is_valid:
            if verbose:
                logger.warning(f"❌ Sentiment adjustment rejected: {reason}")
            return False, None
        
        # Calculate optimal scaling factor (ratio of means)
        mean_sentiment = np.mean(raw_sentiments)
        mean_return = np.mean(actual_returns)
        
        if mean_sentiment == 0:
            logger.warning("Mean sentiment is zero, cannot calculate scaling factor")
            return False, None
        
        scaling_factor = mean_return / mean_sentiment
        
        if verbose:
            logger.info(
                f"✅ Sentiment scaling factor learned: {scaling_factor:.4f} "
                f"(mean_sentiment={mean_sentiment:.2f}, mean_return={mean_return:.4f})"
            )
        
        return True, scaling_factor
    
    def get_learning_summary(self) -> Dict:
        """
        Get summary of learning progress.
        
        Returns:
            Dict with learning statistics
        
        Example:
            >>> summary = learner.get_learning_summary()
            >>> print(f"Sources learned: {summary['n_sources_learned']}")
            >>> print(f"Total attempts: {summary['total_attempts']}")
            >>> print(f"Success rate: {summary['success_rate']:.0%}")
        """
        total_attempts = len(self.learning_history)
        successful = sum(1 for h in self.learning_history if h["action"] == "learned")
        rejected = sum(1 for h in self.learning_history if h["action"] == "rejected")
        
        return {
            "n_sources_learned": len(self.source_credibility),
            "total_attempts": total_attempts,
            "successful_learnings": successful,
            "rejected_learnings": rejected,
            "success_rate": successful / total_attempts if total_attempts > 0 else 0.0,
            "source_credibilities": self.source_credibility.copy(),
            "recent_history": self.learning_history[-10:]  # Last 10 events
        }


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🧪 Testing NewsAgentLearning\n")
    
    learner = NewsAgentLearning()
    
    # Simulate TechCrunch predictions
    print("Test 1: Valid pattern (TechCrunch)")
    np.random.seed(42)
    n = 50
    tech_crunch_sentiments = np.random.randn(n) * 0.2 + 0.6  # Bullish bias
    actual_returns = tech_crunch_sentiments * 0.03 + np.random.randn(n) * 0.01
    
    success, reason = learner.learn_source_credibility(
        "TechCrunch",
        tech_crunch_sentiments.tolist(),
        actual_returns.tolist()
    )
    print(f"Result: {success}")
    print(f"Reason: {reason}")
    print(f"Credibility: {learner.get_source_credibility('TechCrunch'):.2f}\n")
    
    # Simulate random noise source
    print("Test 2: Random noise (BadSource)")
    random_sentiments = np.random.randn(50).tolist()
    random_returns = np.random.randn(50).tolist()
    
    success, reason = learner.learn_source_credibility(
        "BadSource",
        random_sentiments,
        random_returns
    )
    print(f"Result: {success}")
    print(f"Reason: {reason}\n")
    
    # Learning summary
    print("Learning Summary:")
    summary = learner.get_learning_summary()
    print(f"Sources learned: {summary['n_sources_learned']}")
    print(f"Success rate: {summary['success_rate']:.0%}")
    print(f"Credibilities: {summary['source_credibilities']}")
