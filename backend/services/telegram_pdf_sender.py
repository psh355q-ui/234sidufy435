"""
Telegram PDF Sender - PDF 파일 전송

완전 무료:
- Telegram Bot API (무료)
- aiohttp (무료)
"""
import os
import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TelegramPDFSender:
    """Telegram PDF 전송 서비스"""
    
    def __init__(self):
        """Initialize Telegram PDF sender"""
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.bot_token or not self.chat_id:
            logger.warning("⚠️  Telegram BOT_TOKEN or CHAT_ID not configured")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"✅ Telegram PDF sender initialized")
    
    async def send_pdf(
        self,
        pdf_bytes: bytes,
        filename: str,
        caption: str = ""
    ) -> bool:
        """
        Send PDF file via Telegram
        
        Args:
            pdf_bytes: PDF file content as bytes
            filename: File name (e.g., "report.pdf")
            caption: Message caption
        
        Returns:
            Success status
        """
        if not self.enabled:
            logger.warning("Telegram is not enabled")
            return False
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
        
        try:
            async with aiohttp.ClientSession() as session:
                # Create form data
                form = aiohttp.FormData()
                form.add_field('chat_id', self.chat_id)
                form.add_field('caption', caption)
                form.add_field(
                    'document',
                    pdf_bytes,
                    filename=filename,
                    content_type='application/pdf'
                )
                
                # Send request
                async with session.post(url, data=form, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        logger.info(f"[Telegram] ✅ PDF sent successfully: {filename}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"[Telegram] ❌ Failed to send PDF: {error_text}")
                        return False
                        
        except asyncio.TimeoutError:
            logger.error("[Telegram] ❌ Timeout while sending PDF")
            return False
        except Exception as e:
            logger.error(f"[Telegram] ❌ Error sending PDF: {e}")
            return False


# Import asyncio
import asyncio

# Global instance
telegram_pdf_sender = TelegramPDFSender()
