"""
Test: Send complete AI report via Telegram
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Import generators
from backend.services.complete_report_generator import CompleteReportGenerator
from backend.services.telegram_pdf_sender import TelegramPDFSender


async def test_complete_report_telegram():
    """완전한 리포트 생성 및 Telegram 전송"""
    
    print("="*60)
    print("Complete AI Report + Telegram Test")
    print("="*60)
    
    # Load environment variables
    load_dotenv()
    
    # Step 1: Generate complete report
    print("\n[Step 1/3] Generating complete AI report...")
    generator = CompleteReportGenerator()
    pdf_path = generator.generate_complete_report("complete_ai_report.pdf")
    print(f"✅ Report generated: {pdf_path}")
    
    # Step 2: Read PDF bytes
    print("\n[Step 2/3] Reading PDF bytes...")
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    file_size_kb = len(pdf_bytes) / 1024
    print(f"✅ PDF loaded: {file_size_kb:.2f} KB")
    
    # Step 3: Send via Telegram
    print("\n[Step 3/3] Sending to Telegram...")
    sender = TelegramPDFSender()
    
    caption = f"""📊 AI Trading System - Daily Report

Date: {generator._get_mock_data()['page1']['date'].strftime('%Y-%m-%d')}

✅ Pages Included:
• Page 1: Executive Market Narrative
• Page 3: Skeptic & Contradiction Analysis

📈 Key Insights:
• Market Summary: Strong but with internal risks
• Skeptic Accuracy: 67% (3 vetoes)
• Avoided Loss: $3,250.75

🔍 This report shows:
→ What AI is thinking
→ Where AI might be wrong
→ How AI avoids losses

Open the PDF for detailed analysis!"""
    
    success = await sender.send_pdf(
        pdf_bytes=pdf_bytes,
        filename="ai_daily_report.pdf",
        caption=caption
    )
    
    if success:
        print("\n" + "="*60)
        print("✅ SUCCESS!")
        print("="*60)
        print("\n✓ Complete AI report generated")
        print("✓ PDF sent to Telegram")
        print(f"✓ File size: {file_size_kb:.2f} KB")
        print("\nCheck your Telegram to see the complete report!")
    else:
        print("\n❌ Failed to send PDF")
    
    return success


if __name__ == "__main__":
    asyncio.run(test_complete_report_telegram())
