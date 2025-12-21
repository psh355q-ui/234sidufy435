# 🤖 AI Agent Catalog - Complete Reference

**Last Updated**: 2025-12-21  
**Total Agents**: 23  
**Categories**: 4 (War Room, Analysis, Video Production, System)

---

## Overview

This document provides a complete catalog of all 23 AI agents in the system, organized by category. Each agent has a corresponding `SKILL.md` file that defines its role, capabilities, decision framework, and integration points.

---

## 📊 Summary Table

| ID | Agent Name | Category | Model | Cost/Use | Status |
|----|------------|----------|-------|----------|--------|
| W01 | Trader Agent | War Room | Claude Haiku | $0.008 | ✅ Spec Complete |
| W02 | Risk Agent | War Room | Claude Haiku | $0.008 | ✅ Spec Complete |
| W03 | Analyst Agent | War Room | Gemini 2.0 Flash | $0.004 | ✅ Spec Complete |
| W04 | Macro Agent | War Room | Gemini 2.0 Flash | $0.004 | ✅ Spec Complete |
| W05 | Institutional Agent | War Room | Gemini 2.0 Flash | $0.004 | ✅ Spec Complete |
| W06 | News Agent | War Room | Gemini 2.0 Flash | $0.004 | ✅ Spec Complete |
| W07 | PM Agent | War Room | Claude Haiku | $0.010 | ✅ Spec Complete |
| A01 | Quick Analyzer | Analysis | Claude Haiku | $0.014 | ✅ Spec Complete |
| A02 | Deep Reasoning | Analysis | Gemini 2.0 Flash | $0.020 | ✅ Spec Complete |
| A03 | CEO Speech Analyzer | Analysis | Gemini 2.0 Flash | $0.015 | ✅ Spec Complete |
| A04 | News Intelligence | Analysis | Rule-based | $0.000 | ✅ Spec Complete |
| A05 | Emergency News | Analysis | Grounding API | $0.100 | ✅ Spec Complete |
| V01 | News Collector | Video | Rule-based | $0.000 | ✅ Spec Complete |
| V02 | Story Writer | Video | Gemini 2.0 Flash | $0.012 | ✅ Spec Complete |
| V03 | Character Designer | Video | Gemini 2.0 Flash | $0.002 | ✅ Spec Complete |
| V04 | Director Agent | Video | Gemini 2.0 Flash | $0.008 | ✅ Spec Complete |
| S01 | Constitution Validator | System | Rule-based | $0.000 | ✅ Spec Complete |
| S02 | Signal Generator | System | Rule-based | $0.000 | ✅ Spec Complete |
| S03 | Portfolio Manager | System | Rule-based | $0.000 | ✅ Spec Complete |
| S04 | Backtest Analyzer | System | Rule-based | $0.000 | ✅ Spec Complete |
| S05 | Meta Analyst | System | Gemini 2.0 Flash | $0.005 | ✅ Spec Complete |
| S06 | Report Writer | System | Gemini 2.0 Flash | $0.003 | ✅ Spec Complete |
| S07 | Notification Agent | System | Rule-based | $0.000 | ✅ Spec Complete |

**Total Estimated Cost**: ~$0.22/full system run (all agents)

---

## 🏛️ War Room Agents (7)

### W01: Trader Agent
**File**: `backend/ai/skills/war-room/trader-agent/SKILL.md`

**Role**: Offensive / Technical Analyst  
**Personality**: Aggressive, momentum-focused, short-term oriented  
**Vote Weight**: 15%

**Core Capabilities**:
- Chart pattern recognition (Head \u0026 Shoulders, Cup \u0026 Handle, etc.)
- Momentum indicators (RSI, MACD, Bollinger Bands)
- Volume analysis (unusual spikes, whale movements)
- Entry/exit timing optimization
- Support/Resistance identification

**Decision Framework**:
```python
if RSI \u003c 30 and volume_spike \u003e 2x:
    action = "BUY"
    confidence = 0.8
elif RSI \u003e 70 and bearish_divergence:
    action = "SELL"
    confidence = 0.75
else:
    action = "HOLD"
```

**Output Format**:
```json
{
  "agent": "trader",
  "action": "BUY",
  "confidence": 0.8,
  "reasoning": "RSI oversold + volume breakout",
  "key_signals": ["RSI: 28", "Volume: 3.2x avg", "Breakout at $145"]
}
```

