"""
Standalone test runner for Macro Agent

Run this directly: python run_macro_tests.py

Author: ai-trading-system
Date: 2025-12-28
"""

import sys
import os
from pathlib import Path

# Add paths for imports
backend_path = Path(__file__).parent.parent.parent
root_path = backend_path.parent
sys.path.insert(0, str(root_path))  # For 'backend' module
sys.path.insert(0, str(backend_path))  # For relative imports
os.chdir(backend_path)

# Set environment variable to avoid database initialization
os.environ["TESTING"] = "true"

import asyncio
from ai.debate.macro_agent import MacroAgent


def test_oil_price_high():
    """Test HIGH oil price signal (> $90)"""
    print("\n=== Test: Oil Price HIGH ===")
    agent = MacroAgent()
    result = agent._analyze_oil_price(wti_price=95.0, wti_change_30d=12.5)

    assert result["signal"] == "HIGH", f"Expected HIGH, got {result['signal']}"
    assert result["inflation_pressure"] == "INCREASING"
    assert result["sector_impact"]["energy"] == "POSITIVE"
    assert result["sector_impact"]["airlines"] == "NEGATIVE"
    print(f"✓ Oil price HIGH signal: ${result['oil_price']}")
    print(f"✓ Inflation pressure: {result['inflation_pressure']}")
    print(f"✓ Reasoning: {result['reasoning']}")


def test_oil_price_low():
    """Test LOW oil price signal (< $60)"""
    print("\n=== Test: Oil Price LOW ===")
    agent = MacroAgent()
    result = agent._analyze_oil_price(wti_price=55.0, wti_change_30d=-8.5)

    assert result["signal"] == "LOW"
    assert result["inflation_pressure"] == "DECREASING"
    assert result["sector_impact"]["airlines"] == "POSITIVE"
    print(f"✓ Oil price LOW signal: ${result['oil_price']}")
    print(f"✓ Airlines benefit: {result['sector_impact']['airlines']}")


def test_dollar_index_strong():
    """Test STRONG dollar signal (> 105)"""
    print("\n=== Test: Dollar Index STRONG ===")
    agent = MacroAgent()
    result = agent._analyze_dollar_index(dxy=108.5, dxy_change_30d=6.2)

    assert result["signal"] == "STRONG"
    assert result["impact"]["us_exporters"] == "NEGATIVE"
    assert result["impact"]["gold"] == "NEGATIVE"
    print(f"✓ Dollar STRONG signal: DXY {result['dxy']}")
    print(f"✓ Exporters impact: {result['impact']['us_exporters']}")


def test_dollar_index_weak():
    """Test WEAK dollar signal (< 95)"""
    print("\n=== Test: Dollar Index WEAK ===")
    agent = MacroAgent()
    result = agent._analyze_dollar_index(dxy=92.5, dxy_change_30d=-3.8)

    assert result["signal"] == "WEAK"
    assert result["impact"]["us_exporters"] == "POSITIVE"
    assert result["impact"]["gold"] == "POSITIVE"
    print(f"✓ Dollar WEAK signal: DXY {result['dxy']}")
    print(f"✓ Gold impact: {result['impact']['gold']}")


def test_sector_mapping():
    """Test sector mapping"""
    print("\n=== Test: Sector Mapping ===")
    agent = MacroAgent()

    assert agent._get_sector("XOM") == "Energy"
    assert agent._get_sector("DAL") == "Airlines"
    assert agent._get_sector("AAPL") == "Technology"
    assert agent._get_sector("GLD") == "Gold"
    assert agent._get_sector("UNKNOWN") == "Unknown"
    print("✓ Energy sector: XOM")
    print("✓ Airlines sector: DAL")
    print("✓ Technology sector: AAPL")
    print("✓ Gold sector: GLD")


def test_us_exporter():
    """Test US exporter identification"""
    print("\n=== Test: US Exporter Identification ===")
    agent = MacroAgent()

    assert agent._is_us_exporter("AAPL") == True
    assert agent._is_us_exporter("NVDA") == True
    assert agent._is_us_exporter("BA") == True
    assert agent._is_us_exporter("WMT") == False
    assert agent._is_us_exporter("JPM") == False
    print("✓ Exporters: AAPL, NVDA, BA")
    print("✓ Non-exporters: WMT, JPM")


