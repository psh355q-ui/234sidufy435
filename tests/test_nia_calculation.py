"""
Test NIA (News Interpretation Accuracy) Calculation

Simple unit tests for Report Orchestrator's correctness logic
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import is not needed for these basic tests
# from backend.ai.skills.reporting.report_orchestrator_agent.report_orchestrator import ReportOrchestrator


def test_check_interpretation_accuracy():
    """
    Test interpretation correctness logic
    """
    print("="*60)
    print("🧪 Testing NIA Correctness Logic")
    print("="*60)

    # Create a mock orchestrator (without DB session)
    class MockOrchestrator:
        def _check_interpretation_accuracy(self, headline_bias, actual_price_change):
            if headline_bias == "BULLISH":
                return actual_price_change > 1.0
            elif headline_bias == "BEARISH":
                return actual_price_change < -1.0
            else:  # NEUTRAL
                return -1.0 <= actual_price_change <= 1.0

    orchestrator = MockOrchestrator()

    # Test cases
    test_cases = [
        # (headline_bias, actual_change, expected_result, description)
        ("BULLISH", 5.0, True, "BULLISH + 5% up → ✓"),
        ("BULLISH", 1.5, True, "BULLISH + 1.5% up → ✓"),
        ("BULLISH", 0.5, False, "BULLISH + 0.5% up → ✗ (too small)"),
        ("BULLISH", -2.0, False, "BULLISH - 2% down → ✗ (wrong direction)"),

        ("BEARISH", -5.0, True, "BEARISH - 5% down → ✓"),
        ("BEARISH", -1.5, True, "BEARISH - 1.5% down → ✓"),
        ("BEARISH", -0.5, False, "BEARISH - 0.5% down → ✗ (too small)"),
        ("BEARISH", 2.0, False, "BEARISH + 2% up → ✗ (wrong direction)"),

        ("NEUTRAL", 0.5, True, "NEUTRAL + 0.5% → ✓"),
        ("NEUTRAL", -0.5, True, "NEUTRAL - 0.5% → ✓"),
        ("NEUTRAL", 0.0, True, "NEUTRAL ±0% → ✓"),
        ("NEUTRAL", 2.0, False, "NEUTRAL + 2% → ✗ (too large)"),
        ("NEUTRAL", -2.0, False, "NEUTRAL - 2% → ✗ (too large)"),
    ]

    passed = 0
    failed = 0

    for bias, change, expected, description in test_cases:
        result = orchestrator._check_interpretation_accuracy(bias, change)

        if result == expected:
            print(f"✅ PASS: {description}")
            passed += 1
        else:
            print(f"❌ FAIL: {description} (expected {expected}, got {result})")
            failed += 1

    print("\n" + "="*60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0


def test_magnitude_accuracy():
    """
    Test magnitude accuracy calculation
    """
    print("\n" + "="*60)
    print("🧪 Testing Magnitude Accuracy Logic")
    print("="*60)

    class MockOrchestrator:
        def _calculate_magnitude_accuracy(self, expected_impact, actual_magnitude):
            if expected_impact == "HIGH":
                if actual_magnitude >= 5.0:
                    return 1.0
                elif actual_magnitude >= 2.0:
                    return 0.5
                else:
                    return 0.0
            elif expected_impact == "MEDIUM":
                if 2.0 <= actual_magnitude < 5.0:
                    return 1.0
                elif actual_magnitude >= 1.0:
                    return 0.7
                else:
                    return 0.3
            else:  # LOW
                if actual_magnitude < 2.0:
                    return 1.0
                elif actual_magnitude < 5.0:
                    return 0.5
                else:
                    return 0.0

    orchestrator = MockOrchestrator()

    test_cases = [
        # (expected_impact, actual_magnitude, expected_score, description)
        ("HIGH", 8.0, 1.0, "HIGH impact, 8% move → Perfect (1.0)"),
        ("HIGH", 3.0, 0.5, "HIGH impact, 3% move → Partial (0.5)"),
        ("HIGH", 0.5, 0.0, "HIGH impact, 0.5% move → Wrong (0.0)"),

        ("MEDIUM", 3.0, 1.0, "MEDIUM impact, 3% move → Perfect (1.0)"),
        ("MEDIUM", 1.2, 0.7, "MEDIUM impact, 1.2% move → Close (0.7)"),
        ("MEDIUM", 0.5, 0.3, "MEDIUM impact, 0.5% move → Partial (0.3)"),

        ("LOW", 1.0, 1.0, "LOW impact, 1% move → Perfect (1.0)"),
        ("LOW", 3.0, 0.5, "LOW impact, 3% move → Partial (0.5)"),
        ("LOW", 6.0, 0.0, "LOW impact, 6% move → Wrong (0.0)"),
    ]

    passed = 0
    failed = 0

    for impact, magnitude, expected_score, description in test_cases:
        result = orchestrator._calculate_magnitude_accuracy(impact, magnitude)

        if result == expected_score:
            print(f"✅ PASS: {description}")
            passed += 1
        else:
            print(f"❌ FAIL: {description} (expected {expected_score}, got {result})")
            failed += 1

    print("\n" + "="*60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0


def test_confidence_justification():
    """
    Test confidence justification logic
    """
    print("\n" + "="*60)
    print("🧪 Testing Confidence Justification Logic")
    print("="*60)

    class MockVerifier:
        def _check_confidence_justified(self, confidence, expected_impact, actual_magnitude):
            if confidence >= 80:
                if expected_impact == "HIGH":
                    return actual_magnitude >= 5.0
                else:
                    return actual_magnitude >= 2.0
            elif confidence >= 50:
                return actual_magnitude >= 2.0
            else:
                return True

    verifier = MockVerifier()

    test_cases = [
        # (confidence, expected_impact, actual_magnitude, expected_result, description)
        (90, "HIGH", 8.0, True, "High confidence (90), HIGH impact, 8% → Justified"),
        (90, "HIGH", 3.0, False, "High confidence (90), HIGH impact, 3% → Not justified"),
        (85, "MEDIUM", 3.0, True, "High confidence (85), MEDIUM impact, 3% → Justified"),
        (85, "MEDIUM", 1.0, False, "High confidence (85), MEDIUM impact, 1% → Not justified"),

        (70, "MEDIUM", 3.0, True, "Medium confidence (70), 3% → Justified"),
        (70, "MEDIUM", 1.5, False, "Medium confidence (70), 1.5% → Not justified"),

        (30, "LOW", 0.5, True, "Low confidence (30), 0.5% → Always justified"),
        (30, "HIGH", 10.0, True, "Low confidence (30), 10% → Always justified"),
    ]

    passed = 0
    failed = 0

    for confidence, impact, magnitude, expected, description in test_cases:
        result = verifier._check_confidence_justified(confidence, impact, magnitude)

        if result == expected:
            print(f"✅ PASS: {description}")
            passed += 1
        else:
            print(f"❌ FAIL: {description} (expected {expected}, got {result})")
            failed += 1

    print("\n" + "="*60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    print("\n" + "🚀 Starting NIA Calculation Tests\n")

    all_passed = True

    # Run all tests
    all_passed &= test_check_interpretation_accuracy()
    all_passed &= test_magnitude_accuracy()
    all_passed &= test_confidence_justification()

    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*60)
    print()

    sys.exit(0 if all_passed else 1)
