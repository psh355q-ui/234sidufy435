"""
Complete Debugging Agent Test Runner

이 스크립트는 전체 디버깅 에이전트 워크플로우를 실행합니다:
1. 로그 읽기
2. 패턴 감지
3. 개선 제안 생성
4. 결과 출력

Usage:
    python run_debugging_agent.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
# File location: ai-trading-system/backend/ai/skills/system/debugging-agent/scripts/run_debugging_agent.py
# We need to go up 7 levels to reach ai-trading-system root (not backend)
project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("🔍 Debugging Agent - Complete Workflow")
print("="*80)
print(f"Project root: {project_root}")
print()

try:
    # 1. Log Reader
    print("Step 1/3: Reading logs...")
    print("-"*80)
    
    # Import using importlib to handle hyphenated directory names
    import importlib.util
    scripts_dir = Path(__file__).parent
    
    # Load log_reader
    log_reader_path = scripts_dir / "log_reader.py"
    spec = importlib.util.spec_from_file_location("log_reader", log_reader_path)
    log_reader_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(log_reader_module)
    log_reader_module.main()
    print("✅ Log reading complete\n")
    
    # 2. Pattern Detector
    print("Step 2/3: Detecting patterns...")
    print("-"*80)
    
    # Load pattern_detector
    pattern_detector_path = scripts_dir / "pattern_detector.py"
    spec = importlib.util.spec_from_file_location("pattern_detector", pattern_detector_path)
    pattern_detector_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pattern_detector_module)
    pattern_detector_module.main()
    print("✅ Pattern detection complete\n")
    
    # 3. Improvement Proposer
    print("Step 3/3: Generating improvement proposals...")
    print("-"*80)
    
    # Load improvement_proposer
    improvement_proposer_path = scripts_dir / "improvement_proposer.py"
    spec = importlib.util.spec_from_file_location("improvement_proposer", improvement_proposer_path)
    improvement_proposer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(improvement_proposer_module)
    improvement_proposer_module.main()
    print("✅ Improvement proposals generated\n")
    
    print("="*80)
    print("🎉 Debugging Agent workflow completed successfully!")
    print("="*80)
    print()
    print("📁 Output files:")
    print("  - agent_execution_logs.json")
    print("  - complete_patterns.json")
    print("  - backend/ai/skills/debugging/proposals/*.md")
    print()
    
except Exception as e:
    print()
    print("="*80)
    print(f"❌ Error: {e}")
    print("="*80)
    import traceback
    traceback.print_exc()
    sys.exit(1)
