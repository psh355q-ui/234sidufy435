"""
AI Model Registry

최신 AI 모델 정보와 deprecation 상태 관리
"""

from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum


class ModelStatus(Enum):
    """모델 상태"""
    STABLE = "stable"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"  # 완전 지원 종료
    EXPERIMENTAL = "experimental"


class ModelInfo:
    """모델 정보"""
    def __init__(
        self,
        name: str,
        status: ModelStatus,
        deprecation_date: Optional[str] = None,
        sunset_date: Optional[str] = None,
        replacement: Optional[str] = None,
        description: str = ""
    ):
        self.name = name
        self.status = status
        self.deprecation_date = deprecation_date
        self.sunset_date = sunset_date
        self.replacement = replacement
        self.description = description
    
    def is_deprecated(self) -> bool:
        """Deprecated 상태인지 확인"""
        return self.status in [ModelStatus.DEPRECATED, ModelStatus.SUNSET]
    
    def days_until_sunset(self) -> Optional[int]:
        """지원 종료까지 남은 일수"""
        if not self.sunset_date:
            return None
        
        sunset = datetime.fromisoformat(self.sunset_date)
        now = datetime.now()
        return (sunset - now).days


# =============================================================================
# Gemini Models
# =============================================================================
# Source: https://ai.google.dev/gemini-api/docs/models/gemini
# Updated: 2025-12-27

GEMINI_MODELS = {
    # Current (Stable)
    "gemini-2.0-flash": ModelInfo(
        name="gemini-2.0-flash",
        status=ModelStatus.STABLE,
        description="Latest Gemini 2.0 Flash - Fast, cost-effective"
    ),
    "gemini-2.5-flash": ModelInfo(
        name="gemini-2.5-flash",
        status=ModelStatus.STABLE,
        description="Gemini 2.5 Flash - Enhanced capabilities"
    ),
    "gemini-2.5-pro": ModelInfo(
        name="gemini-2.5-pro",
        status=ModelStatus.STABLE,
        description="Gemini 2.5 Pro - Highest quality"
    ),
    
    # Experimental
    "gemini-2.0-flash-exp": ModelInfo(
        name="gemini-2.0-flash-exp",
        status=ModelStatus.EXPERIMENTAL,
        description="Experimental version - may change"
    ),
    
    # Deprecated (예시 - 실제 날짜는 Google 발표 기준)
    "gemini-1.5-flash": ModelInfo(
        name="gemini-1.5-flash",
        status=ModelStatus.DEPRECATED,
        deprecation_date="2025-02-15",
        sunset_date="2025-08-15",
        replacement="gemini-2.0-flash",
        description="Deprecated - use gemini-2.0-flash"
    ),
    "gemini-1.5-pro": ModelInfo(
        name="gemini-1.5-pro",
        status=ModelStatus.DEPRECATED,
        deprecation_date="2025-02-15",
        sunset_date="2025-08-15",
        replacement="gemini-2.5-pro",
        description="Deprecated - use gemini-2.5-pro"
    ),
}


# =============================================================================
# OpenAI Models
# =============================================================================
# Source: https://platform.openai.com/docs/models
# Updated: 2025-12-27

OPENAI_MODELS = {
    # Current (Stable)
    "gpt-4o": ModelInfo(
        name="gpt-4o",
        status=ModelStatus.STABLE,
        description="GPT-4 Optimized - High performance"
    ),
    "gpt-4o-mini": ModelInfo(
        name="gpt-4o-mini",
        status=ModelStatus.STABLE,
        description="GPT-4o Mini - Cost-effective, recommended"
    ),
    "gpt-4-turbo": ModelInfo(
        name="gpt-4-turbo",
        status=ModelStatus.STABLE,
        description="GPT-4 Turbo - Fast, capable"
    ),
    
    # Deprecated
    "gpt-3.5-turbo": ModelInfo(
        name="gpt-3.5-turbo",
        status=ModelStatus.DEPRECATED,
        deprecation_date="2024-12-31",
        sunset_date="2025-06-30",
        replacement="gpt-4o-mini",
        description="Deprecated - use gpt-4o-mini"
    ),
}


