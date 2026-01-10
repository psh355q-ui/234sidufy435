
from typing import Dict, Any, Optional
from .base_analyzer import BaseStockAnalyzer

class NVDAAnalyzer(BaseStockAnalyzer):
    """
    NVIDIA (NVDA) Specific Analyzer
    Focus:
    - AI Capex Cycles (Hyperscaler Spending)
    - Next-Gen Chips (Blackwell/Rubin) Supply/Yield
    - China Export Controls (Geopolitics)
    - Competition (AMD MI300, Custom ASICs)
    """

    def analyze_specifics(
        self,
        news_articles: Optional[list] = None,
        market_data: Optional[Dict[str, Any]] = None,
        event_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        
        specific_risks = []
        specific_catalysts = []
        score_adjustment = 0.0
        
        if news_articles:
            for article in news_articles:
                text = (article.get('title', '') + article.get('summary', '')).lower()
                
                # Positive Catalysts
                if 'blackwell' in text and ('sold out' in text or 'demand' in text):
                    specific_catalysts.append("Strong Blackwell Demand")
                    score_adjustment += 0.5
                if 'capex' in text and 'increase' in text:
                    specific_catalysts.append("Rising Hyperscaler AI Capex")
                    score_adjustment += 0.5
                
                # Negative Risks
                if 'export control' in text or 'ban' in text or 'china' in text:
                    specific_risks.append("China Export Restrictions")
                    score_adjustment -= 1.0  # High Impact
                if 'delay' in text and ('shipment' in text or 'yield' in text):
                    specific_risks.append("Product Roadmap Delay/Yield Issues")
                    score_adjustment -= 0.8
                if 'competition' in text and 'amd' in text:
                    specific_risks.append("Competitor Market Share Gain")
                    score_adjustment -= 0.2

        return {
            "specific_risks": list(set(specific_risks)),
            "specific_catalysts": list(set(specific_catalysts)),
            "score_adjustment": max(min(score_adjustment, 2.0), -2.0),
            "specific_metrics": {
                "key_focus": "AI Capex, China Ban, Blackwell Yield"
            }
        }

    def get_prompt_addition(self) -> str:
        return """
        [NVDA Special Focus]
        1. 하이퍼스케일러(MSFT, META, GOOGL, AMZN)들의 AI Capex 지출 계획
        2. 차세대 칩(Blackwell, Rubin 등)의 생산 수율 및 출시 일정 지연 여부
        3. 대중국 수출 규제 강화 여부 및 "Chip War" 지정학적 리스크
        4. 경쟁사(AMD, 자체 칩)의 시장 점유율 침투 여부
        5. 데이터센터 매출 비중 및 성장률 유지 가능성
        """
