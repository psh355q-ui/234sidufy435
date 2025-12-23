"""
RiskAgent Learning - Stress Testing and VaR Calibration

This module implements self-learning for the RiskAgent with tail risk protection.

Key Features:
- VaR (Value at Risk) model calibration
- Stress scenario testing
- Tail event tracking
- Crisis-period learning prohibition

Learning Process:
1. Only learn during volatile periods (prevents calm-period bias)
2. Test VaR model against historical stress scenarios
3. Track tail events (>3 sigma moves)
4. Update VaR only if stress tests pass

Author: AI Trading System
Date: 2025-12-23
Phase: 25.2
"""

import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy import stats

from backend.ai.learning.hallucination_detector import HallucinationDetector

logger = logging.getLogger(__name__)


class RiskAgentLearning:
    """
    Self-learning system for RiskAgent with crisis protection.
    
    Prevents:
    - Learning during calm periods (underestimates risk)
    - Tail risk underestimation
    - VaR models that fail in crises
    
    Example:
        learner = RiskAgentLearning()
        
        # Historical returns
        returns = [0.01, 0.02, -0.03, ..., -0.35]  # Include crisis!
        
        success, new_var = learner.calibrate_var_model(returns)
        if success:
            print(f"New VaR (95%): {new_var:.2%}")
    """
    
    # Historical stress scenarios
    STRESS_SCENARIOS = [
        {"name": "COVID-19", "max_drawdown": -0.35, "duration_days": 30},
        {"name": "2008 Crisis", "max_drawdown": -0.50, "duration_days": 180},
        {"name": "Flash Crash", "max_drawdown": -0.10, "duration_days": 1},
        {"name": "Dot-com Bust", "max_drawdown": -0.78, "duration_days": 900}
    ]
    
    def __init__(
        self,
        min_volatility: float =0.15,
        confidence_level: float = 0.95,
        min_stress_pass_rate: float = 0.75
    ):
        """
        Initialize RiskAgent learning system.
        
        Args:
            min_volatility: Minimum volatility required to learn (default: 0.15 = 15%)
            confidence_level: VaR confidence level (default: 0.95 = 95%)
            min_stress_pass_rate: Min scenarios to pass (default: 0.75 = 75%)
        """
        self.min_volatility = min_volatility
        self.confidence_level = confidence_level
        self.min_stress_pass_rate = min_stress_pass_rate
        
        # Current VaR parameters
        self.var_params = {
            "confidence_level": confidence_level,
            "method": "historical",
            "lookback_days": 90
        }
        
        # Tail event tracking
        self.tail_events: List[Dict] = []
        
        # Learning history
        self.learning_history: List[Dict] = []
        
        logger.info(
            f"RiskAgentLearning initialized: "
            f"min_vol={min_volatility:.1%}, "
            f"confidence={confidence_level:.1%}"
        )
    
    def calibrate_var_model(
        self,
        historical_returns: List[float],
        verbose: bool = True
    ) -> Tuple[bool, Optional[float]]:
        """
        Calibrate VaR model with stress test validation.
        
        Args:
            historical_returns: Historical daily returns
            verbose: Whether to log details
        
        Returns:
            Tuple of (success, new_var)
            Returns VaR as positive number (e.g., 0.05 = 5% loss)
        
        Example:
            >>> returns = [-0.01, 0.02, -0.35, ...]  # Include crisis
            >>> success, var = learner.calibrate_var_model(returns)
            >>> if success:
            ...     print(f"VaR (95%): -{var:.2%}")
        """
        if verbose:
            logger.info(f"🧠 Calibrating VaR model ({len(historical_returns)} samples)")
        
        returns = np.array(historical_returns)
        
        # Gate 1: Only learn during volatile periods
        recent_volatility = np.std(returns[-90:]) if len(returns) >= 90 else np.std(returns)
        
        if recent_volatility < self.min_volatility:
            reason = (
                f"Volatility too low: {recent_volatility:.1%} < {self.min_volatility:.1%}. "
                f"Cannot calibrate VaR during calm periods (risk underestimation)."
            )
            if verbose:
                logger.warning(f"❌ VaR calibration rejected: {reason}")
            
            self.learning_history.append({
                "timestamp": datetime.now(),
                "action": "rejected",
                "reason": reason,
                "volatility": recent_volatility
            })
            
            return False, None
        
        if verbose:
            logger.info(f"✅ Gate 1 passed: Volatility = {recent_volatility:.1%} >= {self.min_volatility:.1%}")
        
        # Calculate VaR (historical method)
        var_percentile = (1 - self.confidence_level) * 100
        var_value = -np.percentile(returns, var_percentile)  # Negative for loss
        
        # Gate 2: Stress test against historical scenarios
        stress_test_results = []
        
        for scenario in self.STRESS_SCENARIOS:
            # Simulate scenario
            scenario_return = scenario["max_drawdown"]
            
            # Check if VaR would have warned us
            if var_value >= abs(scenario_return):
                # VaR captured this scenario ✅
                stress_test_results.append(True)
                if verbose:
                    logger.info(
                        f"✅ Stress test passed: {scenario['name']} "
                        f"(VaR={var_value:.1%} >= loss={abs(scenario_return):.1%})"
                    )
            else:
                # VaR failed to capture this scenario ❌
                stress_test_results.append(False)
                if verbose:
                    logger.warning(
                        f"❌ Stress test failed: {scenario['name']} "
                        f"(VaR={var_value:.1%} < loss={abs(scenario_return):.1%})"
                    )
        
        pass_rate = sum(stress_test_results) / len(stress_test_results)
        
        if pass_rate < self.min_stress_pass_rate:
            reason = (
                f"Stress test failure: {pass_rate:.0%} < {self.min_stress_pass_rate:.0%}. "
                f"VaR model fails to capture historical crises."
            )
            if verbose:
                logger.warning(f"❌ Gate 2 failed: {reason}")
            
            self.learning_history.append({
                "timestamp": datetime.now(),
                "action": "rejected",
                "reason": reason,
                "var_value": var_value,
                "stress_pass_rate": pass_rate
            })
            
            return False, None
        
        if verbose:
            logger.info(
                f"✅ Gate 2 passed: Stress test pass rate = {pass_rate:.0%} "
                f">= {self.min_stress_pass_rate:.0%}"
            )
        
        # All gates passed!
        if verbose:
            logger.info(
                f"✅ VaR calibration accepted: "
                f"VaR({self.confidence_level:.0%}) = {var_value:.2%}"
            )
        
        self.learning_history.append({
            "timestamp": datetime.now(),
            "action": "calibrated",
            "var_value": var_value,
            "volatility": recent_volatility,
            "stress_pass_rate": pass_rate
        })
        
        return True, var_value
    
    def track_tail_event(
        self,
        return_value: float,
        expected_volatility: float,
        verbose: bool = True
    ):
        """
        Track tail events (>3 sigma moves).
        
        Args:
            return_value: Actual return observed
            expected_volatility: Expected volatility (std dev)
            verbose: Log details
        
        Example:
            >>> learner.track_tail_event(return_value=-0.10, expected_volatility=0.02)
            # -10% move when expecting 2% vol = 5 sigma event!
        """
        if expected_volatility == 0:
            logger.warning("Expected volatility is zero, cannot calculate sigma")
            return
        
        # Calculate how many sigmas this move was
        sigma_level = abs(return_value) / expected_volatility
        
        if sigma_level > 3.0:
            # Tail event detected!
            self.tail_events.append({
                "timestamp": datetime.now(),
                "return": return_value,
                "expected_vol": expected_volatility,
                "sigma_level": sigma_level
            })
            
            if verbose:
                logger.warning(
                    f"⚠️  Tail event detected: {return_value:.2%} return "
                    f"({sigma_level:.1f}σ move, expected vol={expected_volatility:.2%})"
                )
    
    def get_tail_event_frequency(self, days: int = 365) -> float:
        """
        Get frequency of tail events (>3σ) over recent period.
        
        Args:
            days: Lookback period
        
        Returns:
            Frequency (events per day)
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent_events = [e for e in self.tail_events if e['timestamp'] >= cutoff]
        
        return len(recent_events) / days
    
    def get_learning_summary(self) -> Dict:
        """Get learning summary."""
        total_attempts = len(self.learning_history)
        calibrated = sum(1 for h in self.learning_history if h['action'] == 'calibrated')
        
        return {
            "current_var_params": self.var_params.copy(),
            "total_attempts": total_attempts,
            "successful_calibrations": calibrated,
            "rejected_calibrations": total_attempts - calibrated,
            "success_rate": calibrated / total_attempts if total_attempts > 0 else 0.0,
            "tail_events_tracked": len(self.tail_events),
            "tail_event_frequency_365d": self.get_tail_event_frequency(365),
            "recent_history": self.learning_history[-5:]
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🧪 Testing RiskAgentLearning\n")
    
    learner = RiskAgentLearning()
    
    # Test 1: Calm market (should reject)
    print("Test 1: Calm market")
    np.random.seed(42)
    calm_returns = np.random.randn(100) * 0.01  # 1% daily vol (calm)
    success, var = learner.calibrate_var_model(calm_returns.tolist())
    print(f"Result: {success} (expected: False)\n")
    
    # Test 2: Volatile market with crisis
    print("Test 2: Volatile market with crisis")
    volatile_returns = list(np.random.randn(200) * 0.03)  # 3% daily vol
    volatile_returns += [-0.10, -0.15, -0.35]  # Add crisis events
    
    success, var = learner.calibrate_var_model(volatile_returns)
    print(f"Result: {success}")
    if success:
        print(f"VaR (95%): {var:.2%}\n")
    
    # Track tail event
    learner.track_tail_event(return_value=-0.35, expected_volatility=0.03)
    
    # Summary
    summary = learner.get_learning_summary()
    print(f"Learning summary:")
    print(f"Calibrations: {summary['successful_calibrations']}/{summary['total_attempts']}")
    print(f"Tail events: {summary['tail_events_tracked']}")
