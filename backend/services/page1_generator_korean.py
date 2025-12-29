"""
Page 1 Generator (Korean Version): Executive Market Narrative

목표: 오늘 시장의 본질을 한 눈에

개선사항:
1. 줄간격 수정 (leading 20)
2. 테이블 한글 폰트 적용
3. 전체 한글화
4. 용어 해설 추가 (ECB, Fed, VIX 등)
"""
import logging
from datetime import datetime
from typing import Dict, List
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

# Import Korean font setup
from backend.services.korean_font_setup import ensure_fonts_registered, get_korean_font_name

logger = logging.getLogger(__name__)


class Page1GeneratorKorean:
    """
    Page 1: Executive Market Narrative Generator (Korean Version)
    
    서사 비중: 80% (숫자는 최소)
    """
    
    def __init__(self):
        """Initialize generator"""
        # Ensure Korean fonts are registered
        ensure_fonts_registered()
        self.setup_styles()
        logger.info("✅ Page1GeneratorKorean initialized")
    
    def setup_styles(self):
        """스타일 설정"""
        self.title_style = ParagraphStyle(
            'Title',
            fontName=get_korean_font_name(bold=True),
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            alignment=1,  # Center
            spaceAfter=20,
            leading=30  # 줄간격 증가
        )
        
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            fontName=get_korean_font_name(),
            fontSize=14,
            textColor=colors.HexColor('#6b7280'),
            alignment=1,
            spaceAfter=30,
            leading=20
        )
        
        self.heading_style = ParagraphStyle(
            'Heading',
            fontName=get_korean_font_name(bold=True),
            fontSize=14,
            textColor=colors.HexColor('#374151'),
            spaceBefore=15,
            spaceAfter=10,
            leading=20
        )
        
        self.body_style = ParagraphStyle(
            'Body',
            fontName=get_korean_font_name(),
            fontSize=11,
            leading=20,  # 줄간격 증가 (16 -> 20)
            textColor=colors.HexColor('#4b5563')
        )
        
        self.summary_style = ParagraphStyle(
            'Summary',
            fontName=get_korean_font_name(bold=True),
            fontSize=16,
            textColor=colors.HexColor('#1f2937'),
            alignment=1,
            spaceAfter=20,
            leftIndent=40,
            rightIndent=40,
            leading=28  # 줄간격 증가 (중요!)
        )
        
        self.footnote_style = ParagraphStyle(
            'Footnote',
            fontName=get_korean_font_name(),
            fontSize=9,
            textColor=colors.HexColor('#9ca3af'),
            leftIndent=10,
            leading=12
        )
    
    def generate(self, data: Dict) -> List:
        """
        Page 1 생성 (한글 버전)
        """
        story = []
        
        # 1. Header
        story.extend(self._create_header(data.get("date", datetime.now())))
        
        # 2. One-sentence summary
        story.append(self._create_summary(data.get("market_summary", "")))
        story.append(Spacer(1, 0.4*inch))
        
        # 3. Market flow + 용어 해설
        story.extend(self._create_market_flow_korean(data.get("market_flow", {})))
        story.append(Spacer(1, 0.3*inch))
        
        # 4. Key questions + 용어 해설
        story.extend(self._create_key_questions_korean(data.get("key_questions", [])))
        story.append(Spacer(1, 0.3*inch))
        
        # 5. Indicators table + 용어 해설
        story.extend(self._create_indicators_korean(data.get("key_indicators", [])))
        
        return story
    
    def _create_header(self, date: datetime) -> List:
        """리포트 헤더"""
        story = []
        
        story.append(Paragraph("AI TRADING SYSTEM", self.title_style))
        story.append(Paragraph("Daily Market Report", self.subtitle_style))
        story.append(Paragraph(
            date.strftime("%Y-%m-%d"),
            self.subtitle_style
        ))
        
        # Separator
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_summary(self, summary: str) -> Paragraph:
        """AI 한 문장 요약"""
        if not summary:
            summary = "시장은 강세였지만, 내부적으로는 위험 신호가 누적되는 하루였다."
        
        # Add quotation marks
        formatted = f'"{summary}"'
        
        return Paragraph(formatted, self.summary_style)
    
    def _create_market_flow_korean(self, flow: Dict) -> List:
        """시장 흐름 (한글 + 용어 해설)"""
        story = []
        
        story.append(Paragraph("시장 흐름", self.heading_style))
        
        # 기본 데이터로 한글화된 내용 사용
        regions = [
            ("아시아", flow.get("asia", "중국 경기 우려로 약세 (-0.5%)")),
            ("유럽", flow.get("europe", "ECB※ 완화 기대로 강세 (+0.8%)")),
            ("미국", flow.get("us", "기술주 주도 상승, 하지만 거래량 감소 (-18%)"))
        ]
        
        for region, desc in regions:
            text = f"• <b>{region}</b>: {desc}"
            story.append(Paragraph(text, self.body_style))
            story.append(Spacer(1, 0.05*inch))
        
        # 용어 해설
        story.append(Spacer(1, 0.1*inch))
        footnote = "※ ECB: 유럽중앙은행(European Central Bank) - 유럽연합의 중앙은행"
        story.append(Paragraph(footnote, self.footnote_style))
        
        return story
    
    def _create_key_questions_korean(self, questions: List[Dict]) -> List:
        """핵심 질문 (한글 + 용어 해설)"""
        story = []
        
        story.append(Paragraph("오늘 시장의 핵심 질문", self.heading_style))
        story.append(Spacer(1, 0.15*inch))
        
        # 한글화된 기본 질문 사용
        default_questions = [
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
        ]
        
        questions_to_use = questions if questions else default_questions
        
        for i, q in enumerate(questions_to_use[:2], 1):
            text = f"""
<b>{i}. "{q.get('question', 'N/A')}"</b><br/>
→ AI 판단: {q.get('ai_answer', 'N/A')}<br/>
   (근거: {q.get('reasoning', 'N/A')})
"""
            story.append(Paragraph(text, self.body_style))
            story.append(Spacer(1, 0.15*inch))
        
        # 용어 해설
        story.append(Spacer(1, 0.05*inch))
        footnotes = """
<b>※ 용어 해설:</b><br/>
• VIX: 변동성 지수 - 시장 불안도를 나타내는 지표<br/>
• Fed: 미국 연방준비제도(Federal Reserve) - 미국의 중앙은행<br/>
• 피봇: 금리 정책 방향 전환 (인상 → 인하)
"""
        story.append(Paragraph(footnotes, self.footnote_style))
        
        return story
    
    def _create_indicators_korean(self, indicators: List[Dict]) -> List:
        """지표 테이블 (한글 폰트 + 용어 해설)"""
        story = []
        
        # 기본 데이터 (한글화)
        default_indicators = [
            {"name": "S&P 500", "change": "+0.8%", "signal": "⚠️"},
            {"name": "VIX", "change": "-5.2%", "signal": "⚠️"},
            {"name": "거래량", "change": "-18%", "signal": "⚠️"},
            {"name": "10년물 금리", "change": "+0.05%", "signal": "📈"},
        ]
        
        indicators_to_use = indicators if indicators else default_indicators
        
        # Header (한글)
        data = [
            ["지표", "변화", "신호"]
        ]
        
        # Add indicators
        for ind in indicators_to_use[:5]:
            data.append([
                ind.get("name", ""),
                ind.get("change", ""),
                ind.get("signal", "")
            ])
        
        # Create table with KOREAN FONT
        table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), get_korean_font_name(bold=True)),  # 한글 폰트!
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), get_korean_font_name()),  # 한글 폰트!
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.15*inch))
        
        # Signal 설명
        signal_note = "⚠️ = 모순 신호 발생 (상승하지만 내부 구조는 약함)"
        story.append(Paragraph(signal_note, self.footnote_style))
        story.append(Spacer(1, 0.1*inch))
        
        # 용어 해설
        footnotes = """
<b>※ 지표 해설:</b><br/>
• S&P 500: 미국 대표 500개 기업 주가지수<br/>
• VIX: 변동성 지수 (공포지수) - 낮을수록 시장 안정<br/>
• 거래량: 하루 동안 거래된 주식 수 - 많을수록 강한 추세<br/>
• 10년물 금리: 미국 10년 만기 국채 수익률 - 금리 방향 선행지표
"""
        story.append(Paragraph(footnotes, self.footnote_style))
        
        return story


# Test function
def test_page1_korean():
    """Page 1 한글 버전 테스트"""
    from reportlab.platypus import SimpleDocTemplate
    
    print("="*60)
    print("Page 1 Generator (Korean Version) Test")
    print("="*60)
    
    # Mock data
    mock_data = {
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
    }
    
    # Generate
    generator = Page1GeneratorKorean()
    story = generator.generate(mock_data)
    
    # Create PDF
    output_path = "test_page1_korean.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    doc.build(story)
    
    print(f"\n✅ Page 1 (Korean) generated: {output_path}")
    print(f"📄 Total elements: {len(story)}")
    print("\n수정사항:")
    print("  ✓ 줄간격 조정 (leading 20-28)")
    print("  ✓ 테이블 한글 폰트 적용")
    print("  ✓ 전체 한글화")
    print("  ✓ 용어 해설 추가 (ECB, Fed, VIX, S&P 500 등)")
    print("\n" + "="*60)
    print("✅ Test completed! Open the PDF to view.")


if __name__ == "__main__":
    test_page1_korean()
