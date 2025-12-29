"""
Sample Professional Trading Report Generator

완전 무료 라이브러리:
- ReportLab (PDF 생성)
- matplotlib (차트)
- pandas/numpy (데이터 처리)
"""
import os
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class SampleReportGenerator:
    """샘플 리포트 생성기 (완전 무료)"""
    
    def __init__(self):
        self.colors = {
            "primary": "#667eea",
            "success": "#10b981",
            "danger": "#ef4444",
            "warning": "#f59e0b",
            "gray": "#6b7280"
        }
        self.setup_styles()
    
    def setup_styles(self):
        """스타일 설정"""
        styles = getSampleStyleSheet()
        
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor(self.colors["primary"]),
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        )
        
        # Heading style
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor(self.colors["gray"]),
            spaceBefore=15,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        # Body style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor(self.colors["gray"])
        )
    
    def generate_sample_report(self, output_path: str = None):
        """샘플 일일 거래 결산 리포트 생성"""
        
        if output_path is None:
            output_path = "sample_daily_report.pdf"
        
        # Create output directory
        Path(output_path).parent.mkdir(exist_ok=True, parents=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Page 1: Cover & Executive Summary
        story.extend(self._create_cover_page())
        story.append(PageBreak())
        
        # Page 2: Trading Details
        story.extend(self._create_trading_details())
        story.append(PageBreak())
        
        # Page 3: Performance Charts
        story.extend(self._create_charts_page())
        story.append(PageBreak())
        
        # Page 4: AI Analysis
        story.extend(self._create_ai_analysis())
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer,
                 onLaterPages=self._add_header_footer)
        
        print(f"✅ Sample report generated: {output_path}")
        print(f"📄 File size: {os.path.getsize(output_path) / 1024:.2f} KB")
        
        return output_path
    
    def _create_cover_page(self):
        """커버 페이지"""
        story = []
        
        # Title
        title = Paragraph("AI TRADING SYSTEM", self.title_style)
        story.append(title)
        
        subtitle = Paragraph("Daily Trading Summary Report", self.title_style)
        story.append(subtitle)
        story.append(Spacer(1, 0.5*inch))
        
        # Date box
        date_text = f"<b>Report Date:</b> {datetime.now().strftime('%Y-%m-%d')}"
        date_para = Paragraph(date_text, self.body_style)
        story.append(date_para)
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        summary_data = [
            ["Metric", "Value"],
            ["Total Trades", "8 (5 Buy, 3 Sell)"],
            ["Total P&L", "$2,450.75 (+2.45%)"],
            ["Win Rate", "75% (6 wins, 2 losses)"],
            ["Average Profit", "$306.34/trade"],
            ["Best Trade", "NVDA +$850 (+4.2%)"],
            ["Worst Trade", "TSLA -$120 (-0.8%)"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.colors["primary"])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        story.append(summary_table)
        
        return story
    
    def _create_trading_details(self):
        """거래 상세"""
        story = []
        
        story.append(Paragraph("Trading Details", self.heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Trading table
        trade_data = [
            ["Time", "Ticker", "Action", "Qty", "Price", "P&L"],
            ["10:05", "AAPL", "BUY", "10", "$195.50", "+$245.00"],
            ["11:30", "NVDA", "BUY", "5", "$485.20", "+$850.00"],
            ["12:15", "MSFT", "BUY", "8", "$380.15", "+$320.50"],
            ["13:30", "GOOGL", "BUY", "3", "$142.80", "+$180.25"],
            ["14:45", "TSLA", "SELL", "3", "$245.80", "-$120.00"],
            ["15:15", "AAPL", "SELL", "5", "$196.20", "+$350.00"],
            ["15:45", "AMD", "BUY", "12", "$125.30", "+$420.00"],
            ["16:00", "INTC", "SELL", "8", "$42.15", "-$95.00"],
        ]
        
        trade_table = Table(trade_data, colWidths=[0.8*inch, 0.8*inch, 0.8*inch, 
                                                   0.8*inch, 1*inch, 1.2*inch])
        trade_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.colors["primary"])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(trade_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Performance metrics
        story.append(Paragraph("Performance Metrics", self.heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        metrics_data = [
            ["Total P&L", "Win Rate", "Sharpe Ratio"],
            ["$2,450.75", "75.0%", "1.85"],
            ["(+2.45%)", "(6/8 trades)", "(30-day)"],
            ["", "", ""],
            ["Avg Win", "Avg Loss", "Max Drawdown"],
            ["$553.92", "-$107.50", "-$380.00"],
            ["(6 trades)", "(2 trades)", "(-0.38%)"],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.colors["success"])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 14),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica'),
            ('FONTSIZE', (0, 2), (-1, 2), 9),
            ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor(self.colors["warning"])),
            ('TEXTCOLOR', (0, 4), (-1, 4), colors.white),
            ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 4), (-1, 4), 12),
            ('FONTNAME', (0, 5), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 5), (-1, -1), 14),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(metrics_table)
        
        return story
    
    def _create_charts_page(self):
        """차트 페이지"""
        story = []
        
        story.append(Paragraph("Performance Charts", self.heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Chart 1: Intraday P&L
        story.append(Paragraph("Intraday P&L Progression", self.body_style))
        story.append(Spacer(1, 0.1*inch))
        
        fig1 = self._create_pnl_chart()
        img1 = self._fig_to_reportlab_image(fig1, width=6*inch, height=3*inch)
        story.append(img1)
        story.append(Spacer(1, 0.3*inch))
        
        # Chart 2: Position Returns
        story.append(Paragraph("Position Returns", self.body_style))
        story.append(Spacer(1, 0.1*inch))
        
        fig2 = self._create_position_chart()
        img2 = self._fig_to_reportlab_image(fig2, width=6*inch, height=3*inch)
        story.append(img2)
        
        return story
    
    def _create_ai_analysis(self):
        """AI 분석"""
        story = []
        
        story.append(Paragraph("AI War Room Analysis", self.heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        # War Room decisions
        decisions_data = [
            ["Time", "Ticker", "AI Decision", "Confidence", "Executed"],
            ["10:00", "AAPL", "BUY", "85%", "Yes"],
            ["11:25", "NVDA", "BUY", "92%", "Yes"],
            ["12:10", "MSFT", "BUY", "78%", "Yes"],
            ["13:25", "GOOGL", "BUY", "82%", "Yes"],
            ["14:40", "TSLA", "HOLD", "65%", "No"],
            ["15:10", "AAPL", "SELL", "88%", "Yes"],
        ]
        
        decisions_table = Table(decisions_data, colWidths=[1*inch, 1*inch, 1.2*inch, 
                                                          1.2*inch, 1*inch])
        decisions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.colors["primary"])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(decisions_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Agent performance
        story.append(Paragraph("Agent Performance", self.body_style))
        story.append(Spacer(1, 0.1*inch))
        
        agent_data = [
            ["Agent", "Votes", "Accuracy", "Weight"],
            ["Trader Agent", "12", "83%", "15%"],
            ["News Agent", "12", "92%", "14%"],
            ["Risk Agent", "12", "75%", "15%"],
            ["Macro Agent", "12", "67%", "14%"],
            ["Analyst Agent", "12", "82%", "12%"],
        ]
        
        agent_table = Table(agent_data, colWidths=[1.5*inch, 1*inch, 1.2*inch, 1*inch])
        agent_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.colors["success"])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(agent_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Tomorrow outlook
        story.append(Paragraph("Tomorrow's Outlook", self.heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        outlook_text = """
        <b>Maintain Positions:</b><br/>
        • NVDA: Strong momentum (92% confidence)<br/>
        • AAPL: Stable growth (85% confidence)<br/>
        <br/>
        <b>Watch Closely:</b><br/>
        • TSLA: Increasing volatility (consider partial exit)<br/>
        <br/>
        <b>Monitor:</b><br/>
        • GOOGL: Awaiting AI catalyst<br/>
        • AMD: Semiconductor sector trend<br/>
        """
        
        story.append(Paragraph(outlook_text, self.body_style))
        
        return story
    
    def _create_pnl_chart(self):
        """일중 P&L 차트"""
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Sample data
        times = pd.date_range('09:30', periods=8, freq='H').time
        pnl_cumulative = [0, 245, 1095, 1415, 1595, 1475, 1825, 2450]
        
        ax.plot(range(len(times)), pnl_cumulative, 
               marker='o', linewidth=2, color='#667eea', markersize=8)
        ax.fill_between(range(len(times)), pnl_cumulative, 
                        alpha=0.3, color='#667eea')
        
        ax.set_title('Intraday P&L Progression', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time')
        ax.set_ylabel('Cumulative P&L ($)')
        ax.set_xticks(range(len(times)))
        ax.set_xticklabels([t.strftime('%H:%M') for t in times], rotation=45)
        ax.grid(True, alpha=0.3)
        ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
        
        plt.tight_layout()
        return fig
    
    def _create_position_chart(self):
        """포지션 수익률 차트"""
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Sample data
        tickers = ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMD', 'TSLA', 'INTC']
        returns = [4.2, 1.8, 1.2, 0.9, 0.5, -0.8, -1.2]
        colors_list = ['green' if r > 0 else 'red' for r in returns]
        
        bars = ax.barh(tickers, returns, color=colors_list, alpha=0.7)
        
        # Add value labels
        for i, (ticker, ret) in enumerate(zip(tickers, returns)):
            ax.text(ret, i, f' {ret:+.1f}%', va='center', fontsize=10)
        
        ax.set_title('Position Returns', fontsize=14, fontweight='bold')
        ax.set_xlabel('Return (%)')
        ax.axvline(0, color='black', linewidth=0.8)
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        return fig
    
    def _fig_to_reportlab_image(self, fig, width=6*inch, height=3*inch):
        """Matplotlib figure를 ReportLab Image로 변환"""
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return Image(buf, width=width, height=height)
    
    def _add_header_footer(self, canvas, doc):
        """헤더/푸터 추가"""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 9)
        canvas.setFillColor(colors.HexColor(self.colors["gray"]))
        canvas.drawString(
            0.75*inch, 
            doc.height + 1.2*inch, 
            "AI Trading System - Confidential"
        )
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(
            doc.width + 0.75*inch,
            0.5*inch,
            f"Page {doc.page} - Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        canvas.restoreState()


def main():
    """메인 실행"""
    print("="*60)
    print("Sample Trading Report Generator (100% Free)")
    print("="*60)
    print("\nUsing Free Libraries:")
    print("✓ ReportLab (Free/Open Source)")
    print("✓ matplotlib (Free)")
    print("✓ pandas/numpy (Free)")
    print("\nGenerating report...\n")
    
    generator = SampleReportGenerator()
    output_path = generator.generate_sample_report()
    
    print(f"\n{'='*60}")
    print("✅ Complete!")
    print(f"{'='*60}")
    print(f"\nReport location: {os.path.abspath(output_path)}")
    print("\nOpen this file with a PDF viewer!")


if __name__ == "__main__":
    main()
