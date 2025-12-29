"""
Page 3 Generator: Skeptic & Contradiction Report

가장 중요한 페이지 - AI가 스스로를 의심하고 있음을 보여줌

포함 내용:
1. 오늘 판단이 틀릴 수 있는 이유 3가지
2. Contradiction Radar (모순 지표 시각화)
3. Skeptic 최종 의견
4. Constitutional Validation 체크리스트
"""
import logging
from datetime import datetime
from typing import Dict, List
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

# Import Korean font  setup
from backend.services.korean_font_setup import ensure_fonts_registered, get_korean_font_name

# Import our skeptic tracker
from backend.services.skeptic_performance_tracker import skeptic_tracker

logger = logging.getLogger(__name__)


class Page3Generator:
    """
    Page 3: Skeptic & Contradiction Report Generator
    
    이 페이지가 있으면: "AI가 조심스럽다 = 신뢰할 수 있다"
    """
    
    def __init__(self):
        """Initialize generator"""
        # Ensure Korean fonts are registered
        ensure_fonts_registered()
        self.setup_styles()
        logger.info("✅ Page3Generator initialized")
    
    def setup_styles(self):
        """스타일 설정"""
        self.title_style = ParagraphStyle(
            'Title',
            fontName=get_korean_font_name(bold=True),
            fontSize=18,
            textColor=colors.HexColor('#ef4444'),
            spaceAfter=20
        )
        
        self.heading_style = ParagraphStyle(
            'Heading',
            fontName=get_korean_font_name(bold=True),
            fontSize=14,
            textColor=colors.HexColor('#6b7280'),
            spaceBefore=15,
            spaceAfter=10
        )
        
        self.body_style = ParagraphStyle(
            'Body',
            fontName=get_korean_font_name(),
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#374151')
        )
        
        self.warning_style = ParagraphStyle(
            'Warning',
            fontName=get_korean_font_name(),
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#dc2626'),
            leftIndent=20
        )
    
    def generate(self, data: Dict) -> List:
        """
        Page 3 생성
        
        Args:
            data: {
                "date": datetime,
                "risk_reasons": List[Dict],  # 틀릴 수 있는 이유
                "contradictions": List[Dict],  # 모순 지표
                "skeptic_opinion": str,
                "constitutional_checks": List[Dict]
            }
        
        Returns:
            List of reportlab elements
        """
        story = []
        
        # 1. Title with warning emoji
        story.append(Paragraph(
            "🔍 Skeptic & Contradiction Report",
            self.title_style
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # 2. Why AI might be wrong (3 reasons)
        story.extend(self._create_wrong_reasons(data.get("risk_reasons", [])))
        story.append(Spacer(1, 0.3*inch))
        
        # 3. Contradiction Radar
        story.append(self._create_contradiction_radar(data.get("contradictions", [])))
        story.append(Spacer(1, 0.3*inch))
        
        # 4. Skeptic Final Opinion
        story.extend(self._create_skeptic_opinion(data.get("skeptic_opinion", "")))
        story.append(Spacer(1, 0.3*inch))
        
        # 5. Constitutional Checklist
        story.append(self._create_constitutional_check(data.get("constitutional_checks", [])))
        story.append(Spacer(1, 0.3*inch))
        
        # 6. Skeptic Performance Stats
        story.extend(self._create_skeptic_stats())
        
        return story
    
    def _create_wrong_reasons(self, reasons: List[Dict]) -> List:
        """
        오늘 판단이 틀릴 수 있는 이유 3가지
        
        Args:
            reasons: [
                {
                    "category": "밸류에이션 리스크",
                    "current": "Tech P/E 38x",
                    "risk": "금리 재상승 시 급격한 조정",
                    "probability": 15
                },
                ...
            ]
        """
        story = []
        
        story.append(Paragraph(
            "⚠️ 오늘 판단이 틀릴 수 있는 이유 3가지",
            self.heading_style
        ))
        story.append(Spacer(1, 0.2*inch))
        
        for i, reason in enumerate(reasons[:3], 1):
            text = f"""
<b>{i}. {reason.get('category', 'Unknown Risk')}</b><br/>
• 현재: {reason.get('current', 'N/A')}<br/>
• 위험: {reason.get('risk', 'N/A')}<br/>
• 확률: {reason.get('probability', 0)}% (다음 2주 내)<br/>
"""
            story.append(Paragraph(text, self.body_style))
            story.append(Spacer(1, 0.15*inch))
        
        return story
    
    def _create_contradiction_radar(self, contradictions: List[Dict]) -> Table:
        """
        Contradiction Radar 테이블
        
        Args:
            contradictions: [
                {
                    "indicator": "지수",
                    "signal": "상승",
                    "interpretation": "Bullish"
                },
                ...
            ]
        """
        # Header
        data = [
            ["지표", "신호", "해석"]
        ]
        
        # Add contradiction data
        for item in contradictions:
            signal = item["signal"]
            interp = item["interpretation"]
            
            # Add warning emoji if contradiction
            if "Warning" in interp or "모순" in interp:
                interp = f"⚠️ {interp}"
            
            data.append([
                item["indicator"],
                signal,
                interp
            ])
        
        # Summary row
        warning_count = sum(1 for c in contradictions if "Warning" in c["interpretation"] or "모순" in c["interpretation"])
        consensus = ((len(contradictions) - warning_count) / len(contradictions) * 100) if contradictions else 0
        
        data.append([
            "",
            f"⚠️ 모순: {warning_count}/{len(contradictions)}",
            f"합의도: {consensus:.0f}%"
        ])
        
        # Create table
        table = Table(data, colWidths=[2*inch, 1.5*inch, 2*inch])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey]),
            
            # Summary row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fef3c7')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table
    
    def _create_skeptic_opinion(self, opinion: str) -> List:
        """Skeptic 최종 의견"""
        story = []
        
        story.append(Paragraph("Skeptic 최종 의견", self.heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        if not opinion:
            opinion = """
상승 추세는 맞으나, 내부 구조는 건강하지 않음.
현재 포지션 유지하되, 추가매수는 신중해야 함.
특히 Tech 집중도가 높아 섹터 조정 시 취약.
"""
        
        # Add quotation marks and styling
        formatted_opinion = f'"{opinion.strip()}"'
        
        story.append(Paragraph(formatted_opinion, self.warning_style))
        
        return story
    
    def _create_constitutional_check(self, checks: List[Dict]) -> Table:
        """
        Constitutional Validation 체크리스트 (간결!)
        
        Args:
            checks: [
                {
                    "rule": "과잉 확신 방지",
                    "status": "Pass" | "Warning" | "Fail"
                },
                ...
            ]
        """
        # Header
        data = [
            ["Constitutional Validation", "Status"]
        ]
        
        # Add checks
        for check in checks:
            status = check["status"]
            rule = check["rule"]
            
            # Add emoji
            if status == "Pass":
                status_display = "✓ Pass"
            elif status == "Warning":
                status_display = "⚠ Warning"
            else:
                status_display = "✗ Fail"
            
            data.append([rule, status_display])
        
        # Create table
        table = Table(data, colWidths=[4*inch, 1.5*inch])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ]))
        
        return table
    
    def _create_skeptic_stats(self) -> List:
        """Skeptic Performance Stats 추가"""
        story = []
        
        story.append(Paragraph("📊 Skeptic 성과 기록 (30일)", self.heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Get stats from tracker
        stats = skeptic_tracker.get_cumulative_avoided_loss(30)
        
        stats_data = [
            ["Metric", "Value"],
            ["Total Vetoes", str(stats["num_vetoes"])],
            ["Correct Vetoes", f"{stats['correct_vetoes']} ({stats['skeptic_accuracy']:.0f}%)"],
            ["Avoided Loss", f"${stats['total_avoided_loss']:,.2f}"],
            ["Avg per Veto", f"${stats['avg_avoided_per_veto']:,.2f}"],
        ]
        
        table = Table(stats_data, colWidths=[3*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.1*inch))
        
        # Add interpretation
        interp_text = f"💡 Skeptic has prevented {stats['skeptic_accuracy']:.0f}% of potentially bad trades"
        story.append(Paragraph(interp_text, self.body_style))
        
        return story


# Test function
def test_page3_generator():
    """Page 3 생성 테스트"""
    from reportlab.platypus import SimpleDocTemplate
    
    print("="*60)
    print("Page 3 Generator Test")
    print("="*60)
    
    # Mock data
    mock_data = {
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
                "risk": "옵션 신호가 항상 정확하지 않음 (최근 오신호 33%)",
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
    
    # Generate
    generator = Page3Generator()
    story = generator.generate(mock_data)
    
    # Create PDF
    output_path = "test_page3_skeptic.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    doc.build(story)
    
    print(f"\n✅ Page 3 generated: {output_path}")
    print(f"📄 Total elements: {len(story)}")
    print("\n" + "="*60)
    print("✅ Test completed! Open the PDF to view.")


if __name__ == "__main__":
    test_page3_generator()