---

### W02: Risk Agent  
**File**: `backend/ai/skills/war-room/risk-agent/SKILL.md`

**Role**: Defensive / Risk Manager  
**Personality**: Conservative, loss-averse, detail-oriented  
**Vote Weight**: 20% (highest!)

**Core Capabilities**:
- Volatility analysis (historical β, σ)
- Correlation risk (portfolio-level)
- Maximum loss scenarios (VaR, stress tests)
- Constitutional compliance checking
- Tail risk assessment

**Decision Framework**:
```python
if beta \u003e 1.5 or volatility \u003e 40%:
    action = "SELL" or reduce_position_size()
elif correlation_with_portfolio \u003e 0.8:
    action = "HOLD"  # diversification risk
elif constitutional_violation:
    action = "REJECT"  # hard veto
```

**Veto Power**: Can override other agents if Constitutional rules violated

---

### W03: Analyst Agent
**File**: `backend/ai/skills/war-room/analyst-agent/SKILL.md`

**Role**: Fundamental Analyst  
**Personality**: Data-driven, patient, long-term focused  
**Vote Weight**: 15%

**Core Capabilities**:
- Revenue growth analysis (YoY, QoQ trends)
- Profitability metrics (Gross Margin, EBITDA, FCF)
- Valuation (P/E, P/B, PEG, DCF)
- Competitive moat assessment
- Management quality evaluation

**Decision Framework**:
```python
if revenue_growth \u003e 20% and PE \u003c sector_avg:
    action = "BUY"
elif revenue_declining and PE \u003e 30:
    action = "SELL"
```

---

### W04: Macro Agent
**File**: `backend/ai/skills/war-room/macro-agent/SKILL.md`

**Role**: Macroeconomic Strategist  
**Personality**: Top-down thinker, contrarian, policy-focused  
**Vote Weight**: 15%

**Core Capabilities**:
- Interest rate impact analysis (Fed policy)
- Currency effects (US Dollar Index)
- VIX / fear gauge monitoring
- Sector rotation recommendations
- Global economic trends (China, Europe)

**Key Indicators**:
- VIX: Market fear level
- US10Y: Treasury yield (risk-free rate)
- DXY: Dollar strength (EM impact)
- FRED Data: Unemployment, CPI, GDP

**Decision Framework**:
```python
if VIX \u003e 30:  # High fear
    action = "SELL" or "Defensive stocks only"
elif Fed_rate_cut and VIX \u003c 15:
    action = "BUY Growth"
```

---

### W05: Institutional Agent
**File**: `backend/ai/skills/war-room/institutional-agent/SKILL.md`

**Role**: Smart Money Tracker  
**Personality**: Follow-the-leader, patient, herd-aware  
**Vote Weight**: 10%

**Core Capabilities**:
- 13F filing analysis (hedge fund holdings)
- Whale movement detection (large buy/sell orders)
- Insider trading tracking (SEC Form 4)
- Institutional ownership trends
- Dark pool volume analysis

**Data Sources**:
- SEC EDGAR (13F quarterly filings)
- Whale Alert APIs
-Insider transaction databases
- Bloomberg-style data (if available)

**Decision Framework**:
```python
if top_10_funds_buying and insider_buying \u003e $1M:
    action = "BUY"
    confidence = 0.75
elif institutional_selling \u003e 20% of shares:
    action = "SELL"
```

---

### W06: News Agent  
**File**: `backend/ai/skills/war-room/news-agent/SKILL.md`

**Role**: Real-time News Intelligence  
**Personality**: Reactive, headline-driven, sentiment-focused  
**Vote Weight**: 10%

**Core Capabilities**:
- Emergency news detection (Grounding API)
- Sentiment analysis (Gemini NLP)
- Ticker extraction from news articles
- Duplicate news filtering
- Urgency classification (CRITICAL/HIGH/MEDIUM/LOW)

**Data Sources**:
1. `grounding_search_log` (Emergency News)
2. `news_articles` (Last 24 hours)
3. RSS feeds (real-time)

**Decision Framework**:
```python
if emergency_news_count \u003e 0 and sentiment \u003c -0.7:
    action = "SELL"
    confidence = 0.9
    reasoning = f"{emergency_news_count} critical negative alerts"
elif positive_headlines \u003e 5 and sentiment \u003e 0.6:
    action = "BUY"
    confidence = 0.7
```

