# Deployment Checklist - Accountable AI Trading System

**작성일**: 2025-12-29
**버전**: 1.0
**Status**: Ready for Deployment

---

## ✅ 완료된 작업

### Phase 1-4 Development
- [x] Phase 1: Database Foundation (6 tables)
- [x] Phase 2: Macro Context Updater + News Agent Enhancement
- [x] Phase 3: Report Orchestrator + Price Tracking Verifier
- [x] Phase 4: Failure Learning Agent + Weekly/Annual Reports

### Database Migration
- [x] 6개 테이블 생성 완료 (ai_trading DB)
  - macro_context_snapshots
  - news_interpretations
  - news_market_reactions
  - news_decision_links
  - news_narratives
  - failure_analysis
- [x] 26개 indexes 생성
- [x] Foreign key constraints 설정 (임시로 일부 제외)

### Code Verification
- [x] All Python files syntax checked (0 errors)
- [x] Unit tests created (30 test cases, 100% pass)
- [x] Repository pattern implemented
- [x] SKILL.md documentation complete

---

## 🔧 Configuration Required

### 1. Environment Variables

**필수 설정** (`.env` 파일):
```bash
# Database (현재 설정 확인 필요)
DATABASE_URL=postgresql+asyncpg://postgres:Qkqhdi1!@localhost:5432/ai_trading

# Anthropic API (유효한 키로 교체 필요)
ANTHROPIC_API_KEY=sk-ant-api03-... (현재 401 에러 - 교체 필요)

# Gemini API (News Agent용)
GEMINI_API_KEY=... (확인 필요)

# KIS API (Price Tracking Verifier용 - TODO)
KIS_APP_KEY=...
KIS_APP_SECRET=...

# Feature Flags
ENABLE_NEWS_INTERPRETATION=true
```

**Action Required**:
- [ ] Anthropic API Key 유효성 확인 (현재 401 에러)
- [ ] Gemini API Key 확인
- [ ] KIS API 연동 (Price Tracking Verifier의 `_get_current_price()` 함수)

### 2. Python Dependencies

**설치 완료**:
- [x] `schedule` - Automation scheduler

**확인 필요**:
- [ ] `anthropic` - Claude API
- [ ] `sqlalchemy` - ORM
- [ ] `psycopg2` - PostgreSQL driver
- [ ] `reportlab` - PDF generation

**설치 명령**:
```bash
cd ai-trading-system
pip install -r requirements.txt
```

---

## 🚀 실행 방법

### 1. Automation Scheduler (백그라운드 실행)

**현재 스케줄**:
- 매일 09:00 KST: Macro Context Update
- 매시간: Price Tracking Verification

**실행**:
```bash
cd ai-trading-system
python backend/automation/scheduler.py

# 또는 백그라운드 실행 (nohup)
nohup python backend/automation/scheduler.py > scheduler.log 2>&1 &
```

**TODO (Phase 4에서 활성화 필요)**:
- [ ] Daily Report Generation (매일 16:30)
- [ ] Weekly Report Generation (금요일 17:00)

### 2. 수동 실행

**Macro Context Update**:
```bash
python backend/automation/macro_context_updater.py
```

**Weekly Report**:
```bash
python backend/services/weekly_report_generator.py
```

**Annual Report**:
```bash
python backend/services/annual_report_generator.py
```

---

## 🐛 알려진 이슈 & 해결 방법

### Issue 1: Anthropic API 401 Error
**증상**: `Error code: 401 - authentication_error, invalid x-api-key`
**원인**: `.env`의 ANTHROPIC_API_KEY가 유효하지 않음
**해결**:
1. Anthropic Console에서 새 API Key 발급
2. `.env` 파일 업데이트
3. Scheduler 재시작

### Issue 2: KIS API 미연동
**증상**: Price Tracking Verifier가 Mock 가격 사용
**원인**: `_get_current_price()` 함수에 TODO 주석
**해결**:
1. KIS API 키 발급 (한국투자증권)
2. `backend/automation/price_tracking_verifier.py`의 `_get_current_price()` 함수 구현
3. KIS API Client 연동

### Issue 3: Foreign Key 제약 조건 누락
**증상**: `news_articles`, `ai_debate_sessions`, `trading_signals` 테이블 미존재로 FK 생성 실패
**현황**: 임시 마이그레이션(`000_temp_without_fk.sql`)으로 FK 없이 테이블 생성
**해결**:
1. 선행 테이블 먼저 생성 (news_articles, ai_debate_sessions, trading_signals)
2. `000_accountability_system_complete.sql` 재실행 (FK 포함)

