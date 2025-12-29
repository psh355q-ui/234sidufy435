"""
Telegram Notification Service

Simple Telegram bot for real-time trading alerts.
"""
import logging
import os
import aiohttp
from typing import Optional

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Telegram 알림 전송 서비스"""
    
    def __init__(self):
        """Initialize Telegram notifier"""
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.bot_token or not self.chat_id:
            logger.warning("⚠️  Telegram BOT_TOKEN or CHAT_ID not configured")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"✅ Telegram notifier initialized (chat_id: {self.chat_id})")
    
    async def send_message(
        self,
        message: str,
        priority: str = "INFO",
        parse_mode: str = "Markdown"
    ) -> bool:
        """
        Send Telegram message
        
        Args:
            message: Message content
            priority: CRITICAL, HIGH, MEDIUM, LOW, INFO
            parse_mode: Markdown or HTML
        
        Returns:
            Success status
        """
        if not self.enabled:
            logger.debug(f"Telegram disabled, skipping message: {message[:50]}...")
            return False
        
        # Add priority emoji
        emoji_map = {
            "CRITICAL": "🚨",
            "HIGH": "⚠️",
            "MEDIUM": "📊",
            "LOW": "ℹ️",
            "INFO": "💬"
        }
        emoji = emoji_map.get(priority.upper(), "💬")
        formatted_message = f"{emoji} *{priority}*\n\n{message}"
        
        # Call Telegram API
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": formatted_message,
            "parse_mode": parse_mode
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        logger.info(f"[Telegram] ✅ Message sent: {priority}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"[Telegram] ❌ Failed: {error_text}")
                        return False
        except asyncio.TimeoutError:
            logger.error("[Telegram] ❌ Timeout")
            return False
        except Exception as e:
            logger.error(f"[Telegram] ❌ Error: {e}")
            return False
    
    async def send_trading_alert(
        self,
        alert_type: str,
        ticker: str,
        action: str,
        details: dict
    ) -> bool:
        """
        Send trading alert
        
        Args:
            alert_type: Alert type (ORDER_FILLED, CIRCUIT_BREAKER, etc.)
            ticker: Stock ticker
            action: BUY, SELL, HOLD
            details: Additional details dict
        """
        message = f"""*Trading Alert: {alert_type}*

📈 Ticker: `{ticker}`
🎯 Action: *{action}*

{self._format_details(details)}
"""
        
        priority = self._get_priority(alert_type)
        return await self.send_message(message.strip(), priority=priority)
    
    async def send_system_alert(
        self,
        alert_type: str,
        message: str,
        details: Optional[dict] = None
    ) -> bool:
        """
        Send system alert
        
        Args:
            alert_type: Alert type
            message: Alert message
            details: Optional details dict
        """
        full_message = f"""*System Alert: {alert_type}*

{message}

{self._format_details(details) if details else ''}
"""
        
        priority = self._get_priority(alert_type)
        return await self.send_message(full_message.strip(), priority=priority)
    
    def _format_details(self, details: dict) -> str:
        """Format details dictionary"""
        if not details:
            return ""
        
        lines = []
        for key, value in details.items():
            # Format numbers
            if isinstance(value, float):
                if abs(value) >= 1:
                    value = f"{value:,.2f}"
                else:
                    value = f"{value:.4f}"
            lines.append(f"• {key}: {value}")
        
        return "\n".join(lines)
    
    def _get_priority(self, alert_type: str) -> str:
        """Extract priority from alert type"""
        alert_type_upper = alert_type.upper()
        
        if any(x in alert_type_upper for x in ["CIRCUIT_BREAKER", "STOP_LOSS", "ERROR", "FAILED", "CRITICAL"]):
            return "CRITICAL"
        elif any(x in alert_type_upper for x in ["ORDER", "FILL", "FILLED", "THRESHOLD", "EXCEEDED"]):
            return "HIGH"
        elif any(x in alert_type_upper for x in ["SUMMARY", "WEIGHT", "DECISION", "ADJUSTED"]):
            return "MEDIUM"
        else:
            return "LOW"


# Import asyncio
import asyncio

# Global instance
telegram_notifier = TelegramNotifier()
