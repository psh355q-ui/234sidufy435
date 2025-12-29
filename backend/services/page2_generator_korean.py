"""
Page 2 Generator (Korean): AI Decision Logic Transparency

목적: AI가 어떻게 생각했는가 보여주기

섹션:
1. Decision Flow (의사결정 흐름)
2. 실행/거부 트레이드 테이블
3. War Room 토론 요약

실제 데이터 연동 준비:
- War Room DB에서 토론 내용 조회
- Trades DB에서 실행/거부 거래 조회
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


class Page2GeneratorKorean:
    """
    Page 2: AI Decision Logic Transparency (Korean)
    
    실제 데이터 통합 가능한 구조
    """
    
    def __init__(self):
        """Initialize generator"""
        ensure_fonts_registered()
        self.setup_styles()
        logger.info("✅ Page2GeneratorKorean initialized")
    
    def setup_styles(self):
        """스타일 설정"""
        self.title_style = ParagraphStyle(
            'Title',
            fontName=get_korean_font_name(bold=True),
            fontSize=18,
            textColor=colors.HexColor('#3b82f6'),
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
        
        self.flow_style = ParagraphStyle(
            'Flow',
            fontName=get_korean_font_name(),
            fontSize=10,
            leading=18,
            textColor=colors.HexColor('#4b5563'),
            leftIndent=20
        )
    
    def generate(self, data: Dict) -> List:
        """Page 2 생성"""
        story = []
        
        # Title
        story.append(Paragraph(
            "🤖 AI 의사결정 로직 투명성",
            self.title_style
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # 1. Decision Flow
        story.extend(self._create_decision_flow(data.get("decision_flow", {})))
        story.append(Spacer(1, 0.3*inch))
        
        # 2. Executed Trades
        story.extend(self._create_executed_trades(data.get("executed_trades", [])))
        story.append(Spacer(1, 0.3*inch))
        
        # 3. Rejected Trades
        story.extend(self._create_rejected_trades(data.get("rejected_trades", [])))
        story.append(Spacer(1, 0.3*inch))
        
        # 4. War Room Summary
        story.extend(self._create_war_room_summary(data.get("war_room_summary", {})))
        
        return story
    
    def _create_decision_flow(self, flow: Dict) -> List:
        """의사결정 흐름 다이어그램"""
        story = []
        
        story.append(Paragraph("의사결정 흐름", self.heading_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Default flow
        default_flow = {
            "market_data": "지수 상승 +0.8%, VIX -5.2%",
            "agents_initial": "5/8 Agents BUY 제안",
            "war_room_pivot": "Skeptic: 거래량 -18% 경고",
            "final_decision": "6/8 Agents HOLD로 전환"
        }
        
        flow_data = flow if flow else default_flow
        
        # Create flow diagram (text-based)
        flow_text = f"""
<b>1. 시장 데이터 수집</b><br/>
   → {flow_data.get('market_data', 'N/A')}<br/>
<br/>
<b>2. 8 Agents 초기 분석</b><br/>
   → {flow_data.get('agents_initial', 'N/A')}<br/>
<br/>
<b>3. War Room 토론 (전환점)</b><br/>
   → {flow_data.get('war_room_pivot', 'N/A')}<br/>
<br/>
<b>4. 최종 결정</b><br/>
   → {flow_data.get('final_decision', 'N/A')}
