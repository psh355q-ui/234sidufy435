"""
Annual Report Generator

연간 AI Accountability 리포트 생성

구성:
- Annual NIA Summary (by type)
- Top 3 Failures with Lessons
- System Improvements Timeline
- Overall AI Evolution
"""

import logging
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors

from backend.database.repository import get_sync_session
from backend.ai.skills.reporting.report_orchestrator_agent.report_orchestrator import ReportOrchestrator
from backend.ai.skills.reporting.failure_learning_agent.failure_analyzer import FailureAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnnualReportGenerator:
    """연간 AI Accountability 리포트 생성기"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        logger.info("✅ AnnualReportGenerator initialized")

    def generate_report(self, output_path: str = None) -> str:
        """
        연간 리포트 생성

        Args:
            output_path: PDF 출력 경로 (기본: annual_report_YYYY.pdf)

        Returns:
            str: 생성된 파일 경로
        """
        year = datetime.now().year

        if not output_path:
            output_path = f"annual_report_{year}.pdf"

        logger.info(f"📊 Generating Annual Report {year}: {output_path}")

        # Collect data
        with get_sync_session() as session:
            orchestrator = ReportOrchestrator(session)
            analyzer = FailureAnalyzer(session)

            # Get annual accountability report
            annual_data = orchestrator.generate_annual_accountability_report()

            # Get system improvements
            improvements = analyzer.suggest_system_improvements()

        # Create PDF
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            spaceAfter=30
        )
        story.append(Paragraph(f"{year} AI Accountability Report", title_style))
        story.append(Paragraph("AI Trading System - Annual Review", self.styles['Normal']))
        story.append(Spacer(1, 0.5*inch))

        # Section 1: Overall NIA
        story.append(Paragraph("1. Overall Performance", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        overall_data = [
            ["Metric", "Score"],
            ["Overall NIA", f"{annual_data['nia_overall']}%"]
        ]

        overall_table = Table(overall_data, colWidths=[3*inch, 3*inch])
        overall_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(overall_table)
        story.append(Spacer(1, 0.5*inch))

        # Section 2: NIA by Type
        story.append(Paragraph("2. Performance by News Type", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        type_data = [["News Type", "NIA"]]
        for news_type, nia in annual_data['by_type'].items():
            type_data.append([news_type, f"{nia}%"])

        type_table = Table(type_data, colWidths=[3*inch, 3*inch])
        type_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(type_table)
        story.append(Spacer(1, 0.5*inch))

        # Section 3: Top 3 Failures
        story.append(Paragraph("3. Top Learning Opportunities", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        for i, failure in enumerate(annual_data['top_3_failures'], 1):
            story.append(Paragraph(f"<b>#{i}: {failure['description']}</b>", self.styles['Normal']))
            story.append(Paragraph(f"<i>Lesson:</i> {failure['lesson']}", self.styles['Normal']))
            story.append(Paragraph(f"<i>Fix:</i> {failure['fix']}", self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))

        story.append(PageBreak())

        # Section 4: System Improvements
        story.append(Paragraph("4. System Improvements", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        # Completed improvements
        story.append(Paragraph("<b>✅ Completed Improvements:</b>", self.styles['Heading3']))
        story.append(Spacer(1, 0.1*inch))

        for improvement in improvements['completed_improvements']:
            story.append(Paragraph(
                f"• [{improvement['date']}] {improvement['improvement']}",
                self.styles['Normal']
            ))

        story.append(Spacer(1, 0.3*inch))

        # Pending improvements
        story.append(Paragraph("<b>⏳ Pending Improvements:</b>", self.styles['Heading3']))
        story.append(Spacer(1, 0.1*inch))

        for improvement in improvements['pending_improvements']:
            story.append(Paragraph(
                f"• [Priority: {improvement['priority']}] {improvement['improvement']}",
                self.styles['Normal']
            ))
            story.append(Paragraph(
                f"  Justification: {improvement['justification']}",
                self.styles['Normal']
            ))

        story.append(Spacer(1, 0.3*inch))

        # Rejected improvements
        if improvements['rejected_improvements']:
            story.append(Paragraph("<b>❌ Rejected Improvements:</b>", self.styles['Heading3']))
            story.append(Spacer(1, 0.1*inch))

            for improvement in improvements['rejected_improvements']:
                story.append(Paragraph(
                    f"• {improvement['improvement']}",
                    self.styles['Normal']
                ))
                story.append(Paragraph(
                    f"  Reason: {improvement['reason']}",
                    self.styles['Normal']
                ))

        # Build PDF
        doc.build(story)

        logger.info(f"✅ Annual Report generated: {output_path}")
        return output_path


# ========== Standalone Usage ==========

if __name__ == "__main__":
    generator = AnnualReportGenerator()
    report_path = generator.generate_report()

    print("="*60)
    print(f"✅ Annual Report generated: {report_path}")
    print("="*60)
