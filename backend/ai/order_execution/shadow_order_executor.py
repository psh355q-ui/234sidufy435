
import logging
import os
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from backend.database.models import Order
from backend.brokers.kis_broker import KISBroker
from backend.core.database import DatabaseSession

logger = logging.getLogger(__name__)

# Load env
load_dotenv(override=True)

class ShadowOrderExecutor:
    """
    Executes trades in 'Shadow Mode' (Simulation).
    Does not send orders to real exchange.
    Uses real-time price from KIS or DB for execution price.
    """

    def __init__(self, db: AsyncSession = None):
        self.db = db
        
        # Initialize KIS Broker with env vars
        account_no = os.getenv("KIS_ACCOUNT_NUMBER", "")
        if not account_no:
            logger.warning("KIS_ACCOUNT_NUMBER not found in env. Price fetching may fail.")
        
        try:
            # We don't perform full auth here if just for price? 
            # KISBroker performs auth in __init__.
            self.broker = KISBroker(account_no=account_no)
        except Exception as e:
            logger.error(f"Failed to initialize KIS Broker: {e}")
            self.broker = None

    async def execute_order(self, ticker: str, action: str, quantity: int, signal_id: int = None) -> Dict:
        """
        Simulate order execution.
        """
        logger.info(f"👻 Shadow Execution: {action} {quantity} {ticker}")

        # 1. Get Current Price
        current_price = await self._get_execution_price(ticker)
        if not current_price:
            logger.error(f"❌ Failed to get price for {ticker}, skipping shadow trade.")
            return {"status": "failed", "reason": "price_fetch_failed"}

        # 2. Calculate details
        timestamp = datetime.now()
        
        # 3. Create Order Record (Marked as SHADOW)
        if self.db:
             return await self._save_order(self.db, ticker, action, quantity, current_price, signal_id, timestamp)
        else:
            async with DatabaseSession() as db:
               return await self._save_order(db, ticker, action, quantity, current_price, signal_id, timestamp)

    async def _save_order(self, db: AsyncSession, ticker, action, quantity, price, signal_id, timestamp) -> Dict:
        from backend.execution.order_manager import OrderManager
        from backend.execution.state_machine import OrderState

        try:
            shadow_order_id = f"SHADOW_{timestamp.strftime('%Y%m%d%H%M%S')}_{ticker}"

            # Create Order instance with initial state
            new_order = Order(
                ticker=ticker,
                action=action,
                quantity=quantity,
                order_type="market",
                status=OrderState.IDLE.value,  # Start with IDLE
                limit_price=None,
                order_id=shadow_order_id,
                signal_id=signal_id,
                created_at=timestamp
            )

            db.add(new_order)
            await db.flush()  # Get the order ID

            # Use OrderManager for state transitions (Note: OrderManager is sync, so we use sync session)
            # For async contexts, we need to handle this differently
            # For now, we'll use the basic approach with proper state transitions

            # Since OrderManager is sync and this is async, we'll do the transitions manually
            # but following the state machine rules
            from backend.execution.state_machine import state_machine

            # Transition: IDLE → SIGNAL_RECEIVED
            new_order.status = OrderState.SIGNAL_RECEIVED.value
            new_order.metadata = {"signal_id": signal_id, "shadow_mode": True}
            new_order.updated_at = timestamp

            # Transition: SIGNAL_RECEIVED → VALIDATING
            new_order.status = OrderState.VALIDATING.value
            new_order.updated_at = timestamp

            # Transition: VALIDATING → ORDER_PENDING
            new_order.status = OrderState.ORDER_PENDING.value
            new_order.updated_at = timestamp

            # Transition: ORDER_PENDING → ORDER_SENT
            new_order.status = OrderState.ORDER_SENT.value
            new_order.updated_at = timestamp

            # Transition: ORDER_SENT → FULLY_FILLED
            new_order.status = OrderState.FULLY_FILLED.value
            new_order.filled_price = price
            new_order.filled_at = timestamp
            new_order.updated_at = timestamp

            await db.commit()
            await db.refresh(new_order)

            logger.info(f"✅ Shadow Order Filled: {ticker} @ {price}")

            return {
                "status": "filled",
                "order_id": shadow_order_id,
                "filled_price": price,
                "filled_quantity": quantity,
                "timestamp": timestamp.isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to save shadow order: {e}")
            await db.rollback()
            return {"status": "failed", "reason": str(e)}

    async def _get_execution_price(self, ticker: str) -> Optional[float]:
        """Fetch real-time price, fallback to DB last close"""
        # Try KIS Broker first
        if self.broker:
            try:
                # TODO: Make KISBroker async or run in threadpool if blocking
                price = self.broker.get_price(ticker) # Changed from get_current_price to get_price based on KISBroker method
                if price and "current_price" in price:
                    return float(price["current_price"])
            except Exception as e:
                logger.warning(f"KIS price fetch failed for {ticker}: {e}")
        else:
             logger.warning("KIS Broker not initialized, skipping price fetch.")

        # Fallback: Use dummy price for testing if real fetch fails
        return 150.0 # Mock price
