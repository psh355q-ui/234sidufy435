"""
Weekly Report Generator

주간 AI Accountability 리포트 생성

구성:
- Weekly NIA Summary
- AI 판단 진화 로그 (Best/Worst judgments)
- Lesson Learned
- 주간 실패 패턴 분석
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from backend.database.repository import get_sync_session
from backend.ai.skills.reporting.report_orchestrator_agent.report_orchestrator import ReportOrchestrator
from backend.ai.skills.reporting.failure_learning_agent.failure_analyzer import FailureAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeeklyReportGenerator:
    """주간 AI Accountability 리포트 생성기"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        logger.info("✅ WeeklyReportGenerator initialized")

    def generate_report(self, output_path: str = None) -> str:
        """
        주간 리포트 생성

        Args:
            output_path: PDF 출력 경로 (기본: weekly_report_YYYYMMDD.pdf)

        Returns:
            str: 생성된 파일 경로
        """
        if not output_path:
            output_path = f"weekly_report_{datetime.now().strftime('%Y%m%d')}.pdf"

        logger.info(f"📊 Generating Weekly Report: {output_path}")

        # Collect data
        with get_sync_session() as session:
            orchestrator = ReportOrchestrator(session)
            analyzer = FailureAnalyzer(session)

            # Get weekly accountability section
            weekly_data = orchestrator.generate_weekly_accountability_section()

            # Get recurring failure patterns
            patterns = analyzer.get_top_recurring_failures(limit=5)

        # Create PDF
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        story.append(Paragraph("Weekly AI Accountability Report", title_style))
        story.append(Paragraph(f"Week of {datetime.now().strftime('%Y-%m-%d')}", self.styles['Normal']))
        story.append(Spacer(1, 0.5*inch))

        # Section 1: NIA Summary
        story.append(Paragraph("1. News Interpretation Accuracy (NIA) Summary", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        nia_data = [
            ["Metric", "Value"],
            ["NIA Score", f"{weekly_data['nia_score']}%"],
            ["Improvement vs Last Week", weekly_data['improvement']]
        ]

        nia_table = Table(nia_data, colWidths=[3*inch, 3*inch])
        nia_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(nia_table)
        story.append(Spacer(1, 0.5*inch))

        # Section 2: Best/Worst Judgments
        story.append(Paragraph("2. AI Judgment Highlights", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        if weekly_data.get('best_judgment'):
            story.append(Paragraph(f"<b>✅ Best Judgment:</b>", self.styles['Normal']))
            story.append(Paragraph(weekly_data['best_judgment'], self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))

        if weekly_data.get('worst_judgment'):
            story.append(Paragraph(f"<b>❌ Worst Judgment:</b>", self.styles['Normal']))
            story.append(Paragraph(weekly_data['worst_judgment'], self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))

        story.append(Paragraph(f"<b>📚 Lesson Learned:</b>", self.styles['Normal']))
        story.append(Paragraph(weekly_data['lesson_learned'], self.styles['Normal']))
        story.append(Spacer(1, 0.5*inch))

        # Section 3: Recurring Failure Patterns
        if patterns:
            story.append(Paragraph("3. Recurring Failure Patterns", self.styles['Heading2']))
            story.append(Spacer(1, 0.2*inch))

            for i, pattern in enumerate(patterns, 1):
                story.append(Paragraph(
                    f"<b>Pattern {i}:</b> {pattern['type']} (count: {pattern['count']})",
                    self.styles['Normal']
                ))
                story.append(Paragraph(
                    f"Description: {pattern['pattern'][:200]}...",
                    self.styles['Normal']
                ))
                story.append(Spacer(1, 0.1*inch))

        # Build PDF
        doc.build(story)

        logger.info(f"✅ Weekly Report generated: {output_path}")
        return output_path


# ========== Standalone Usage ==========

if __name__ == "__main__":
    generator = WeeklyReportGenerator()
    report_path = generator.generate_report()

    print("="*60)
    print(f"✅ Weekly Report generated: {report_path}")
    print("="*60)
