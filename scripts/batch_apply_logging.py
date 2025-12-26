#!/usr/bin/env python3
"""
Batch apply logging decorator to all routers
"""

import subprocess
import sys
from pathlib import Path

routers = [
    "tendency_router.py",
    "news_processing_router.py",
    "ceo_analysis_router.py",
    "v2_router.py",
    "kis_sync_router.py",
    "auth_router.py",
    "approvals_router.py",
    "reasoning_router.py",
    "stock_price_router.py",
    "auto_trade_router.py",
    "sec_router.py",
    "position_router.py",
    "incremental_router.py",
    "weight_adjustment_router.py",
    "emergency_router.py",
    "ai_review_router.py",
    "global_macro_router.py",
    "screener_router.py",
    "phase_integration_router.py",
    "gemini_free_router.py",
    "forensics_router.py",
    "notifications_router.py",
    "kis_integration_router.py",
    "monitoring_router.py",
    "portfolio_router.py",
    "consensus_router.py",
    "options_flow_router.py",
    "ai_chat_router.py",
    "ai_signals_router.py",
    "simple_news_router.py",
    "ai_quality_router.py",
    "mock_router.py",
    "news_router.py",
    "performance_router.py",
    "feeds_router.py",
    "data_backfill_router.py",
    "reports_router.py",
    "signals_router.py",
    "backtest_router.py",
]

success_count = 0
skip_count = 0
fail_count = 0

for i, router in enumerate(routers, 1):
    print(f"\n[{i}/{len(routers)}] Processing {router}...")
    
    router_path = Path("backend/api") / router
    
    if not router_path.exists():
        print(f"  ⚠️  File not found, skipping")
        skip_count += 1
        continue
    
    try:
        result = subprocess.run(
            [sys.executable, "scripts/apply_logging.py", str(router_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"  ✅ Success")
            print(result.stdout)
            success_count += 1
        else:
            print(f"  ⚠️  Warning or skipped")
            print(result.stdout)
            skip_count += 1
            
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        fail_count += 1

print("\n" + "="*60)
print("🎉 Batch Processing Complete!")
print("="*60)
print(f"✅ Success: {success_count}")
print(f"⚠️  Skipped: {skip_count}")
print(f"❌ Failed: {fail_count}")
print(f"📊 Total: {len(routers)}")
