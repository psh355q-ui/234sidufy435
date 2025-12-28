"""
Unit tests for Macro Agent

Tests for oil price analysis, dollar index analysis, and helper methods.

Author: ai-trading-system
Date: 2025-12-28
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from ai.debate.macro_agent import MacroAgent


class TestMacroAgentOilAnalysis:
    """Test oil price analysis methods"""

    @pytest.fixture
    def macro_agent(self):
        """Create MacroAgent instance"""
        return MacroAgent()

    def test_oil_price_high(self, macro_agent):
        """Test HIGH oil price signal (> $90)"""
        result = macro_agent._analyze_oil_price(wti_price=95.0, wti_change_30d=12.5)

        assert result["signal"] == "HIGH"
        assert result["inflation_pressure"] == "INCREASING"
        assert result["oil_price"] == 95.0
        assert result["oil_change_30d"] == 12.5
        assert "energy" in result["sector_impact"]
        assert result["sector_impact"]["energy"] == "POSITIVE"
        assert result["sector_impact"]["airlines"] == "NEGATIVE"

    def test_oil_price_low(self, macro_agent):
        """Test LOW oil price signal (< $60)"""
        result = macro_agent._analyze_oil_price(wti_price=55.0, wti_change_30d=-8.5)

        assert result["signal"] == "LOW"
        assert result["inflation_pressure"] == "DECREASING"
        assert result["sector_impact"]["energy"] == "NEGATIVE"
        assert result["sector_impact"]["airlines"] == "POSITIVE"
        assert result["sector_impact"]["consumer"] == "POSITIVE"

    def test_oil_price_normal(self, macro_agent):
        """Test NORMAL oil price signal ($60-90)"""
        result = macro_agent._analyze_oil_price(wti_price=75.0, wti_change_30d=3.2)

        assert result["signal"] == "NORMAL"
        assert result["inflation_pressure"] == "STABLE"
        assert result["sector_impact"] == {}

    def test_oil_price_spike(self, macro_agent):
        """Test oil price spike (> +20% in 30 days)"""
        result = macro_agent._analyze_oil_price(wti_price=85.0, wti_change_30d=25.5)

        assert result["oil_change_30d"] == 25.5
        assert "급등" in result["reasoning"]

    def test_oil_price_crash(self, macro_agent):
        """Test oil price crash (< -20% in 30 days)"""
        result = macro_agent._analyze_oil_price(wti_price=55.0, wti_change_30d=-22.3)

        assert result["oil_change_30d"] == -22.3
        assert "급락" in result["reasoning"]


class TestMacroAgentDollarAnalysis:
    """Test dollar index analysis methods"""

    @pytest.fixture
    def macro_agent(self):
        """Create MacroAgent instance"""
        return MacroAgent()

    def test_dollar_index_strong(self, macro_agent):
        """Test STRONG dollar signal (> 105)"""
        result = macro_agent._analyze_dollar_index(dxy=108.5, dxy_change_30d=6.2)

        assert result["signal"] == "STRONG"
        assert result["dxy"] == 108.5
        assert result["dxy_change_30d"] == 6.2
        assert result["impact"]["us_exporters"] == "NEGATIVE"
        assert result["impact"]["multinationals"] == "NEGATIVE"
        assert result["impact"]["gold"] == "NEGATIVE"

    def test_dollar_index_weak(self, macro_agent):
        """Test WEAK dollar signal (< 95)"""
        result = macro_agent._analyze_dollar_index(dxy=92.5, dxy_change_30d=-3.8)

        assert result["signal"] == "WEAK"
        assert result["impact"]["us_exporters"] == "POSITIVE"
        assert result["impact"]["multinationals"] == "POSITIVE"
        assert result["impact"]["gold"] == "POSITIVE"

    def test_dollar_index_neutral(self, macro_agent):
        """Test NEUTRAL dollar signal (95-105)"""
        result = macro_agent._analyze_dollar_index(dxy=100.0, dxy_change_30d=1.5)

        assert result["signal"] == "NEUTRAL"
        assert result["impact"] == {}

    def test_dollar_index_spike(self, macro_agent):
        """Test dollar spike (> +5% in 30 days)"""
        result = macro_agent._analyze_dollar_index(dxy=108.5, dxy_change_30d=7.2)

        assert result["dxy_change_30d"] == 7.2
        assert "급강세" in result["reasoning"]

    def test_dollar_index_crash(self, macro_agent):
        """Test dollar crash (< -5% in 30 days)"""
        result = macro_agent._analyze_dollar_index(dxy=92.0, dxy_change_30d=-6.5)

        assert result["dxy_change_30d"] == -6.5
        assert "급약세" in result["reasoning"]


class TestMacroAgentHelperMethods:
    """Test helper methods for sector/company classification"""

    @pytest.fixture
    def macro_agent(self):
        """Create MacroAgent instance"""
        return MacroAgent()

    def test_get_sector_energy(self, macro_agent):
        """Test Energy sector identification"""
        assert macro_agent._get_sector("XOM") == "Energy"
        assert macro_agent._get_sector("CVX") == "Energy"
        assert macro_agent._get_sector("XLE") == "Energy"

    def test_get_sector_airlines(self, macro_agent):
        """Test Airlines sector identification"""
        assert macro_agent._get_sector("DAL") == "Airlines"
        assert macro_agent._get_sector("AAL") == "Airlines"
        assert macro_agent._get_sector("UAL") == "Airlines"

    def test_get_sector_technology(self, macro_agent):
        """Test Technology sector identification"""
        assert macro_agent._get_sector("AAPL") == "Technology"
        assert macro_agent._get_sector("MSFT") == "Technology"
        assert macro_agent._get_sector("NVDA") == "Technology"

    def test_get_sector_gold(self, macro_agent):
        """Test Gold sector identification"""
        assert macro_agent._get_sector("GLD") == "Gold"
        assert macro_agent._get_sector("GDX") == "Gold"

    def test_get_sector_unknown(self, macro_agent):
        """Test unknown ticker"""
        assert macro_agent._get_sector("UNKNOWN") == "Unknown"

    def test_is_us_exporter_true(self, macro_agent):
        """Test US exporter identification - TRUE cases"""
        assert macro_agent._is_us_exporter("AAPL") == True
        assert macro_agent._is_us_exporter("NVDA") == True
        assert macro_agent._is_us_exporter("BA") == True
        assert macro_agent._is_us_exporter("CAT") == True

    def test_is_us_exporter_false(self, macro_agent):
        """Test US exporter identification - FALSE cases"""
        assert macro_agent._is_us_exporter("WMT") == False
        assert macro_agent._is_us_exporter("JPM") == False
        assert macro_agent._is_us_exporter("DAL") == False

    def test_is_multinational_true(self, macro_agent):
        """Test multinational identification - TRUE cases"""
        assert macro_agent._is_multinational("AAPL") == True
        assert macro_agent._is_multinational("MSFT") == True
        assert macro_agent._is_multinational("KO") == True
        assert macro_agent._is_multinational("MCD") == True

    def test_is_multinational_false(self, macro_agent):
        """Test multinational identification - FALSE cases"""
        assert macro_agent._is_multinational("DAL") == False
        assert macro_agent._is_multinational("XOM") == False


class TestMacroAgentIntegration:
    """Test integration of oil/dollar analysis into main analysis"""

    @pytest.fixture
    def macro_agent(self):
        """Create MacroAgent instance"""
        return MacroAgent()

    @pytest.mark.asyncio
    async def test_high_oil_energy_sector(self, macro_agent):
        """Test high oil price benefits Energy sector (XOM)"""
        macro_data = {
            "fed_rate": 5.25,
            "fed_direction": "HOLDING",
            "cpi_yoy": 3.2,
            "gdp_growth": 2.5,
            "unemployment": 3.7,
            "wti_crude": 95.0,
            "wti_change_30d": 12.5
        }

        result = await macro_agent._analyze_with_real_data("XOM", macro_data)

        assert "macro_factors" in result
        assert "oil_price" in result["macro_factors"]
        assert result["macro_factors"]["oil_price"]["signal"] == "HIGH"
        assert "고유가" in result["reasoning"]
        assert "에너지 섹터 수혜" in result["reasoning"]

    @pytest.mark.asyncio
    async def test_high_oil_airline_sector(self, macro_agent):
        """Test high oil price hurts Airlines sector (DAL)"""
        macro_data = {
            "fed_rate": 5.25,
            "fed_direction": "HOLDING",
            "cpi_yoy": 3.2,
            "gdp_growth": 2.5,
            "unemployment": 3.7,
            "wti_crude": 95.0,
            "wti_change_30d": 12.5
        }

        result = await macro_agent._analyze_with_real_data("DAL", macro_data)

        assert "고유가" in result["reasoning"]
        assert "운송 비용 증가" in result["reasoning"]

    @pytest.mark.asyncio
    async def test_low_oil_consumer_sector(self, macro_agent):
        """Test low oil price benefits Consumer sector"""
        macro_data = {
            "fed_rate": 5.25,
            "fed_direction": "HOLDING",
            "cpi_yoy": 3.0,
            "gdp_growth": 2.5,
            "unemployment": 3.7,
            "wti_crude": 55.0,
            "wti_change_30d": -8.5
        }

        result = await macro_agent._analyze_with_real_data("WMT", macro_data)

        assert "저유가" in result["reasoning"]
        assert "비용 절감 수혜" in result["reasoning"]

    @pytest.mark.asyncio
    async def test_strong_dollar_exporter(self, macro_agent):
        """Test strong dollar hurts exporters (AAPL)"""
        macro_data = {
            "fed_rate": 5.25,
            "fed_direction": "HOLDING",
            "cpi_yoy": 3.0,
            "gdp_growth": 2.5,
            "unemployment": 3.7,
            "dxy": 108.5,
            "dxy_change_30d": 6.2
        }

        result = await macro_agent._analyze_with_real_data("AAPL", macro_data)

        assert "macro_factors" in result
        assert "dollar_index" in result["macro_factors"]
        assert result["macro_factors"]["dollar_index"]["signal"] == "STRONG"
        assert "강달러" in result["reasoning"]
        assert "수출 기업 불리" in result["reasoning"]

    @pytest.mark.asyncio
    async def test_weak_dollar_gold(self, macro_agent):
        """Test weak dollar benefits gold (GLD)"""
        macro_data = {
            "fed_rate": 4.75,
            "fed_direction": "CUTTING",
            "cpi_yoy": 2.8,
            "gdp_growth": 2.0,
            "unemployment": 4.0,
            "dxy": 92.5,
            "dxy_change_30d": -3.8
        }

        result = await macro_agent._analyze_with_real_data("GLD", macro_data)

        assert "약달러" in result["reasoning"]
        assert "금 가격 상승" in result["reasoning"]

    @pytest.mark.asyncio
    async def test_oil_extreme_movement(self, macro_agent):
        """Test extreme oil price movement reduces confidence"""
        macro_data = {
            "fed_rate": 5.25,
            "fed_direction": "HOLDING",
            "cpi_yoy": 3.5,
            "gdp_growth": 2.2,
            "unemployment": 3.8,
            "wti_crude": 95.0,
            "wti_change_30d": 25.5  # Extreme spike
        }

        result = await macro_agent._analyze_with_real_data("XOM", macro_data)

        assert "유가 급등" in result["reasoning"]

    @pytest.mark.asyncio
    async def test_dollar_extreme_movement(self, macro_agent):
        """Test extreme dollar movement reduces confidence"""
        macro_data = {
            "fed_rate": 5.25,
            "fed_direction": "HOLDING",
            "cpi_yoy": 3.0,
            "gdp_growth": 2.5,
            "unemployment": 3.7,
            "dxy": 108.5,
            "dxy_change_30d": 7.2  # Extreme spike
        }

        result = await macro_agent._analyze_with_real_data("AAPL", macro_data)

        assert "달러 급등" in result["reasoning"]

    @pytest.mark.asyncio
    async def test_combined_oil_dollar_analysis(self, macro_agent):
        """Test combined oil and dollar analysis"""
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

        result = await macro_agent._analyze_with_real_data("AAPL", macro_data)

        assert "macro_factors" in result
        assert "oil_price" in result["macro_factors"]
        assert "dollar_index" in result["macro_factors"]
        # AAPL should be affected by strong dollar
        assert "강달러" in result["reasoning"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
