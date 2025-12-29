"""
Complete 5-Page AI Report Generator

통합: Page 1-5를 모두 결합하여 완전한 리포트 생성
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, PageBreak

# Import all page generators
from backend.services.page1_generator import Page1Generator
from backend.services.page3_generator import Page3Generator

logger = logging.getLogger(__name__)


class CompleteReportGenerator:
    """
    5-Page 완전 AI 리포트 생성기
    
    Page 1: Executive Market Narrative
    Page 2: AI Decision Logic (TBD)
    Page 3: Skeptic & Contradiction
    Page 4: Trades & Performance (기존 sample)
    Page 5: Tomorrow Risk Playbook (TBD)
    """
    
    def __init__(self):
        """Initialize all generators"""
        self.page1_gen = Page1Generator()
        self.page3_gen = Page3Generator()
        logger.info("✅ CompleteReportGenerator initialized")
    
    def generate_complete_report(self, output_path: str = "complete_ai_report.pdf") -> str:
        """
        완전한 5-페이지 리포트 생성 (현재 구현된 것만)
        
        Returns:
            output_path
        """
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Get mock data
        data = self._get_mock_data()
        
        # Page 1: Market Narrative
        story.extend(self.page1_gen.generate(data["page1"]))
        story.append(PageBreak())
        
        # Page 3: Skeptic (Page 2는 아직 구현 안 됨)
        story.extend(self.page3_gen.generate(data["page3"]))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"✅ Complete report generated: {output_path}")
        return output_path
    
    def _get_mock_data(self) -> Dict:
        """Mock 데이터 생성"""
        return {
            "page1": {
                "date": datetime.now(),
                "market_summary": "시장은 강세였지만, 내부적으로는 위험 신호가 누적되는 하루였다.",
                "market_flow": {
                    "asia": "중국 경기 우려로 약세 (-0.5%)",
                    "europe": "ECB 완화 기대로 강세 (+0.8%)",
                    "us": "Tech 주도 상승, 하지만 거래량 감소 (-18%)"
                },
                "key_questions": [
                    {
                        "question": "이 상승은 추세인가, 숏커버인가?",
                        "ai_answer": "숏커버 가능성 65%",
                        "reasoning": "거래량 부족 + VIX 급락"
                    },
                    {
                        "question": "Fed는 정말 피봇할까?",
                        "ai_answer": "아직 시기상조 (확률 30%)",
                        "reasoning": "고용 지표 여전히 강함"
                    }
                ],
                "key_indicators": [
                    {"name": "S&P 500", "change": "+0.8%", "signal": "⚠️"},
                    {"name": "VIX", "change": "-5.2%", "signal": "⚠️"},
                    {"name": "Volume", "change": "-18%", "signal": "⚠️"},
                    {"name": "10Y Yield", "change": "+0.05%", "signal": "📈"},
                ]
            },
            "page3": {
                "date": datetime.now(),
                "risk_reasons": [
                    {
                        "category": "밸류에이션 리스크",
                        "current": "Tech 섹터 P/E 38x (역사적 고점)",
                        "risk": "금리 재상승 시 급격한 조정 가능성",
                        "probability": 15
                    },
                    {
                        "category": "거래량 부족",
                        "current": "오늘 거래량 평균 대비 -18%",
                        "risk": "실질 수요 없이 상승 → 취약한 구조",
                        "probability": 25
                    },
                    {
                        "category": "옵션 시장 과신",
                        "current": "Call 우세 (C/P Ratio 2.5)",
                        "risk": "옵션 신호가 항상 정확하지 않음",
                        "probability": 20
                    }
                ],
                "contradictions": [
                    {"indicator": "지수", "signal": "상승", "interpretation": "Bullish"},
                    {"indicator": "거래량", "signal": "감소", "interpretation": "Warning"},
                    {"indicator": "VIX", "signal": "급락", "interpretation": "Warning (과도한 낙관)"},
                    {"indicator": "Put/Call", "signal": "0.65", "interpretation": "Bullish"},
                    {"indicator": "10Y 수익률", "signal": "상승", "interpretation": "모순 (금리 상승)"},
                ],
                "skeptic_opinion": """
상승 추세는 맞으나, 내부 구조는 건강하지 않음.
현재 포지션 유지하되, 추가매수는 신중해야 함.
특히 Tech 집중도가 높아 섹터 조정 시 취약.
""",
                "constitutional_checks": [
                    {"rule": "✓ 과잉 확신 방지 (Confidence < 95%)", "status": "Pass"},
                    {"rule": "✓ 반대 시나리오 검토 완료", "status": "Pass"},
                    {"rule": "✓ 포지션 한도 준수 (< 30%)", "status": "Pass"},
                    {"rule": "✗ 단기 유동성 리스크 완전 해소", "status": "Warning"},
                ]
            }
        }


def test_complete_report():
    """완전한 리포트 생성 테스트"""
    print("="*60)
    print("Complete AI Report Generator Test")
    print("="*60)
    print("\nGenerating 5-page report (Pages 1+3 currently)...")
    
    generator = CompleteReportGenerator()
    output_path = generator.generate_complete_report()
    
    print(f"\n✅ Complete report generated: {output_path}")
    print("\nPages included:")
    print("  ✓ Page 1: Market Narrative")
    print("  ○ Page 2: Decision Logic (TBD)")
    print("  ✓ Page 3: Skeptic & Contradiction")
    print("  ○ Page 4: Trades & Performance (TBD)")
    print("  ○ Page 5: Tomorrow Risk Playbook (TBD)")
    
    print("\n" + "="*60)
    print("✅ Test completed! Open the PDF to view.")


if __name__ == "__main__":
    test_complete_report()
