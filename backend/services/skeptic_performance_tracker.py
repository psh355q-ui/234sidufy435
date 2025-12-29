"""
Skeptic Performance Tracker - Veto된 거래의 회피 손실 추적

Counterfactual Analysis:
- Veto 시점 가격 기록
- 24시간 후 실제 가격 확인
- 가상 손익 계산으로 회피 손실 추정
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import select, and_
from decimal import Decimal

logger = logging.getLogger(__name__)


class SkepticPerformanceTracker:
    """
    Skeptic이 막은 손실을 추정하고 추적
    
    핵심 메트릭:
    - Total Avoided Loss: 회피한 총 손실 추정치
    - Skeptic Accuracy: 올바른 Veto 비율
    - Avg Avoided per Veto: Veto당 평균 회피 손실
    """
    
    def __init__(self, db_session=None):
        """Initialize tracker"""
        self.db = db_session
        logger.info("✅ SkepticPerformanceTracker initialized")
    
    def calculate_avoided_loss(self, vetoed_trade: Dict) -> Dict:
        """
        거부된 트레이드의 가상 손실 계산
        
        Args:
            vetoed_trade: {
                "ticker": str,
                "proposed_price": float,
                "veto_time": datetime,
                "action": "BUY" | "SELL",
                "quantity": int,
                "veto_reason": str
            }
        
        Returns:
            {
                "avoided_loss": float,  # 음수면 회피한 손실
                "actual_move": float,   # 실제 가격 변동
                "was_correct": bool,    # Skeptic이 옳았는가
                "confidence": float     # 판단 확신도
            }
        """
        ticker = vetoed_trade["ticker"]
        veto_price = vetoed_trade["proposed_price"]
        veto_time = vetoed_trade["veto_time"]
        proposed_action = vetoed_trade["action"]
        proposed_qty = vetoed_trade["quantity"]
        
        try:
            # 24시간 후 가격 (실제로는 DB나 API에서 가져옴)
            end_time = veto_time + timedelta(hours=24)
            end_price = self._get_price_at(ticker, end_time)
            
            if end_price is None:
                logger.warning(f"Cannot get price for {ticker} at {end_time}")
                return {
                    "avoided_loss": 0,
                    "actual_move": 0,
                    "was_correct": None,
                    "confidence": 0
                }
            
            # 가격 변동률
            price_change_pct = ((end_price - veto_price) / veto_price) * 100
            
            # 가상 손익 계산
            if proposed_action == "BUY":
                # 샀으면 얼마였을까?
                hypothetical_pnl = (end_price - veto_price) * proposed_qty
            else:  # SELL
                hypothetical_pnl = (veto_price - end_price) * proposed_qty
            
            # 음수면 회피한 손실
            avoided_loss = -hypothetical_pnl if hypothetical_pnl < 0 else 0
            
            # Skeptic이 옳았는가?
            # BUY 거부 → 가격 하락했으면 옳음
            # SELL 거부 → 가격 상승했으면 옳음
            if proposed_action == "BUY":
                was_correct = (end_price < veto_price)
            else:
                was_correct = (end_price > veto_price)
            
            # 확신도 (가격 변동폭에 비례)
            confidence = min(abs(price_change_pct) / 5.0, 1.0) * 100  # 5% 변동 = 100% 확신
            
            return {
                "avoided_loss": avoided_loss,
                "actual_move": price_change_pct,
                "was_correct": was_correct,
                "confidence": confidence,
                "hypothetical_pnl": hypothetical_pnl,
                "end_price": end_price
            }
            
        except Exception as e:
            logger.error(f"Error calculating avoided loss for {ticker}: {e}")
            return {
                "avoided_loss": 0,
                "actual_move": 0,
                "was_correct": None,
                "confidence": 0
            }
    
    def get_cumulative_avoided_loss(self, period_days: int = 30) -> Dict:
        """
        누적 회피 손실 통계
        
        Returns:
            {
                "total_avoided_loss": float,
                "num_vetoes": int,
                "correct_vetoes": int,
                "skeptic_accuracy": float,
                "avg_avoided_per_veto": float
            }
        """
        try:
            # 기간 내 Veto된 거래 조회 (실제로는 DB에서)
            vetoes = self._get_skeptic_vetoes(period_days)
            
            if not vetoes:
                return {
                    "total_avoided_loss": 0,
                    "num_vetoes": 0,
                    "correct_vetoes": 0,
                    "skeptic_accuracy": 0,
                    "avg_avoided_per_veto": 0
                }
            
            total_avoided = 0
            correct_vetoes = 0
            
            for veto in vetoes:
                result = self.calculate_avoided_loss(veto)
                if result["avoided_loss"] > 0:
                    total_avoided += result["avoided_loss"]
                
                if result["was_correct"]:
                    correct_vetoes += 1
            
            accuracy = (correct_vetoes / len(vetoes)) * 100 if vetoes else 0
            avg_avoided = total_avoided / len(vetoes) if vetoes else 0
            
            return {
                "total_avoided_loss": round(total_avoided, 2),
                "num_vetoes": len(vetoes),
                "correct_vetoes": correct_vetoes,
                "skeptic_accuracy": round(accuracy, 1),
                "avg_avoided_per_veto": round(avg_avoided, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating cumulative avoided loss: {e}")
            return {
                "total_avoided_loss": 0,
                "num_vetoes": 0,
                "correct_vetoes": 0,
                "skeptic_accuracy": 0,
                "avg_avoided_per_veto": 0
            }
    
    def _get_skeptic_vetoes(self, period_days: int) -> List[Dict]:
        """
        기간 내 Skeptic이 거부한 거래 조회
        
        TODO: 실제 DB에서 조회
        현재는 Mock 데이터 반환
        """
        # Mock data for testing
        now = datetime.now()
        
        mock_vetoes = [
            {
                "ticker": "TSLA",
                "proposed_price": 245.80,
                "veto_time": now - timedelta(days=1),
                "action": "BUY",
                "quantity": 10,
                "veto_reason": "옵션 Put/Call Ratio 급등 (1.2)"
            },
            {
                "ticker": "META",
                "proposed_price": 385.50,
                "veto_time": now - timedelta(days=3),
                "action": "BUY",
                "quantity": 5,
                "veto_reason": "Tech 섹터 집중도 과다"
            },
            {
                "ticker": "NVDA",
                "proposed_price": 490.20,
                "veto_time": now - timedelta(days=7),
                "action": "SELL",
                "veto_reason": "상승 모멘텀 지속 중"
            }
        ]
        
        return mock_vetoes
    
    def _get_price_at(self, ticker: str, timestamp: datetime) -> Optional[float]:
        """
        특정 시점의 가격 조회
        
        TODO: 실제 KIS API 또는 Yahoo Finance에서 조회
        현재는 Mock 데이터 반환
        """
        # Mock price data (실제로는 API 호출)
        mock_prices = {
            "TSLA": 240.50,  # TSLA는 하락 (Veto 옳음)
            "META": 388.20,  # META는 상승 (Veto 틀림)
            "NVDA": 495.80,  # NVDA는 상승 (SELL Veto 옳음)
        }
        
        return mock_prices.get(ticker)
    
    def format_report_data(self, period_days: int = 30) -> str:
        """
        리포트용 포맷팅된 문자열 생성
        
        Returns:
            Markdown formatted string
        """
        stats = self.get_cumulative_avoided_loss(period_days)
        
        report = f"""
