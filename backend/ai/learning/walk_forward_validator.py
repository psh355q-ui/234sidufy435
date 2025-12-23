"""
Walk-Forward Validator - Out-of-Sample Testing for AI Strategy Validation

This module implements walk-forward validation to prevent overfitting.
The key idea: Train on historical data, test on future unseen data.

Prevents:
- Curve fitting to training data
- Strategies that only work in specific market regimes
- Parameter optimization bias

Author: AI Trading System
Date: 2025-12-23
Phase: 25.1
"""

import logging
from typing import List, Dict, Tuple, Callable, Optional, Any
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class WalkForwardValidator:
    """
    Walk-forward validation for robustness testing.
    
    Process:
    1. Split data into training and testing windows
    2. Train strategy on training window
    3. Test on next unseen testing window
    4. Roll forward and repeat
    
    Example:
        Data: [Day 1 ------- Day 120]
        
        Window 1:
        Train: [Day 1-90]    Test: [Day 91-120]
        
        Window 2:
        Train: [Day 31-120]  Test: [Day 121-150]
        
        ...and so on
    """
    
    def __init__(
        self,
        train_window: int = 90,
        test_window: int = 30,
        min_win_rate: float = 0.55,
        step_size: Optional[int] = None
    ):
        """
        Initialize WalkForwardValidator.
        
        Args:
            train_window: Days of data for training (default: 90)
            test_window: Days of data for testing (default: 30)
            min_win_rate: Minimum acceptable win rate (default: 0.55 = 55%)
            step_size: How many days to roll forward (default: test_window)
        """
        self.train_window = train_window
        self.test_window = test_window
        self.min_win_rate = min_win_rate
        self.step_size = step_size if step_size else test_window
        
        logger.info(
            f"WalkForwardValidator initialized: "
            f"train={train_window}d, test={test_window}d, "
            f"min_win_rate={min_win_rate:.1%}, step={self.step_size}d"
        )
    
    def validate_strategy(
        self,
        historical_data: pd.DataFrame,
        strategy_func: Callable[[pd.DataFrame], pd.DataFrame],
        optimize_func: Optional[Callable[[pd.DataFrame], Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Run walk-forward validation on a trading strategy.
        
        Args:
            historical_data: DataFrame with columns ['date', 'price', 'signal', etc.]
            strategy_func: Function that takes DataFrame and returns predictions
                           def strategy_func(data: pd.DataFrame) -> pd.DataFrame:
                               return data_with_predictions
            optimize_func: Optional function to optimize parameters on training data
                          def optimize_func(train_data) -> Dict[str, Any]:
                              return {"param1": value1, ...}
        
        Returns:
            Dict with validation results:
            {
                "overall_win_rate": 0.62,
                "windows": [
                    {
                        "train_period": (start_date, end_date),
                        "test_period": (start_date, end_date),
                        "test_win_rate": 0.65,
                        "test_trades": 10,
                        "parameters": {...}
                    },
                    ...
                ],
                "is_valid": True,
                "reason": "Passed minimum win rate threshold"
            }
        
        Example:
            >>> def my_strategy(data):
            ...     data['prediction'] = data['rsi'] < 30  # Buy when RSI < 30
            ...     return data
            >>> 
            >>> validator = WalkForwardValidator(train_window=90, test_window=30)
            >>> results = validator.validate_strategy(historical_data, my_strategy)
            >>> print(f"Win rate: {results['overall_win_rate']:.1%}")
        """
        
        if len(historical_data) < self.train_window + self.test_window:
            reason = (
                f"Insufficient data: {len(historical_data)} rows < "
                f"{self.train_window + self.test_window} required"
            )
            logger.error(reason)
            return {
                "overall_win_rate": 0.0,
                "windows": [],
                "is_valid": False,
                "reason": reason
            }
        
        windows_results = []
        all_test_trades = []
        
        # Walk forward through data
        start_idx = 0
        window_num = 1
        
        while start_idx + self.train_window + self.test_window <= len(historical_data):
            # Split train/test
            train_end_idx = start_idx + self.train_window
            test_end_idx = train_end_idx + self.test_window
            
            train_data = historical_data.iloc[start_idx:train_end_idx].copy()
            test_data = historical_data.iloc[train_end_idx:test_end_idx].copy()
            
            train_period = (
                train_data.iloc[0]['date'] if 'date' in train_data.columns else start_idx,
                train_data.iloc[-1]['date'] if 'date' in train_data.columns else train_end_idx
            )
            test_period = (
                test_data.iloc[0]['date'] if 'date' in test_data.columns else train_end_idx,
                test_data.iloc[-1]['date'] if 'date' in test_data.columns else test_end_idx
            )
            
            logger.info(f"Window {window_num}: Train {train_period}, Test {test_period}")
            
            # Optimize parameters on training data (if optimize_func provided)
            parameters = {}
            if optimize_func:
                try:
                    parameters = optimize_func(train_data)
                    logger.info(f"Optimized parameters: {parameters}")
                except Exception as e:
                    logger.error(f"Parameter optimization failed: {e}")
                    parameters = {}
            
            # Apply strategy to test data (out-of-sample!)
            try:
                test_predictions = strategy_func(test_data)
                
                # Calculate test performance
                test_metrics = self._calculate_metrics(test_predictions)
                
                windows_results.append({
                    "window_num": window_num,
                    "train_period": train_period,
                    "test_period": test_period,
                    "test_win_rate": test_metrics["win_rate"],
                    "test_trades": test_metrics["n_trades"],
                    "test_avg_return": test_metrics["avg_return"],
                    "parameters": parameters
                })
                
                all_test_trades.extend(test_metrics["trades"])
                
                logger.info(
                    f"Window {window_num} results: "
                    f"Win rate={test_metrics['win_rate']:.1%}, "
                    f"Trades={test_metrics['n_trades']}"
                )
                
            except Exception as e:
                logger.error(f"Strategy application failed on window {window_num}: {e}")
            
            # Roll forward
            start_idx += self.step_size
            window_num += 1
        
        # Calculate overall metrics
        if not windows_results:
            return {
                "overall_win_rate": 0.0,
                "windows": [],
                "is_valid": False,
                "reason": "No windows completed successfully"
            }
        
        overall_win_rate = np.mean([w["test_win_rate"] for w in windows_results])
        is_valid = overall_win_rate >= self.min_win_rate
        
        reason = (
            f"Overall win rate: {overall_win_rate:.1%} "
            f"{'≥' if is_valid else '<'} {self.min_win_rate:.1%} threshold"
        )
        
        logger.info(
            f"Walk-forward validation complete: {len(windows_results)} windows, "
            f"{reason}, valid={is_valid}"
        )
        
        return {
            "overall_win_rate": overall_win_rate,
            "n_windows": len(windows_results),
            "windows": windows_results,
            "is_valid": is_valid,
            "reason": reason
        }
    
    def _calculate_metrics(self, predictions_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate performance metrics from predictions DataFrame.
        
        Expected columns:
        - 'prediction': Boolean or int (1=buy, 0=hold, -1=sell)
        - 'return': Actual return achieved
        
        Returns:
            Dict with metrics: win_rate, n_trades, avg_return, trades
        """
        # Handle missing columns
        if 'prediction' not in predictions_df.columns:
            logger.warning("No 'prediction' column found")
            return {
                "win_rate": 0.0,
                "n_trades": 0,
                "avg_return": 0.0,
                "trades": []
            }
        
        # Filter to actual trades (prediction != 0/False)
        if predictions_df['prediction'].dtype == bool:
            trades = predictions_df[predictions_df['prediction'] == True]
        else:
            trades = predictions_df[predictions_df['prediction'] != 0]
        
        if len(trades) == 0:
            return {
                "win_rate": 0.0,
                "n_trades": 0,
                "avg_return": 0.0,
                "trades": []
            }
        
        # Calculate metrics
        if 'return' in trades.columns:
            returns = trades['return'].values
            winning_trades = np.sum(returns > 0)
            win_rate = winning_trades / len(returns)
            avg_return = np.mean(returns)
        else:
            logger.warning("No 'return' column found, assuming 50% win rate")
            win_rate = 0.5
            avg_return = 0.0
            returns = []
        
        return {
            "win_rate": win_rate,
            "n_trades": len(trades),
            "avg_return": avg_return,
            "trades": returns.tolist()
        }
    
    def validate_across_regimes(
        self,
        historical_data: pd.DataFrame,
        strategy_func: Callable,
        regime_column: str = "regime"
    ) -> Dict[str, Any]:
        """
        Validate strategy across different market regimes (bull/bear/sideways).
        
        Args:
            historical_data: DataFrame with regime labels
            strategy_func: Trading strategy function
            regime_column: Column name containing regime labels
        
        Returns:
            Dict with per-regime performance
        
        Example:
            >>> data['regime'] = ['bull', 'bull', 'bear', 'sideways', ...]
            >>> results = validator.validate_across_regimes(data, my_strategy)
            >>> for regime, metrics in results['regimes'].items():
            ...     print(f"{regime}: {metrics['win_rate']:.1%}")
        """
        if regime_column not in historical_data.columns:
            logger.error(f"Regime column '{regime_column}' not found")
            return {
                "regimes": {},
                "is_valid": False,
                "reason": f"Regime column '{regime_column}' not found"
            }
        
        regimes = historical_data[regime_column].unique()
        regime_results = {}
        
        for regime in regimes:
            regime_data = historical_data[historical_data[regime_column] == regime]
            
            if len(regime_data) < self.test_window:
                logger.warning(f"Insufficient data for regime '{regime}': {len(regime_data)} rows")
                continue
            
            # Apply strategy
            try:
                predictions = strategy_func(regime_data)
                metrics = self._calculate_metrics(predictions)
                
                regime_results[regime] = metrics
                
                logger.info(
                    f"Regime '{regime}': Win rate={metrics['win_rate']:.1%}, "
                    f"Trades={metrics['n_trades']}"
                )
            except Exception as e:
                logger.error(f"Strategy failed on regime '{regime}': {e}")
        
        # Check if strategy works in ALL regimes
        min_regime_win_rate = 0.52  # At least 52% in each regime
        is_valid = all(
            metrics["win_rate"] >= min_regime_win_rate 
            for metrics in regime_results.values()
        )
        
        reason = (
            f"Strategy {'passes' if is_valid else 'fails'} across all regimes "
            f"(min {min_regime_win_rate:.0%} per regime)"
        )
        
        return {
            "regimes": regime_results,
            "is_valid": is_valid,
            "reason": reason
        }


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🧪 Testing WalkForwardValidator\n")
    
    # Create sample data
    np.random.seed(42)
    n_days = 200
    dates = pd.date_range(start='2024-01-01', periods=n_days, freq='D')
    
    data = pd.DataFrame({
        'date': dates,
        'price': 100 + np.cumsum(np.random.randn(n_days) * 0.5),
        'rsi': np.random.randint(20, 80, n_days)
    })
    
    # Simple strategy: Buy when RSI < 30
    def simple_strategy(df):
        df = df.copy()
        df['prediction'] = df['rsi'] < 30
        # Simulate returns (for demo)
        df['return'] = np.where(df['prediction'], np.random.randn(len(df)) * 0.02 + 0.01, 0)
        return df
    
    # Run validation
    validator = WalkForwardValidator(train_window=90, test_window=30)
    results = validator.validate_strategy(data, simple_strategy)
    
    print(f"\nResults:")
    print(f"Overall win rate: {results['overall_win_rate']:.1%}")
    print(f"Number of windows: {results['n_windows']}")
    print(f"Valid: {results['is_valid']}")
    print(f"Reason: {results['reason']}")
    
    print(f"\nPer-window results:")
    for window in results['windows']:
        print(
            f"Window {window['window_num']}: "
            f"Test win rate={window['test_win_rate']:.1%}, "
            f"Trades={window['test_trades']}"
        )
