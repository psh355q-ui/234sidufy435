"""
Safety Guard - Real Trading Safety Enforcement

Phase 7: Real Trading Implementation
Date: 2026-01-10

Purpose:
    실거래(Real Trading) 시 자금 보호를 위한 최후의 안전장치.
    OrderValidator나 KillSwitch보다 더 엄격하고 즉각적인 제약을 적용합니다.
    특히 소형주(Small Cap) 거래 시 유동성 부족이나 슬리피지를 방지합니다.

Features:
    1. Max Order Limit: 1회 주문 최대 금액 제한 (예: 100만원)
    2. Daily Loss Limit: 일일 손실 한도 도달 시 즉시 차단
    3. Liquidity Check: 호가 공백/거래량 부족 시 주문 거부
    4. Spread Check: 호가 스프레드가 너무 크면 거부

Usage:
    guard = SafetyGuard()
    is_safe, reason = guard.check_order(symbol, price, quantity, portfolio_state)
"""

import logging
from typing import Dict, Tuple, Optional
from datetime import datetime
from backend.execution.kill_switch import get_kill_switch, TriggerType

logger = logging.getLogger(__name__)

class SafetyGuard:
    """실거래 안전장치 (Safety Guard)"""
    
    def __init__(self):
        # === Safety Configuration ===
        self.MAX_ORDER_AMOUNT_KRW = 1000000  # 1회 최대 주문금액 (100만원)
        self.MAX_DAILY_LOSS_PCT = 3.0       # 일일 손실 한도 (3%) - KillSwitch(5%)보다 보수적
        
        # Liquidity Config
        self.MIN_5MIN_VOLUME = 1000         # 최소 5분 거래량
        self.MAX_SPREAD_PCT = 2.0           # 최대 허용 스프레드 (2%)
        
        self.kill_switch = get_kill_switch()
        
    def check_order(
        self, 
        symbol: str, 
        price: float, 
        quantity: int, 
        portfolio_state: Dict,
        market_data: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """
        주문 안전성 검사
        
        Args:
            symbol: 종목코드
            price: 주문가격
            quantity: 주문수량
            portfolio_state: 포트폴리오 상태 (balance, daily_pnl 등)
            market_data: 시장 데이터 (volume, ask/bid 등) - Optional
            
        Returns:
            (is_safe, reason)
        """
        # 1. Kill Switch Global Check
        if not self.kill_switch.can_trade():
            return False, f"Kill Switch is ACTIVE ({self.kill_switch.trigger_reason})"

        # 2. Check Daily Loss Limit (Stricter than KillSwitch)
        current_loss_pct = self._calculate_daily_loss_pct(portfolio_state)
        if current_loss_pct >= self.MAX_DAILY_LOSS_PCT:
            # Trigger Kill Switch specifically for this
            self.kill_switch.trigger(
                TriggerType.DAILY_LOSS, 
                {"current_loss": current_loss_pct, "limit": self.MAX_DAILY_LOSS_PCT}
            )
            return False, f"Daily loss {current_loss_pct:.2f}% exceeds safety limit {self.MAX_DAILY_LOSS_PCT}%"

        # 3. Max Order Amount Check
        order_amount = price * quantity
        # USD -> KRW approximate conversion if needed, assuming price is in ensuring currency matches limits
        # For now assuming config matches currency or handling conversion outside. 
        # Let's assume input limits are in the same currency as price (USD for US stocks).
        # $1000 approx 1.4M KRW. Let's set limit to $1000 for US stocks.
        MAX_ORDER_USD = 1000.0 
        
        if order_amount > MAX_ORDER_USD:
            return False, f"Order amount ${order_amount:,.2f} exceeds limit ${MAX_ORDER_USD:,.2f}"

        # 4. Liquidity & Spread Check (if market data provided)
        if market_data:
            # Volume Check
            volume_5min = market_data.get('volume_5min', float('inf'))
            if volume_5min < self.MIN_5MIN_VOLUME:
                return False, f"Insufficient liquidity: 5min volume {volume_5min} < {self.MIN_5MIN_VOLUME}"
            
            # Spread Check
            ask = market_data.get('ask_price')
            bid = market_data.get('bid_price')
            if ask and bid and bid > 0:
                spread_pct = ((ask - bid) / bid) * 100
                if spread_pct > self.MAX_SPREAD_PCT:
                    return False, f"Spread too high: {spread_pct:.2f}% > {self.MAX_SPREAD_PCT}%"

        return True, "Safe"

    def _calculate_daily_loss_pct(self, state: Dict) -> float:
        """일일 손실률 계산"""
        daily_pnl = state.get('daily_pnl', 0.0)
        start_capital = state.get('initial_capital', 1.0) # Avoid div by zero
        
        if start_capital <= 0: return 0.0
        
        loss_pct = (daily_pnl / start_capital) * -100
        return max(0.0, loss_pct)

# Singleton
_safety_guard = None

def get_safety_guard() -> SafetyGuard:
    global _safety_guard
    if _safety_guard is None:
        _safety_guard = SafetyGuard()
    return _safety_guard
