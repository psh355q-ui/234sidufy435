"""
Page 3 Generator (Korean Version): Skeptic & Contradiction Report

개선사항:
1. 줄간격 수정
2. 테이블 한글 폰트 적용 (모든 테이블)
3. 전체 한글화
4. 용어 해설 추가 (P/E, C/P Ratio, Put/Call 등)
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

# Import skeptic tracker
from backend.services.skeptic_performance_tracker import skeptic_tracker

logger = logging.getLogger(__name__)


class Page3GeneratorKorean:
    """
    Page 3: Skeptic & Contradiction Report Generator (Korean Version)
    
    이 페이지가 있으면: "AI가 조심스럽다 = 신뢰할 수 있다"
    """
    
    def __init__(self):
        """Initialize generator"""
        # Ensure Korean fonts are registered
        ensure_fonts_registered()
        self.setup_styles()
        logger.info("✅ Page3GeneratorKorean initialized")
    
    def setup_styles(self):
        """스타일 설정"""
        self.title_style = ParagraphStyle(
            'Title',
            fontName=get_korean_font_name(bold=True),
            fontSize=18,
            textColor=colors.HexColor('#ef4444'),
            spaceAfter=20,
            leading=24
        )
        
        self.heading_style = ParagraphStyle(
            'Heading',
            fontName=get_korean_font_name(bold=True),
            fontSize=14,
            textColor=colors.HexColor('#6b7280'),
            spaceBefore=15,
            spaceAfter=10,
            leading=20
        )
        
        self.body_style = ParagraphStyle(
            'Body',
            fontName=get_korean_font_name(),
            fontSize=11,
            leading=20,  # 줄간격 증가
            textColor=colors.HexColor('#374151')
        )
        
        self.warning_style = ParagraphStyle(
            'Warning',
            fontName=get_korean_font_name(),
            fontSize=11,
            leading=20,
            textColor=colors.HexColor('#dc2626'),
            leftIndent=20
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
        """Page 3 생성 (한글 버전)"""
        story = []
        
        # 1. Title
        story.append(Paragraph(
            "🔍 회의론자 분석 & 모순 신호 보고서",
            self.title_style
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # 2. Wrong reasons
        story.extend(self._create_wrong_reasons_korean(data.get("risk_reasons", [])))
        story.append(Spacer(1, 0.3*inch))
        
        # 3. Contradiction Radar
        story.extend(self._create_contradiction_radar_korean(data.get("contradictions", [])))
        story.append(Spacer(1, 0.3*inch))
        
        # 4. Skeptic Opinion
        story.extend(self._create_skeptic_opinion(data.get("skeptic_opinion", "")))
        story.append(Spacer(1, 0.3*inch))
        
        # 5. Constitutional Checklist
        story.extend(self._create_constitutional_check_korean(data.get("constitutional_checks", [])))
        story.append(Spacer(1, 0.3*inch))
        
        # 6. Skeptic Stats
        story.extend(self._create_skeptic_stats_korean())
        
        return story
    
    def _create_wrong_reasons_korean(self, reasons: List[Dict]) -> List:
        """틀릴 수 있는 이유 (한글 + 용어 해설)"""
        story = []
        
        story.append(Paragraph(
            "⚠️ 오늘 판단이 틀릴 수 있는 이유 3가지",
            self.heading_style
        ))
        story.append(Spacer(1, 0.2*inch))
        
        # 기본 데이터 (한글화 + 용어 설명)
        default_reasons = [
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
        ]
        
        reasons_to_use = reasons if reasons else default_reasons
        
        for i, reason in enumerate(reasons_to_use[:3], 1):
            text = f"""
<b>{i}. {reason.get('category', 'Unknown Risk')}</b><br/>
• 현재: {reason.get('current', 'N/A')}<br/>
• 위험: {reason.get('risk', 'N/A')}<br/>
• 확률: {reason.get('probability', 0)}% (다음 2주 내)<br/>
"""
            story.append(Paragraph(text, self.body_style))
            story.append(Spacer(1, 0.15*inch))
        
        # 용어 해설
        story.append(Spacer(1, 0.1*inch))
        footnotes = """
