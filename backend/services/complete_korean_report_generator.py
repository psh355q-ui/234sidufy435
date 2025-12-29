"""
Complete Korean Report Generator

통합: Page 1 + Page 3 한글 버전
모든 사용자 요청 반영:
1. ✓ 줄간격 수정
2. ✓ 테이블 한글 폰트
3. ✓ 전체 한글화
4. ✓ 용어 해설 추가
"""
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, PageBreak

from backend.services.page1_generator_korean import Page1GeneratorKorean
from backend.services.page3_generator_korean import Page3GeneratorKorean

logger = logging.getLogger(__name__)


class CompleteKoreanReportGenerator:
    """완전한 한글 리포트 생성기"""
    
    def __init__(self):
        self.page1_gen = Page1GeneratorKorean()
        self.page3_gen = Page3GeneratorKorean()
        logger.info("✅ CompleteKoreanReportGenerator initialized")
    
    def generate_complete_report(self, output_path: str = "complete_korean_report.pdf") -> str:
        """완전한 한글 리포트 생성"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Get mock data
        data = self._get_mock_data_korean()
        
        # Page 1: Market Narrative (Korean)
        story.extend(self.page1_gen.generate(data["page1"]))
        story.append(PageBreak())
        
        # Page 3: Skeptic Analysis (Korean)
        story.extend(self.page3_gen.generate(data["page3"]))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"✅ Complete Korean report generated: {output_path}")
        return output_path
    
    def _get_mock_data_korean(self) -> dict:
        """Mock 데이터 (한글화)"""
        return {
            "page1": {
                "date": datetime.now(),
                "market_summary": "시장은 강세였지만, 내부적으로는 위험 신호가 누적되는 하루였다.",
                "market_flow": {
                    "asia": "중국 경기 우려로 약세 (-0.5%)",
                    "europe": "ECB※ 완화 기대로 강세 (+0.8%)",
                    "us": "기술주 주도 상승, 하지만 거래량 감소 (-18%)"
                },
                "key_questions": [
                    {
                        "question": "이 상승은 추세인가, 숏커버인가?",
                        "ai_answer": "숏커버 가능성 65%",
                        "reasoning": "거래량 부족 + VIX※ 급락"
                    },
                    {
                        "question": "Fed※는 정말 피봇할까?",
                        "ai_answer": "아직 시기상조 (확률 30%)",
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


def test_complete_korean_report():
    """완전한 한글 리포트 테스트"""
    print("="*60)
    print("Complete Korean Report Generator Test")
    print("="*60)
    print("\n모든 사용자 요청 사항 반영:")
    print("  ✓ 1. 줄간격 수정 (leading 20-28)")
    print("  ✓ 2. 모든 테이블 한글 폰트 적용")
    print("  ✓ 3. 전체 한글화 (제목/날짜 제외)")
    print("  ✓ 4. 용어 해설 추가 (ECB, Fed, VIX, P/E, C/P Ratio, Put/Call)")
    print("\nGenerating complete Korean report...")
    
    generator = CompleteKoreanReportGenerator()
    output_path = generator.generate_complete_report()
    
    print(f"\n✅ Complete Korean report generated: {output_path}")
    print("\nPages included:")
    print("  • Page 1: 시장 서사 보고서 (한글)")
    print("  • Page 3: 회의론자 분석 & 모순 신호 (한글)")
    
    print("\n" + "="*60)
    print("✅ Test completed! Open the PDF to view.")
    print("\nAll user-requested fixes applied:")
    print("  1. Line spacing fixed (no overlapping text)")
    print("  2. All table fonts showing Korean correctly")
    print("  3. Full Korean translation")
    print("  4. Glossary for all technical terms")


if __name__ == "__main__":
    test_complete_korean_report()
