"""
War Room Debate Visualizer

토론 과정 분석 및 시각화 데이터 생성:
- Agent별 투표 분포
- 의견 충돌 패턴 분석
- Confidence 통계
- 토론 타임라인

Author: AI Trading System
Date: 2025-12-28
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class DebateVisualizer:
    """
    War Room 토론 분석 및 시각화 클래스
    
    주요 기능:
    - 토론 세션 분석
    - Agent 투표 패턴 분석
    - 의견 충돌 감지
    - 토론 타임라인 생성
    """
    
    def __init__(self, db_session=None):
        """
        Args:
            db_session: Database session (optional, for production use)
        """
        self.db = db_session
        logger.info("DebateVisualizer initialized")
    
    async def analyze_debate_session(self, session_data: Dict) -> Dict[str, Any]:
        """
        War Room 토론 세션 분석
        
        Args:
            session_data: War Room 세션 데이터
            {
                "session_id": str,
                "ticker": str,
                "timestamp": datetime,
                "agent_votes": {
                    "trader": {"action": "BUY", "confidence": 0.85, "reasoning": "..."},
                    "news": {"action": "BUY", "confidence":  0.75, ...},
                    "risk": {"action": "HOLD", "confidence": 0.60, ...},
                    ...
                },
                "final_decision": {
                    "action": "BUY",
                    "confidence": 0.78,
                    "vote_weights": {...}
                }
            }
        
        Returns:
            분석 결과 딕셔너리
        """
        try:
            session_id = session_data.get("session_id", "unknown")
            ticker = session_data.get("ticker", "")
            agent_votes = session_data.get("agent_votes", {})
            final_decision = session_data.get("final_decision", {})
            
            # 1. 투표 분포 계산
            vote_distribution = self._calculate_vote_distribution(agent_votes, final_decision.get("vote_weights", {}))
            
            # 2. 의견 충돌 분석
            conflict_analysis = self._analyze_conflicts(agent_votes)
            
            # 3. Confidence 통계
            confidence_stats = self._calculate_confidence_stats(agent_votes)
            
            # 4. Agent 기여도 분석
            agent_contributions = self._analyze_agent_contributions(agent_votes, final_decision)
            
            result = {
                "session_id": session_id,
                "timestamp": session_data.get("timestamp", datetime.now()),
                "ticker": ticker,
                "final_decision": final_decision,
                "agent_votes": self._format_agent_votes(agent_votes),
                "vote_distribution": vote_distribution,
                "conflict_analysis": conflict_analysis,
                "confidence_stats": confidence_stats,
                "agent_contributions": agent_contributions
            }
            
            logger.info(f"Analyzed debate session {session_id} for {ticker}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing debate session: {e}")
            raise
    
    def _calculate_vote_distribution(self, agent_votes: Dict, vote_weights: Dict) -> Dict:
        """
        투표 분포 계산 (가중치 적용)
        
        Returns:
            {
                "BUY": {"count": 4, "unweighted_pct": 0.50, "weighted_pct": 0.55},
                "SELL": {...},
                "HOLD": {...}
            }
        """
        action_counts = Counter()
        weighted_scores = defaultdict(float)
        
        total_agents = len(agent_votes)
        
        for agent_name, vote_data in agent_votes.items():
            action = vote_data.get("action", "HOLD")
            weight = vote_weights.get(agent_name, 1.0 / total_agents if total_agents > 0 else 0.125)
            
            action_counts[action] += 1
            weighted_scores[action] += weight
        
        # 분포 계산
        distribution = {}
        for action in ["BUY", "SELL", "HOLD"]:
            count = action_counts.get(action, 0)
            unweighted_pct = count / total_agents if total_agents > 0 else 0
            weighted_pct = weighted_scores.get(action, 0)
            
            distribution[action] = {
                "count": count,
                "unweighted_pct": round(unweighted_pct, 3),
                "weighted_pct": round(weighted_pct, 3)
            }
        
        return distribution
    
    def _analyze_conflicts(self, agent_votes: Dict) -> Dict:
        """
        의견 충돌 분석
        
        Returns:
            {
                "disagreement_score": 0.0-1.0,
                "conflicting_pairs": [(agent1, agent2), ...],
                "consensus_level": "STRONG|MODERATE|WEAK",
                "majority_action": "BUY|SELL|HOLD",
                "unanimous": bool
            }
        """
        if not agent_votes:
            return {
                "disagreement_score": 0.0,
                "conflicting_pairs": [],
                "consensus_level": "NONE",
                "majority_action": None,
                "unanimous": False
            }
        
        # 1. 다수 의견 찾기
        action_counts = Counter(vote["action"] for vote in agent_votes.values())
        majority_action, majority_count = action_counts.most_common(1)[0]
        total_agents = len(agent_votes)
        
        # 2. Disagreement Score 계산
        disagreement_score = 1.0 - (majority_count / total_agents)
        
        # 3. 충돌 쌍 찾기 (BUY vs SELL)
        conflicting_pairs = []
        buy_agents = [name for name, vote in agent_votes.items() if vote["action"] == "BUY"]
        sell_agents = [name for name, vote in agent_votes.items() if vote["action"] == "SELL"]
        
        for buy_agent in buy_agents:
            for sell_agent in sell_agents:
                conflicting_pairs.append((buy_agent, sell_agent))
        
        # 4. Consensus Level 결정
        if majority_count == total_agents:
            consensus_level = "STRONG"  # 만장일치
            unanimous = True
        elif majority_count >= total_agents * 0.75:
            consensus_level = "STRONG"  # 75% 이상
            unanimous = False
        elif majority_count >= total_agents * 0.6:
            consensus_level = "MODERATE"  # 60% 이상
            unanimous = False
        else:
            consensus_level = "WEAK"  # 60% 미만
            unanimous = False
        
        return {
            "disagreement_score": round(disagreement_score, 3),
            "conflicting_pairs": conflicting_pairs[:5],  # 최대 5개만
            "consensus_level": consensus_level,
            "majority_action": majority_action,
            "unanimous": unanimous
        }
    
    def _calculate_confidence_stats(self, agent_votes: Dict) -> Dict:
        """
        Confidence 통계 계산
        
        Returns:
            {
                "avg_confidence": 0.75,
                "min_confidence": 0.60,
                "max_confidence": 0.90,
                "std_dev": 0.10,
                "confidence_spread": 0.30
            }
        """
        if not agent_votes:
            return {
                "avg_confidence": 0.0,
                "min_confidence": 0.0,
                "max_confidence": 0.0,
                "std_dev": 0.0,
                "confidence_spread": 0.0
            }
        
        confidences = [vote.get("confidence", 0.5) for vote in agent_votes.values()]
        
        avg_confidence = sum(confidences) / len(confidences)
        min_confidence = min(confidences)
        max_confidence = max(confidences)
        
        # 표준편차 계산
        variance = sum((c - avg_confidence) ** 2 for c in confidences) / len(confidences)
        std_dev = variance ** 0.5
        
        confidence_spread = max_confidence - min_confidence
        
        return {
            "avg_confidence": round(avg_confidence, 3),
            "min_confidence": round(min_confidence, 3),
            "max_confidence": round(max_confidence, 3),
            "std_dev": round(std_dev, 3),
            "confidence_spread": round(confidence_spread, 3)
        }
    
    def _analyze_agent_contributions(self, agent_votes: Dict, final_decision: Dict) -> Dict:
        """
        Agent별 기여도 분석
        
        Returns:
            {
                "trader": {
                    "vote": "BUY",
                    "confidence": 0.85,
                    "weight": 0.15,
                    "contribution_score": 0.1275,  # confidence * weight
                    "aligned_with_final": true
                },
                ...
            }
        """
        final_action = final_decision.get("action", "HOLD")
        vote_weights = final_decision.get("vote_weights", {})
        
        contributions = {}
        
        for agent_name, vote_data in agent_votes.items():
            action = vote_data.get("action", "HOLD")
            confidence = vote_data.get("confidence", 0.5)
            weight = vote_weights.get(agent_name, 0.125)
            
            contribution_score = confidence * weight
            aligned = (action == final_action)
            
            contributions[agent_name] = {
                "vote": action,
                "confidence": round(confidence, 3),
                "weight": round(weight, 3),
                "contribution_score": round(contribution_score, 4),
                "aligned_with_final": aligned
            }
        
        return contributions
    
    def _format_agent_votes(self, agent_votes: Dict) -> Dict:
        """Agent 투표 데이터 포맷팅"""
        formatted = {}
        
        for agent_name, vote_data in agent_votes.items():
            formatted[agent_name] = {
                "action": vote_data.get("action", "HOLD"),
                "confidence": round(vote_data.get("confidence", 0.5), 3),
                "reasoning_preview": vote_data.get("reasoning", "")[:100] + "..." if len(vote_data.get("reasoning", "")) > 100 else vote_data.get("reasoning", "")
            }
        
        return formatted
    
    async def get_debate_timeline(self, ticker: str, sessions: List[Dict], days: int = 30) -> List[Dict]:
        """
        티커의 최근 N일 토론 타임라인 생성
        
        Args:
            ticker: 티커 심볼
            sessions: 세션 데이터 리스트
            days: 조회 기간 (일)
        
        Returns:
            일별 요약 리스트
        """
        if not sessions:
            return []
        
        # 날짜별 그룹화
        daily_sessions = defaultdict(list)
        
        for session in sessions:
            session_date = session.get("timestamp", datetime.now()).date()
            daily_sessions[session_date].append(session)
        
        # 타임라인 생성
        timeline = []
        
        for date in sorted(daily_sessions.keys(), reverse=True)[:days]:
            day_sessions = daily_sessions[date]
            
            # 일일 통계 계산
            actions = [s.get("final_decision", {}).get("action", "HOLD") for s in day_sessions]
            action_counts = Counter(actions)
            dominant_action = action_counts.most_common(1)[0][0] if action_counts else "HOLD"
            
            avg_consensus = sum(
                1.0 - self._analyze_conflicts(s.get("agent_votes", {})).get("disagreement_score", 0.5)
                for s in day_sessions
            ) / len(day_sessions) if day_sessions else 0.5
            
            timeline.append({
                "date": date.isoformat(),
                "session_count": len(day_sessions),
                "avg_consensus": round(avg_consensus, 3),
                "dominant_action": dominant_action,
                "action_distribution": dict(action_counts)
            })
        
        return timeline
    
    async def get_agent_voting_patterns(self, agent_name: str, sessions: List[Dict], days: int = 30) -> Dict:
        """
        특정 Agent의 투표 패턴 분석
        
        Args:
            agent_name: Agent 이름
            sessions: 세션 데이터 리스트
            days: 조회 기간
        
        Returns:
            Agent 투표 패턴 통계
        """
        if not sessions:
            return self._empty_pattern_result(agent_name)
        
        # Agent 투표 수집
        agent_votes_list = []
        final_actions = []
        
        for session in sessions:
            agent_votes = session.get("agent_votes", {})
            if agent_name in agent_votes:
                vote = agent_votes[agent_name]
                agent_votes_list.append(vote)
                final_actions.append(session.get("final_decision", {}).get("action", "HOLD"))
        
        if not agent_votes_list:
            return self._empty_pattern_result(agent_name)
        
        # 통계 계산
        total_votes = len(agent_votes_list)
        action_counts = Counter(vote["action"] for vote in agent_votes_list)
        
        # Action별 분포
        action_distribution = {}
        for action in ["BUY", "SELL", "HOLD"]:
            count = action_counts.get(action, 0)
            pct = count / total_votes if total_votes > 0 else 0
            action_distribution[action] = {
                "count": count,
                "pct": round(pct, 3)
            }
        
        # 평균 confidence
        avg_confidence = sum(vote.get("confidence", 0.5) for vote in agent_votes_list) / total_votes
        
        # Action별 평균 confidence
        confidence_by_action = {}
        for action in ["BUY", "SELL", "HOLD"]:
            action_votes = [vote["confidence"] for vote in agent_votes_list if vote["action"] == action]
            avg = sum(action_votes) / len(action_votes) if action_votes else 0
            confidence_by_action[action] = round(avg, 3)
        
        # 최종 결정 일치율
        agreement_count = sum(
            1 for vote, final in zip(agent_votes_list, final_actions)
            if vote["action"] == final
        )
        agreement_rate = agreement_count / total_votes if total_votes > 0 else 0
        
        # 소수 의견(Contrarian) 비율 계산 (추후 구현 - 다수 의견과 비교 필요)
        contrarian_rate = 1.0 - agreement_rate
        
        return {
            "agent": agent_name,
            "total_votes": total_votes,
            "action_distribution": action_distribution,
            "avg_confidence": round(avg_confidence, 3),
            "agreement_rate": round(agreement_rate, 3),
            "contrarian_rate": round(contrarian_rate, 3),
            "confidence_by_action": confidence_by_action
        }
    
    def _empty_pattern_result(self, agent_name: str) -> Dict:
        """빈 패턴 결과 반환"""
        return {
            "agent": agent_name,
            "total_votes": 0,
            "action_distribution": {
                "BUY": {"count": 0, "pct": 0.0},
                "SELL": {"count": 0, "pct": 0.0},
                "HOLD": {"count": 0, "pct": 0.0}
            },
            "avg_confidence": 0.0,
            "agreement_rate": 0.0,
            "contrarian_rate": 0.0,
            "confidence_by_action": {
                "BUY": 0.0,
                "SELL": 0.0,
                "HOLD": 0.0
            }
        }
