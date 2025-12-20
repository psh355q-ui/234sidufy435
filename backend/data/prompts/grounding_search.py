"""
Grounding Search Prompt Template
=================================

PURPOSE: Phase 1 of Grounding pipeline - Real web search
SYNC WITH: RSS news crawler schema
LAST UPDATED: 2024-12-21
CHANGE TRIGGER: RSS news schema 변경 시 함께 수정 필요

이 프롬프트는 Google 웹 검색을 통해 실제 뉴스를 수집합니다.
RSS crawler와 동일한 정보를 수집하도록 설계되었습니다.
"""

GROUNDING_SEARCH_PROMPT = """
Search the web for recent news and information about {ticker} stock.

Focus areas:
1. Company Announcements
   - Earnings reports and financial results
   - Revenue and profit guidance
   - Product launches or updates
   - Strategic partnerships or acquisitions

2. Market Events
   - Stock price movements and reasons
   - Analyst ratings and price target changes
   - Regulatory news or legal issues
   - Industry trends affecting {ticker}

3. Financial Data
   - Quarterly/annual results
   - Key metrics (revenue, EPS, margins)
   - Cash flow and balance sheet highlights
   - Comparisons to competitors

Time Range: Past 24-48 hours (prioritize most recent)

For each relevant article, provide:
- Full article title
- Publisher/Source name
- Publication date and time
- Comprehensive summary (3-5 sentences)
- Key facts, figures, and quotes
- Impact on stock price (if mentioned)

Prioritize:
- Official sources (company press releases, SEC filings)
- Major financial news outlets (Reuters, Bloomberg, WSJ)
- Analyst reports from major firms
- Market-moving news

Format as detailed numbered list with all information.
"""

# 유지보수 주석:
# 1. RSS crawler와 동일한 카테고리 수집 (earnings, product, regulation 등)
# 2. 필드 추가 시 analysis_extraction.py도 함께 업데이트
# 3. Time range는 RSS crawler 설정과 동기화 (현재 24시간)