def test_multinational():
    """Test multinational identification"""
    print("\n=== Test: Multinational Identification ===")
    agent = MacroAgent()

    assert agent._is_multinational("AAPL") == True
    assert agent._is_multinational("KO") == True
    assert agent._is_multinational("MCD") == True
    assert agent._is_multinational("DAL") == False
    print("✓ Multinationals: AAPL, KO, MCD")
    print("✓ Non-multinationals: DAL")


async def test_integration_high_oil_energy():
    """Test high oil price benefits Energy sector (XOM)"""
    print("\n=== Test: Integration - High Oil + Energy Sector ===")
    agent = MacroAgent()

    macro_data = {
        "fed_rate": 5.25,
        "fed_direction": "HOLDING",
        "cpi_yoy": 3.2,
        "gdp_growth": 2.5,
        "unemployment": 3.7,
        "wti_crude": 95.0,
        "wti_change_30d": 12.5
    }

    result = await agent._analyze_with_real_data("XOM", macro_data)

    assert "oil_price" in result["macro_factors"]
    assert result["macro_factors"]["oil_price"]["signal"] == "HIGH"
    assert "고유가" in result["reasoning"]
    assert "에너지 섹터 수혜" in result["reasoning"]
    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Reasoning: {result['reasoning']}")


async def test_integration_strong_dollar_exporter():
    """Test strong dollar hurts exporters (AAPL)"""
    print("\n=== Test: Integration - Strong Dollar + Exporter ===")
    agent = MacroAgent()

    macro_data = {
        "fed_rate": 5.25,
        "fed_direction": "HOLDING",
        "cpi_yoy": 3.0,
        "gdp_growth": 2.5,
        "unemployment": 3.7,
        "dxy": 108.5,
        "dxy_change_30d": 6.2
    }

    result = await agent._analyze_with_real_data("AAPL", macro_data)

    assert "dollar_index" in result["macro_factors"]
    assert result["macro_factors"]["dollar_index"]["signal"] == "STRONG"
    assert "강달러" in result["reasoning"]
    assert "수출 기업 불리" in result["reasoning"]
    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Reasoning: {result['reasoning']}")


async def test_integration_combined():
    """Test combined oil and dollar analysis"""
    print("\n=== Test: Integration - Combined Oil + Dollar ===")
    agent = MacroAgent()

    macro_data = {
        "fed_rate": 5.25,
        "fed_direction": "HOLDING",
        "cpi_yoy": 3.2,
        "gdp_growth": 2.5,
        "unemployment": 3.7,
        "wti_crude": 95.0,
        "wti_change_30d": 12.5,
        "dxy": 108.5,
        "dxy_change_30d": 6.2
    }

    result = await agent._analyze_with_real_data("AAPL", macro_data)

    assert "oil_price" in result["macro_factors"]
    assert "dollar_index" in result["macro_factors"]
    assert "강달러" in result["reasoning"]
    print(f"✓ Oil signal: {result['macro_factors']['oil_price']['signal']}")
    print(f"✓ Dollar signal: {result['macro_factors']['dollar_index']['signal']}")
    print(f"✓ Action: {result['action']}")
    print(f"✓ Confidence: {result['confidence']:.2f}")
    print(f"✓ Reasoning: {result['reasoning']}")


async def run_async_tests():
    """Run async integration tests"""
    await test_integration_high_oil_energy()
    await test_integration_strong_dollar_exporter()
    await test_integration_combined()


def main():
    """Run all tests"""
    print("=" * 80)
    print("Macro Agent Unit Tests")
    print("=" * 80)

    tests_passed = 0
    tests_failed = 0

    # Synchronous tests
    sync_tests = [
        test_oil_price_high,
        test_oil_price_low,
        test_dollar_index_strong,
        test_dollar_index_weak,
        test_sector_mapping,
        test_us_exporter,
        test_multinational,
    ]

    for test in sync_tests:
        try:
            test()
            tests_passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {test.__name__}")
            print(f"  Error: {e}")
            tests_failed += 1
        except Exception as e:
            print(f"✗ Test error: {test.__name__}")
            print(f"  Error: {e}")
            tests_failed += 1

    # Async tests
    try:
        asyncio.run(run_async_tests())
        tests_passed += 3  # 3 async tests
    except AssertionError as e:
        print(f"✗ Async test failed")
        print(f"  Error: {e}")
        tests_failed += 3
    except Exception as e:
        print(f"✗ Async test error")
        print(f"  Error: {e}")
        tests_failed += 3

    # Summary
    print("\n" + "=" * 80)
    print(f"Test Summary: {tests_passed} passed, {tests_failed} failed")
    print("=" * 80)

    if tests_failed == 0:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {tests_failed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
