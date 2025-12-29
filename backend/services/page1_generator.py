"""
Page 1 Generator: Executive Market Narrative

목표: 오늘 시장의 본질을 한 눈에

포함 내용:
1. AI 한 문장 요약 (자동 생성)
2. 시장 흐름 (Overnight → Intraday)
3. 오늘 시장의 핵심 질문 2개 + AI 답변
4. 최소 지표 테이블 (숫자는 최소)
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


class Page1Generator:
    """
    Page 1: Executive Market Narrative Generator
    
    서사 비중: 80% (숫자는 최소)
    """
    
    def __init__(self):
        """Initialize generator"""
        # Ensure Korean fonts are registered
        ensure_fonts_registered()
        self.setup_styles()
        logger.info("✅ Page1Generator initialized")
    
    def setup_styles(self):
        """스타일 설정"""
        self.title_style = ParagraphStyle(
            'Title',
            fontName=get_korean_font_name(bold=True),
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            alignment=1,  # Center
            spaceAfter=20
        )
        
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            fontName=get_korean_font_name(),
            fontSize=14,
            textColor=colors.HexColor('#6b7280'),
            alignment=1,
            spaceAfter=30
        )
        
        self.heading_style = ParagraphStyle(
            'Heading',
            fontName=get_korean_font_name(bold=True),
            fontSize=14,
            textColor=colors.HexColor('#374151'),
            spaceBefore=15,
            spaceAfter=10
        )
        
        self.body_style = ParagraphStyle(
            'Body',
            fontName=get_korean_font_name(),
            fontSize=11,
            leading=16,
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
            rightIndent=40
        )
    
    def generate(self, data: Dict) -> List:
        """
        Page 1 생성
        
        Args:
            data: {
                "date": datetime,
                "market_summary": str,  # AI 한 문장 요약
                "market_flow": Dict,  # Asia/Europe/US 흐름
                "key_questions": List[Dict],  # 핵심 질문 2개
                "key_indicators": List[Dict]  # 최소 지표
            }
        """
        story = []
        
        # 1. Header
        story.extend(self._create_header(data.get("date", datetime.now())))
        
        # 2. One-sentence summary (핵심!)
        story.append(self._create_summary(data.get("market_summary", "")))
        story.append(Spacer(1, 0.4*inch))
        
        # 3. Market flow
        story.extend(self._create_market_flow(data.get("market_flow", {})))
        story.append(Spacer(1, 0.3*inch))
        
        # 4. Key questions
        story.extend(self._create_key_questions(data.get("key_questions", [])))
        story.append(Spacer(1, 0.3*inch))
        
        # 5. Minimal indicators
        story.append(self._create_indicators(data.get("key_indicators", [])))
        
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
        """
        AI 한 문장 요약
        
        Template Logic:
        - 강세 + 건강: "시장은 강세를 이어가며 내부 구조도 개선됐다"
        - 강세 + 위험: "시장은 강세였지만 내부 위험 신호가 누적됐다"
        - 약세 + 기회: "시장은 약세였으나 저점 매수 기회가 나타났다"
        - 약세 + 악화: "시장은 약세를 지속하며 추가 하락 위험이 크다"
        """
        if not summary:
            summary = "시장은 강세였지만, 내부적으로는 위험 신호가 누적되는 하루였다."
        
        # Add quotation marks
        formatted = f'"{summary}"'
        
        return Paragraph(formatted, self.summary_style)
    
    def _create_market_flow(self, flow: Dict) -> List:
        """
        시장 흐름 (Asia → Europe → US)
        
        Args:
            flow: {
                "asia": "중국 경기 우려로 약세 (-0.5%)",
                "europe": "ECB 완화 기대로 강세 (+0.8%)",
                "us": "Tech 주도 상승, 하지만 거래량 감소 (-18%)"
            }
        """
        story = []
        
        story.append(Paragraph("시장 흐름", self.heading_style))
        
        regions = [
            ("아시아", flow.get("asia", "N/A")),
            ("유럽", flow.get("europe", "N/A")),
            ("미국", flow.get("us", "N/A"))
        ]
        
        for region, desc in regions:
            text = f"• <b>{region}</b>: {desc}"
            story.append(Paragraph(text, self.body_style))
            story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _create_key_questions(self, questions: List[Dict]) -> List:
        """
        오늘 시장의 핵심 질문 2개 + AI 답변
        
        Args:
            questions: [
                {
                    "question": "이 상승은 추세인가, 숏커버인가?",
                    "ai_answer": "숏커버 가능성 65%",
                    "reasoning": "거래량 부족 + VIX 급락"
                },
                ...
            ]
        """
        story = []
        
        story.append(Paragraph("오늘 시장의 핵심 질문", self.heading_style))
        story.append(Spacer(1, 0.15*inch))
        
        for i, q in enumerate(questions[:2], 1):
            text = f"""
<b>{i}. "{q.get('question', 'N/A')}"</b><br/>
→ AI 판단: {q.get('ai_answer', 'N/A')}<br/>
   (근거: {q.get('reasoning', 'N/A')})
"""
            story.append(Paragraph(text, self.body_style))
            story.append(Spacer(1, 0.15*inch))
        
        return story
    
    def _create_indicators(self, indicators: List[Dict]) -> Table:
        """
        최소 지표 테이블
        
        Args:
            indicators: [
                {
                    "name": "S&P 500",
                    "change": "+0.8%",
                    "signal": "⚠️"
                },
                ...
            ]
        """
        # Header
        data = [
            ["Index", "Change", "Signal"]
        ]
        
        # Add indicators
        for ind in indicators[:5]:  # 최대 5개만
            data.append([
                ind.get("name", ""),
                ind.get("change", ""),
                ind.get("signal", "")
            ])
        
        # Add note
        note = "⚠️ = 모순 신호 발생"
        
        # Create table
        table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        return table


# Test function
def test_page1_generator():
    """Page 1 생성 테스트"""
    from reportlab.platypus import SimpleDocTemplate
    
    print("="*60)
    print("Page 1 Generator Test")
    print("="*60)
    
    # Mock data
    mock_data = {
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
    }
    
    # Generate
    generator = Page1Generator()
    story = generator.generate(mock_data)
    
    # Create PDF
    output_path = "test_page1_narrative.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    doc.build(story)
    
    print(f"\n✅ Page 1 generated: {output_path}")
    print(f"📄 Total elements: {len(story)}")
    print("\n" + "="*60)
    print("✅ Test completed! Open the PDF to view.")


if __name__ == "__main__":
    test_page1_generator()