<b>※ 용어 해설:</b><br/>
• P/E: 주가수익비율 (Price-to-Earnings Ratio) - 주가를 주당순이익으로 나눈 값, 높을수록 고평가<br/>
• C/P Ratio: 콜옵션/풋옵션 비율 - 낙관적 베팅/비관적 베팅 비율, 높을수록 강세 전망
"""
        story.append(Paragraph(footnotes, self.footnote_style))
        
        return story
    
    def _create_contradiction_radar_korean(self, contradictions: List[Dict]) -> List:
        """모순 레이더 (한글 폰트)"""
        story = []
        
        story.append(Paragraph("모순 신호 레이더", self.heading_style))
        story.append(Spacer(1, 0.15*inch))
        
        # 기본 데이터 (한글화)
        default_contradictions = [
            {"indicator": "지수", "signal": "상승", "interpretation": "강세"},
            {"indicator": "거래량", "signal": "감소", "interpretation": "경고"},
            {"indicator": "VIX", "signal": "급락", "interpretation": "경고 (과도한 낙관)"},
            {"indicator": "Put/Call※", "signal": "0.65", "interpretation": "강세"},
            {"indicator": "10년물 금리", "signal": "상승", "interpretation": "모순 (금리 상승)"},
        ]
        
        contradictions_to_use = contradictions if contradictions else default_contradictions
        
        # Header
        data = [
            ["지표", "신호", "해석"]
        ]
        
        # Add data
        for item in contradictions_to_use:
            signal = item["signal"]
            interp = item["interpretation"]
            
            # Add warning emoji
            if "경고" in interp or "모순" in interp or "Warning" in interp:
                interp = f"⚠️ {interp}"
            
            data.append([
                item["indicator"],
                signal,
                interp
            ])
        
        # Summary row
        warning_count = sum(1 for c in contradictions_to_use if "경고" in c["interpretation"] or "모순" in c["interpretation"] or "Warning" in c["interpretation"])
        consensus = ((len(contradictions_to_use) - warning_count) / len(contradictions_to_use) * 100) if contradictions_to_use else 0
        
        data.append([
            "",
            f"⚠️ 모순: {warning_count}/{len(contradictions_to_use)}",
            f"합의도: {consensus:.0f}%"
        ])
        
        # Create table with KOREAN FONT
        table = Table(data, colWidths=[2*inch, 1.5*inch, 2*inch])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), get_korean_font_name(bold=True)),  # 한글 폰트!
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('FONTNAME', (0, 1), (-1, -2), get_korean_font_name()),  # 한글 폰트!
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey]),
            
            # Summary
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fef3c7')),
            ('FONTNAME', (0, -1), (-1, -1), get_korean_font_name(bold=True)),  # 한글 폰트!
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.15*inch))
        
        # 용어 해설
        footnotes = """
<b>※ 용어 해설:</b><br/>
• Put/Call: 풋옵션/콜옵션 비율 - 하락 베팅/상승 베팅 비율, 낮을수록 강세 전망
"""
        story.append(Paragraph(footnotes, self.footnote_style))
        
        return story
    
    def _create_skeptic_opinion(self, opinion: str) -> List:
        """회의론자 최종 의견"""
        story = []
        
        story.append(Paragraph("회의론자 최종 의견", self.heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        if not opinion:
            opinion = """
