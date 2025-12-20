"""
Analysis Extraction Prompt Template
====================================

PURPOSE: Phase 2 of Grounding pipeline - Auto-extraction of structured data
SYNC WITH: backend/data/news_analyzer.py (RSS analysis schema)
LAST UPDATED: 2024-12-21
CHANGE TRIGGER: RSS analysis schema 변경 시 함께 수정 필요

이 프롬프트는 Grounding 검색 결과를 구조화된 데이터로 변환합니다.
자동태깅, 임베딩, RAG에 최적화된 포맷을 생성합니다.
"""

ANALYSIS_EXTRACTION_PROMPT = """
Analyze the following news search results and extract structured data for each article.

Search Results:
{grounding_text}

Extract for EACH article found in the search results:

1. BASIC INFO (RSS 호환 필수)
   - title: string (article headline)
   - url: string (direct article URL - prefer search result URL)
   - source: string (publisher name: Reuters, Bloomberg, etc.)
   - published_date: string (ISO 8601 format: 2024-12-20T10:30:00Z)
   - summary: string (2-3 sentence comprehensive summary)

2. TICKER EXTRACTION (자동태깅용)
   - tickers: array of strings (all mentioned stock symbols)
   - primary_ticker: string (main focus ticker)
   - related_tickers: array of strings (related/mentioned tickers)

3. SENTIMENT ANALYSIS (RSS 동기화 - news_analyzer.py 참조)
   - sentiment: "positive" | "negative" | "neutral"
   - sentiment_score: number (-1.0 to 1.0, precise decimal)
   - confidence: number (0.0 to 1.0, how confident in sentiment)

4. MARKET IMPACT (RSS 동기화)
   - market_impact: "bullish" | "bearish" | "neutral"
   - urgency: "low" | "medium" | "high" | "critical"
   - actionable: boolean (true if contains tradeable insight)

5. AUTO-TAGGING (태깅 시스템용)
   - categories: array of strings from: 
     ["earnings", "revenue", "product", "merger", "acquisition", 
      "partnership", "regulation", "lawsuit", "leadership", 
      "market_share", "competition", "innovation", "guidance"]
   - keywords: array of 5-10 important terms
   - entities: array of objects with:
     - type: "company" | "person" | "location" | "product"
     - name: string

6. EMBEDDING METADATA (임베딩 생성 최적화용)
   - content_for_embedding: string (title + summary + key facts, optimized for semantic search)
   - semantic_tags: array of 3-5 high-level concepts
   - context: string (broader market/industry context in 1 sentence)

7. RAG METADATA (검색 및 컨텍스트 최적화용)
   - key_facts: array of strings (5-7 factual statements)
   - numerical_data: array of objects with:
     - metric: string (e.g., "revenue", "EPS", "price_target")
     - value: number
     - unit: string (e.g., "USD", "percent", "shares")
   - temporal_context: string (time relevance: Q3 2024, next earnings, etc.)
   - relevance_score: number (0.0 to 1.0, importance for trading decisions)

Return ONLY a valid JSON array of articles.
Do not include markdown code blocks, explanations, or any text outside the JSON.

Example format:
[
  {{
    "title": "NVIDIA Reports Record Q3 Revenue",
    "url": "https://...",
    "source": "Reuters",
    "published_date": "2024-12-20T14:30:00Z",
    "summary": "NVIDIA reported record Q3 revenue...",
    "tickers": ["NVDA"],
    "primary_ticker": "NVDA",
    "related_tickers": [],
    "sentiment": "positive",
    "sentiment_score": 0.85,
    "confidence": 0.92,
    "market_impact": "bullish",
    "urgency": "high",
    "actionable": true,
    "categories": ["earnings", "revenue"],
    "keywords": ["Q3", "revenue", "record", "AI chips"],
    "entities": [
      {{"type": "company", "name": "NVIDIA"}},
      {{"type": "person", "name": "Jensen Huang"}}
    ],
    "content_for_embedding": "NVIDIA Q3 earnings revenue record AI chips...",
    "semantic_tags": ["earnings_beat", "AI_growth", "semiconductor_leader"],
    "context": "NVIDIA continues AI chip market dominance amid strong demand",
    "key_facts": [
      "Q3 revenue increased 34% year-over-year",
      "Data center segment grew 55%"
    ],
    "numerical_data": [
      {{"metric": "revenue", "value": 18.12, "unit": "billion USD"}},
      {{"metric": "EPS", "value": 4.02, "unit": "USD"}}
    ],
    "temporal_context": "Q3 2024 earnings report",
    "relevance_score": 0.95
  }}
]
"""

# 유지보수 주석:
# =====================================================================
# CRITICAL: RSS news_analyzer.py와 100% 호환 유지!
# =====================================================================
#
# 동기화 필수 파일:
# - backend/data/news_analyzer.py (analyze_article 메서드)
#
# 필드 변경 체크리스트:
# 1. sentiment_score 범위 변경 시 → news_analyzer.py 동기화
# 2. categories 추가 시 → news_analyzer.py의 카테고리 리스트 업데이트
# 3. numerical_data 구조 변경 시 → RAG 시스템 검토
# 4. embedding 필드 변경 시 → 임베딩 모델 호환성 확인
#
# 변경 이력:
# 2024-12-21: Initial version (RSS schema v1.0 sync)
# 향후 변경사항은 이 주석에 기록할 것
