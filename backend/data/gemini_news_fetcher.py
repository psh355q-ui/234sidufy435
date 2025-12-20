"""
Gemini 3.0 Pro News Fetcher Prototype
Real-time news discovery and analysis using Gemini's grounding capabilities
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import google.generativeai as genai

class GeminiNewsFetcher:
    """
    Prototype: Use Gemini to fetch and analyze real-time news
    
    Features:
    - Real-time web search via grounding
    - Automatic ticker extraction
    - Sentiment analysis
    - Market impact assessment
    """
    
    def __init__(self):
        # Load environment first
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Load model from environment (consistent with news_analyzer.py)
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        
        # Add 'models/' prefix if not present
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"
        
        self.model = genai.GenerativeModel(model_name)
        print(f"✅ GeminiNewsFetcher initialized with model: {model_name}")
    
    def fetch_news(
        self, 
        query: str = "latest stock market news", 
        max_articles: int = 10,
        use_grounding: bool = True
    ) -> List[Dict[str, Any]]:
        """
        DEPRECATED: Use fetch_news_v2 for new 2-phase pipeline
        
        Kept for backward compatibility
        """
        return self.fetch_news_v2(query=query, max_articles=max_articles)
    
    def fetch_news_v2(
        self,
        query: str = "latest stock market news",
        max_articles: int = 10
    ) -> List[Dict[str, Any]]:
        """
        2-Phase Grounding Pipeline (공식 문서 기반)
        
        Phase 1: Grounding Search - 실제 웹 검색 (text response)
        Phase 2: Auto-Extraction - 구조화된 데이터 추출 (JSON)
        
        Returns:
            List of structured articles with grounding validation
        """
        from .prompts import GROUNDING_SEARCH_PROMPT, ANALYSIS_EXTRACTION_PROMPT
        
        try:
            # ================================================================
            # PHASE 1: GROUNDING SEARCH (실제 웹 검색)
            # ================================================================
            print(f"\n🔍 Phase 1: Grounding web search for '{query}'")
            
            grounding_prompt = GROUNDING_SEARCH_PROMPT.format(ticker=query)
            
            # 공식 문서 레거시 방식 (google.generativeai SDK 호환)
            # REST API 형식으로 전달
            response_grounding = self.model.generate_content(
                grounding_prompt,
                tools=[{
                    "google_search_retrieval": {
                        "dynamic_retrieval_config": {
                            "mode": "MODE_DYNAMIC",
                            "dynamic_threshold": 0.3  # 30% 신뢰도 이상일 때 검색
                        }
                    }
                }],
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=3000,
                )
            )
            
            grounding_text = response_grounding.text
            print(f"✅ Grounding completed: {len(grounding_text)} chars")
            
            # 실제 URL 추출 (Grounding metadata)
            real_urls = []
            if hasattr(response_grounding, 'candidates') and response_grounding.candidates:
                for candidate in response_grounding.candidates:
                    if hasattr(candidate, 'grounding_metadata'):
                        metadata = candidate.grounding_metadata
                        if hasattr(metadata, 'grounding_chunks'):
                            for chunk in metadata.grounding_chunks:
                                if hasattr(chunk, 'web'):
                                    real_urls.append({
                                        'uri': chunk.web.uri,
                                        'title': chunk.web.title if hasattr(chunk.web, 'title') else None
                                    })
            
            print(f"📊 Found {len(real_urls)} grounding sources (real URLs)")
            
            # ================================================================
            # PHASE 2: AUTO-EXTRACTION (JSON 구조화)
            # ================================================================
            print(f"\n🔄 Phase 2: Auto-extracting structured data")
            
            extraction_prompt = ANALYSIS_EXTRACTION_PROMPT.format(
                grounding_text=grounding_text
            )
            
            response_extraction = self.model.generate_content(
                extraction_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=4000,
                    response_mime_type="application/json",  # JSON mode (Grounding OFF)
                )
            )
            
            # JSON 파싱
            articles = json.loads(response_extraction.text)
            print(f"✅ Extracted {len(articles)} structured articles")
            
            # ================================================================
            # URL 병합 및 메타데이터 추가
            # ================================================================
            for i, article in enumerate(articles):
                # Grounding URL 병합 (진짜 URL!)
                if i < len(real_urls):
                    grounding_url = real_urls[i]['uri']
                    llm_url = article.get('url', '')
                    
                    # URL 검증
                    if llm_url and llm_url != grounding_url:
                        article['url_mismatch_warning'] = True
                        print(f"⚠️ URL mismatch detected for article {i+1}")
                    
                    article['url'] = grounding_url  # Grounding URL 우선!
                    article['grounding_source'] = real_urls[i]
                    article['grounding_validated'] = True
                
                # 메타데이터 추가
                article['fetched_at'] = datetime.utcnow().isoformat()
                article['source_type'] = 'gemini_grounding_v2'
                article['model_version'] = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
                article['pipeline_version'] = '2.0'
            
            return articles
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error in Phase 2: {e}")
            print(f"Response preview: {response_extraction.text[:500]}")
            return []
        except Exception as e:
            print(f"❌ Pipeline error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def fetch_ticker_news(
        self, 
        ticker: str, 
        max_articles: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fetch news for a specific ticker using 2-phase pipeline
        """
        query = f"latest news about {ticker} stock"
        return self.fetch_news_v2(query=query, max_articles=max_articles)
    
    def fetch_breaking_news(self) -> List[Dict[str, Any]]:
        """
        Fetch breaking market news
        """
        query = "breaking stock market news today"
        return self.fetch_news(query, max_articles=5)


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    print("🔬 Gemini News Fetcher Prototype\n")
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test 1: General market news
    print("📰 Test 1: General Market News")
    fetcher = GeminiNewsFetcher()
    articles = fetcher.fetch_news("tech stock news today", max_articles=3)
    
    print(f"Found {len(articles)} articles:\n")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article.get('title', 'No title')}")
        print(f"   Source: {article.get('source', 'Unknown')}")
        print(f"   Tickers: {article.get('tickers', [])}")
        print(f"   Sentiment: {article.get('sentiment', 'N/A')}")
        print(f"   Actionable: {article.get('actionable', False)}")
        print()
    
    # Test 2: Specific ticker
    print("\n📊 Test 2: Ticker-Specific News (NVDA)")
    nvda_news = fetcher.fetch_ticker_news("NVDA", max_articles=2)
    
    print(f"Found {len(nvda_news)} NVDA articles:\n")
    for article in nvda_news:
        print(f"- {article.get('title', 'No title')}")
        print(f"  Impact: {article.get('market_impact', 'N/A')}")
        print()
    
    # Results summary
    print("\n" + "="*60)
    print("📊 Summary:")
    print(f"Total articles fetched: {len(articles) + len(nvda_news)}")
    print(f"Average tickers per article: {sum(len(a.get('tickers', [])) for a in articles + nvda_news) / (len(articles) + len(nvda_news)) if articles + nvda_news else 0:.1f}")
    print(f"Actionable articles: {sum(1 for a in articles + nvda_news if a.get('actionable'))}")