## Skeptic Performance (Last {period_days} Days)

┌─────────────────────────┬──────────────┐
│ Total Trades Vetoed     │ {stats['num_vetoes']:>12} │
│ Correct Vetoes          │ {stats['correct_vetoes']:>9} ({stats['skeptic_accuracy']:.0f}%) │
│ Avoided Loss (Est.)     │ ${stats['total_avoided_loss']:>10,.2f} │
│ Avg Avoided per Veto    │ ${stats['avg_avoided_per_veto']:>10,.2f} │
└─────────────────────────┴──────────────┘

💡 Skeptic has prevented {stats['skeptic_accuracy']:.0f}% of potentially bad trades
"""
        
        return report.strip()


# Global instance
skeptic_tracker = SkepticPerformanceTracker()


# Test function
def test_skeptic_tracker():
    """테스트 함수"""
    print("="*60)
    print("Skeptic Performance Tracker Test")
    print("="*60)
    
    tracker = SkepticPerformanceTracker()
    
    # 1. Individual veto test
    print("\n[Test 1] Individual Veto Analysis")
    veto = {
        "ticker": "TSLA",
        "proposed_price": 245.80,
        "veto_time": datetime.now() - timedelta(days=1),
        "action": "BUY",
        "quantity": 10,
        "veto_reason": "옵션 Put/Call Ratio 급등"
    }
    
    result = tracker.calculate_avoided_loss(veto)
    print(f"Ticker: {veto['ticker']}")
    print(f"Avoided Loss: ${result['avoided_loss']:.2f}")
    print(f"Was Correct: {result['was_correct']}")
    print(f"Actual Move: {result['actual_move']:.2f}%")
    
    # 2. Cumulative stats
    print("\n[Test 2] Cumulative Performance")
    print(tracker.format_report_data(30))
    
    print("\n" + "="*60)
    print("✅ Test completed!")


if __name__ == "__main__":
    test_skeptic_tracker()
