"""
AI Model Auto-Fallback Utility

Deprecated 모델 자동 감지 및 권장 모델로 전환
"""

import os
import logging
from typing import Optional
from backend.ai.model_registry import (
    MODEL_REGISTRY,
    get_model_info,
    get_recommended_model,
    ModelStatus
)

logger = logging.getLogger(__name__)


class ModelDeprecationWarning(Warning):
    """모델 deprecation 경고"""
    pass


def get_model(
    provider: str,
    fallback: bool = True,
    warn_on_deprecated: bool = True
) -> str:
    """
    모델 조회 with auto-fallback
    
    Args:
        provider: 'gemini', 'openai', 'claude'
        fallback: Deprecated 모델일 때 자동 전환 (default: True)
        warn_on_deprecated: Deprecated 시 경고 로그 (default: True)
    
    Returns:
        사용할 모델 이름
    
    Examples:
        >>> get_model('gemini')
        'gemini-2.0-flash'  # .env에서 읽거나 권장 모델
        
        >>> get_model('openai', fallback=False)  # Deprecated면 에러
        ModelDeprecationWarning: gpt-3.5-turbo is deprecated!
    """
    
    if provider not in MODEL_REGISTRY:
        logger.error(f"Unknown provider: {provider}")
        return None
    
    registry_info = MODEL_REGISTRY[provider]
    
    # 1. 환경변수에서 현재 설정된 모델 읽기
    model_env = registry_info["model_env"]
    current_model = os.getenv(model_env)
    
    # 2. 설정이 없으면 권장 모델 사용
    if not current_model:
        recommended = registry_info["recommended"]
        logger.info(f"{provider}: No model specified, using recommended: {recommended}")
        return recommended
    
    # 3. 모델 정보 조회
    model_info = get_model_info(provider, current_model)
    
    if not model_info:
        # 모델 정보가 없으면 (registry에 없는 새 모델?) 그대로 사용
        logger.warning(f"{provider}: Model '{current_model}' not in registry, using as-is")
        return current_model
    
    # 4. Deprecated 체크
    if model_info.is_deprecated():
        days_left = model_info.days_until_sunset()
        
        replacement = model_info.replacement or registry_info["recommended"]
        
        # 경고 로그
        if warn_on_deprecated:
            if model_info.status == ModelStatus.SUNSET:
                logger.error(
                    f"⛔ {provider.upper()}: Model '{current_model}' is SUNSET (no longer supported)! "
                    f"Using replacement: '{replacement}'"
                )
            elif days_left is not None and days_left < 30:
                logger.warning(
                    f"⚠️ {provider.upper()}: Model '{current_model}' deprecated! "
                    f"Sunset in {days_left} days. "
                    f"Update to: '{replacement}'"
                )
            else:
                logger.warning(
                    f"⚠️ {provider.upper()}: Model '{current_model}' is deprecated. "
                    f"Recommended replacement: '{replacement}'"
                )
        
        # Fallback 처리
        if fallback:
            logger.info(f"↪️ Auto-fallback: {current_model} → {replacement}")
            return replacement
        else:
            raise ModelDeprecationWarning(
                f"{provider}: Model '{current_model}' is deprecated! "
                f"Use '{replacement}' instead."
            )
    
    # 5. 정상 모델 사용
    return current_model


def get_all_models() -> dict:
    """
    모든 provider의 모델 조회 (auto-fallback 포함)
    
    Returns:
        {
            'gemini': 'gemini-2.0-flash',
            'openai': 'gpt-4o-mini',
            'claude': 'claude-3-5-haiku-20241022'
        }
    """
    return {
        provider: get_model(provider, fallback=True)
        for provider in MODEL_REGISTRY.keys()
    }


def check_current_config() -> dict:
    """
    현재 .env 설정 확인 및 deprecation 체크
    
    Returns:
        {
            'gemini': {
                'configured': 'gemini-1.5-flash',
                'status': 'deprecated',
                'recommended': 'gemini-2.0-flash',
                'days_until_sunset': 45
            },
            ...
        }
    """
    result = {}
    
    for provider, registry_info in MODEL_REGISTRY.items():
        model_env = registry_info["model_env"]
        current_model = os.getenv(model_env)
        
        if not current_model:
            result[provider] = {
                "configured": None,
                "status": "not_configured",
                "recommended": registry_info["recommended"]
            }
            continue
        
        model_info = get_model_info(provider, current_model)
        
        if not model_info:
            result[provider] = {
                "configured": current_model,
                "status": "unknown",
                "in_registry": False
            }
            continue
        
        result[provider] = {
            "configured": current_model,
            "status": model_info.status.value,
            "recommended": registry_info["recommended"],
            "is_deprecated": model_info.is_deprecated(),
            "deprecation_date": model_info.deprecation_date,
            "sunset_date": model_info.sunset_date,
            "days_until_sunset": model_info.days_until_sunset(),
            "replacement": model_info.replacement
        }
    
    return result


if __name__ == "__main__":
    # Test
    print("🔍 AI Model Auto-Fallback Test")
    print("="*60)
    
    # 현재 설정 확인
    print("\n📋 Current Configuration:")
    config = check_current_config()
    for provider, info in config.items():
        print(f"\n{provider.upper()}:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    # Auto-fallback 테스트
    print("\n🔄 Auto-Fallback Test:")
    for provider in MODEL_REGISTRY.keys():
        model = get_model(provider, fallback=True)
        print(f"{provider}: {model}")
