"""
Statistical Validators - Advanced Statistical Testing Tools

This module provides statistical testing utilities for validating
AI learning patterns beyond basic correlation tests.

Key Features:
- Bootstrap significance testing
- T-test for mean differences
- Mann-Whitney U test (non-parametric)
- Chi-square test for categorical data
- Effect size calculations (Cohen's d)

Author: AI Trading System
Date: 2025-12-23
Phase: 25.1
"""

import logging
from typing import List, Tuple, Optional
import numpy as np
from scipy import stats
from scipy.stats import pearsonr, spearmanr, ttest_ind, mannwhitneyu, chi2_contingency

logger = logging.getLogger(__name__)


class StatisticalValidators:
    """
    Collection of statistical validation tools for AI learning safety.
    
    These tools provide additional layers of validation beyond basic
    correlation testing to ensure patterns are robust and reproducible.
    """
    
    @staticmethod
    def bootstrap_significance(
        data: List[float],
        statistic_func: callable = np.mean,
        n_iterations: int = 1000,
        confidence_level: float = 0.95,
        random_seed: Optional[int] = None
    ) -> Tuple[float, Tuple[float, float], float]:
        """
        Bootstrap resampling to estimate sampling distribution and confidence intervals.
        
        Useful for:
        - Small sample sizes
        - Non-normal distributions
        - Custom statistics (not just mean)
        
        Args:
            data: Original sample data
            statistic_func: Function to calculate statistic (default: mean)
            n_iterations: Number of bootstrap samples (default: 1000)
            confidence_level: Confidence level for intervals (default: 0.95)
            random_seed: Random seed for reproducibility
        
        Returns:
            Tuple of (observed_statistic, confidence_interval, p_value)
        
        Example:
            >>> returns = [0.02, 0.03, -0.01, 0.04, ...]
            >>> stat, (lower, upper), p_val = bootstrap_significance(returns)
            >>> print(f"Mean return: {stat:.3f}, 95% CI: [{lower:.3f}, {upper:.3f}]")
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        data = np.array(data)
        n = len(data)
        
        # Calculate observed statistic
        observed_stat = statistic_func(data)
        
        # Bootstrap resampling
        bootstrap_stats = []
        for _ in range(n_iterations):
            # Resample with replacement
            resample = np.random.choice(data, size=n, replace=True)
            bootstrap_stat = statistic_func(resample)
            bootstrap_stats.append(bootstrap_stat)
        
        bootstrap_stats = np.array(bootstrap_stats)
        
        # Calculate confidence interval
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        confidence_interval = (
            np.percentile(bootstrap_stats, lower_percentile),
            np.percentile(bootstrap_stats, upper_percentile)
        )
        
        # Calculate p-value (two-tailed test against zero)
        # p-value = proportion of bootstrap samples with opposite sign
        if observed_stat >= 0:
            p_value = np.mean(bootstrap_stats <= 0) * 2
        else:
            p_value = np.mean(bootstrap_stats >= 0) * 2
        
        p_value = min(p_value, 1.0)  # Cap at 1.0
        
        logger.info(
            f"Bootstrap test: stat={observed_stat:.4f}, "
            f"CI=[{confidence_interval[0]:.4f}, {confidence_interval[1]:.4f}], "
            f"p={p_value:.4f}"
        )
        
        return observed_stat, confidence_interval, p_value
    
    @staticmethod
    def t_test_significance(
        group1: List[float],
        group2: List[float],
        alpha: float = 0.05
    ) -> Tuple[float, float, bool, float]:
        """
        Independent t-test to compare means of two groups.
        
        Useful for:
        - Comparing agent performance (before vs after learning)
        - A/B testing strategies
        - Comparing returns across market regimes
        
        Args:
            group1: First group (e.g., returns before learning)
            group2: Second group (e.g., returns after learning)
            alpha: Significance level (default: 0.05)
        
        Returns:
            Tuple of (t_statistic, p_value, is_significant, effect_size)
        
        Example:
            >>> before_learning = [0.01, 0.02, -0.01, ...]
            >>> after_learning = [0.03, 0.04, 0.02, ...]
            >>> t_stat, p_val, is_sig, effect = t_test_significance(before_learning, after_learning)
            >>> if is_sig:
            ...     print(f"Improvement is significant! Effect size: {effect:.2f}")
        """
        group1 = np.array(group1)
        group2 = np.array(group2)
        
        # Perform independent t-test
        t_statistic, p_value = ttest_ind(group1, group2)
        
        # Check significance
        is_significant = p_value < alpha
        
        # Calculate Cohen's d (effect size)
        mean1, mean2 = np.mean(group1), np.mean(group2)
        std1, std2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
        
        pooled_std = np.sqrt(((len(group1) - 1) * std1**2 + (len(group2) - 1) * std2**2) / 
                             (len(group1) + len(group2) - 2))
        
        cohens_d = (mean2 - mean1) / pooled_std if pooled_std > 0 else 0.0
        
        logger.info(
            f"T-test: t={t_statistic:.3f}, p={p_value:.4f}, "
            f"significant={is_significant}, Cohen's d={cohens_d:.3f}"
        )
        
        return t_statistic, p_value, is_significant, cohens_d
    
    @staticmethod
    def mann_whitney_test(
        group1: List[float],
        group2: List[float],
        alpha: float = 0.05
    ) -> Tuple[float, float, bool]:
        """
        Mann-Whitney U test (non-parametric alternative to t-test).
        
        Useful for:
        - Non-normal distributions
        - Ordinal data
        - Robust to outliers
        
        Args:
            group1: First group
            group2: Second group
            alpha: Significance level
        
        Returns:
            Tuple of (u_statistic, p_value, is_significant)
        
        Example:
            >>> old_strategy = [0.01, 0.02, 0.15, ...]  # Has outliers
            >>> new_strategy = [0.03, 0.04, 0.02, ...]
            >>> u_stat, p_val, is_sig = mann_whitney_test(old_strategy, new_strategy)
        """
        group1 = np.array(group1)
        group2 = np.array(group2)
        
        # Perform Mann-Whitney U test
        u_statistic, p_value = mannwhitneyu(group1, group2, alternative='two-sided')
        
        is_significant = p_value < alpha
        
        logger.info(
            f"Mann-Whitney test: U={u_statistic:.3f}, p={p_value:.4f}, "
            f"significant={is_significant}"
        )
        
        return u_statistic, p_value, is_significant
    
    @staticmethod
    def spearman_correlation(
        predictions: List[float],
        outcomes: List[float],
        alpha: float = 0.05
    ) -> Tuple[float, float, bool]:
        """
        Spearman rank correlation (non-parametric alternative to Pearson).
        
        Useful for:
        - Non-linear monotonic relationships
        - Ordinal data
        - Robust to outliers
        
        Args:
            predictions: Predicted values
            outcomes: Actual outcome values
            alpha: Significance level
        
        Returns:
            Tuple of (rho, p_value, is_significant)
        
        Example:
            >>> sentiment_scores = [0.5, 0.7, 0.3, ...]
            >>> returns = [0.02, 0.05, -0.01, ...]  # May have outliers
            >>> rho, p_val, is_sig = spearman_correlation(sentiment_scores, returns)
        """
        predictions = np.array(predictions)
        outcomes = np.array(outcomes)
        
        # Calculate Spearman's rho
        rho, p_value = spearmanr(predictions, outcomes)
        
        is_significant = p_value < alpha
        
        logger.info(
            f"Spearman correlation: rho={rho:.3f}, p={p_value:.4f}, "
            f"significant={is_significant}"
        )
        
        return rho, p_value, is_significant
    
    @staticmethod
    def rolling_correlation_stability(
        predictions: List[float],
        outcomes: List[float],
        window_size: int = 15,
        max_std: float = 0.15
    ) -> Tuple[bool, float, List[float]]:
        """
        Check if correlation is stable across rolling windows.
        
        Useful for detecting:
        - Regime changes
        - Pattern degradation
        - Overfitting to recent data
        
        Args:
            predictions: Predicted values
            outcomes: Actual outcomes
            window_size: Size of rolling window
            max_std: Maximum allowed standard deviation of correlations
        
        Returns:
            Tuple of (is_stable, correlation_std, rolling_correlations)
        
        Example:
            >>> predictions = [...]  # 60+ predictions
            >>> outcomes = [...]
            >>> is_stable, std, corrs = rolling_correlation_stability(predictions, outcomes)
            >>> if not is_stable:
            ...     print(f"Pattern unstable! Correlation std: {std:.3f}")
        """
        predictions = np.array(predictions)
        outcomes = np.array(outcomes)
        
        if len(predictions) < window_size * 2:
            logger.warning(
                f"Insufficient data for rolling correlation: "
                f"{len(predictions)} < {window_size * 2}"
            )
            return True, 0.0, []  # Not enough data to check, assume stable
        
        # Calculate rolling correlations
        rolling_corrs = []
        for i in range(len(predictions) - window_size + 1):
            window_preds = predictions[i:i+window_size]
            window_outcomes = outcomes[i:i+window_size]
            
            try:
                corr, _ = pearsonr(window_preds, window_outcomes)
                rolling_corrs.append(corr)
            except Exception as e:
                logger.warning(f"Rolling correlation calculation error: {e}")
                continue
        
        if not rolling_corrs:
            return True, 0.0, []
        
        # Calculate stability (standard deviation of rolling correlations)
        correlation_std = np.std(rolling_corrs)
        is_stable = correlation_std <= max_std
        
        logger.info(
            f"Rolling correlation stability: std={correlation_std:.3f}, "
            f"stable={is_stable}, n_windows={len(rolling_corrs)}"
        )
        
        return is_stable, correlation_std, rolling_corrs
    
    @staticmethod
    def detect_outliers(
        data: List[float],
        method: str = "iqr",
        threshold: float = 1.5
    ) -> Tuple[List[int], List[float]]:
        """
        Detect outliers in data using IQR or Z-score method.
        
        Args:
            data: Input data
            method: "iqr" (Interquartile Range) or "zscore"
            threshold: Threshold for outlier detection
                      - For IQR: typically 1.5 or 3.0
                      - For Z-score: typically 3.0
        
        Returns:
            Tuple of (outlier_indices, outlier_values)
        
        Example:
            >>> returns = [0.01, 0.02, 0.15, -0.01, ...]  # 0.15 is outlier
            >>> indices, values = detect_outliers(returns, method="iqr")
            >>> print(f"Found {len(indices)} outliers: {values}")
        """
        data = np.array(data)
        
        if method == "iqr":
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            
            outlier_mask = (data < lower_bound) | (data > upper_bound)
        
        elif method == "zscore":
            mean = np.mean(data)
            std = np.std(data)
            
            if std == 0:
                logger.warning("Zero standard deviation, no outliers detected")
                return [], []
            
            z_scores = np.abs((data - mean) / std)
            outlier_mask = z_scores > threshold
        
        else:
            raise ValueError(f"Unknown method: {method}. Use 'iqr' or 'zscore'.")
        
        outlier_indices = np.where(outlier_mask)[0].tolist()
        outlier_values = data[outlier_mask].tolist()
        
        logger.info(
            f"Outlier detection ({method}): found {len(outlier_indices)} outliers "
            f"out of {len(data)} samples"
        )
        
        return outlier_indices, outlier_values


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🧪 Testing StatisticalValidators\n")
    
    # Test 1: Bootstrap significance
    print("Test 1: Bootstrap test")
    np.random.seed(42)
    sample_data = np.random.randn(30) + 0.5  # Mean around 0.5
    stat, ci, p_val = StatisticalValidators.bootstrap_significance(sample_data, n_iterations=1000)
    print(f"Observed mean: {stat:.3f}")
    print(f"95% CI: [{ci[0]:.3f}, {ci[1]:.3f}]")
    print(f"P-value: {p_val:.4f}\n")
    
    # Test 2: T-test
    print("Test 2: T-test")
    group1 = np.random.randn(30)
    group2 = np.random.randn(30) + 0.5  # Slightly higher mean
    t_stat, p_val, is_sig, effect = StatisticalValidators.t_test_significance(group1.tolist(), group2.tolist())
    print(f"T-statistic: {t_stat:.3f}")
    print(f"P-value: {p_val:.4f}")
    print(f"Significant: {is_sig}")
    print(f"Effect size (Cohen's d): {effect:.3f}\n")
    
    # Test 3: Outlier detection
    print("Test 3: Outlier detection")
    data_with_outliers = np.concatenate([np.random.randn(40), [10, -10]])  # Add 2 outliers
    indices, values = StatisticalValidators.detect_outliers(data_with_outliers.tolist())
    print(f"Found {len(indices)} outliers: {values}")
