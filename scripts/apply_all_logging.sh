#!/bin/bash
# Batch apply logging to all routers

routers=(
    "tendency_router.py"
    "news_processing_router.py"
    "ceo_analysis_router.py"
    "v2_router.py"
    "kis_sync_router.py"
    "auth_router.py"
    "approvals_router.py"
    "reasoning_router.py"
    "stock_price_router.py"
    "auto_trade_router.py"
    "sec_router.py"
    "position_router.py"
    "incremental_router.py"
    "weight_adjustment_router.py"
    "emergency_router.py"
    "ai_review_router.py"
    "global_macro_router.py"
    "screener_router.py"
    "phase_integration_router.py"
    "gemini_free_router.py"
    "forensics_router.py"
    "notifications_router.py"
    "kis_integration_router.py"
    "monitoring_router.py"
    "portfolio_router.py"
    "consensus_router.py"
    "options_flow_router.py"
    "ai_chat_router.py"
    "ai_signals_router.py"
    "simple_news_router.py"
    "ai_quality_router.py"
    "mock_router.py"
    "news_router.py"
    "performance_router.py"
    "feeds_router.py"
    "data_backfill_router.py"
    "reports_router.py"
    "signals_router.py"
    "backtest_router.py"
)

for router in "${routers[@]}"; do
    echo "Processing $router..."
    python scripts/apply_logging.py "backend/api/$router"
    if [ $? -eq 0 ]; then
        echo "✅ $router done"
    else
        echo "⚠️  $router failed"
    fi
    echo "---"
done

echo "🎉 Batch processing complete!"
