"""
Hallucination Detector - Base Class for AI Learning Safety

This module implements a 3-gate validation system to prevent AI agents
from learning spurious patterns based on:
- Small sample sizes (< 30)
- Random correlations (p-value > 0.05)
- Temporal instability (pattern drift)

Key Features:
1. Sample Size Gate: Requires minimum 30 data points
2. Statistical Significance Gate: p-value < 0.05
3. Temporal Stability Gate: Recent vs older correlation consistency

Author: AI Trading System
Date: 2025-12-23
Phase: 25.1
"""

import logging
from typing import List, Tuple, Optional
import numpy as np
from scipy.stats import pearsonr
from datetime import datetime

logger = logging.getLogger(__name__)


class HallucinationDetector:
    """
    Base class for hallucination prevention in AI learning.
    
    Implements a 3-gate validation system to ensure only statistically
    valid patterns are learned by AI agents.
    
    Usage:
        detector = HallucinationDetector()
        is_valid, reason = detector.validate_pattern(predictions, outcomes)
        if is_valid:
            # Safe to learn from this pattern
            agent.update_weights(...)
        else:
            # Reject learning, log reason
            logger.warning(f"Pattern rejected: {reason}")
    """
    
    # Configuration constants
    MIN_SAMPLE_SIZE = 30
    MIN_P_VALUE = 0.05
    MAX_TEMPORAL_DRIFT = 0.30
    
    def __init__(
        self,
        min_sample_size: int = 30,
        min_p_value: float = 0.05,
        max_temporal_drift: float = 0.30
    ):
        """
        Initialize HallucinationDetector with custom thresholds.
        
        Args:
            min_sample_size: Minimum number of samples required (default: 30)
            min_p_value: Maximum p-value for significance (default: 0.05)
            max_temporal_drift: Maximum allowed correlation drift (default: 0.30)
        """
        self.min_sample_size = min_sample_size
        self.min_p_value = min_p_value
        self.max_temporal_drift = max_temporal_drift
        
        logger.info(
            f"HallucinationDetector initialized: "
            f"min_samples={min_sample_size}, "
            f"min_p={min_p_value}, "
            f"max_drift={max_temporal_drift}"
        )
    
    def validate_pattern(
        self,
        predictions: List[float],
        outcomes: List[float],
        verbose: bool = True
    ) -> Tuple[bool, str]:
        """
        Validate a learning pattern through 3 gates.
        
        Args:
            predictions: Agent's predictions (e.g., sentiment scores)
            outcomes: Actual outcomes (e.g., stock returns)
            verbose: Whether to log detailed gate results
        
        Returns:
            Tuple of (is_valid, reason)
            - is_valid: True if all gates passed
            - reason: Explanation of result
        
        Example:
            >>> predictions = [0.5, 0.7, 0.3, ...]  # 30+ predictions
            >>> outcomes = [0.02, 0.03, -0.01, ...]  # actual returns
            >>> is_valid, reason = detector.validate_pattern(predictions, outcomes)
            >>> print(reason)
            "Valid pattern (corr=0.68, p=0.0023)"
        """
        # Convert to numpy arrays for easier computation
        predictions = np.array(predictions)
        outcomes = np.array(outcomes)
        
        # Gate 1: Sample Size
        if len(predictions) < self.min_sample_size:
            reason = (
                f"Insufficient sample size: {len(predictions)} < {self.min_sample_size}. "
                f"Need more data to validate pattern."
            )
            if verbose:
                logger.warning(f"❌ Gate 1 FAILED: {reason}")
            return False, reason
        
        if verbose:
            logger.info(f"✅ Gate 1 PASSED: Sample size = {len(predictions)} >= {self.min_sample_size}")
        
        # Gate 2: Statistical Significance
        try:
            correlation, p_value = pearsonr(predictions, outcomes)
        except Exception as e:
            reason = f"Correlation calculation failed: {str(e)}"
            if verbose:
                logger.error(f"❌ Gate 2 ERROR: {reason}")
            return False, reason
        
        if p_value > self.min_p_value:
            reason = (
                f"Not statistically significant: p-value={p_value:.4f} > {self.min_p_value}. "
                f"Correlation (r={correlation:.3f}) may be due to random chance."
            )
            if verbose:
                logger.warning(f"❌ Gate 2 FAILED: {reason}")
            return False, reason
        
        if verbose:
            logger.info(
                f"✅ Gate 2 PASSED: p-value = {p_value:.4f} < {self.min_p_value}, "
                f"correlation = {correlation:.3f}"
            )
        
        # Gate 3: Temporal Stability
        # Check if pattern is stable over time (recent vs older data)
        if len(predictions) >= self.min_sample_size * 2:
            # We have enough data to check temporal stability
            midpoint = len(predictions) // 2
            
            # Recent data (second half)
            recent_predictions = predictions[midpoint:]
            recent_outcomes = outcomes[midpoint:]
            
            # Older data (first half)
            older_predictions = predictions[:midpoint]
            older_outcomes = outcomes[:midpoint]
            
            try:
                recent_corr, _ = pearsonr(recent_predictions, recent_outcomes)
                older_corr, _ = pearsonr(older_predictions, older_outcomes)
                
                correlation_drift = abs(recent_corr - older_corr)
                
                if correlation_drift > self.max_temporal_drift:
                    reason = (
                        f"Temporal instability detected: "
                        f"recent_corr={recent_corr:.3f}, older_corr={older_corr:.3f}, "
                        f"drift={correlation_drift:.3f} > {self.max_temporal_drift}. "
                        f"Pattern is not stable over time."
                    )
                    if verbose:
                        logger.warning(f"❌ Gate 3 FAILED: {reason}")
                    return False, reason
                
                if verbose:
                    logger.info(
                        f"✅ Gate 3 PASSED: Temporal stability OK "
                        f"(recent={recent_corr:.3f}, older={older_corr:.3f}, drift={correlation_drift:.3f})"
                    )
            except Exception as e:
                reason = f"Temporal stability check failed: {str(e)}"
                if verbose:
                    logger.error(f"❌ Gate 3 ERROR: {reason}")
                return False, reason
        else:
            # Not enough data for temporal check, but we passed other gates
            if verbose:
                logger.info(
                    f"⚠️  Gate 3 SKIPPED: Need {self.min_sample_size * 2}+ samples "
                    f"for temporal check (have {len(predictions)})"
                )
        
        # All gates passed!
        reason = (
            f"Valid pattern: correlation={correlation:.3f}, "
            f"p-value={p_value:.4f}, "
            f"n={len(predictions)}"
        )
        if verbose:
            logger.info(f"✅ ALL GATES PASSED: {reason}")
        
        return True, reason
    
    def _calc_correlation(
        self,
        predictions: np.ndarray,
        outcomes: np.ndarray
    ) -> float:
        """
        Helper method to calculate Pearson correlation coefficient.
        
        Args:
            predictions: Prediction values
            outcomes: Actual outcome values
        
        Returns:
            Correlation coefficient (-1 to 1)
        """
        try:
            corr, _ = pearsonr(predictions, outcomes)
            return corr
        except Exception as e:
            logger.error(f"Correlation calculation error: {e}")
            return 0.0
    
    def batch_validate(
        self,
        patterns: List[Tuple[List[float], List[float]]],
        labels: Optional[List[str]] = None
    ) -> List[Tuple[bool, str]]:
        """
        Validate multiple patterns in batch.
        
        Args:
            patterns: List of (predictions, outcomes) tuples
            labels: Optional labels for each pattern (for logging)
        
        Returns:
            List of (is_valid, reason) tuples
        
        Example:
            >>> patterns = [
            ...     ([0.5, 0.7, ...], [0.02, 0.03, ...]),  # Pattern 1
            ...     ([0.3, 0.4, ...], [-0.01, 0.01, ...]), # Pattern 2
            ... ]
            >>> results = detector.batch_validate(patterns, labels=["TechCrunch", "Reuters"])
            >>> for label, (is_valid, reason) in zip(labels, results):
            ...     print(f"{label}: {is_valid} - {reason}")
        """
        results = []
        
        for i, (predictions, outcomes) in enumerate(patterns):
            label = labels[i] if labels and i < len(labels) else f"Pattern_{i}"
            
            logger.info(f"🔍 Validating {label}...")
            is_valid, reason = self.validate_pattern(predictions, outcomes, verbose=True)
            results.append((is_valid, reason))
        
        # Summary
        valid_count = sum(1 for is_valid, _ in results if is_valid)
        logger.info(f"📊 Batch validation complete: {valid_count}/{len(patterns)} patterns valid")
        
        return results


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🧪 Testing HallucinationDetector\n")
    
    detector = HallucinationDetector()
    
    # Test 1: Valid pattern (strong correlation, large sample)
    print("Test 1: Valid pattern")
    np.random.seed(42)
    predictions = np.random.randn(50)
    outcomes = predictions * 0.7 + np.random.randn(50) * 0.3  # Strong correlation
    is_valid, reason = detector.validate_pattern(predictions.tolist(), outcomes.tolist())
    print(f"Result: {is_valid}")
    print(f"Reason: {reason}\n")
    
    # Test 2: Small sample (should fail)
    print("Test 2: Small sample")
    small_predictions = np.random.randn(20)
    small_outcomes = small_predictions * 0.8
    is_valid, reason = detector.validate_pattern(small_predictions.tolist(), small_outcomes.tolist())
    print(f"Result: {is_valid}")
    print(f"Reason: {reason}\n")
    
    # Test 3: Random noise (should fail p-value test)
    print("Test 3: Random noise")
    random_predictions = np.random.randn(50)
    random_outcomes = np.random.randn(50)
    is_valid, reason = detector.validate_pattern(random_predictions.tolist(), random_outcomes.tolist())
    print(f"Result: {is_valid}")
    print(f"Reason: {reason}\n")
