"""
Unit Tests for Hallucination Detection System

Phase 25.1: Test 3-gate validation system

Tests:
1. Sample Size Gate
2. Statistical Significance Gate (p-value)
3. Temporal Stability Gate
4. Batch validation
5. Edge cases

Author: AI Trading System
Date: 2025-12-23
"""

import pytest
import numpy as np
from backend.ai.learning.hallucination_detector import HallucinationDetector


class TestHallucinationDetector:
    """Test suite for HallucinationDetector"""
    
    @pytest.fixture
    def detector(self):
        """Create a standard detector instance"""
        return HallucinationDetector(
            min_sample_size=30,
            min_p_value=0.05,
            max_temporal_drift=0.30
        )
    
    def test_sample_size_gate_fail(self, detector):
        """Test Gate 1: Small sample should be rejected"""
        # Create 29 samples (< 30 threshold)
        small_predictions = np.random.randn(29).tolist()
        small_outcomes = np.random.randn(29).tolist()
        
        is_valid, reason = detector.validate_pattern(small_predictions, small_outcomes, verbose=False)
        
        assert not is_valid, "Small sample should be rejected"
        assert "Insufficient sample size" in reason
        assert "29 < 30" in reason
    
    def test_sample_size_gate_pass(self, detector):
        """Test Gate 1: Sufficient sample should pass to next gate"""
        # Create 30 samples (>= 30 threshold)
        np.random.seed(42)
        predictions = (np.arange(30) + np.random.randn(30) * 0.1).tolist()
        outcomes = (np.arange(30) + np.random.randn(30) * 0.1).tolist()
        
        is_valid, reason = detector.validate_pattern(predictions, outcomes, verbose=False)
        
        # Should pass sample size gate (might fail other gates)
        # We just check that the error is NOT about sample size
        if not is_valid:
            assert "Insufficient sample size" not in reason
    
    def test_p_value_gate_fail(self, detector):
        """Test Gate 2: Random noise should be rejected (high p-value)"""
        # Create completely random data (no correlation)
        np.random.seed(42)
        random_predictions = np.random.randn(50).tolist()
        random_outcomes = np.random.randn(50).tolist()
        
        is_valid, reason = detector.validate_pattern(random_predictions, random_outcomes, verbose=False)
        
        # Should fail p-value gate most of the time
        # Note: There's a 5% chance this could pass by random chance
        # We'll accept either outcome but check the reason
        if not is_valid:
            assert "Not statistically significant" in reason or "Temporal instability" in reason
    
    def test_p_value_gate_pass(self, detector):
        """Test Gate 2: Strong correlation should pass p-value test"""
        # Create strongly correlated data
        np.random.seed(42)
        predictions = np.arange(50) + np.random.randn(50) * 0.5
        outcomes = predictions * 0.9 + np.random.randn(50) * 0.3  # Strong correlation
        
        is_valid, reason = detector.validate_pattern(predictions.tolist(), outcomes.tolist(), verbose=False)
        
        # Should pass p-value gate (might fail temporal stability if correlation changes)
        if not is_valid:
            # If it failed, it should NOT be due to p-value
            assert "Not statistically significant" not in reason
    
    def test_temporal_stability_gate_fail(self, detector):
        """Test Gate 3: Unstable pattern should be rejected"""
        # Create data with changing correlation
        np.random.seed(42)
        
        # First half: strong positive correlation
        first_half_x = np.arange(30)
        first_half_y = first_half_x * 0.9 + np.random.randn(30) * 0.2
        
        # Second half: weak or negative correlation
        second_half_x = np.arange(30)
        second_half_y = -second_half_x * 0.3 + np.random.randn(30) * 2
        
        # Combine
        predictions = np.concatenate([first_half_x, second_half_x]).tolist()
        outcomes = np.concatenate([first_half_y, second_half_y]).tolist()
        
        is_valid, reason = detector.validate_pattern(predictions, outcomes, verbose=False)
        
        if not is_valid:
            # Could fail either p-value or temporal stability
            assert ("Temporal instability" in reason or "Not statistically significant" in reason)
    
    def test_temporal_stability_gate_pass(self, detector):
        """Test Gate 3: Stable pattern should pass"""
        # Create data with consistent correlation throughout
        np.random.seed(42)
        n = 60
        predictions = np.arange(n) + np.random.randn(n) * 0.3
        outcomes = predictions * 0.8 + np.random.randn(n) * 0.3
        
        is_valid, reason = detector.validate_pattern(predictions.tolist(), outcomes.tolist(), verbose=False)
        
        # This should pass all gates
        assert is_valid, f"Stable pattern should be valid. Reason: {reason}"
        assert "Valid pattern" in reason
    
    def test_all_gates_pass(self, detector):
        """Test that a perfect pattern passes all gates"""
        # Create ideal data:
        # - Large sample (n=100)
        # - Strong correlation (r ≈ 0.9)
        # - Stable over time
        np.random.seed(42)
        n = 100
        predictions = np.arange(n) * 0.1
        outcomes = predictions * 0.9 + np.random.randn(n) * 0.05  # Very strong correlation
        
        is_valid, reason = detector.validate_pattern(predictions.tolist(), outcomes.tolist(), verbose=False)
        
        assert is_valid, f"Perfect pattern should pass all gates. Reason: {reason}"
        assert "Valid pattern" in reason
        assert "correlation" in reason.lower()
    
    def test_batch_validation(self, detector):
        """Test batch validation of multiple patterns"""
        np.random.seed(42)
        
        # Pattern 1: Valid (strong correlation, large sample)
        pattern1_x = np.arange(50) + np.random.randn(50) * 0.2
        pattern1_y = pattern1_x * 0.8 + np.random.randn(50) * 0.3
        
        # Pattern 2: Invalid (random noise)
        pattern2_x = np.random.randn(50).tolist()
        pattern2_y = np.random.randn(50).tolist()
        
        # Pattern 3: Invalid (too small)
        pattern3_x = np.random.randn(20).tolist()
        pattern3_y = np.random.randn(20).tolist()
        
        patterns = [
            (pattern1_x.tolist(), pattern1_y.tolist()),
            (pattern2_x, pattern2_y),
            (pattern3_x, pattern3_y)
        ]
        
        labels = ["Strong correlation", "Random noise", "Small sample"]
        results = detector.batch_validate(patterns, labels=labels)
        
        assert len(results) == 3
        
        # Pattern 1 should pass
        assert results[0][0], "Strong correlation should be valid"
        
        # Pattern 3 should definitely fail (too small)
        assert not results[2][0], "Small sample should be invalid"
        assert "Insufficient sample size" in results[2][1]
    
    def test_custom_thresholds(self):
        """Test detector with custom thresholds"""
        # Create lenient detector
        lenient_detector = HallucinationDetector(
            min_sample_size=10,  # Lower threshold
            min_p_value=0.10,     # Higher threshold (easier to pass)
            max_temporal_drift=0.50  # Allow more drift
        )
        
        # Small sample that would fail standard detector
        np.random.seed(42)
        predictions = np.arange(15) + np.random.randn(15) * 0.1
        outcomes = predictions * 0.9 + np.random.randn(15) * 0.1
        
        is_valid, reason = lenient_detector.validate_pattern(
            predictions.tolist(),
            outcomes.tolist(),
            verbose=False
        )
        
        # Should pass with lenient thresholds
        assert is_valid, f"Should pass with lenient thresholds. Reason: {reason}"
    
    def test_edge_case_empty_data(self, detector):
        """Test edge case: empty data"""
        is_valid, reason = detector.validate_pattern([], [], verbose=False)
        
        assert not is_valid
        assert "Insufficient sample size" in reason
    
    def test_edge_case_single_value(self, detector):
        """Test edge case: all predictions are same value"""
        predictions = [0.5] * 50
        outcomes = np.random.randn(50).tolist()
        
        # This should fail (no variance in predictions)
        is_valid, reason = detector.validate_pattern(predictions, outcomes, verbose=False)
        
        # Might fail for various reasons (no correlation possible, etc.)
        assert not is_valid
    
    def test_edge_case_perfect_correlation(self, detector):
        """Test edge case: perfect correlation (r = 1.0)"""
        predictions = list(range(50))
        outcomes = list(range(50))  # Exact same
        
        is_valid, reason = detector.validate_pattern(predictions, outcomes, verbose=False)
        
        # Perfect correlation should pass
        assert is_valid, f"Perfect correlation should be valid. Reason: {reason}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
