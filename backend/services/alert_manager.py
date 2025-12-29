"""
Central Alert Management System

Manages all alerts for the AI Trading System.
Routes alerts to appropriate notification channels.
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AlertManager:
    """중앙 알림 관리 시스템"""
    
    def __init__(self):
        """Initialize alert manager"""
        self.last_alert_time = {}  # Rate limiting
        self.min_alert_interval = {
            "CRITICAL": 0,      # Send immediately
            "HIGH": 60,         # 1 minute
            "MEDIUM": 300,      # 5 minutes
            "LOW": 900,         # 15 minutes
        }
        logger.info("✅ AlertManager initialized")
    
    async def send_alert(
        self,
        alert_type: str,
        message: str,
        priority: str = "INFO",
        details: Optional[Dict[str, Any]] = None,
        force: bool = False
    ) -> bool:
        """
        Send alert through configured channels
        
        Args:
            alert_type: Alert type (ORDER_FILLED, CIRCUIT_BREAKER, etc.)
            message: Message content
            priority: CRITICAL, HIGH, MEDIUM, LOW, INFO
            details: Additional details
            force: Bypass rate limiting
        
        Returns:
            Success status
        """
        # Import here to avoid circular dependency
        from backend.services.notifiers.telegram_notifier import telegram_notifier
        
        # Rate limiting check
        if not force and not self._should_send(alert_type, priority):
            logger.debug(f"Alert rate limited: {alert_type}")
            return False
        
        # Format message
        formatted_message = self._format_message(alert_type, message, details)
        
        # Send via Telegram
        success = await telegram_notifier.send_message(
            message=formatted_message,
            priority=priority
        )
        
        if success:
            # Record sent time
            self.last_alert_time[alert_type] = datetime.now()
        
        return success
    
    async def trading_alert(
        self,
        ticker: str,
        action: str,
        quantity: int,
        price: float,
        alert_type: str = "ORDER_FILLED"
    ) -> bool:
        """
        Send trading alert
        
        Args:
            ticker: Stock ticker
            action: BUY or SELL
            quantity: Number of shares
            price: Execution price
            alert_type: Alert type
        """
        from backend.services.notifiers.telegram_notifier import telegram_notifier
        
        return await telegram_notifier.send_trading_alert(
            alert_type=alert_type,
            ticker=ticker,
            action=action,
            details={
                "Quantity": quantity,
                "Price": f"${price:.2f}",
                "Total Value": f"${quantity * price:,.2f}"
            }
        )
    
    async def circuit_breaker_alert(
        self,
        reason: str,
        daily_pnl: float,
        threshold: float
    ) -> bool:
        """
        Send circuit breaker alert
        
        Args:
            reason: Reason for circuit breaker
            daily_pnl: Current daily P&L
            threshold: Loss threshold
        """
        message = f"""🚨 *CIRCUIT BREAKER TRIGGERED*

Reason: {reason}
Daily P&L: ${daily_pnl:,.2f} ({daily_pnl/threshold*100:.1f}%)
Threshold: ${threshold:,.2f}

⛔ All trading stopped.
"""
        
        return await self.send_alert(
            alert_type="CIRCUIT_BREAKER",
            message=message,
            priority="CRITICAL",
            force=True
        )
    
    async def war_room_decision(
        self,
        ticker: str,
        action: str,
        confidence: float,
        num_votes: int
    ) -> bool:
        """
        Send War Room decision alert
        
        Args:
            ticker: Stock ticker
            action: Final decision
            confidence: Confidence level
            num_votes: Number of agent votes
        """
        message = f"""📊 *War Room Decision*

Ticker: `{ticker}`
Action: *{action}*
Confidence: {confidence:.0%}
Agents: {num_votes}/8 voted
"""
        
        return await self.send_alert(
            alert_type="WAR_ROOM_DECISION",
            message=message,
            priority="MEDIUM"
        )
    
    async def daily_summary(
        self,
        total_pnl: float,
        win_rate: float,
        num_trades: int
    ) -> bool:
        """
        Send daily performance summary
        
        Args:
            total_pnl: Total P&L
            win_rate: Win rate percentage
            num_trades: Number of trades
        """
        # Emoji based on P&L
        pnl_emoji = "📈" if total_pnl >= 0 else "📉"
        
        message = f"""{pnl_emoji} *Daily Performance Summary*

Total P&L: ${total_pnl:,.2f}
Win Rate: {win_rate:.1f}%
Trades: {num_trades}

{self._get_performance_comment(total_pnl, win_rate)}
"""
        
        return await self.send_alert(
            alert_type="DAILY_SUMMARY",
            message=message,
            priority="MEDIUM"
        )
    
    async def agent_weight_adjusted(
        self,
        agent_name: str,
        old_weight: float,
        new_weight: float,
        reason: str
    ) -> bool:
        """
        Send agent weight adjustment alert
        
        Args:
            agent_name: Agent name
            old_weight: Previous weight
            new_weight: New weight
            reason: Adjustment reason
        """
        change = new_weight - old_weight
        change_emoji = "📈" if change > 0 else "📉"
        
        message = f"""🎯 *Agent Weight Adjusted*

Agent: {agent_name}
{change_emoji} {old_weight:.0%} → {new_weight:.0%} ({change:+.0%})

Reason: {reason}
"""
        
        return await self.send_alert(
            alert_type="AGENT_WEIGHT_ADJUSTED",
            message=message,
            priority="MEDIUM"
        )
    
    def _should_send(self, alert_type: str, priority: str) -> bool:
        """Check if alert should be sent (rate limiting)"""
        if alert_type not in self.last_alert_time:
            return True
        
        interval = self.min_alert_interval.get(priority, 900)
        if interval == 0:
            return True
        
        elapsed = (datetime.now() - self.last_alert_time[alert_type]).total_seconds()
        return elapsed >= interval
    
    def _format_message(
        self,
        alert_type: str,
        message: str,
        details: Optional[Dict] = None
    ) -> str:
        """Format alert message"""
        lines = [message]
        
        if details:
            lines.append("")
            for key, value in details.items():
                lines.append(f"• {key}: {value}")
        
        return "\n".join(lines)
    
    def _get_performance_comment(self, pnl: float, win_rate: float) -> str:
        """Get performance comment"""
        if pnl > 0 and win_rate >= 70:
            return "🎉 Excellent performance!"
        elif pnl > 0 and win_rate >= 50:
            return "👍 Good job!"
        elif pnl < 0 and win_rate < 40:
            return "⚠️ Review strategy needed"
        else:
            return "📝 Keep monitoring"


# Global instance
alert_manager = AlertManager()
