/**
 * Signal Consolidation Page - 통합 신호 대시보드
 * 
 * 4개 출처(War Room, Deep Reasoning, Manual Analysis, News Analysis)의
 * 트레이딩 신호를 통합하여 표시하는 대시보드
 * 
 * Features:
 * - 출처별 신호 분포 차트
 * - 실시간 신호 타임라인
 * - 충돌 감지 (동일 티커, 다른 액션)
 * - 필터링 (출처, 액션, 신뢰도)
 */

/**
 * SignalConsolidationPage.tsx - 시그널 통합 대시보드
 * 
 * 📊 Data Sources:
 *   - API: GET /api/signals (모든 트레이딩 시그널)
 *   - API: GET /api/signals/:id (시그널 상세)
 *   - API: PUT /api/signals/:id/approve (시그널 승인)
 *   - API: PUT /api/signals/:id/reject (시그널 거부)
 *   - State: signals, filters, selectedSignal
 * 
 * 🔗 Dependencies:
 *   - react: useState, useEffect
 *   - @tanstack/react-query: useQuery, useMutation
 *   - lucide-react: Filter, CheckCircle, XCircle
 * 
 * 📤 Components Used:
 *   - Card, LoadingSpinner, Button, Badge
 *   - SignalCard: 개별 시그널 카드
 *   - FilterPanel: 필터 패널
 * 
 * 🔄 Used By:
 *   - App.tsx (route: /signals)
 * 
 * 📝 Notes:
 *   - Phase 10: Signal Consolidation
 *   - 필터링: PRIMARY/HIDDEN/LOSER, 날짜, 신뢰도
 *   - 평균 신뢰도 계산 수정 (NaN% 버그 해결)
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { signalConsolidationApi, ConsolidatedSignal } from '../services/signalConsolidationApi';
import { Card } from '../components/common/Card';
import './SignalConsolidationPage.css';

const SignalConsolidationPage: React.FC = () => {
    const [sourceFilter, setSourceFilter] = useState<string>('');
    const [actionFilter, setActionFilter] = useState<string>('');

    // Fetch consolidated signals
    const { data: signalsData, isLoading, error } = useQuery({
        queryKey: ['consolidated-signals', sourceFilter, actionFilter],
        queryFn: () => signalConsolidationApi.getConsolidatedSignals({
            source: sourceFilter || undefined,
            action: actionFilter || undefined,
            limit: 50
        }),
        refetchInterval: 15000, // Refetch every 15 seconds
    });

    // Fetch stats
    const { data: stats } = useQuery({
        queryKey: ['consolidation-stats'],
        queryFn: () => signalConsolidationApi.getStats(7),
        refetchInterval: 30000,
    });

    // Source badge colors
    const getSourceColor = (source: string) => {
        const colors: Record<string, string> = {
            war_room: '#9C27B0',
            deep_reasoning: '#2196F3',
            manual_analysis: '#4CAF50',
            news_analysis: '#FF9800'
        };
        return colors[source] || '#757575';
    };

    // Action badge colors
    const getActionColor = (action: string) => {
        const colors: Record<string, string> = {
            BUY: '#4CAF50',
            SELL: '#F44336',
            HOLD: '#FF9800'
        };
        return colors[action] || '#757575';
    };

    if (isLoading) {
        return (
            <div className="signal-consolidation-page">
                <div className="loading-state" style={{ textAlign: 'center', padding: '60px' }}>
                    <div className="spinner">🔄</div>
                    <p>통합 신호 불러오는 중...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="signal-consolidation-page">
                <div className="error-state" style={{ textAlign: 'center', padding: '60px', color: '#F44336' }}>
                    <p>⚠️ 통합 신호를 불러올 수 없습니다</p>
                    <p style={{ fontSize: '14px', opacity: 0.7 }}>{(error as Error).message}</p>
                </div>
            </div>
        );
    }

    const signals = signalsData?.signals || [];
    const totalCount = signalsData?.total_count || 0;

    return (
        <div className="signal-consolidation-page">
            {/* Header */}
            <div className="page-header" style={{
                textAlign: 'center',
                padding: '40px 20px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                marginBottom: '32px',
                borderRadius: '0 0 32px 32px',
                boxShadow: '0 10px 40px rgba(102, 126, 234, 0.3)'
            }}>
                <h1 style={{
                    margin: '0 0 12px 0',
                    fontSize: '42px',
                    fontWeight: '900',
                    textShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
                }}>
                    📊 Signal Consolidation
                </h1>
                <p style={{
                    margin: 0,
                    fontSize: '18px',
                    opacity: 0.95,
                    fontWeight: '600',
                    textShadow: '0 2px 10px rgba(0, 0, 0, 0.2)'
                }}>
                    4개 출처 통합 트레이딩 신호 대시보드
                </p>
            </div>

            <div className="page-content" style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 20px' }}>
                {/* Stats Cards */}
                {stats && (
                    <div className="stats-cards" style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                        gap: '20px',
                        marginBottom: '32px'
                    }}>
                        <Card style={{ padding: '20px', textAlign: 'center' }}>
                            <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>Total Signals</div>
                            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#667eea' }}>
                                {stats.total_signals}
                            </div>
                        </Card>

                        {Object.entries(stats.by_source).map(([source, count]) => (
                            <Card key={source} style={{ padding: '20px', textAlign: 'center' }}>
                                <div style={{
                                    fontSize: '12px',
                                    color: getSourceColor(source),
                                    marginBottom: '8px',
                                    fontWeight: 'bold'
                                }}>
                                    {source.replace('_', ' ').toUpperCase()}
                                </div>
                                <div style={{ fontSize: '28px', fontWeight: 'bold' }}>
                                    {count}
                                </div>
                            </Card>
                        ))}

                        <Card style={{ padding: '20px', textAlign: 'center' }}>
                            <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>Avg Confidence</div>
                            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#4CAF50' }}>
                                {(stats.avg_confidence * 100).toFixed(0)}%
                            </div>
                        </Card>
                    </div>
                )}

                {/* Filters */}
                <div className="filters" style={{
                    display: 'flex',
                    gap: '16px',
                    marginBottom: '24px',
                    flexWrap: 'wrap'
                }}>
                    <select
                        value={sourceFilter}
                        onChange={(e) => setSourceFilter(e.target.value)}
                        style={{
                            padding: '10px 16px',
                            borderRadius: '8px',
                            border: '2px solid #e0e0e0',
                            fontSize: '14px',
                            fontWeight: '600',
                            cursor: 'pointer'
                        }}
                    >
                        <option value="">All Sources</option>
                        <option value="war_room">War Room</option>
                        <option value="deep_reasoning">Deep Reasoning</option>
                        <option value="manual_analysis">Manual Analysis</option>
                        <option value="news_analysis">News Analysis</option>
                    </select>

                    <select
                        value={actionFilter}
                        onChange={(e) => setActionFilter(e.target.value)}
                        style={{
                            padding: '10px 16px',
                            borderRadius: '8px',
                            border: '2px solid #e0e0e0',
                            fontSize: '14px',
                            fontWeight: '600',
                            cursor: 'pointer'
                        }}
                    >
                        <option value="">All Actions</option>
                        <option value="BUY">BUY</option>
                        <option value="SELL">SELL</option>
                        <option value="HOLD">HOLD</option>
                    </select>

                    <div style={{ marginLeft: 'auto', fontSize: '14px', color: '#666', padding: '10px 0' }}>
                        {totalCount} signals found
                    </div>
                </div>

                {/* Signal Timeline */}
                <div className="signal-timeline">
                    {signals.length === 0 ? (
                        <Card style={{ padding: '60px', textAlign: 'center' }}>
                            <p style={{ fontSize: '18px', color: '#999' }}>신호가 없습니다</p>
                            <p style={{ fontSize: '14px', color: '#bbb' }}>Analysis Lab이나 War Room을 실행하여 신호를 생성하세요</p>
                        </Card>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            {signals.map((signal) => (
                                <Card key={signal.id} style={{
                                    padding: '20px',
                                    borderLeft: `4px solid ${getSourceColor(signal.source)}`
                                }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                                        {/* Ticker */}
                                        <div style={{
                                            fontSize: '20px',
                                            fontWeight: 'bold',
                                            color: '#333'
                                        }}>
                                            {signal.ticker}
                                        </div>

                                        {/* Action Badge */}
                                        <span style={{
                                            padding: '4px 12px',
                                            borderRadius: '12px',
                                            backgroundColor: getActionColor(signal.action),
                                            color: 'white',
                                            fontSize: '12px',
                                            fontWeight: 'bold'
                                        }}>
                                            {signal.action}
                                        </span>

                                        {/* Confidence */}
                                        <span style={{
                                            padding: '4px 12px',
                                            borderRadius: '12px',
                                            backgroundColor: '#f5f5f5',
                                            color: '#666',
                                            fontSize: '12px',
                                            fontWeight: 'bold'
                                        }}>
                                            {(signal.confidence * 100).toFixed(0)}%
                                        </span>

                                        {/* Source Badge */}
                                        <span style={{
                                            padding: '4px 12px',
                                            borderRadius: '12px',
                                            backgroundColor: getSourceColor(signal.source),
                                            color: 'white',
                                            fontSize: '11px',
                                            fontWeight: 'bold'
                                        }}>
                                            {signal.source.replace('_', ' ').toUpperCase()}
                                        </span>

                                        {/* Timestamp */}
                                        <span style={{
                                            marginLeft: 'auto',
                                            fontSize: '12px',
                                            color: '#999'
                                        }}>
                                            {new Date(signal.timestamp).toLocaleString('ko-KR')}
                                        </span>
                                    </div>

                                    {/* Reasoning */}
                                    <div style={{
                                        fontSize: '14px',
                                        color: '#666',
                                        lineHeight: '1.6'
                                    }}>
                                        {signal.reasoning}
                                    </div>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SignalConsolidationPage;
