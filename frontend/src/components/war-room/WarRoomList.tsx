/**
 * War Room List - 여러 티커의 토론 목록
 */

import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { DebateSession } from '../../data/mockDebateSessions';
import { warRoomApi } from '../../services/warRoomApi';
import WarRoomCard from './WarRoomCard';
import { TickerAutocompleteInput } from '../common/TickerAutocompleteInput';
import './WarRoomList.css';

type StatusFilter = 'all' | 'active' | 'completed' | 'pending';

const WarRoomList: React.FC = () => {
    // Fetch real War Room sessions from API
    const { data: apiSessions, isLoading, error } = useQuery({
        queryKey: ['war-room-sessions'],
        queryFn: () => warRoomApi.getSessions({ limit: 20 }),
        refetchInterval: 10000, // Refetch every 10 seconds for real-time updates
    });

    // Transform API response to match DebateSession interface
    const sessions: DebateSession[] = useMemo(() => {
        if (!apiSessions) return [];

        return apiSessions.map(session => ({
            id: session.id.toString(),
            ticker: session.ticker,
            status: session.signal_generated ? 'completed' : 'active',
            startedAt: new Date(session.created_at),
            completedAt: session.signal_generated ? new Date(session.created_at) : undefined,
            messages: [], // Messages loaded separately when card is expanded
            consensus: session.consensus_confidence,
            finalDecision: {
                action: session.consensus_action,
                confidence: session.consensus_confidence
            },
            constitutionalResult: {
                isValid: session.constitutional_valid,
                violations: session.constitutional_valid ? [] : ['제3조 위반: 인간 승인이 필요합니다'],
                violatedArticles: session.constitutional_valid ? [] : ['제3조: 인간 최종 결정권']
            }
        }));
    }, [apiSessions]);
    const [searchTicker, setSearchTicker] = useState('');
    const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
    const [expandedCardId, setExpandedCardId] = useState<string | null>(null);

    // 필터링된 세션
    const filteredSessions = useMemo(() => {
        return sessions.filter(session => {
            // 티커 검색
            const matchesTicker = searchTicker === '' ||
                session.ticker.toUpperCase().includes(searchTicker.toUpperCase());

            // 상태 필터
            const matchesStatus = statusFilter === 'all' ||
                session.status === statusFilter;

            return matchesTicker && matchesStatus;
        });
    }, [sessions, searchTicker, statusFilter]);

    // 통계
    const stats = useMemo(() => {
        return {
            total: sessions.length,
            active: sessions.filter(s => s.status === 'active').length,
            completed: sessions.filter(s => s.status === 'completed').length,
            pending: sessions.filter(s => s.status === 'pending').length
        };
    }, [sessions]);

    // 카드 토글
    const handleCardToggle = (cardId: string) => {
        setExpandedCardId(prev => prev === cardId ? null : cardId);
    };

    // 빈 공간 클릭 시 카드 닫기
    const handleBackdropClick = () => {
        setExpandedCardId(null);
    };

    // Loading state
    if (isLoading) {
        return (
            <div className="war-room-list">
                <div className="loading-state" style={{ textAlign: 'center', padding: '40px' }}>
                    <div className="spinner">🔄</div>
                    <p>War Room 세션 불러오는 중...</p>
                </div>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="war-room-list">
                <div className="error-state" style={{ textAlign: 'center', padding: '40px', color: '#F44336' }}>
                    <p>⚠️ War Room 세션을 불러올 수 없습니다</p>
                    <p style={{ fontSize: '14px', opacity: 0.7 }}>{(error as Error).message}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="war-room-list">
            {/* 검색 & 필터 */}
            <div className="list-controls">
                <div className="search-section">
                    <TickerAutocompleteInput
                        label=""
                        value={searchTicker}
                        onChange={setSearchTicker}
                        placeholder="🔍 티커 검색... (예: NVDA, AAPL)"
                    />
                </div>

                <div className="filter-section">
                    <button
                        className={`filter-btn ${statusFilter === 'all' ? 'active' : ''}`}
                        onClick={() => setStatusFilter('all')}
                    >
                        전체 ({stats.total})
                    </button>
                    <button
                        className={`filter-btn ${statusFilter === 'active' ? 'active' : ''}`}
                        onClick={() => setStatusFilter('active')}
                    >
                        🔄 진행중 ({stats.active})
                    </button>
                    <button
                        className={`filter-btn ${statusFilter === 'completed' ? 'active' : ''}`}
                        onClick={() => setStatusFilter('completed')}
                    >
                        ✅ 완료 ({stats.completed})
                    </button>
                    <button
                        className={`filter-btn ${statusFilter === 'pending' ? 'active' : ''}`}
                        onClick={() => setStatusFilter('pending')}
                    >
                        ⏳ 대기중 ({stats.pending})
                    </button>
                </div>
            </div>

            {/* 결과 표시 */}
            <div className="results-info">
                {filteredSessions.length}개의 토론 세션
            </div>

            {/* 세션 카드 목록 */}
            <div className="sessions-container" onClick={handleBackdropClick}>
                {filteredSessions.length > 0 ? (
                    filteredSessions.map(session => (
                        <WarRoomCard
                            key={session.id}
                            session={session}
                            isExpanded={expandedCardId === session.id}
                            onToggle={() => handleCardToggle(session.id)}
                        />
                    ))
                ) : (
                    <div className="empty-result">
                        <p>검색 결과가 없습니다</p>
                        <p className="hint">다른 티커를 검색해보세요</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default WarRoomList;