**Urgency Boost**: Critical alerts increase confidence by +0.2

---

### W07: PM Agent (Portfolio Manager)
**File**: `backend/ai/skills/war-room/pm-agent/SKILL.md`

**Role**: Final Decision Maker / Consensus Builder  
**Personality**: Balanced, diplomatic, risk-aware  
**Vote Weight**: 15% (+ synthesis role)

**Core Capabilities**:
- Vote aggregation (weighted average)
- Conflict resolution (disagreement handling)
- Position sizing calculation
- Portfolio-level risk check
- Final proposal generation

**Consensus Algorithm**:
```python
def calculate_consensus(votes):
    weighted_sum = sum(vote["confidence"] * vote["weight"])
    
    if weighted_sum \u003e 0.7:
        action = majority_action
    elif 0.3 \u003c weighted_sum \u003c 0.7:
        action = "HOLD"  # No clear consensus
    else:
        action = "SELL" / "Do Nothing"
    
    return {
        "consensus_action": action,
        "confidence": weighted_sum,
        "summary": synthesis_of_all_votes
    }
```

**Special Rules**:
- If Risk Agent votes SELL → reduce position size by 50%
- If \u003e3 agents disagree → automatic HOLD
- If Constitutional violation → proposal rejected

---

## 🔬 Analysis Agents (5)

### A01: Quick Analyzer
**File**: `backend/ai/skills/analysis/quick-analyzer-agent/SKILL.md`

**Purpose**: Fast 60-second analysis for any ticker  
**Model**: Claude Haiku 4  
**Cost**: $0.014/analysis  
**Use Case**: User requests "Analyze AAPL quickly"

**Output**:
```json
{
  "signal": "BUY",
  "confidence": 0.75,
  "summary": "Strong fundamentals, oversold",
  "key_points": [
    "Revenue +12% YoY",
    "P/E ratio: 24 (below sector avg 28)",
    "RSI: 32 (oversold)",
    "Analyst upgrades: 3 in last week",
    "Risk: High valuation if growth slows"
  ],
  "target_price": 185.00,
  "stop_loss": 165.00
}
```

---

### A02: Deep Reasoning Agent
**File**: `backend/ai/skills/analysis/deep-reasoning-agent/SKILL.md`

**Purpose**: 3-Step Chain-of-Thought news analysis  
**Model**: Gemini 2.0 Flash  
**Cost**: $0.020/analysis  
**Use Case**: User selects news article → "Deep Analyze"

**3-Step Process**:
1. **Direct Impact**: Which tickers are directly affected? (e.g., NVDA GPU shortage)
2. **Secondary Impact**: Supply chain, competitors, customers (e.g., MSFT, GOOGL need GPUs)
3. **Final Conclusion**: Trade recommendations with confidence scores

**Example Output**:
```json
{
  "theme": "NVIDIA GPU Supply Shortage",
  "step1_direct_impact": {
    "tickers": ["NVDA"],
    "impact": "Negative (can't meet demand)",
    "confidence": 0.8
  },
  "step2_secondary_impact": {
    "tickers": ["MSFT", "GOOGL", "AMZN"],  // Cloud providers need GPUs
    "impact": "Mixed (delayed AI projects, but AMD benefits)",
    "confidence": 0.6
  },
  "step3_conclusion": {
    "trades": [
      {"ticker": "NVDA", "action": "HOLD", "confidence": 0.7},
      {"ticker": "AMD", "action": "BUY", "confidence": 0.75},  // Competitor
      {"ticker": "MSFT", "action": "SELL", "confidence": 0.5}
    ]
  }
}
```

---

### A03: CEO Speech Analyzer
**File**: `backend/ai/skills/analysis/ceo-speech-agent/SKILL.md`

**Purpose**: Detect tone shifts in executive commentary  
**Model**: Gemini 2.0 Flash  
**Cost**: $0.015/analysis  
**Data Source**: SEC filings (10-K, 8-K), earnings call transcripts

**Tone Shift Detection**:
- Optimistic → Cautious: Red flag
- Cautious → Optimistic: Green flag
- Keyword changes: "strong" vs "challenging", "growth" vs "headwinds"

