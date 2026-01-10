
from typing import Dict, Any, Optional
from .base_analyzer import BaseStockAnalyzer

class TSLAAnalyzer(BaseStockAnalyzer):
    """
    Tesla (TSLA) Specific Analyzer
    Focus:
    - EV Deliveries & Margins
    - FSD / Robotaxi Progress
    - Elon Musk (Key Person Risk)
    - Energy Storage Growth
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

        # Simple keyword heuristics (placeholder for deeper logic)
        # In a real system, this would use LLM analysis or structured data sources
        
        if news_articles:
            for article in news_articles:
                text = (article.get('title', '') + article.get('summary', '')).lower()
                
                # Positive Catalysts
                if 'fsd' in text and ('approve' in text or 'breakthrough' in text):
                    specific_catalysts.append("FSD Regulatory/Tech Progress")
                    score_adjustment += 0.5
                if 'delivery' in text and 'record' in text:
                    specific_catalysts.append("Record Deliveries")
                    score_adjustment += 0.5
                if 'cybercab' in text or 'robotaxi' in text:
                    specific_catalysts.append("Robotaxi Hype")
                    score_adjustment += 0.3

                # Negative Risks
                if 'margin' in text and ('drop' in text or 'compress' in text):
                    specific_risks.append("Auto Gross Margin Compression")
                    score_adjustment -= 0.5
                if 'musk' in text and ('sell' in text or 'lawsuit' in text or 'tweet' in text):
                    specific_risks.append("Elon Musk Key Person Risk")
                    score_adjustment -= 0.3
                if 'competition' in text and ('byd' in text or 'china' in text):
                    specific_risks.append("China EV Competition")
                    score_adjustment -= 0.2

        return {
            "specific_risks": list(set(specific_risks)),
            "specific_catalysts": list(set(specific_catalysts)),
            "score_adjustment": max(min(score_adjustment, 2.0), -2.0), # Cap at +/- 2.0
            "specific_metrics": {
                "key_focus": "Margins, FSD, Deliveries"
            }
        }

    def get_prompt_addition(self) -> str:
        return """
        [TSLA Special Focus]
        1. 전기차 인도량 및 마진율 추이 (Auto Gross Margin ex-credits)
        2. FSD (Full Self-Driving) 규제 승인 및 기술 진척도 (v12, v13 등)
        3. 로보택시(Cybercab) 관련 구체적 일정 및 실행 가능성
        4. CEO Elon Musk 관련 리스크 (트위터/X 발언, 지분 매각 등)
        5. 에너지 저장 장치(Megapack) 사업 성장 속도
        """
