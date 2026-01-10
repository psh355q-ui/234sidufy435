"""
Daily Briefing Service
- Aggregates data from multiple sources
- Generates Daily Briefing Markdown Report
- Saves to Database
"""
import logging
import json
from datetime import datetime, date
from typing import Dict, Any, Optional

from backend.database.repository import get_sync_session
from backend.database.models import DailyBriefing

# Analyzers & Services
from backend.analysis.market_gap_analyzer import MarketGapAnalyzer
from backend.analysis.sector_rotation_analyzer import SectorRotationAnalyzer
from backend.services.earnings_calendar_service import EarningsCalendarService
from backend.services.economic_calendar_service import EconomicCalendarService
from backend.ai.enhanced_trading_agent import EnhancedTradingAgent

logger = logging.getLogger(__name__)

class DailyBriefingService:
    def __init__(self):
        self.gap_analyzer = MarketGapAnalyzer()
        self.sector_analyzer = SectorRotationAnalyzer()
        self.earnings_service = EarningsCalendarService()
        self.economic_service = EconomicCalendarService()
        # Initialize EnhancedTradingAgent for AI Picks
        self.trading_agent = EnhancedTradingAgent(enable_skeptic=True, enable_macro_check=True)
        
    async def generate_briefing(self) -> Dict[str, Any]:
        """
        Generate the full daily briefing.
        1. Gather Data
        2. Generate Markdown
        3. Save to DB
        """
        today = date.today()
        logger.info(f"Generating Daily Briefing for {today}...")

        # 1. Gather Data
        gap_data = await self.gap_analyzer.analyze_gaps()
        sector_data = await self.sector_analyzer.analyze_sectors(period="5d")
        earnings_data = await self.earnings_service.get_upcoming_earnings(days=7)
        economic_data = await self.economic_service.get_upcoming_events(days=7)
        
        # 2. Get AI Recommendations (Validated by Deep Reasoning)
        ai_picks = []
        try:
            # Get candidates from Screener
            candidates = await self.trading_agent.get_daily_candidates(force_scan=False)
            
            # Run quick validation for top 3
            for candidate in candidates[:3]:
                analysis = await self.trading_agent.analyze_enhanced(candidate.ticker, skip_skeptic=False)
                
                # Check Skeptic Recommendation
                skeptic_rec = "PROCEED"
                if analysis.get("skeptic_analysis"):
                     skeptic_rec = analysis["skeptic_analysis"].get("recommendation", "PROCEED")
                
                # Only include if not AVOID
                if skeptic_rec != "AVOID":
                    ai_picks.append({
                        "ticker": candidate.ticker,
                        "action": analysis["decision"].action,
                        "score": candidate.score,
                        "reason": candidate.reasons[0] if candidate.reasons else "AI Technical Score High",
                        "skeptic_rec": skeptic_rec
                    })
        except Exception as e:
            logger.error(f"AI Picks generation failed: {e}")
        
        # 3. Synthesize Content
        markdown = self._format_markdown(
            today=today,
            gaps=gap_data,
            sectors=sector_data,
            earnings=earnings_data,
            economics=economic_data,
            ai_picks=ai_picks
        )
        
        # 4. Create Metrics Dict
        metrics = {
            "gaps_count": len(gap_data),
            "leading_sector": sector_data.get('leading_sectors', [{}])[0].get('name') if sector_data.get('leading_sectors') else "N/A",
            "high_impact_events": len([e for e in economic_data if e['impact'] in ['HIGH', 'CRITICAL']]),
            "ai_picks_count": len(ai_picks)
        }
        
        # 5. Save to DB
        briefing = self._save_to_db(today, markdown, metrics)
        
        return {
            "id": briefing.id,
            "date": briefing.date,
            "content": briefing.content,
            "metrics": briefing.metrics
        }

    def _format_markdown(self, today, gaps, sectors, earnings, economics, ai_picks) -> str:
        """Format the gathered data into a nice Markdown report (Korean)"""
        
        md = f"# 📅 AI 일일 브리핑: {today.strftime('%Y-%m-%d')}\n\n"
        
        # 0. AI Watchlist (New)
        md += "## 🤖 AI 오늘의 추천주 (Pre-Validated)\n"
        if ai_picks:
            for pick in ai_picks:
                rec_icon = "🟢" if pick['skeptic_rec'] == "PROCEED" else "🟡"
                md += f"- **{pick['ticker']}**: {pick['reason']} (Screener: {pick['score']:.0f})\n"
                md += f"  - 검증 결과: {rec_icon} {pick['skeptic_rec']} ({pick['action']})\n"
        else:
            md += "오늘 Deep Reasoning 기준을 통과한 추천주가 없습니다. (보수적 접근 권장)\n"
            
        md += "\n---\n\n"
        
        # 1. Market Pulse (Gaps)
        md += "## 🚀 프리마켓 활성 종목 (Pre-Market Pulse)\n"
        if gaps:
            up = [g for g in gaps if g['gap_pct'] > 0][:5]
            down = [g for g in gaps if g['gap_pct'] < 0][:5]
            
            if up:
                md += "**📈 상승 출발 (Gap Up):**\n"
                for g in up:
                    md += f"- **{g['ticker']}**: +{g['gap_pct']}% (${g['current_price']})\n"
            
            if down:
                md += "\n**📉 하락 출발 (Gap Down):**\n"
                for g in down:
                    md += f"- **{g['ticker']}**: {g['gap_pct']}% (${g['current_price']})\n"
        else:
            md += "특이할 만한 프리마켓 갭 변동이 감지되지 않았습니다.\n"
            
        md += "\n---\n\n"
        
        # 2. Sector Rotation
        md += "## 🔄 섹터 로테이션 (최근 5일)\n"
        if sectors and sectors.get('leading_sectors'):
            md += f"**💡 시장 흐름**: {sectors.get('rotation_insight')}\n\n"
            
            md += "| 섹터 (ETF) | 수익률 |\n|---|---|\n"
            for s in sectors['leading_sectors']:
                 md += f"| {s['name']} ({s['ticker']}) | +{s['return_pct']}% |\n"
            for s in sectors['lagging_sectors']:
                 md += f"| {s['name']} ({s['ticker']}) | {s['return_pct']}% |\n"
        else:
            md += "섹터 데이터를 가져올 수 없습니다.\n"

        md += "\n---\n\n"

        # 3. Economic Calendar
        md += "## 🌎 거시경제 일정 (Macro Outlook)\n"
        if economics:
            for e in economics:
                icon = "🔥" if e['impact'] == "CRITICAL" else "📅"
                # Translate impacts broadly if needed, or keep English for clarity
                impact_kr = "매우 중요" if e['impact'] == "CRITICAL" else "중요" if e['impact'] == "HIGH" else "보통"
                md += f"- {icon} **{e['event']}** ({e['date']}): {impact_kr}\n"
        else:
            md += "향후 7일간 주요 경제 이벤트가 없습니다.\n"

        md += "\n---\n\n"

        # 4. Earnings
        md += "## 💰 주요 실적 발표 (Earnings)\n"
        if earnings:
            for e in earnings:
                md += f"- **{e['ticker']}**: {e['date']} (예상 EPS: {e['eps_estimate']})\n"
        else:
            md += "주요 테크 기업 실적 발표가 없습니다.\n"
            
        return md

    def _save_to_db(self, briefing_date, content, metrics):
        """Save to PostgreSQL"""
        db = get_sync_session()
        try:
            # Check existing
            existing = db.query(DailyBriefing).filter(DailyBriefing.date == briefing_date).first()
            
            if existing:
                existing.content = content
                existing.metrics = metrics
                existing.updated_at = datetime.now()
                db.commit()
                db.refresh(existing)
                logger.info(f"Updated Daily Briefing for {briefing_date}")
                return existing
            else:
                new_briefing = DailyBriefing(
                    date=briefing_date,
                    content=content,
                    metrics=metrics
                )
                db.add(new_briefing)
                db.commit()
                db.refresh(new_briefing)
                logger.info(f"Created Daily Briefing for {briefing_date}")
                return new_briefing
        finally:
            db.close()

    async def get_latest_briefing(self):
        """Get the most recent briefing"""
        db = get_sync_session()
        try:
             latest = db.query(DailyBriefing).order_by(DailyBriefing.date.desc()).first()
             return latest
        finally:
            db.close()
