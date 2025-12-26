# AI Model Version Management Guide

**Version**: 1.0  
**Date**: 2025-12-27  
**Status**: Production Ready

---

## Overview

The AI Model Version Management system provides automatic lifecycle management for AI models across Gemini, Claude, and OpenAI providers. It handles deprecation detection, automatic fallback to recommended models, and proactive notifications.

---

## Features

### 1. Centralized Model Registry
- Track all AI models and their status
- Maintain deprecation/sunset dates
- Provide recommended replacements

### 2. Auto-Fallback
- Automatically switch from deprecated models
- Severity-based warnings
- Seamless integration with existing code

### 3. Deprecation Monitoring
- Periodic checking
- Telegram notifications
- Severity calculation based on sunset dates

---

## Architecture

```
backend/ai/
├── model_registry.py         ← Model information database
├── model_utils.py             ← Auto-fallback logic
└── ../scripts/
    └── check_model_deprecations.py  ← Monitoring script
```

---

## Configuration

### Environment Variables

Add to `.env`:
```bash
# Gemini
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Claude
ANTHROPIC_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# OpenAI
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o

# Telegram (for notifications)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

See `.env.example` for detailed examples and links.

---

## Usage

### Basic Usage

```python
from backend.ai.model_utils import get_model

# Get model with auto-fallback
gemini_model = get_model("gemini")
claude_model = get_model("claude")
openai_model = get_model("openai")
```

**What happens**:
1. Reads model name from environment variable
2. Checks if model is deprecated
3. If deprecated:
   - Logs warning with severity
   - Automatically uses recommended replacement
   - Returns replacement model name

### Check Current Configuration

```python
from backend.ai.model_utils import check_current_config

results = check_current_config()
for provider, info in results.items():
    print(f"{provider}: {info['model']} - {info['status']}")
```

### Get Model Information

```python
from backend.ai.model_registry import get_model_info, ModelStatus

# Get specific model info
info = get_model_info("gemini", "gemini-1.5-pro-latest")
print(f"Status: {info.status}")
print(f"Deprecated: {info.deprecation_date}")
print(f"Sunset: {info.sunset_date}")
print(f"Replacement: {info.replacement}")
```

### List Deprecated Models

```python
from backend.ai.model_registry import list_deprecated_models

deprecated = list_deprecated_models()
for model in deprecated:
    print(f"{model.provider}/{model.name}: sunset on {model.sunset_date}")
```

---

## Deprecation Checker

### Manual Execution

```bash
python backend/scripts/check_model_deprecations.py
```

**Output**:
```
🔍 Checking AI Model Deprecations...

✅ Gemini: gemini-2.0-flash-exp (stable)
✅ Claude: claude-3-5-sonnet-20241022 (stable)
✅ OpenAI: gpt-4o (stable)

📊 Summary:
  Total models checked: 3
  Deprecated models: 0
  Action required: None
```

### Telegram Notifications

If deprecated models are found:
```
🚨 AI Model Deprecation Alert

Provider: gemini
Model: gemini-1.5-pro-latest
Status: deprecated
Sunset Date: 2025-05-01
Severity: HIGH

Recommended Action:
Update GEMINI_MODEL to: gemini-2.0-flash-exp

Days until sunset: 124
```

### Severity Levels

| Days Until Sunset | Severity | Notification |
|-------------------|----------|--------------|
| < 30 days | CRITICAL | 🚨 Immediate action |
| < 60 days | HIGH | ⚠️ Plan migration |
| < 90 days | MEDIUM | 📊 Monitor |
| 90+ days | LOW | ℹ️ Awareness |

---

## Integration Examples

### FastAPI Startup

Add to `backend/main.py`:

```python
from backend.scripts.check_model_deprecations import ModelDeprecationChecker

@app.on_event("startup")
async def startup_event():
    # ... existing startup code ...
    
    # Check model deprecations
    checker = ModelDeprecationChecker()
    asyncio.create_task(checker.run_periodic_check(
        interval_hours=24,
        send_notifications=True
    ))
