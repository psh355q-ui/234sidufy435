"""
Automation Scheduler

시스템 자동화 작업 스케줄러:
- Macro Context 업데이트 (매일 09:00 KST)
- Daily Report 생성 (매일 16:30 KST)
- Weekly Report 생성 (금요일 17:00 KST)
- Price Tracking 검증 (1시간마다)

사용법:
    python backend/automation/scheduler.py

또는 백그라운드 실행:
    nohup python backend/automation/scheduler.py &
"""

import schedule
import time
import logging
from datetime import datetime
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file (override shell variables)
load_dotenv(override=True)

from backend.automation.macro_context_updater import MacroContextUpdater
from backend.automation.price_tracking_verifier import PriceTrackingVerifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutomationScheduler:
    """자동화 작업 스케줄러"""

    def __init__(self):
        self.macro_updater = MacroContextUpdater()
        self.price_verifier = PriceTrackingVerifier()

    def setup_schedules(self):
        """스케줄 설정"""

        # 1. Macro Context 업데이트 (매일 09:00 KST)
        schedule.every().day.at("09:00").do(self.run_macro_context_update)
        logger.info("✅ Scheduled: Macro Context Update at 09:00 daily")

        # 2. Daily Report 생성 (매일 16:30 KST)
        # TODO: Phase 4에서 구현
        # schedule.every().day.at("16:30").do(self.run_daily_report_generation)
        # logger.info("✅ Scheduled: Daily Report Generation at 16:30 daily")

        # 3. Weekly Report 생성 (금요일 17:00 KST)
        # TODO: Phase 4에서 구현
        # schedule.every().friday.at("17:00").do(self.run_weekly_report_generation)
        # logger.info("✅ Scheduled: Weekly Report Generation on Fridays at 17:00")

        # 4. Price Tracking 검증 (1시간마다)
        schedule.every().hour.do(self.run_price_tracking_verification)
        logger.info("✅ Scheduled: Price Tracking Verification every hour")

    def run_macro_context_update(self):
        """Macro Context 업데이트 실행"""
        try:
            logger.info("="*60)
            logger.info(f"🕐 Starting Macro Context Update - {datetime.now()}")
            logger.info("="*60)

            snapshot = self.macro_updater.update_daily_snapshot()

            logger.info("="*60)
            logger.info(f"✅ Macro Context Update Complete")
            logger.info(f"   Date: {snapshot.snapshot_date}")
            logger.info(f"   Regime: {snapshot.regime}")
            logger.info(f"   Fed Stance: {snapshot.fed_stance}")
            logger.info(f"   VIX: {snapshot.vix_level} ({snapshot.vix_category})")
            logger.info(f"   Market Sentiment: {snapshot.market_sentiment}")
            logger.info("="*60)

        except Exception as e:
            logger.error(f"❌ Macro Context Update failed: {e}", exc_info=True)

    def run_daily_report_generation(self):
        """Daily Report 생성 실행 (TODO: Phase 4)"""
        logger.info("📊 Daily Report Generation - Not implemented yet (Phase 4)")
        pass

    def run_weekly_report_generation(self):
        """Weekly Report 생성 실행 (TODO: Phase 4)"""
        logger.info("📊 Weekly Report Generation - Not implemented yet (Phase 4)")
        pass

    def run_price_tracking_verification(self):
        """Price Tracking 검증 실행"""
        try:
            logger.info("="*60)
            logger.info(f"📈 Starting Price Tracking Verification - {datetime.now()}")
            logger.info("="*60)

            # Run async verification
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(self.price_verifier.verify_all_horizons())
            loop.close()

            logger.info("="*60)
            logger.info(f"✅ Price Tracking Verification Complete")

            for horizon, result in results.items():
                logger.info(f"   {horizon}: {result['correct_count']}/{result['verified_count']} correct ({result['accuracy']*100:.1f}%)")

            logger.info("="*60)

        except Exception as e:
            logger.error(f"❌ Price Tracking Verification failed: {e}", exc_info=True)

    def start(self):
        """스케줄러 시작"""
        logger.info("🚀 Automation Scheduler Starting...")
        self.setup_schedules()

        logger.info("")
        logger.info("📅 Active Schedules:")
        for job in schedule.get_jobs():
            logger.info(f"   - {job}")
        logger.info("")

        logger.info("⏰ Scheduler running... (Press Ctrl+C to stop)")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("\n⏹️  Scheduler stopped by user")
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}", exc_info=True)


if __name__ == "__main__":
    scheduler = AutomationScheduler()
    scheduler.start()
