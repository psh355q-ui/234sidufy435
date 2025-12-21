# 전략 확장 계획: 실시간 뉴스, 배당 엔진 및 SaaS (국문)

**날짜**: 2025-12-22
**상태**: Planning
**소스**: `ideas/251221 ideas/`

## 📋 개요 (Executive Summary)
사용자의 새로운 아이디어를 바탕으로 시스템을 확장하기 위한 3가지 핵심 영역을 정의합니다.
1. **실시간 뉴스 및 크롤링 방어 우회 (Real-time News & Anti-Scraping)**: 시장보다 빠르게 정보를 입수 (Finviz, SEC, Telegram)
2. **배당 최적화 엔진 (Dividend Optimization Engine)**: 사용자 성향별 맞춤형 배당 포트폴리오 자동 설계
3. **SaaS 수익화 (SaaS Commercialization)**: 웹 서비스화 및 결제 시스템 구축 (장기 목표)

---

## 🚀 Phase 20: 실시간 뉴스 및 속보 시그널 (Real-time News)
**목표**: 기존 RSS/API의 지연(Latency)을 극복하고, "기관급 속도"의 정보 수집 능력 확보.

### 1-1. Finviz "The Scout" 수집기
- **소스**: `finviz.com/news.ashx` (시장의 모든 헤드라인이 가장 빨리 올라오는 곳)
- **기술 스택**: `curl_cffi` (강력한 크롤링 방어 우회), `BeautifulSoup`
- **로직**:
  - `impersonate="chrome110"` 옵션을 사용해 실제 크롬 브라우저인 것처럼 TLS 지문(Fingerprint) 위장
  - 10~30초 단위로 초고속 스크래핑 수행
  - **Impact Score** 분석 (Gemini Flash) → 80점 이상 시 즉시 알림 발송

### 1-2. SEC "The Official Truth" 모니터링
- **소스**: SEC EDGAR RSS (8-K, 13-F 공시)
- **로직**:
  - 기업의 중대 사건(CEO 사임, 부도, 합병 등)이 담긴 **8-K 공시**를 즉시 감지
  - 뉴스 기사가 나오기 전, 팩트(Fact) 원문만으로 가장 빠르게 대응
  - SEC의 Fair Access 규정 준수 (User-Agent에 봇 정보 명시)

### 1-3. Telegram/Twitter "The Breaking Wire"
- **소스**: Telegram 주요 속보 채널 (예: Walter Bloomberg 등)
- **기술 스택**: `Telethon` (MTProto 프로토콜)
- **로직**:
  - 서버가 텔레그램 클라이언트로 직접 로그인하여 메시지 수신
  - Push 방식이므로 지연 시간 거의 없음 (Real-time)
  - 속보 채널 메시지를 파싱하여 뉴스 파이프라인에 즉시 주입

### 1-4. News Router (초고속 분류기)
- **역할**: 대량으로 들어오는 데이터(RSS + Finviz + SEC + Telegram)를 1차 필터링
- **프로세스**:
  - Gemini Flash (L1 필터) → 점수 < 50점은 무시 (DB 저장만)
  - 점수 >= 80점 (긴급 호재/악재) → **Deep Reasoning (Phase 14)** 즉시 호출하여 정밀 분석

---

## 💰 Phase 21: 배당 전략 엔진 (Dividend Strategy Engine)
**목표**: 사용자 성향(월배당, 연금형, 성장형 등)에 맞춰 최적의 배당 포트폴리오를 자동으로 설계해주는 시스템.

### 2-1. 데이터 및 설정 (Data & Config)
- **유니버스**: 미국 배당주 및 ETF 유니버스 파일 (`universe_seed.json`)
- **태그 시스템**: `monthly_payer`(월배당), `dividend_growth`(배당성장), `covered_call`(커버드콜), `reit`(리츠) 등 29개 태그 정의
- **배당 플랜**: 10가지 핵심 테마 정의 (`max_monthly_income`, `silver_pension` 등)

### 2-2. 백엔드 엔진 (Backend Engine)
- **데이터 로더(Loader)**: `yfinance`를 통해 배당률(Yield), 배당성향(Payout Ratio), 성장률(Growth) 데이터 수집
- **최적화기(Optimizer)**: 
  - 사용자가 선택한 **Plan(테마)** + **Tier(방어/균형/공격)**에 따라 종목 비중 자동 계산
  - 제약 조건 적용 (ETF 최소 비중, 단일 종목 최대 비중 10% 제한 등)
- **분석기(Analytics)**:
  - 에상 월 배당금 시뮬레이션
  - 포트폴리오 낙폭(MDD) 및 리스크 분석

### 2-3. 프론트엔드 UI (Frontend)
- **배당 대시보드**: 현재 내 포트폴리오의 배당 현황 시각화
- **플랜 선택기(Plan Selector)**: 카드 형태의 직관적인 테마 선택 UI
- **시뮬레이션**: "1억 투자하면 월 얼마 받나요?" 즉시 계산기

---

## 💼 Phase 22: SaaS 수익화 (SaaS Commercialization) - 장기 목표
**목표**: 구축된 AI 트레이딩 & 배당 시스템을 일반 사용자 대상의 B2C 웹 서비스로 전환.

### 3-1. 인프라 및 배포
- **스택**: Next.js (프론트엔드), Supabase (인증/DB), Vercel/Cloudflare (배포)
- **스토리지**: Cloudflare R2 (이미지 및 데이터 영구 보관, 비용 절감)

### 3-2. 사용자 기능
- **소셜 로그인**: 구글, 카카오 등 간편 로그인
- **크레딧 시스템**: AI 분석 요청 1회당 크레딧 차감 방식
- **마이 갤러리**: 사용자가 요청한 분석 리포트 보관함

### 3-3. 관리자 및 결제
- **관리자 페이지**: 회원 관리, 프롬프트 관리, 매출 통계 확인
- **결제 시스템**: 토스 페이먼츠 연동 (크레딧 충전, 구독 결제)

---

## 📊 구현 로드맵 (Implementation Roadmap)

### 1주차: Phase 18 (뉴스 신뢰도) & Phase 20 (실시간 뉴스)
- [ ] 4-Signal Consensus (뉴스 신뢰도 검증) 구현
- [ ] `curl_cffi` 기반 Finviz 수집기 구현 (안티 스크래핑 우회)
- [ ] SEC Monitor 8-K 공시 감지 구현

### 2주차: Phase 21 (배당 엔진) - 백엔드
- [ ] 배당 설정(Config) 및 유니버스(Universe) 데이터 구축
- [ ] 배당 데이터 로더 (`yfinance`) 구현
- [ ] 포트폴리오 최적화(Optimizer) 로직 구현

### 3주차: Phase 21 (배당 엔진) - 프론트엔드
- [ ] 배당 대시보드 및 플랜 선택 UI 개발
- [ ] 배당 시뮬레이터 연동

### Future: Phase 22 (SaaS)
- 별도의 프로젝트(`ai-trading-saas`)로 분리하여 진행하는 것을 권장합니다.