**Example**:
```json
{
  "ticker": "TSLA",
  "tone_shift": "Optimistic → Cautious",
  "magnitude": 0.65,  // 0-1 scale
  "key_quotes": [
    "Q1 2024: 'Production ramping faster than expected'",
    "Q2 2024: 'Supply chain challenges impacting delivery timelines'"
  ],
  "sentiment_score": -0.3,  // -1 to +1
  "recommendation": {
    "action": "SELL",
    "confidence": 0.7,
    "reasoning": "CEO tone became cautious, possible earnings miss"
  }
}
```

---

### A04: News Intelligence Agent
**File**: `backend/ai/skills/analysis/news-intelligence-agent/SKILL.md`

**Purpose**: Real-time news aggregation \u0026 classification  
**Model**: Rule-based + NLP  
**Cost**: $0/use (no AI calls)  
**Data Source**: RSS feeds (15 sources), NewsAPI

**Capabilities**:
- Duplicate detection (Jaccard similarity \u003e 0.8)
- Ticker extraction (NER + regex)
- Sentiment scoring (keyword-based)
- Urgency classification
- News clustering (similar stories)

**Output**:
```json
{
  "clusters": [
    {
      "theme": "Fed Rate Decision",
      "article_count": 12,
      "sentiment_avg": 0.2,
      "related_tickers": ["SPY", "QQQ", "IWM"],
      "urgency": "HIGH"
    }
  ],
  "new_articles": 45,
  "duplicates_removed": 18
}
```

---

### A05: Emergency News Agent
**File**: `backend/ai/skills/analysis/emergency-news-agent/SKILL.md`

**Purpose**: Critical alert detection → War Room trigger  
**Model**: Anthropic Grounding API  
**Cost**: $0.10/search (paid!)  
**Trigger**: Every 15 minutes (96 searches/day max)

**Urgency Levels**:
```python
CRITICAL = [
    "bankruptcy", "fraud", "CEO resign", "data breach",
    "product recall", "lawsuit settlement", "FDA rejection"
]

HIGH = [
    "earnings miss", "downgrade", "merger collapse",
    "factory fire", "strike", "cyberattack"
]

MEDIUM = [
    "analyst downgrade", "competitor launch",
    "regulatory review", "executive departure"
]
```

**Actions**:
- **CRITICAL**: Immediate Telegram alert + War Room debate + WebSocket broadcast
- **HIGH**: Push notification + log to DB
- **MEDIUM/LOW**: Background logging only

**Cost Control**:
- Monthly budget: $15 (300 searches/month)
- Auto-pause if budget exceeded
- Weekly usage reports

---

## 🎬 Video Production Agents (4)

### V01: News Collector Agent
**File**: `backend/ai/skills/video-production/news-collector-agent/SKILL.md`

**Purpose**: Gather trending market news (top 5 stories/day)  
**Model**: Rule-based  
**Cost**: $0  
**Data Source**: `news_articles` table

**Selection Criteria**:
1. Ticker mention frequency (\u003e10 articles)
2. Market impact (stock price movement \u003e3%)
3. Recency (last 24 hours preferred)
4. Entertainment value (drama, conflict, surprise)

**Output**:
```json
{
  "top_stories": [
    {
      "title": "Tesla Cybertruck delivery delays",
      "ticker": "TSLA",
      "mentions": 15,
      "price_change": -4.2%,
      "entertainment_score": 0.85
    },
    ...
  ]
}
```

---

### V02: Story Writer Agent
**File**: `backend/ai/skills/video-production/story-writer-agent/SKILL.md`

**Purpose**: Generate humorous scripts using Korean stock memes  
**Model**: Gemini 2.0 Flash  
**Cost**: $0.012/video  
**Meme Dictionary**: 50+ Korean stock market memes

**Script Format**:
```
Scene 1: 삼전 고양이 (Samsung Cat) walks into a bar
삼전: "형님들, 오늘도 반도체 팔았습니다 🐱" (Sold chips again today)
엔비디아 고양이: "ㅋㅋㅋ 우리는 AI 칩으로 바빠" (We're busy with AI chips lol)

Scene 2: Plot Twist!
뉴스속보: "삼성전자, HBM3 승인!" (Samsung HBM3 approved!)
삼전: "역시 난 '하이브리드' 메모리 고양이!" (I'm the hybrid memory cat!)

[Meme: "형 나 하이닉스야" - Brother, I'm Hynix (competitor joke)]

Scene 3: Ending
삼전: *선글라스 끼며* "안정적 현금흐름의 맛, 알려줄까?" 
(Want to know the taste of stable cash flow?)
```

