import os
import sys
import logging

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.config.secrets_manager import get_secrets_manager, get_secret
from backend.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_secrets_encryption():
    print("🔐 Testing Secrets Encryption...")
    
    manager = get_secrets_manager()
    
    # 1. Encrypt a dummy key
    test_key = "TEST_SECRET_KEY"
    test_value = "secret_value_12345"
    
    # Check if current secrets exist
    current_secrets = manager.decrypt_secrets()
    current_secrets[test_key] = test_value
    
    # Encrypt
    manager.encrypt_secrets(current_secrets)
    print(f"✅ Encrypted '{test_key}' into .secrets.enc")
    
    # 2. Verify Retrieval via helper
    retrieved = get_secret(test_key)
    print(f"Retrieved via get_secret(): {retrieved}")
    
    if retrieved == test_value:
        print("✅ SUCCESS: Secret retrieved correctly.")
    else:
        print(f"❌ FAILURE: Expected '{test_value}', got '{retrieved}'")

    # 3. Verify Integration with Settings (Mocking Env)
    # Note: Pydantic Settings are loaded at import time or instantiation.
    # Since we already instantiated 'settings' object in the module, let's check if we can re-instantiate or check behavior.
    
    # Use a fresh instance of Settings to trigger default_factory
    # But first, ensure env var is NOT set (or set to something else to test precedence if needed)
    if test_key in os.environ:
        del os.environ[test_key]
        
    print("\nNote: To fully test Settings integration, we'd need to add a field to Settings class dynamically or check existing ones.")
    print("Since we modified critical keys (OPENAI_API_KEY, etc.), we should verify they are not broken.")
    
    # Check if critical keys are still accessible (likely from .env via os.getenv inside get_secret fallback or pydantic env override)
    # get_secret priority: 1. Env, 2. Encrypted.
    # Pydantic priority: 1. Env, 2. default_factory (which calls get_secret)
    
    # So if we have .env file, it works as before.
    # If we remove .env var and have it in secrets.enc, it should work.
    
    print(f"Current OPENAI_API_KEY available? {'Yes' if settings.openai_api_key else 'No'}")

if __name__ == "__main__":
    test_secrets_encryption()