상승 추세는 맞으나, 내부 구조는 건강하지 않음.
현재 포지션 유지하되, 추가매수는 신중해야 함.
특히 기술주 집중도가 높아 섹터 조정 시 취약.
"""
        
        formatted = f'"{opinion.strip()}"'
        
        story.append(Paragraph(formatted, self.warning_style))
        
        return story
    
    def _create_constitutional_check_korean(self, checks: List[Dict]) -> List:
        """헌법 검증 체크리스트 (한글 폰트)"""
        story = []
        
        story.append(Paragraph("헌법 검증 체크리스트", self.heading_style))
        story.append(Spacer(1, 0.15*inch))
        
        # 기본 데이터 (한글화)
        default_checks = [
            {"rule": "과잉 확신 방지 (신뢰도 < 95%)", "status": "Pass"},
            {"rule": "반대 시나리오 검토 완료", "status": "Pass"},
            {"rule": "포지션 한도 준수 (< 30%)", "status": "Pass"},
            {"rule": "단기 유동성 리스크 완전 해소", "status": "Warning"},
        ]
        
        checks_to_use = checks if checks else default_checks
        
        # Header
        data = [
            ["검증 항목", "상태"]
        ]
        
        # Add checks
        for check in checks_to_use:
            status = check["status"]
            rule = check["rule"]
            
            # Add emoji
            if status == "Pass":
                status_display = "✓ 통과"
            elif status == "Warning":
                status_display = "⚠ 경고"
            else:
                status_display = "✗ 실패"
            
            data.append([rule, status_display])
        
        # Create table with KOREAN FONT
        table = Table(data, colWidths=[4*inch, 1.5*inch])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), get_korean_font_name(bold=True)),  # 한글 폰트!
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), get_korean_font_name()),  # 한글 폰트!
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ]))
        
        story.append(table)
        
        return story
    
    def _create_skeptic_stats_korean(self) -> List:
        """회의론자 성과 기록 (한글 폰트)"""
        story = []
        
        story.append(Paragraph("📊 회의론자 성과 기록 (30일)", self.heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Get stats
        stats = skeptic_tracker.get_cumulative_avoided_loss(30)
        
        # Header
        data = [
            ["지표", "값"]
        ]
        
        # Add data (한글화)
        data.append(["총 거부 건수", str(stats["num_vetoes"])])
        data.append(["올바른 거부", f"{stats['correct_vetoes']}건 ({stats['skeptic_accuracy']:.0f}%)"])
        data.append(["회피한 손실", f"${stats['total_avoided_loss']:,.2f}"])
        data.append(["거부당 평균", f"${stats['avg_avoided_per_veto']:,.2f}"])
        
        # Create table with KOREAN FONT
        table = Table(data, colWidths=[3*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), get_korean_font_name(bold=True)),  # 한글 폰트!
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 1), (-1, -1), get_korean_font_name()),  # 한글 폰트!
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.1*inch))
        
        # Interpretation
        interp = f"💡 회의론자가 잠재적으로 나쁜 거래의 {stats['skeptic_accuracy']:.0f}%를 방지했습니다"
        story.append(Paragraph(interp, self.body_style))
        
        return story


# Test function
def test_page3_korean():
    """Page 3 한글 버전 테스트"""
    from reportlab.platypus import SimpleDocTemplate
    
    print("="*60)
    print("Page 3 Generator (Korean Version) Test")
    print("="*60)
    
    # Mock data
    mock_data = {
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
    
    # Generate
    generator = Page3GeneratorKorean()
    story = generator.generate(mock_data)
    
    # Create PDF
    output_path = "test_page3_korean.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    doc.build(story)
    
    print(f"\n✅ Page 3 (Korean) generated: {output_path}")
    print(f"📄 Total elements: {len(story)}")
    print("\n수정사항:")
    print("  ✓ 모든 테이블 한글 폰트 적용")
    print("  ✓ 제목 한글화 (회의론자 분석)")
    print("  ✓ 용어 해설 추가 (P/E, C/P Ratio, Put/Call)")
    print("  ✓ 전체 한글화")
    print("\n" + "="*60)
    print("✅ Test completed! Open the PDF to view.")


if __name__ == "__main__":
    test_page3_korean()