---

### V03: Character Designer Agent
**File**: `backend/ai/skills/video-production/character-designer-agent/SKILL.md`

**Purpose**: Create 3D cat personas for 300+ tickers  
**Model**: Gemini 2.0 Flash  
**Cost**: $0.002/character (one-time)  
**Output**: Prompts for HeyGen/Pika AI

**Character Template**:
```json
{
  "ticker": "NVDA",
  "character_name": "엔비디앙 (NVDA-nyan)",
  "visual_description": "Sleek black cat with green LED eyes, wearing a leather jacket with GPU circuit patterns",
  "personality_traits": ["Confident", "Tech-savvy", "Showoff"],
  "catchphrase": "그래픽은 나한테 맡겨!" (Leave graphics to me!),
  "sector": "Technology",
  "market_cap_tier": "Mega-cap",
  "heygen_prompt": "3D animated cat, futuristic, neon green accents, cyberpunk style, confident pose",
  "voice_style": "Deep, robotic, with reverb"
}
```

**Character Archetypes**:
- **Mega-cap** (AAPL, MSFT): Sophisticated, Wise, Calm
- **Growth** (NVDA, TSLA): Energetic, Risky, Bold
- **Value** (JPM, WMT): Conservative, Reliable, Boring
- **Meme Stocks** (GME, AMC): Chaotic, Unpredictable, Funny

---

### V04: Director Agent
**File**: `backend/ai/skills/video-production/director-agent/SKILL.md`

**Purpose**: Assemble final video (storyboard creation)  
**Model**: Gemini 2.0 Flash  
**Cost**: $0.008/video  
**Output**: Scene-by-scene breakdown

**Storyboard Format**:
```json
{
  "video_title": "삼전 vs 엔비디아: GPU 전쟁",
  "duration": "60 seconds",
  "scenes": [
    {
      "scene_num": 1,
      "duration": "10s",
      "characters": ["삼전 Cat", "엔비디아 Cat"],
      "dialogue": "...",
      "camera_angle": "Wide shot, both characters facing each other",
      "background": "Stock exchange floor",
      "music": "Tense, dramatic"
    },
    ...
  ],
  "final_cta": "구독 \u0026 좋아요! 다음 편: 테슬라 사이버트럭 대참사"
}
```

---

## ⚙️ System Agents (7)

### S01: Constitution Validator Agent
**File**: `backend/ai/skills/system/constitution-validator-agent/SKILL.md`

**Purpose**: Enforce immutable rules on all AI proposals  
**Model**: Rule-based (Python)  
**Cost**: $0

**Constitution Rules**:
```python
class RiskLimits:
    MAX_POSITION_SIZE = 0.10  # No single position \u003e 10% of portfolio
    MAX_SECTOR_CONCENTRATION = 0.30  # No sector \u003e 30%
    MAX_DAILY_TRADES = 5
    MAX_LEVERAGE = 1.0  # No margin trading
    
class AllocationRules:
    MIN_CASH_RESERVE = 0.05  # Keep 5% cash
    MAX_CORRELATION = 0.7  # Positions should be diversified
    
class TradingConstraints:
    BLACKLIST = ['PENNY_STOCKS', 'CRYPTO', 'OPTIONS']  # Not allowed
    TRADING_HOURS = (9, 30, 16, 0)  # 9:30 AM - 4:00 PM ET only
    MIN_MARKET_CAP = 1_000_000_000  # $1B minimum
```

**Validation Process**:
```python
def validate_proposal(proposal):
    if proposal.position_size \u003e MAX_POSITION_SIZE:
        return {"valid": False, "violation": "Position size too large"}
    
    if proposal.ticker in BLACKLIST:
        return {"valid": False, "violation": "Blacklisted ticker"}
    
    # Check all rules...
    
    return {"valid": True}
```

**SHA256 Protection**: Rules cannot be modified by AI (hash check on load)

---

### S02: Signal Generator Agent
**File**: `backend/ai/skills/system/signal-generator-agent/SKILL.md`

**Purpose**: Aggregate all trading signals from multiple sources  
**Model**: Rule-based  
**Cost**: $0

