"""
Test: Send sample PDF report via Telegram
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Import our sample generator
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.sample_report_generator import SampleReportGenerator
from services.telegram_pdf_sender import TelegramPDFSender


async def test_pdf_telegram():
    """샘플 PDF 생성 및 Telegram 전송 테스트"""
    
    print("="*60)
    print("PDF Report + Telegram Test")
    print("="*60)
    
    # Load environment variables
    load_dotenv()
    
    # Step 1: Generate sample PDF
    print("\n[Step 1/3] Generating sample PDF report...")
    generator = SampleReportGenerator()
    pdf_path = generator.generate_sample_report("sample_daily_report.pdf")
    
    # Step 2: Read PDF bytes
    print("\n[Step 2/3] Reading PDF bytes...")
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    print(f"✅ PDF loaded: {len(pdf_bytes)} bytes")
    
    # Step 3: Send via Telegram
    print("\n[Step 3/3] Sending to Telegram...")
    sender = TelegramPDFSender()
    
    caption = f"""📊 Sample Daily Trading Report

Date: 2025-12-29
Total P&L: $2,450.75 (+2.45%)
Win Rate: 75% (6/8 trades)

This is a sample report generated with 100% free tools:
✓ ReportLab (PDF)
✓ matplotlib (Charts)
✓ Telegram Bot API (Free)

Check the attached PDF!"""
    
    success = await sender.send_pdf(
        pdf_bytes=pdf_bytes,
        filename="sample_daily_report.pdf",
        caption=caption
    )
    
    if success:
        print("\n" + "="*60)
        print("✅ SUCCESS!")
        print("="*60)
        print("\n✓ PDF generated")
        print("✓ PDF sent to Telegram")
        print("\nCheck your Telegram to see the report!")
    else:
        print("\n❌ Failed to send PDF")
    
    return success


if __name__ == "__main__":
    asyncio.run(test_pdf_telegram())
