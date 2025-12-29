# Development Plans - Index

**작성일**: 2025-12-29

이 폴더는 AI Trading System의 주요 개발 계획 문서들을 포함합니다.

---

## 📋 문서 목록

### 1. [251229_Report_Management_System.md](./251229_Report_Management_System.md)
**리포트 관리 시스템 설계**

- 6가지 리포트 타입 (Daily/Weekly/Monthly/Quarterly/Half-Yearly/Annual)
- 폴더 구조 및 파일명 규칙
- 리포트별 내용 및 생성 시점
- 자동화 계획

---

### 2. [251229_AI_Strategist_Upgrade.md](./251229_AI_Strategist_Upgrade.md)
**AI 전략가 업그레이드 계획**

- 뉴스 기반 시장 평가 시스템 (6개 데이터 레이어)
- Global Strategist Agent 설계
- 리포트 타입별 적용 방안
- Q1-Q3 답변 (뉴스 정확도, 가중치, 시각화)

**핵심 개념**:
- 뉴스 → 해석 → 판단 → 결과 체인
- News Interpretation Accuracy (NIA)
- Alpha Impact 측정

---

### 3. [251229_Page2_Page5_Implementation.md](./251229_Page2_Page5_Implementation.md)
**Page 2 & Page 5 구현 계획**

- Page 2: AI Decision Logic Transparency
  - Decision Flow
  - 실행/거부 트레이드
  - War Room 요약

- Page 5: Tomorrow Risk Playbook
  - Top 3 Risks
  - AI Stance Indicator
  - Scenario Matrix
  - Action Items

---

### 4. [251229_Final_Execution_Roadmap.md](./251229_Final_Execution_Roadmap.md) ⭐
**최종 실행 로드맵 (통합본)**

**검증 완료**: ChatGPT + Gemini × 2 리뷰 통합

**4단계 실행 계획** (총 6주):
1. **Phase 1**: 데이터 기반 구축 (2주)
   - 6개 테이블 스키마
   - Alpha Impact 분리
   - 방향/타이밍 검증

2. **Phase 2**: Global Strategist Agent (2주)
   - Stance Declaration
   - Shadow Penalty
   - Dynamic Persona

3. **Phase 3**: 실패 학습 시스템 (1주)
   - Real-time Post-Mortem
   - RAG 통합
   - Narrative Revision

4. **Phase 4**: 리포트 통합 (1주)
   - Daily: Market Regime
   - Weekly: AI 진화 로그
   - Annual: Accountability Report

**핵심 철학**:
> "우리는 맞추는 AI를 만들지 않는다.  
>  우리는 책임지는 판단 주체를 만든다."

---

## 🎯 현재 상태

### ✅ 완료
- Daily Report (5 pages)
- 한글 폰트 시스템
- 언어 템플릿 (63개 동적 문장)
- 리포트 폴더 구조

### 🔄 진행 중
- 실제 데이터 파이프라인 연결

### 📅 Next Steps
- Phase 1 착수 (데이터베이스 스키마)

---

## 📊 문서 관계도

```
Final_Execution_Roadmap (최종 통합)
    ↓
    ├─ Report_Management_System (리포트 타입 설계)
    ├─ AI_Strategist_Upgrade (뉴스 평가 시스템)
    └─ Page2_Page5_Implementation (페이지 구현)
```

---

**최종 업데이트**: 2025-12-29
**다음 검토일**: Phase 1 완료 후