```

### Scheduled Check (Cron)

```bash
# Check daily at 9 AM
0 9 * * * cd /path/to/ai-trading-system && python backend/scripts/check_model_deprecations.py
```

---

## Model Status Types

```python
class ModelStatus(Enum):
    STABLE = "stable"           # Production-ready
    DEPRECATED = "deprecated"   # Still works, migration recommended
    SUNSET = "sunset"           # No longer available
    EXPERIMENTAL = "experimental"  # Beta/testing only
```

---

## Adding New Models

Edit `backend/ai/model_registry.py`:

```python
# Gemini Models
gemini_models = [
    ModelInfo(
        provider="gemini",
        name="your-new-model",
        status=ModelStatus.STABLE,
        release_date=date(2025, 1, 15),
        deprecation_date=None,
        sunset_date=None,
        replacement=None,
        description="Your new model description"
    ),
]
```

---

## Error Handling

### Deprecated Model with No Replacement

```python
# Logs error and uses configured model
logger.error("Deprecated model with no replacement: gemini-old-model")
# Falls back to configured model name
```

### Invalid Provider

```python
# Raises ValueError
model = get_model("invalid_provider")
# ValueError: Unknown provider: invalid_provider
```

---

## Best Practices

### 1. Regular Monitoring
- Run deprecation checker weekly
- Enable Telegram notifications
- Review logs regularly

### 2. Proactive Updates
- Update models before sunset dates
- Test new models in development first
- Keep `.env.example` updated

### 3. Version Pinning
```bash
# Good: Specific version
GEMINI_MODEL=gemini-2.0-flash-exp

# Avoid: Latest aliases (unpredictable changes)
GEMINI_MODEL=gemini-pro-latest
```

### 4. Testing
```python
# Test model before production
def test_model_fallback():
    from backend.ai.model_utils import get_model
    
    # Should handle deprecated models gracefully
    model = get_model("gemini")
    assert model is not None
    assert len(model) > 0
```

---

## Troubleshooting

### Model Not Found

**Problem**: `get_model_info()` returns `None`

**Solution**: Check model name spelling or add to registry

### Auto-Fallback Not Working

**Problem**: Still using deprecated model

**Solution**:
1. Verify `.env` has correct model name
2. Check `model_utils.py` is imported correctly
3. Restart backend to reload environment variables

### Telegram Notifications Not Sending

**Problem**: No notifications received

**Solution**:
1. Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`
2. Test connection:
```python
from backend.notifications.telegram_notifier import TelegramNotifier
notifier = TelegramNotifier(token, chat_id)
await notifier.test_connection()
```

---

## API Reference

### `get_model(provider: str) -> str`
Get model name with auto-fallback for deprecated models.

**Parameters**:
- `provider`: "gemini", "claude", or "openai"

**Returns**: Model name string

**Raises**: `ValueError` if provider unknown

### `check_current_config() -> dict`
Check status of all configured models.

**Returns**: Dict with provider info

### `get_model_info(provider: str, model_name: str) -> ModelInfo`
Get detailed information about a specific model.

**Returns**: `ModelInfo` object or `None`

### `list_deprecated_models(provider: Optional[str] = None) -> list`
List all deprecated models.

**Parameters**:
- `provider`: Optional filter by provider

**Returns**: List of `ModelInfo` objects

---

## Maintenance

### Updating Model Information

Recommended: Check official deprecation pages monthly

**Gemini**: https://ai.google.dev/gemini-api/docs/models/gemini  
**Claude**: https://docs.anthropic.com/en/docs/about-claude/models  
**OpenAI**: https://platform.openai.com/docs/deprecations

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-27 | Initial release |

---

## Support

For issues or questions:
1. Check logs: `backend/logs/`
2. Review configuration: `.env` and `.env.example`
3. Test with manual checker: `python backend/scripts/check_model_deprecations.py`

---

**Status**: Production Ready ✅  
**Last Updated**: 2025-12-27
