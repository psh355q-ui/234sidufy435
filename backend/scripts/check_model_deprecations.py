"""
AI Model Deprecation Checker

주기적으로 모델 deprecation 상태를 체크하고 알림
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import List, Dict
from pathlib import Path

# Add backend to path for standalone execution
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.ai.model_registry import (
    MODEL_REGISTRY,
    list_deprecated_models,
    get_model_info
)
from backend.ai.model_utils import check_current_config

logger = logging.getLogger(__name__)


class DeprecationChecker:
    """Deprecation 체크 및 알림"""
    
    def __init__(self):
        self.last_check = None
        self.warnings = []
    
    async def check_deprecations(self) -> Dict:
        """
        모든 모델 deprecation 체크
        
        Returns:
            {
                'has_issues': bool,
                'warnings': [...],
                'current_config': {...}
            }
        """
        logger.info("🔍 Checking AI model deprecations...")
        
        self.last_check = datetime.now()
        self.warnings = []
        
        # 1. 현재 설정 확인
        config = check_current_config()
        
        # 2. Deprecated 모델 사용 중인지 체크
        for provider, info in config.items():
            if info.get("is_deprecated"):
                days_left = info.get("days_until_sunset")
                
                warning = {
                    "provider": provider,
                    "model": info["configured"],
                    "status": info["status"],
                    "replacement": info["replacement"],
                    "deprecation_date": info["deprecation_date"],
                    "sunset_date": info["sunset_date"],
                    "days_until_sunset": days_left,
                    "severity": self._get_severity(days_left, info["status"])
                }
                
                self.warnings.append(warning)
                
                # 로그
                if warning["severity"] == "critical":
                    logger.error(
                        f"⛔ CRITICAL: {provider.upper()} model '{info['configured']}' "
                        f"is deprecated! Days left: {days_left}. "
                        f"Use '{info['replacement']}' immediately!"
                    )
                elif warning["severity"] == "high":
                    logger.warning(
                        f"⚠️ HIGH: {provider.upper()} model '{info['configured']}' "
                        f"is deprecated. Days left: {days_left}. "
                        f"Recommended: '{info['replacement']}'"
                    )
                else:
                    logger.info(
                        f"ℹ️ INFO: {provider.upper()} model '{info['configured']}' "
                        f"is deprecated. Recommended: '{info['replacement']}'"
                    )
        
        result = {
            "has_issues": len(self.warnings) > 0,
            "warnings": self.warnings,
            "current_config": config,
            "checked_at": self.last_check.isoformat()
        }
        
        logger.info(f"✅ Deprecation check complete. Issues found: {len(self.warnings)}")
        
        return result
    
    def _get_severity(self, days_left: int, status: str) -> str:
        """경고 심각도 계산"""
        if status == "sunset":
            return "critical"
        
        if days_left is None:
            return "low"
        
        if days_left < 7:
            return "critical"
        elif days_left < 30:
            return "high"
        elif days_left < 90:
            return "medium"
        else:
            return "low"
    
    async def send_notifications(self, warnings: List[Dict]) -> None:
        """
        Deprecation 경고 알림 전송
        
        Args:
            warnings: check_deprecations()의 warnings 리스트
        """
        if not warnings:
            logger.info("✅ No deprecation warnings to send")
            return
        
        # Telegram 알림
        try:
            from backend.notifications.telegram_notifier import TelegramNotifier
            
            notifier = TelegramNotifier()
            
            for warning in warnings:
                message = self._format_warning_message(warning)
                await notifier.send(message, priority="high" if warning["severity"] in ["critical", "high"] else "normal")
            
            logger.info(f"📱 Sent {len(warnings)} deprecation warnings via Telegram")
            
        except ImportError:
            logger.warning("Telegram notifier not available, logging warnings instead")
            for warning in warnings:
                logger.warning(self._format_warning_message(warning, plain=True))
        except Exception as e:
            logger.error(f"Failed to send notifications: {e}")
    
    def _format_warning_message(self, warning: Dict, plain: bool = False) -> str:
        """경고 메시지 포맷"""
        provider = warning["provider"].upper()
        model = warning["model"]
        replacement = warning["replacement"]
        days_left = warning["days_until_sunset"]
        severity = warning["severity"]
        
        # 이모지
        if severity == "critical":
            emoji = "🚨" if not plain else "[CRITICAL]"
        elif severity == "high":
            emoji = "⚠️" if not plain else "[WARNING]"
        else:
            emoji = "ℹ️" if not plain else "[INFO]"
        
        # 메시지 구성
        lines = [
            f"{emoji} AI Model Deprecation Alert",
            f"",
            f"Provider: {provider}",
            f"Current Model: {model}",
            f"Status: DEPRECATED",
        ]
        
        if days_left is not None:
            lines.append(f"⏰ Days Until Sunset: {days_left} days")
        
        lines.append(f"")
        lines.append(f"✅ Recommended Action:")
        lines.append(f"Update .env: {provider}_MODEL={replacement}")
        
        return "\n".join(lines)
    
    async def run_periodic_check(self, interval_hours: int = 24):
        """
        주기적 체크 실행
        
        Args:
            interval_hours: 체크 주기 (시간)
        """
        logger.info(f"🔄 Starting periodic deprecation checks (every {interval_hours}h)")
        
        while True:
            try:
                # 체크 실행
                result = await self.check_deprecations()
                
                # 경고가 있으면 알림 전송
                if result["has_issues"]:
                    await self.send_notifications(result["warnings"])
                
                # 다음 체크까지 대기
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                logger.error(f"Error in periodic check: {e}", exc_info=True)
                # 에러 발생 시 1시간 후 재시도
                await asyncio.sleep(3600)


# Global instance
_checker = None


def get_deprecation_checker() -> DeprecationChecker:
    """DeprecationChecker 싱글톤 인스턴스"""
    global _checker
    if _checker is None:
        _checker = DeprecationChecker()
    return _checker


async def main():
    """CLI 테스트"""
    checker = DeprecationChecker()
    
    print("🔍 AI Model Deprecation Checker")
    print("="*60)
    
    # 체크 실행
    result = await checker.check_deprecations()
    
    print(f"\n✅ Check completed at: {result['checked_at']}")
    print(f"⚠️ Issues found: {len(result['warnings'])}")
    
    if result["warnings"]:
        print("\n📋 Warnings:")
        for warning in result["warnings"]:
            print(f"\n{warning['provider'].upper()}: {warning['model']}")
            print(f"  Severity: {warning['severity']}")
            print(f"  Days left: {warning['days_until_sunset']}")
            print(f"  Replacement: {warning['replacement']}")
        
        print("\n📱 Sending notifications...")
        await checker.send_notifications(result["warnings"])
    else:
        print("\n✅ All models are up to date!")


if __name__ == "__main__":
    asyncio.run(main())
