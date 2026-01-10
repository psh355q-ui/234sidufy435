import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio
import yfinance as yf

logger = logging.getLogger(__name__)

FEEDBACK_FILE = "data/agent_feedback_history.json"

class FeedbackLoopService:
    """
    Service to track AI Agent voting accuracy and calculate bias.
    It implements a 'Self-Reflective Learning' loop.
    """
    
    def __init__(self):
        self.history = self._load_history()
        self.agent_scores = {
            "Trader": 0.5, # Baseline 50%
            "Risk": 0.5,
            "Analyst": 0.5
        }
        self._recalculate_scores()

    def _load_history(self) -> List[Dict]:
        if os.path.exists(FEEDBACK_FILE):
            try:
                with open(FEEDBACK_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load feedback history: {e}")
                return []
        return []

    def _save_history(self):
        os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
        try:
            with open(FEEDBACK_FILE, "w") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save feedback history: {e}")

    def record_vote(self, ticker: str, agent_name: str, vote: str, price: float, confidence: float = 0.0):
        """Record an agent's vote for later validation."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker,
            "agent": agent_name,
            "vote": vote, # BUY, SELL, HOLD
            "entry_price": price,
            "confidence": confidence,
            "validated": False,
            "outcome": None
        }
        self.history.append(entry)
        self._save_history()
        logger.info(f"📝 Recorded vote: {agent_name} -> {vote} on {ticker} @ {price}")

    async def update_scores(self):
        """
        Check historical votes against current prices to validate accuracy.
        Updates internal score metrics.
        """
        now = datetime.now()
        updated_count = 0
        
        tickers_to_check = set()
        for entry in self.history:
            if not entry.get("validated"):
                ts = datetime.fromisoformat(entry["timestamp"])
                # Validate after 1 day (for simplicity in MVP, ideally 1d/3d/5d)
                if (now - ts) > timedelta(days=1): 
                    tickers_to_check.add(entry["ticker"])
        
        if not tickers_to_check:
            return

        # Fetch current prices
        current_prices = {}
        try:
            data = await asyncio.to_thread(yf.download, list(tickers_to_check), period="1d", progress=False)
            # Handle yf structure (similar to before)
            df = data['Close'] if 'Close' in data else data
            for t in tickers_to_check:
                try:
                    if t in df.columns:
                        current_prices[t] = float(df[t].iloc[-1])
                    else:
                        current_prices[t] = float(df.iloc[-1]) if not df.empty else 0.0
                except:
                    pass
        except Exception as e:
            logger.error(f"Failed to fetch validation prices: {e}")
            return

        # Validate entries
        for entry in self.history:
            if not entry.get("validated") and entry["ticker"] in current_prices:
                ts = datetime.fromisoformat(entry["timestamp"])
                if (now - ts) > timedelta(days=1):
                    curr_price = current_prices[entry["ticker"]]
                    entry_price = entry["entry_price"]
                    change_pct = (curr_price - entry_price) / entry_price
                    
                    # Determine success
                    is_correct = False
                    if entry["vote"] == "BUY":
                        is_correct = change_pct > 0.01 # > 1% gain
                    elif entry["vote"] == "SELL":
                        is_correct = change_pct < -0.01 # > 1% drop (saved loss)
                    else: # HOLD
                        is_correct = -0.01 <= change_pct <= 0.01 # Stable
                    
                    entry["validated"] = True
                    entry["outcome"] = "SUCCESS" if is_correct else "FAILURE"
                    entry["exit_price"] = curr_price
                    entry["return_pct"] = change_pct
                    updated_count += 1
        
        if updated_count > 0:
            self._save_history()
            self._recalculate_scores()
            logger.info(f"✅ Feedback Loop: Validated {updated_count} past votes.")

    def _recalculate_scores(self):
        """Calculate weighted accuracy for each agent."""
        stats = {agent: {"correct": 0, "total": 0} for agent in self.agent_scores.keys()}
        
        for entry in self.history:
            if entry.get("validated"):
                agent = entry["agent"]
                if agent not in stats: stats[agent] = {"correct": 0, "total": 0}
                
                stats[agent]["total"] += 1
                if entry["outcome"] == "SUCCESS":
                    stats[agent]["correct"] += 1
        
        for agent, s in stats.items():
            if s["total"] > 0:
                self.agent_scores[agent] = round(s["correct"] / s["total"], 2)
            else:
                self.agent_scores[agent] = 0.5 # Default
                
        logger.info(f"📊 Updated Agent Scores: {self.agent_scores}")

    def get_agent_bias(self, agent_name: str) -> float:
        """
        Return a bias correction factor.
        If agent is 80% accurate, bias = 1.2 (trust more).
        If agent is 30% accurate, bias = 0.8 (trust less).
        Baseline is 0.5 accuracy -> 1.0 bias.
        """
        score = self.agent_scores.get(agent_name, 0.5)
        # Formula: 1.0 + (score - 0.5)
        # 0.8 -> 1.3
        # 0.3 -> 0.8
        return round(1.0 + (score - 0.5), 2)