"""
        
        story.append(Paragraph(flow_text, self.flow_style))
        
        return story
    
    def _create_executed_trades(self, trades: List[Dict]) -> List:
        """실행된 트레이드 테이블"""
        story = []
        
        story.append(Paragraph("✅ 실행된 트레이드", self.heading_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Default trades
        default_trades = [
            {
                "ticker": "NVDA",
                "action": "BUY",
                "quantity": 10,
                "price": 490.20,
                "reason": "AI 칩 수요 급증, 옵션 Call 우세"
            },
            {
                "ticker": "AAPL",
                "action": "HOLD",
                "quantity": 15,
                "price": 195.50,
                "reason": "안정적 흐름, 추가 신호 대기"
            },
        ]
        
        trades_to_use = trades if trades else default_trades
        
        # Header
        data = [
            ["종목", "행동", "수량", "가격", "이유"]
        ]
        
        # Add trades
        for trade in trades_to_use[:5]:  # Top 5
            data.append([
                trade.get("ticker", ""),
                trade.get("action", ""),
                str(trade.get("quantity", "")),
                f"${trade.get('price', 0):.2f}",
                trade.get("reason", "")
            ])
        
        # Create table
        table = Table(data, colWidths=[0.8*inch, 0.7*inch, 0.7*inch, 0.9*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), get_korean_font_name(bold=True)),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), get_korean_font_name()),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
        
        return story
    
    def _create_rejected_trades(self, trades: List[Dict]) -> List:
        """거부된 트레이드 테이블 (Skeptic이 막은 것)"""
        story = []
        
        story.append(Paragraph("🛑 Skeptic이 거부한 트레이드", self.heading_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Default rejections
        default_trades = [
            {
                "ticker": "TSLA",
                "proposed": "BUY",
                "veto_reason": "밸류에이션 과도, 변동성 높음",
                "avoided_loss": 520.0
            },
            {
                "ticker": "META",
                "proposed": "BUY",
                "veto_reason": "Tech 섹터 집중도 30% 초과",
                "avoided_loss": 0.0
            },
        ]
        
        trades_to_use = trades if trades else default_trades
        
        if not trades_to_use:
            story.append(Paragraph("오늘 거부된 트레이드가 없습니다.", self.body_style))
            return story
        
        # Header
        data = [
            ["종목", "제안", "거부 이유", "회피 손실 (추정)"]
        ]
        
        # Add trades
        for trade in trades_to_use[:3]:  # Top 3
            avoided = trade.get("avoided_loss", 0)
            avoided_str = f"${avoided:.2f}" if avoided > 0 else "-"
            
            data.append([
                trade.get("ticker", ""),
                trade.get("proposed", ""),
                trade.get("veto_reason", ""),
                avoided_str
            ])
        
        # Create table
        table = Table(data, colWidths=[0.8*inch, 0.7*inch, 2.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), get_korean_font_name(bold=True)),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), get_korean_font_name()),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
        
        return story
    
    def _create_war_room_summary(self, summary: Dict) -> List:
        """War Room 토론 요약 (전환점만)"""
        story = []
        
        story.append(Paragraph("💬 War Room 토론 요약", self.heading_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Default summary
        default_summary = {
            "initial": "5/8 Agents는 NVDA BUY를 제안했습니다.",
            "pivot": "Skeptic이 거래량 -18% 감소를 지적하며 신중론 제기",
            "final": "최종적으로 6/8 Agents가 HOLD로 입장을 변경했습니다."
        }
        
        summary_data = summary if summary else default_summary
        
        summary_text = f"""
<b>초기 입장:</b><br/>
{summary_data.get('initial', 'N/A')}<br/>
<br/>
<b>전환점:</b><br/>
{summary_data.get('pivot', 'N/A')}<br/>
<br/>
<b>최종 결정:</b><br/>
{summary_data.get('final', 'N/A')}
"""
        
        story.append(Paragraph(summary_text, self.body_style))
        
        return story


# Test function
def test_page2_korean():
    """Page 2 테스트"""
    from reportlab.platypus import SimpleDocTemplate
    
    print("="*60)
    print("Page 2 Generator (Korean) Test")
    print("="*60)
    
    # Mock data
    mock_data = {
        "decision_flow": {
            "market_data": "지수 상승 +0.8%, VIX -5.2%",
            "agents_initial": "5/8 Agents BUY 제안",
            "war_room_pivot": "Skeptic: 거래량 -18% 경고",
            "final_decision": "6/8 Agents HOLD로 전환"
        },
        "executed_trades": [
            {
                "ticker": "NVDA",
                "action": "BUY",
                "quantity": 10,
                "price": 490.20,
                "reason": "AI 칩 수요 급증, 옵션 Call 우세"
            },
            {
                "ticker": "AAPL",
                "action": "HOLD",
                "quantity": 15,
                "price": 195.50,
                "reason": "안정적 흐름, 추가 신호 대기"
            },
        ],
        "rejected_trades": [
            {
                "ticker": "TSLA",
                "proposed": "BUY",
                "veto_reason": "밸류에이션 과도, 변동성 높음",
                "avoided_loss": 520.0
            },
            {
                "ticker": "META",
                "proposed": "BUY",
                "veto_reason": "Tech 섹터 집중도 30% 초과",
                "avoided_loss": 0.0
            },
        ],
        "war_room_summary": {
            "initial": "5/8 Agents는 NVDA BUY를 제안했습니다.",
            "pivot": "Skeptic이 거래량 -18% 감소를 지적하며 신중론 제기",
            "final": "최종적으로 6/8 Agents가 HOLD로 입장을 변경했습니다."
        }
    }
    
    # Generate
    generator = Page2GeneratorKorean()
    story = generator.generate(mock_data)
    
    # Create PDF
    output_path = "test_page2_korean.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    doc.build(story)
    
    print(f"\n✅ Page 2 generated: {output_path}")
    print(f"📄 Total elements: {len(story)}")
    print("\nPage 2 구성:")
    print("  • Decision Flow (4단계)")
    print("  • 실행된 트레이드 (2건)")
    print("  • 거부된 트레이드 (2건)")
    print("  • War Room 요약")
    
    print("\n" + "="*60)
    print("✅ Test completed! Open the PDF to view.")


if __name__ == "__main__":
    test_page2_korean()
