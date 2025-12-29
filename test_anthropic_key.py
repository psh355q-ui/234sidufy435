#!/usr/bin/env python
"""
Test Anthropic API Key Validity
"""
import os
from dotenv import load_dotenv
from pathlib import Path
from anthropic import Anthropic

load_dotenv(Path(__file__).parent / '.env', override=True)

print("="*60)
print("Anthropic API Key Test")
print("="*60)

anthropic_key = os.getenv('ANTHROPIC_API_KEY')
claude_key = os.getenv('CLAUDE_API_KEY')

print(f"ANTHROPIC_API_KEY: {anthropic_key[:20]}... (length: {len(anthropic_key) if anthropic_key else 0})")
print(f"CLAUDE_API_KEY: {claude_key[:20]}... (length: {len(claude_key) if claude_key else 0})")
print(f"Keys match: {anthropic_key == claude_key}")
print()

# Test with ANTHROPIC_API_KEY
print("Testing ANTHROPIC_API_KEY...")
try:
    client = Anthropic(api_key=anthropic_key)
    response = client.messages.create(
        model='claude-3-5-haiku-20241022',
        max_tokens=100,
        messages=[{'role': 'user', 'content': 'Say hello in one word'}]
    )
    print(f"✅ ANTHROPIC_API_KEY works!")
    print(f"Response: {response.content[0].text}")
except Exception as e:
    print(f"❌ ANTHROPIC_API_KEY failed: {e}")

print()

# Test with CLAUDE_API_KEY
print("Testing CLAUDE_API_KEY...")
try:
    client = Anthropic(api_key=claude_key)
    response = client.messages.create(
        model='claude-3-5-haiku-20241022',
        max_tokens=100,
        messages=[{'role': 'user', 'content': 'Say hello in one word'}]
    )
    print(f"✅ CLAUDE_API_KEY works!")
    print(f"Response: {response.content[0].text}")
except Exception as e:
    print(f"❌ CLAUDE_API_KEY failed: {e}")

print()
print("="*60)
print("Key Format Check")
print("="*60)
print(f"ANTHROPIC_API_KEY starts with 'sk-ant-': {anthropic_key.startswith('sk-ant-') if anthropic_key else False}")
print(f"ANTHROPIC_API_KEY has correct format: {len(anthropic_key) > 50 if anthropic_key else False}")
print("="*60)
