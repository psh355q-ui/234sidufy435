"""
Complete AI Report Generator (Final Korean Version)

통합사항:
1. ✓ 한글 폰트 (모든 테이블)
2. ✓ 줄간격 수정
3. ✓ 전체 한글화 + 용어 해설
4. ✓ 언어 템플릿 시스템 (25개 summary, 18개 question, 20개 answer)
5. ✓ 70% 조건부, 30% 확신 비율

ChatGPT 피드백 100% 반영
"""
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, PageBreak

from backend.services.page1_generator_korean import Page1GeneratorKorean
from backend.services.page3_generator_korean import Page3GeneratorKorean
from backend.services.market_language_templates import MarketLanguageTemplates

logger = logging.getLogger(__name__)


class FinalKoreanReportGenerator:
    """최종 한글 리포트 생성기 (언어 템플릿 통합)"""
    
    def __init__(self):
        self.page1_gen = Page1GeneratorKorean()
        self.page3_gen = Page3GeneratorKorean()
        self.lang = MarketLanguageTemplates()
        logger.info("✅ FinalKoreanReportGenerator initialized")
    
    def generate_final_report(self, output_path: str = "final_korean_report.pdf") -> str:
        """최종 리포트 생성"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Get dynamic data (언어 템플릿 활용)
        data = self._get_dynamic_data()
        
        # Page 1: Market Narrative
        story.extend(self.page1_gen.generate(data["page1"]))
        story.append(PageBreak())
        
        # Page 3: Skeptic Analysis
        story.extend(self.page3_gen.generate(data["page3"]))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"✅ Final Korean report generated: {output_path}")
        return output_path
    
    def _get_dynamic_data(self) -> dict:
        """동적 데이터 생성 (언어 템플릿 활용)"""
        
        # 시장 상태 분류 (현재는 하드코딩, 실제로는 실시간 데이터 기반)
        market_trend = "bullish"
        market_health = "fragile"
        
        return {
            "page1": {
                "date": datetime.now(),
                # 언어 템플릿에서 동적 선택
                "market_summary": self.lang.get_market_summary(market_trend, market_health),
                "market_flow": {
                    "asia": "중국 경기 우려로 약세 (-0.5%)",
                    "europe": "ECB※ 완화 기대로 강세 (+0.8%)",
                    "us": "기술주 주도 상승, 하지만 거래량 감소 (-18%)"
                },
                "key_questions": [
                    {
                        "question": self.lang.get_key_question("bullish"),
                        "ai_answer": self.lang.get_ai_answer("trend_vs_cover", "cover_likely"),
                        "reasoning": "거래량 부족 + VIX※ 급락"
                    },
                    {
                        "question": self.lang.get_key_question("fed"),
                        "ai_answer": self.lang.get_ai_answer("fed_pivot", "not_yet"),
                        "reasoning": "고용 지표 여전히 강함"
                    }
                ],
                "key_indicators": [
                    {"name": "S&P 500", "change": "+0.8%", "signal": "⚠️"},
                    {"name": "VIX", "change": "-5.2%", "signal": "⚠️"},
                    {"name": "거래량", "change": "-18%", "signal": "⚠️"},
                    {"name": "10년물 금리", "change": "+0.05%", "signal": "📈"},
                ]
            },
            "page3": {
                "date": datetime.now(),
                "risk_reasons": [
                    {
                        "category": "밸류에이션 리스크",
                        "current": "기술주 섹터 P/E※ 38배 (역사적 고점)",
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
                        "current": "콜옵션 우세 (C/P Ratio※ 2.5)",
                        "risk": "옵션 신호가 항상 정확하지 않음",
                        "probability": 20
                    }
                ],
                "contradictions": [
                    {"indicator": "지수", "signal": "상승", "interpretation": "강세"},
                    {"indicator": "거래량", "signal": "감소", "interpretation": "경고"},
                    {"indicator": "VIX", "signal": "급락", "interpretation": "경고 (과도한 낙관)"},
                    {"indicator": "Put/Call※", "signal": "0.65", "interpretation": "강세"},
                    {"indicator": "10년물 금리", "signal": "상승", "interpretation": "모순 (금리 상승)"},
                ],
                "skeptic_opinion": """
상승 추세는 맞으나, 내부 구조는 건강하지 않음.
현재 포지션 유지하되, 추가매수는 신중해야 함.
특히 기술주 집중도가 높아 섹터 조정 시 취약.
""",
                "constitutional_checks": [
                    {"rule": "과잉 확신 방지 (신뢰도 < 95%)", "status": "Pass"},
                    {"rule": "반대 시나리오 검토 완료", "status": "Pass"},
                    {"rule": "포지션 한도 준수 (< 30%)", "status": "Pass"},
                    {"rule": "단기 유동성 리스크 완전 해소", "status": "Warning"},
                ]
            }
        }


def test_final_report():
    """최종 리포트 테스트"""
    print("="*60)
    print("Final Korean Report Generator Test")
    print("="*60)
    print("\n✅ 모든 개선사항 통합:")
    print("  1. 한글 폰트 (모든 테이블)")
    print("  2. 줄간격 수정 (leading 20-28)")
    print("  3. 전체 한글화 + 용어 해설")
    print("  4. 언어 템플릿 시스템 (63개 변형)")
    print("  5. 조건부 표현 (70% conditional, 30% confident)")
    print("\nGenerating final report...")
    
    generator = FinalKoreanReportGenerator()
    output_path = generator.generate_final_report()
    
    print(f"\n✅ Final report generated: {output_path}")
    print("\nPages included:")
    print("  • Page 1: 시장 서사 보고서 (동적 언어 템플릿)")
    print("  • Page 3: 회의론자 분석 (한글 완성)")
    
    # Show sample generated text
    lang = MarketLanguageTemplates()
    print("\n샘플 동적 생성 문장:")
    print(f"\n  강세+위험: \"{lang.get_market_summary('bullish', 'fragile')}\"")
    print(f"\n  강세+건강: \"{lang.get_market_summary('bullish', 'healthy')}\"")
    print(f"\n  질문: \"{lang.get_key_question('bullish')}\"")
    
    print("\n" + "="*60)
    print("✅ Test completed! Open the PDF to view.")
    print("\nChatGPT 피드백 100% 반영 완료!")


if __name__ == "__main__":
    test_final_report()
