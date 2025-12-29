"""
Page 5 Generator (Korean): Tomorrow Risk Playbook

목적: 내일 뭘 조심해야 하는가 + AI의 자세는?

섹션:
1. Top 3 Risks (확률 + AI 대응)
2. AI Stance Indicator (DEFENSIVE/NEUTRAL/AGGRESSIVE)
3. Tomorrow Scenario Matrix
4. Action Items Checklist

실제 데이터 연동 준비:
- Risk Analysis Engine 결과
- Portfolio Position 기반 AI Stance 계산
"""
import logging
from datetime import datetime
from typing import Dict, List
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from backend.services.korean_font_setup import ensure_fonts_registered, get_korean_font_name

logger = logging.getLogger(__name__)


class Page5GeneratorKorean:
    """
    Page 5: Tomorrow Risk Playbook (Korean)
    
    실제 데이터 통합 가능한 구조
    """
    
    def __init__(self):
        """Initialize generator"""
        ensure_fonts_registered()
        self.setup_styles()
        logger.info("✅ Page5GeneratorKorean initialized")
    
    def setup_styles(self):
        """스타일 설정"""
        self.title_style = ParagraphStyle(
            'Title',
            fontName=get_korean_font_name(bold=True),
            fontSize=18,
            textColor=colors.HexColor('#f59e0b'),
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
            leading=20,
            textColor=colors.HexColor('#374151')
        )
        
        self.stance_style = ParagraphStyle(
            'Stance',
            fontName=get_korean_font_name(bold=True),
            fontSize=14,
            leading=20,
            textColor=colors.HexColor('#1f2937'),
            alignment=1  # Center
        )
    
    def generate(self, data: Dict) -> List:
        """Page 5 생성"""
        story = []
        
        # Title
        story.append(Paragraph(
            "📅 내일의 리스크 플레이북",
            self.title_style
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # 1. Top 3 Risks
        story.extend(self._create_top_risks(data.get("top_risks", [])))
        story.append(Spacer(1, 0.3*inch))
        
        # 2. AI Stance
        story.extend(self._create_ai_stance(data.get("ai_stance", "NEUTRAL")))
        story.append(Spacer(1, 0.3*inch))
        
        # 3. Tomorrow Scenarios
        story.extend(self._create_tomorrow_scenarios(data.get("tomorrow_scenarios", [])))
        story.append(Spacer(1, 0.3*inch))
        
        # 4. Action Items
        story.extend(self._create_action_items(data.get("action_items", [])))
        
        return story
    
    def _create_top_risks(self, risks: List[Dict]) -> List:
        """Top 3 Risks 테이블"""
        story = []
        
        story.append(Paragraph("⚠️ 주요 리스크 Top 3", self.heading_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Default risks
        default_risks = [
            {
                "risk": "Fed 위원 매파 발언",
                "probability": 30,
                "ai_response": "포지션 10% 축소"
            },
            {
                "risk": "Tech 실적 부진",
                "probability": 25,
                "ai_response": "방어 섹터 전환"
            },
            {
                "risk": "10년물 금리 급등",
                "probability": 20,
                "ai_response": "현금 비중 확대"
            },
        ]
        
        risks_to_use = risks if risks else default_risks
        
        # Header
        data = [
            ["리스크", "확률", "AI 대응"]
        ]
        
        # Add risks
        for risk in risks_to_use[:3]:
            data.append([
                risk.get("risk", ""),
                f"{risk.get('probability', 0)}%",
                risk.get("ai_response", "")
            ])
        
        # Create table
        table = Table(data, colWidths=[2.5*inch, 1*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), get_korean_font_name(bold=True)),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), get_korean_font_name()),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
        
        return story
    
    def _create_ai_stance(self, stance: str) -> List:
        """AI Stance 표시기"""
        story = []
        
        story.append(Paragraph("🎯 AI의 현재 자세", self.heading_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Stance mapping
        stance_map = {
            "DEFENSIVE": ("🔴 방어적 (DEFENSIVE)", "현금 비중 확대, 포지션 축소"),
            "NEUTRAL": ("🟡 중립적 (NEUTRAL)", "현 상태 유지, 관망"),
            "AGGRESSIVE": ("🟢 공격적 (AGGRESSIVE)", "기회 포착, 포지션 확대")
        }
        
        stance_info = stance_map.get(stance, stance_map["NEUTRAL"])
        
        # Stance text
        stance_text = f"""
<b>{stance_info[0]}</b><br/>
<br/>
{stance_info[1]}
"""
        
        story.append(Paragraph(stance_text, self.stance_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Visual indicator
        indicator_text = self._create_stance_indicator(stance)
        story.append(Paragraph(indicator_text, self.body_style))
        
        return story
    
    def _create_stance_indicator(self, stance: str) -> str:
        """Stance 시각적 표시기"""
        positions = {
            "DEFENSIVE": "●───────────",
            "NEUTRAL": "──────●─────",
            "AGGRESSIVE": "───────────●"
        }
        
        indicator = positions.get(stance, positions["NEUTRAL"])
        
        return f"""
<font name="{get_korean_font_name()}">
[방어적] {indicator} [공격적]
</font>
"""
    
    def _create_tomorrow_scenarios(self, scenarios: List[Dict]) -> List:
        """Tomorrow Scenario Matrix"""
        story = []
        
        story.append(Paragraph("📊 내일 시나리오 분석", self.heading_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Default scenarios
        default_scenarios = [
            {
                "scenario": "상승 지속 (+0.5~1%)",
                "probability": 40,
                "ai_action": "현 포지션 유지"
            },
            {
                "scenario": "횡보 (±0.3%)",
                "probability": 35,
                "ai_action": "관망"
            },
            {
                "scenario": "조정 (-0.5~1%)",
                "probability": 25,
                "ai_action": "부분 청산 (30%)"
            },
        ]
        
        scenarios_to_use = scenarios if scenarios else default_scenarios
        
        # Header
        data = [
            ["시나리오", "확률", "AI 행동"]
        ]
        
        # Add scenarios
        for scenario in scenarios_to_use:
            data.append([
                scenario.get("scenario", ""),
                f"{scenario.get('probability', 0)}%",
                scenario.get("ai_action", "")
            ])
        
        # Create table
        table = Table(data, colWidths=[2.2*inch, 1*inch, 2.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), get_korean_font_name(bold=True)),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), get_korean_font_name()),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
        
        return story
    
    def _create_action_items(self, items: List[str]) -> List:
        """Action Items 체크리스트"""
        story = []
        
        story.append(Paragraph("✅ 내일 체크할 항목", self.heading_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Default items
        default_items = [
            "Fed 위원 발언 모니터링 (14:00 KST)",
            "Tech 섹터 실적 발표 확인 (장후)",
            "VIX 20선 돌파 여부",
            "10년물 금리 4.5% 수준 주시",
        ]
        
        items_to_use = items if items else default_items
        
        # Create checklist
        checklist_text = ""
        for item in items_to_use:
            checklist_text += f"□ {item}<br/>"
        
        story.append(Paragraph(checklist_text, self.body_style))
        
        return story


# Test function
def test_page5_korean():
    """Page 5 테스트"""
    from reportlab.platypus import SimpleDocTemplate
    
    print("="*60)
    print("Page 5 Generator (Korean) Test")
    print("="*60)
    
    # Mock data
    mock_data = {
        "top_risks": [
            {
                "risk": "Fed 위원 매파 발언",
                "probability": 30,
                "ai_response": "포지션 10% 축소"
            },
            {
                "risk": "Tech 실적 부진",
                "probability": 25,
                "ai_response": "방어 섹터 전환"
            },
            {
                "risk": "10년물 금리 급등",
                "probability": 20,
                "ai_response": "현금 비중 확대"
            },
        ],
        "ai_stance": "NEUTRAL",
        "tomorrow_scenarios": [
            {
                "scenario": "상승 지속 (+0.5~1%)",
                "probability": 40,
                "ai_action": "현 포지션 유지"
            },
            {
                "scenario": "횡보 (±0.3%)",
                "probability": 35,
                "ai_action": "관망"
            },
            {
                "scenario": "조정 (-0.5~1%)",
                "probability": 25,
                "ai_action": "부분 청산 (30%)"
            },
        ],
        "action_items": [
            "Fed 위원 발언 모니터링 (14:00 KST)",
            "Tech 섹터 실적 발표 확인 (장후)",
            "VIX 20선 돌파 여부",
            "10년물 금리 4.5% 수준 주시",
        ]
    }
    
    # Generate
    generator = Page5GeneratorKorean()
    story = generator.generate(mock_data)
    
    # Create PDF
    output_path = "test_page5_korean.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    doc.build(story)
    
    print(f"\n✅ Page 5 generated: {output_path}")
    print(f"📄 Total elements: {len(story)}")
    print("\nPage 5 구성:")
    print("  • Top 3 Risks (확률 + AI 대응)")
    print("  • AI Stance: NEUTRAL 🟡")
    print("  • Tomorrow Scenarios (3가지)")
    print("  • Action Items (4개)")
    
    print("\n" + "="*60)
    print("✅ Test completed! Open the PDF to view.")


if __name__ == "__main__":
    test_page5_korean()