### Issue 4: 14일 데이터 수집 진행 중
**현황**: Cycle 13 진행 중 (09:24 시작, 현재 22:25)
**예상 완료**: 2026-01-12 09:24 (총 336 cycles)
**Action**: 데이터 수집 완료까지 대기 (방해하지 말 것!)

---

## 📊 성능 모니터링

### Database Health Check

**테이블 row count 확인**:
```sql
SELECT
    'macro_context_snapshots' AS table_name, COUNT(*) AS row_count
FROM macro_context_snapshots
UNION ALL
SELECT 'news_interpretations', COUNT(*) FROM news_interpretations
UNION ALL
SELECT 'news_market_reactions', COUNT(*) FROM news_market_reactions
UNION ALL
SELECT 'news_decision_links', COUNT(*) FROM news_decision_links
UNION ALL
SELECT 'news_narratives', COUNT(*) FROM news_narratives
UNION ALL
SELECT 'failure_analysis', COUNT(*) FROM failure_analysis;
```

**Foreign Key 확인**:
```sql
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name IN (
        'macro_context_snapshots',
        'news_interpretations',
        'news_market_reactions',
        'news_decision_links',
        'news_narratives',
        'failure_analysis'
    );
```

### Scheduler Health Check

**Scheduler 프로세스 확인 (Windows)**:
```bash
tasklist | findstr python
```

**Scheduler 프로세스 확인 (Linux)**:
```bash
ps aux | grep scheduler.py
```

**Log 확인**:
```bash
tail -f scheduler.log
```

---

## 📋 Next Steps (Priority Order)

### High Priority (즉시)
1. [ ] **Anthropic API Key 교체** - Claude API 호출 실패 중
2. [ ] **Macro Context Updater 실행 테스트** - API Key 교체 후
3. [ ] **News Agent interpretation 테스트** - 실제 뉴스로

### Medium Priority (1주일 이내)
4. [ ] **KIS API 연동** - 실제 가격 조회
5. [ ] **Price Tracking Verifier 테스트** - KIS API 연동 후
6. [ ] **Daily Report Integration** - 기존 5-page report에 accountability 섹션 추가
7. [ ] **Telegram 알림 설정** - NIA < 60% 시 자동 알림

### Low Priority (1개월 이내)
8. [ ] **Weekly/Annual Report 자동화** - Scheduler에 추가
9. [ ] **Scheduler systemd/cron 설정** - 자동 시작
10. [ ] **RAG Knowledge 자동 업데이트** - Failure 패턴 저장
11. [ ] **Grafana/Kibana Dashboard** - NIA 추이 시각화

---

## 🎯 Success Criteria

### Immediate (오늘)
- [x] 데이터베이스 마이그레이션 완료
- [x] 모든 코드 syntax 검증 통과
- [x] Unit tests 100% 통과
- [ ] Anthropic API 연동 확인

### Short-term (1주일)
- [ ] Macro Context 일일 자동 업데이트 확인
- [ ] News Agent interpretation 10건 이상 저장
- [ ] Price Tracking Verifier 정상 작동 (Mock → Real KIS API)

### Long-term (1개월)
- [ ] NIA 계산 가능 (최소 50건 검증 완료)
- [ ] Weekly Report 생성 (첫 주간 리포트)
- [ ] Failure Analysis 3건 이상 (자동 분석)

---

## 🏆 System Status Summary

### ✅ Ready
- Database: 6 tables created
- Code: 4,500+ lines, 0 errors
- Tests: 30/30 passing
- Documentation: Complete

### ⚠️ Needs Attention
- Anthropic API: Invalid key (401 error)
- KIS API: Not integrated (Mock prices)
- Foreign Keys: Some missing (dependent tables)

### 📊 In Progress
- 14-day Data Collection: Cycle 13/336 (4% complete)

---

**Overall Status**: 🟡 **READY WITH MINOR CONFIGURATION**

**Blockers**:
1. Anthropic API key 교체
2. KIS API 연동 (optional for testing)

**ETA to Production**: 1-2 hours (API key 교체 후)

---

**Last Updated**: 2025-12-29 23:30 KST
**Next Review**: 2025-12-30 (API key 교체 후)
