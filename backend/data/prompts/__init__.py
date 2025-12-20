"""
Prompts Package
===============

Gemini Grounding 및 분석 추출을 위한 프롬프트 템플릿 모음

Modules:
    - grounding_search: Phase 1 웹 검색 프롬프트
    - analysis_extraction: Phase 2 구조화 데이터 추출 프롬프트
"""

from .grounding_search import GROUNDING_SEARCH_PROMPT
from .analysis_extraction import ANALYSIS_EXTRACTION_PROMPT

__all__ = [
    'GROUNDING_SEARCH_PROMPT',
    'ANALYSIS_EXTRACTION_PROMPT',
]