**Signal Sources**:
1. War Room (`ai_debate_sessions`)
2. Deep Reasoning (`analysis_results`)
3. CEO Analysis (converted to `news_articles`)
4. Manual Analysis (`/api/analyze`)
5. Emergency News (Grounding API)

**Deduplication Logic**:
```python
def merge_signals(signals):
    # Group by ticker
    by_ticker = group_by(signals, 'ticker')
    
    merged = []
    for ticker, ticker_signals in by_ticker.items():
        # If War Room and Deep Reasoning both say BUY → high confidence
        if all(s['action'] == 'BUY' for s in ticker_signals):
            confidence = max(s['confidence'] for s in ticker_signals) * 1.2
            merged.append({
                "ticker": ticker,
                "action": "BUY",
                "confidence": min(confidence, 1.0),
                "sources": [s['source'] for s in ticker_signals]
            })
        # If conflicting (BUY vs SELL) → HOLD
        elif conflicting_actions(ticker_signals):
            merged.append({
                "ticker": ticker,
                "action": "HOLD",
                "confidence": 0.5,
                "reason": "Conflicting signals"
            })
    
    return merged
```

---

### S03: Portfolio Manager Agent
**File**: `backend/ai/skills/system/portfolio-manager-agent/SKILL.md`

**Purpose**: Rebalancing, allocation, multi-strategy coordination  
**Model**: Rule-based (mean-variance optimization)  
**Cost**: $0

**Rebalancing Logic**:
```python
def rebalance(current_portfolio, target_allocation):
    # Mean-Variance Optimization
    optimal_weights = optimize_portfolio(
        expected_returns,
        covariance_matrix,
        risk_free_rate
    )
    
    # Generate buy/sell orders
    orders = []
    for ticker, target_weight in optimal_weights.items():
        current_weight = current_portfolio.get(ticker, 0)
        delta = target_weight - current_weight
        
        if abs(delta) \u003e 0.05:  # Only rebalance if \u003e5% difference
            orders.append({
                "ticker": ticker,
                "action": "BUY" if delta \u003e 0 else "SELL",
                "amount_usd": abs(delta) * portfolio_value
            })
    
    return orders
```

---

### S04: Backtest Analyzer Agent
**File**: `backend/ai/skills/system/backtest-analyzer-agent/SKILL.md`

**Purpose**: Event-driven backtesting with realistic assumptions  
**Model**: Rule-based  
**Cost**: $0

**Backtest Features**:
- Event-driven (not just daily close prices)
- Realistic slippage (10 bps for large orders)
- Commission fees ($0.005/share)
- Bid-ask spread simulation
- Tax impact (short-term vs long-term capital gains)

**Metrics Calculated**:
```python
{
  "sharpe_ratio": 1.82,
  "sortino_ratio": 2.14,
  "max_drawdown": -18.2%,
  "win_rate": 64.3%,
  "profit_factor": 2.1,
  "capital_preserved": $34,200,  // Shadow Trades
  "trades_total": 156,
  "avg_holding_period": "23 days"
}
```

---

### S05: Meta Analyst Agent
**File**: `backend/ai/skills/system/meta-analyst-agent/SKILL.md`

**Purpose**: Self-improvement through mistake tracking  
**Model**: Gemini 2.0 Flash  
**Cost**: $0.005/analysis

**Mistake Categories**:
1. **Wrong Direction**: Predicted BUY, stock went down
2. **Missed Opportunity**: Predicted HOLD, stock rallied +20%
3. **Premature Exit**: Sold too early (before rally)
4. **Late Entry**: Bought after peak

**Self-Improvement Process**:
```python
def analyze_mistakes(trades):
    mistakes = []
    
    for trade in trades:
        if trade.action == "BUY" and trade.outcome \u003c 0:
            mistakes.append({
                "type": "WRONG_DIRECTION",
                "ticker": trade.ticker,
                "loss": trade.outcome,
                "root_cause": analyze_root_cause(trade)  // AI call
            })
    
    # Generate improvement proposals
    proposals = gemini_generate_enhancements(mistakes)
    
    return {
        "mistakes": mistakes,
        "proposals": proposals  // e.g., "Add RSI check before BUY"
    }
```