# =============================================================================
# Claude Models
# =============================================================================
# Source: https://docs.anthropic.com/en/docs/about-claude/models
# Updated: 2025-12-27

CLAUDE_MODELS = {
    # Current (Stable)
    "claude-3-5-sonnet-20241022": ModelInfo(
        name="claude-3-5-sonnet-20241022",
        status=ModelStatus.STABLE,
        description="Claude 3.5 Sonnet - Highest capability"
    ),
    "claude-3-5-haiku-20241022": ModelInfo(
        name="claude-3-5-haiku-20241022",
        status=ModelStatus.STABLE,
        description="Claude 3.5 Haiku - Fast, cost-effective, recommended"
    ),
    "claude-3-opus-20240229": ModelInfo(
        name="claude-3-opus-20240229",
        status=ModelStatus.STABLE,
        description="Claude 3 Opus - Most powerful"
    ),
    
    # Deprecated
    "claude-3-haiku-20240307": ModelInfo(
        name="claude-3-haiku-20240307",
        status=ModelStatus.DEPRECATED,
        deprecation_date="2024-10-22",
        sunset_date="2025-04-22",
        replacement="claude-3-5-haiku-20241022",
        description="Deprecated - use claude-3-5-haiku-20241022"
    ),
}


# =============================================================================
# Registry
# =============================================================================

MODEL_REGISTRY = {
    "gemini": {
        "models": GEMINI_MODELS,
        "recommended": "gemini-2.0-flash",
        "env_vars": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
        "model_env": "GEMINI_MODEL"
    },
    "openai": {
        "models": OPENAI_MODELS,
        "recommended": "gpt-4o-mini",
        "env_vars": ["OPENAI_API_KEY"],
        "model_env": "OPENAI_MODEL"
    },
    "claude": {
        "models": CLAUDE_MODELS,
        "recommended": "claude-3-5-haiku-20241022",
        "env_vars": ["ANTHROPIC_API_KEY", "CLAUDE_API_KEY"],
        "model_env": "CLAUDE_MODEL"
    }
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_model_info(provider: str, model_name: str) -> Optional[ModelInfo]:
    """모델 정보 조회"""
    if provider not in MODEL_REGISTRY:
        return None
    
    models = MODEL_REGISTRY[provider]["models"]
    return models.get(model_name)


def get_recommended_model(provider: str) -> Optional[str]:
    """권장 모델 조회"""
    if provider not in MODEL_REGISTRY:
        return None
    
    return MODEL_REGISTRY[provider]["recommended"]


def list_deprecated_models() -> List[Dict]:
    """모든 deprecated 모델 조회"""
    deprecated = []
    
    for provider, info in MODEL_REGISTRY.items():
        for model_name, model_info in info["models"].items():
            if model_info.is_deprecated():
                deprecated.append({
                    "provider": provider,
                    "model": model_name,
                    "status": model_info.status.value,
                    "deprecation_date": model_info.deprecation_date,
                    "sunset_date": model_info.sunset_date,
                    "replacement": model_info.replacement,
                    "days_until_sunset": model_info.days_until_sunset()
                })
    
    return deprecated


def get_all_stable_models() -> Dict[str, List[str]]:
    """모든 stable 모델 조회"""
    stable = {}
    
    for provider, info in MODEL_REGISTRY.items():
        stable[provider] = [
            model_name 
            for model_name, model_info in info["models"].items()
            if model_info.status == ModelStatus.STABLE
        ]
    
    return stable


if __name__ == "__main__":
    # Test
    print("📋 AI Model Registry")
    print("="*60)
    
    print("\n✅ Stable Models:")
    for provider, models in get_all_stable_models().items():
        print(f"\n{provider.upper()}:")
        for model in models:
            info = get_model_info(provider, model)
            print(f"  - {model}: {info.description}")
    
    print("\n⚠️ Deprecated Models:")
    for dep in list_deprecated_models():
        print(f"\n{dep['provider'].upper()}: {dep['model']}")
        print(f"  Deprecated: {dep['deprecation_date']}")
        print(f"  Sunset: {dep['sunset_date']}")
        print(f"  Days left: {dep['days_until_sunset']}")
        print(f"  Use instead: {dep['replacement']}")
