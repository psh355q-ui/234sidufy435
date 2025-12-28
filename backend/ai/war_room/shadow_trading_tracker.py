"""
Unified Shadow Trading Tracker

War Room 공격적 트레이딩 + Backtest 방어적 트래킹 통합

기능:
1. 공격적 Shadow Trading (War Room 실행 추적)
   - BUY/SELL 실행 추적
   - Win rate, Sharpe ratio 계산
   
2. 방어적 Shadow Tracking (거부된 제안 추적)
   - 거부된 제안 가상 추적
   - Shield Report (방어 성공률, 회피 손실)

Author: AI Trading System
Date: 2025-12-28
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.data.models.shadow_trade import ShadowTrade
from backend.data.collectors.api_clients.yahoo_client import YahooFinanceClient

logger = logging.getLogger(__name__)


class UnifiedShadowTracker:
    """
    통합 Shadow Tracker
    
    공격적 트레이딩 + 방어적 트래킹 모두 지원:
    - War Room 결정 실행 추적 (공격)
    - 거부된 제안 추적 (방어)
    - 성과 분석 (Win rate, Sharpe, Shield Report)
    """
    
    def __init__(
        self,
        db_session: Optional[Session] = None,
        yahoo_client: Optional[YahooFinanceClient] = None,
        initial_capital: float = 100000.0
    ):
        """
        Args:
            db_session: Database session (None이면 in-memory)
            yahoo_client: Yahoo Finance client
            initial_capital: 초기 자본
        """
        self.db = db_session
        self.yahoo_client = yahoo_client or YahooFinanceClient()
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # In-memory storage (DB 없을 때)
        self.in_memory_trades = [] if not db_session else None
        
        logger.info(f"UnifiedShadowTracker initialized with ${initial_capital:,.0f}")
    
    # =========================================================================
    # 공격적 트레이딩 (War Room Execution Tracking)
    # =========================================================================
    
    async def execute_offensive_trade(self, war_room_result: Dict) -> Dict[str, Any]:
        """
        War Room 결정을 Shadow Trade로 실행 (공격적)
        
        Args:
            war_room_result: War Room 최종 결정
            {
                "session_id": str,
                "ticker": str,
                "action": "BUY|SELL|HOLD",
                "confidence": 0.0-1.0,
                "price": float,
                "size_usd": float (optional)
            }
        
        Returns:
            실행 결과
        """
        action = war_room_result.get("action", "HOLD")
        
        # HOLD는 거래하지 않음
        if action == "HOLD":
            logger.info(f"Offensive trade skipped: HOLD action")
            return {"status": "SKIPPED", "reason": "HOLD action"}
        
        ticker = war_room_result.get("ticker")
        entry_price = float(war_room_result.get("price", 0))
        confidence = float(war_room_result.get("confidence", 0.5))
        
        # 포지션 크기 계산 (헌법 준수: 10% 이하)
        size_usd = war_room_result.get("size_usd")
        if not size_usd:
            max_position_pct = 0.10
            size_usd = self.current_capital * max_position_pct * confidence
        
        size_usd = min(size_usd, self.current_capital * 0.10)
        shares = int(size_usd / entry_price) if entry_price > 0 else 0
        
        # Shadow Trade 생성
        shadow = ShadowTrade(
            proposal_id=None,
            ticker=ticker,
            action=action,
            entry_price=entry_price,
            shares=shares,
            rejection_reason=None,  # 거부 아님 (실행함)
            violated_articles=None,
            tracking_days=30,  # 기본 30일 추적
            status='TRACKING',
            notes=f"Offensive trade from War Room (confidence: {confidence})"
        )
        
        # DB 또는 메모리에 저장
        if self.db:
            self.db.add(shadow)
            self.db.commit()
        else:
            self.in_memory_trades.append(shadow)
        
        logger.info(
            f"🎯 Offensive trade opened: {action} {ticker} @ ${entry_price:.2f}, "
            f"size ${size_usd:,.0f} ({shares} shares)"
        )
        
        return {
            "shadow_trade_id": str(shadow.id),
            "ticker": ticker,
            "action": action,
            "entry_price": entry_price,
            "shares": shares,
            "position_size_usd": size_usd,
            "status": "TRACKING"
        }
    
    # =========================================================================
    # 방어적 트래킹 (Rejected Proposal Tracking)
    # =========================================================================
    
    def create_defensive_shadow(
        self,
        proposal: Dict[str, Any],
        rejection_reason: str,
        violated_articles: Optional[List[str]] = None,
        tracking_days: int = 7
    ) -> ShadowTrade:
        """
        거부된 제안을 Shadow Trade로 추적 (방어적)
        
        Args:
            proposal: 거부된 제안
            rejection_reason: 거부 사유
            violated_articles: 위반된 헌법 조항
            tracking_days: 추적 기간
        
        Returns:
            생성된 ShadowTrade
        """
        ticker = proposal.get('ticker')
        action = proposal.get('action', 'BUY')
        entry_price = proposal.get('entry_price', 0.0)
        shares = proposal.get('shares', 0)
        
        # 현재 가격 조회 (entry_price 없으면)
        if entry_price == 0.0:
            entry_price = self.yahoo_client.get_current_price(ticker)
        
        # Shadow Trade 생성
        shadow = ShadowTrade(
            proposal_id=proposal.get('id'),
            ticker=ticker,
            action=action,
            entry_price=entry_price,
            shares=shares,
            rejection_reason=rejection_reason,
            violated_articles=', '.join(violated_articles) if violated_articles else None,
            tracking_days=tracking_days,
            status='TRACKING',
            notes=f"Defensive shadow: rejected due to {rejection_reason}"
        )
        
        # DB 또는 메모리에 저장
        if self.db:
            self.db.add(shadow)
            self.db.commit()
        else:
            self.in_memory_trades.append(shadow)
        
        logger.info(
            f"🛡️ Defensive shadow created: {ticker} {action} @ ${entry_price} "
            f"(reason: {rejection_reason})"
        )
        
        return shadow
    
    # =========================================================================
    # 공통 기능 (Update, Close, Query)
    # =========================================================================
    
    def update_shadow_trade(self, shadow: ShadowTrade) -> ShadowTrade:
        """
        Shadow Trade 가격 업데이트
        
        Args:
            shadow: Shadow Trade
        
        Returns:
            업데이트된 Shadow Trade
        """
        try:
            current_price = self.yahoo_client.get_current_price(shadow.ticker)
            
            if current_price:
                shadow.update_pnl(current_price)
                
                if self.db:
                    self.db.commit()
                
                logger.debug(
                    f"Shadow updated: {shadow.ticker} "
                    f"${shadow.entry_price} → ${current_price} "
                    f"({shadow.virtual_pnl_pct:+.2%})"
                )
        
        except Exception as e:
            logger.error(f"Failed to update shadow trade: {shadow.ticker} - {e}")
        
        return shadow
    
    def update_all_shadows(self):
        """모든 활성 Shadow Trades 업데이트"""
        if self.db:
            active_shadows = self.db.query(ShadowTrade).filter(
                ShadowTrade.status == 'TRACKING'
            ).all()
        else:
            active_shadows = [
                s for s in (self.in_memory_trades or [])
                if s.status == 'TRACKING'
            ]
        
        logger.info(f"🔄 Updating {len(active_shadows)} active shadow trades...")
        
        for shadow in active_shadows:
            # 추적 기간 만료 체크
            if shadow.created_at:
                elapsed = datetime.utcnow() - shadow.created_at
                
                if elapsed.days >= shadow.tracking_days:
                    # 추적 종료
                    current_price = self.yahoo_client.get_current_price(shadow.ticker)
                    if current_price:
                        shadow.close_tracking(current_price)
                        logger.info(f"✅ Shadow tracking ended: {shadow.ticker}")
                    continue
            
            # 업데이트
            self.update_shadow_trade(shadow)
        
        if self.db:
            self.db.commit()
    
    async def close_shadow_trade(
        self,
        shadow_id: str,
        exit_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Shadow Trade 청산
        
        Args:
            shadow_id: Shadow Trade ID
            exit_price: 청산가 (None이면 현재 시장가)
        
        Returns:
            청산 결과
        """
        # Shadow Trade 조회
        if self.db:
            shadow = self.db.query(ShadowTrade).filter(
                ShadowTrade.id == shadow_id
            ).first()
        else:
            shadow = next(
                (s for s in (self.in_memory_trades or []) if str(s.id) == shadow_id),
                None
            )
        
        if not shadow:
            return {"status": "ERROR", "reason": "Trade not found"}
        
        # 청산가 결정
        if not exit_price:
            exit_price = self.yahoo_client.get_current_price(shadow.ticker)
        
        # 청산
        shadow.close_tracking(exit_price)
        
        if self.db:
            self.db.commit()
        
        logger.info(
            f"🔒 Shadow trade closed: {shadow.action} {shadow.ticker} | "
            f"Entry ${shadow.entry_price:.2f} → Exit ${exit_price:.2f} | "
            f"PnL: ${shadow.virtual_pnl:+,.2f} ({shadow.virtual_pnl_pct:+.2%})"
        )
        
        return {
            "shadow_trade_id": str(shadow.id),
            "ticker": shadow.ticker,
            "action": shadow.action,
            "entry_price": shadow.entry_price,
            "exit_price": exit_price,
            "pnl_usd": shadow.virtual_pnl,
            "pnl_pct": shadow.virtual_pnl_pct,
            "status": "CLOSED"
        }
    
    # =========================================================================
    # 성과 분석 (Performance Analytics)
    # =========================================================================
    
    async def calculate_offensive_performance(
        self,
        ticker: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        공격적 트레이딩 성과 계산
        
        Returns:
            Win rate, Sharpe ratio, etc.
        """
        # 공격적 트레이드 필터 (rejection_reason이 None)
        if self.db:
            query = self.db.query(ShadowTrade).filter(
                ShadowTrade.rejection_reason == None,
                ShadowTrade.status == 'CLOSED'
            )
            
            if ticker:
                query = query.filter(ShadowTrade.ticker == ticker)
            
            if days:
                cutoff = datetime.utcnow() - timedelta(days=days)
                query = query.filter(ShadowTrade.created_at >= cutoff)
            
            trades = query.all()
        else:
            trades = [
                t for t in (self.in_memory_trades or [])
                if t.rejection_reason is None and t.status == 'CLOSED'
            ]
            
            if ticker:
                trades = [t for t in trades if t.ticker == ticker]
            
            if days:
                cutoff = datetime.utcnow() - timedelta(days=days)
                trades = [t for t in trades if t.created_at >= cutoff]
        
        if not trades:
            return self._empty_performance_result()
        
        # 기본 통계
        total_trades = len(trades)
        win_trades = [t for t in trades if t.virtual_pnl > 0]
        loss_trades = [t for t in trades if t.virtual_pnl < 0]
        
        win_count = len(win_trades)
        loss_count = len(loss_trades)
        win_rate = win_count / total_trades if total_trades > 0 else 0
        
        # 평균 손익
        avg_win = sum(t.virtual_pnl_pct for t in win_trades) / win_count if win_count > 0 else 0
        avg_loss = sum(t.virtual_pnl_pct for t in loss_trades) / loss_count if loss_count > 0 else 0
        
        # Profit Factor
        total_profit = sum(t.virtual_pnl for t in win_trades)
        total_loss = abs(sum(t.virtual_pnl for t in loss_trades))
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        # Sharpe Ratio (간단 계산)
        returns = [t.virtual_pnl_pct for t in trades]
        avg_return = sum(returns) / len(returns) if returns else 0
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns) if len(returns) > 1 else 0
        std_dev = variance ** 0.5
        sharpe_ratio = (avg_return / std_dev) if std_dev > 0 else 0
        
        # Max Drawdown
        max_drawdown = min(returns) if returns else 0
        
        return {
            "type": "OFFENSIVE",
            "total_trades": total_trades,
            "win_trades": win_count,
            "loss_trades": loss_count,
            "win_rate": round(win_rate, 3),
            "avg_win": round(avg_win, 4),
            "avg_loss": round(avg_loss, 4),
            "profit_factor": round(profit_factor, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "max_drawdown": round(max_drawdown, 4),
            "total_pnl_usd": round(sum(t.virtual_pnl for t in trades), 2)
        }
    
    def generate_shield_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Shield Report (방어 성공 보고서) 생성
        
        Args:
            days: 조회 기간
        
        Returns:
            방어 성과 리포트
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # 방어적 트레이드 필터 (rejection_reason이 있음)
        if self.db:
            all_shadows = self.db.query(ShadowTrade).filter(
                ShadowTrade.rejection_reason != None,
                ShadowTrade.created_at >= cutoff
            ).all()
        else:
            all_shadows = [
                t for t in (self.in_memory_trades or [])
                if t.rejection_reason is not None and t.created_at >= cutoff
            ]
        
        # 방어 성공
        wins = [s for s in all_shadows if s.is_defensive_win()]
        total_avoided = sum(s.get_avoided_loss() for s in wins)
        
        report = {
            "type": "DEFENSIVE",
            "period_days": days,
            "total_rejected_proposals": len(all_shadows),
            "defensive_wins": len(wins),
            "defensive_win_rate": len(wins) / len(all_shadows) if all_shadows else 0,
            "total_avoided_loss": total_avoided,
            "highlights": []
        }
        
        # 주요 사례 (손실 방어 금액 상위 3개)
        sorted_wins = sorted(wins, key=lambda x: x.get_avoided_loss(), reverse=True)
        
        for shadow in sorted_wins[:3]:
            report['highlights'].append({
                "ticker": shadow.ticker,
                "action": shadow.action,
                "rejection_reason": shadow.rejection_reason,
                "entry_price": shadow.entry_price,
                "exit_price": shadow.exit_price,
                "avoided_loss": shadow.get_avoided_loss(),
                "pnl_pct": shadow.virtual_pnl_pct,
                "date": shadow.created_at.strftime('%Y-%m-%d') if shadow.created_at else None
            })
        
        return report
    
    def _empty_performance_result(self) -> Dict:
        """빈 성과 결과"""
        return {
            "total_trades": 0,
            "win_trades": 0,
            "loss_trades": 0,
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "profit_factor": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "total_pnl_usd": 0.0
        }
    
    # =========================================================================
    # 조회 기능 (Query)
    # =========================================================================
    
    def get_all_shadows(
        self,
        status: Optional[str] = None,
        ticker: Optional[str] = None,
        limit: int = 100
    ) -> List[ShadowTrade]:
        """
        Shadow Trades 조회
        
        Args:
            status: 상태 필터 (TRACKING/CLOSED)
            ticker: 티커 필터
            limit: 최대 개수
        
        Returns:
            Shadow Trades 리스트
        """
        if self.db:
            query = self.db.query(ShadowTrade)
            
            if status:
                query = query.filter(ShadowTrade.status == status)
            
            if ticker:
                query = query.filter(ShadowTrade.ticker == ticker)
            
            return query.order_by(ShadowTrade.created_at.desc()).limit(limit).all()
        
        else:
            trades = self.in_memory_trades or []
            
            if status:
                trades = [t for t in trades if t.status == status]
            
            if ticker:
                trades = [t for t in trades if t.ticker == ticker]
            
            return sorted(trades, key=lambda t: t.created_at, reverse=True)[:limit]