**Output**:
```json
{
  "period": "2024-Q4",
  "total_mistakes": 12,
  "by_type": {
    "WRONG_DIRECTION": 5,
    "MISSED_OPPORTUNITY": 4,
    "PREMATURE_EXIT": 2,
    "LATE_ENTRY": 1
  },
  "improvement_proposals": [
    "Add VIX check: if VIX \u003e 25, reduce position size by 50%",
    "Enable stop-loss: automatic sell if loss \u003e -8%",
    "Add earnings date filter: avoid buying 3 days before earnings"
  ]
}
```

---

### S06: Report Writer Agent
**File**: `backend/ai/skills/system/report-writer-agent/SKILL.md`

**Purpose**: Automated performance reporting  
**Model**: Gemini 2.0 Flash  
**Cost**: $0.003/report  
**Schedules**: Daily (6 PM), Weekly (Monday 9 AM), Monthly (1st of month)

**Report Sections**:
1. **Summary**: Total P\u0026L, Sharpe Ratio, Win Rate
2. **Top Performers**: Best 5 trades
3. **Worst Performers**: Worst 5 trades
4. **Shadow Trades**: Avoided losses (rejected proposals)
5. **Risk Metrics**: Max Drawdown, Volatility, Beta
6. **AI Performance**: Agent accuracy, consensus rate
7. **Cost Report**: API usage, total operational cost

**Format Options**:
- **PDF**: For compliance/auditing
- **Markdown**: For GitHub/Docs
- **JSON**: For programmatic access
- **Telegram**: Daily summary push notification

---

### S07: Notification Agent
**File**: `backend/ai/skills/system/notification-agent/SKILL.md`

**Purpose**: Multi-channel alert dispatcher  
**Model**: Rule-based  
**Cost**: $0

**Channels**:
1. **Telegram**: Critical alerts, proposal approvals, daily summaries
2. **Slack**: Team notifications, backtest results
3. **Email**: Weekly/monthly reports
4. **WebSocket**: Real-time frontend updates

**Urgency Routing**:
```python
ROUTING_RULES = {
    "CRITICAL": ["Telegram", "WebSocket", "Email"],  // All channels
    "HIGH": ["Telegram", "WebSocket"],
    "MEDIUM": ["WebSocket", "Slack"],
    "LOW": ["Email"]  // Batch send
}
```

**Example Notifications**:
```python
# Critical: Emergency news
send_notification(
    urgency="CRITICAL",
    title="🔴 EMERGENCY: TSLA CEO Resignation",
    message="War Room debate initiated. Awaiting consensus.",
    channels=["Telegram", "WebSocket"]
)

# High: War Room proposal
send_notification(
    urgency="HIGH",
    title="📊 War Room Consensus: BUY NVDA",
    message="7 agents voted. Confidence: 82%. Approve?",
    channels=["Telegram", "WebSocket"],
    actions=["Approve", "Reject"]
)

# Medium: Daily summary
send_notification(
    urgency="MEDIUM",
    title="📈 Daily Summary",
    message="Portfolio: +1.2% | Signals: 3 BUY, 1 SELL",
    channels=["WebSocket", "Slack"]
)
```

---

## 🔗 Integration Points

### Agent Communication Flow

```
User Input (e.g., "Analyze TSLA")
        ↓
 Signal Generator (S02)
        ↓
┌───────────────────────────┐
│   Route to Agents         │
├───────────────────────────┤
│ - Quick Analyzer (A01)    │
│ - War Room (W01-W07)      │
│ - Deep Reasoning (A02)    │
└───────────────┬───────────┘
                ↓
        Constitution Validator (S01)
                ↓
         ✅ Valid?
        ┌───┴───┐
       YES      NO
        │        │
        │        └──→ Reject + Log
        ↓
  Commander Approval
        ↓
  Portfolio Manager (S03)
        ↓
   KIS Broker API
        ↓
    Execution
        ↓
  Report Writer (S06)
        ↓
  Notification Agent (S07)
```

---

## 📚 Related Documentation

- **Main Overview**: [2025_System_Overview.md](2025_System_Overview.md)
- **Agent Skills Guide**: `backend/ai/skills/README.md`
- **Constitution Rules**: `backend/ai/constitution/rules.py`
- **API Documentation**: `docs/07_API_Documentation/`

---

**Version**: 1.0  
**Last Updated**: 2025-12-21  
**Total Agents**: 23 (100% Spec Complete)

