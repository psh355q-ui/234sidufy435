/**
 * Performance Dashboard Page
 *
 * Phase 25.2: Agent Performance Tracking
 * Date: 2025-12-23
 *
 * Features:
 * - Overall performance summary
 * - Action-based accuracy breakdown (BUY/SELL/HOLD)
 * - Daily performance trend chart
 * - Top/bottom performing sessions
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import './Performance.css';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface PerformanceSummary {
  total_predictions: number;
  correct_predictions: number;
  accuracy: number;
  avg_return: number;
  avg_performance_score: number;
  best_action: string | null;
}

interface ActionPerformance {
  action: string;
  total: number;
  correct: number;
  accuracy: number;
  avg_return: number;
  avg_performance_score: number;
}

interface DailyPerformance {
  date: string;
  total: number;
  correct: number;
  accuracy: number;
  avg_return: number;
}

interface SessionPerformance {
  session_id: number;
  ticker: string;
  consensus_action: string;
  consensus_confidence: number;
  return_pct: number;
  is_correct: boolean;
  performance_score: number;
  initial_timestamp: string;
}

// ============================================================================
// Performance Dashboard Component
// ============================================================================

const Performance: React.FC = () => {
  const [sessionView, setSessionView] = useState<'best' | 'worst'>('best');

  // Fetch overall summary
  const { data: summary, isLoading: summaryLoading } = useQuery<PerformanceSummary>({
    queryKey: ['performance-summary'],
    queryFn: async () => {
      const response = await fetch('/api/performance/summary');
      if (!response.ok) {
        throw new Error(`Failed to fetch summary: ${response.statusText}`);
      }
      return response.json();
    },
    refetchInterval: 60000, // Refresh every 60 seconds
  });

  // Fetch action-based performance
  const { data: actionPerformance = [], isLoading: actionsLoading } = useQuery<ActionPerformance[]>({
    queryKey: ['performance-by-action'],
    queryFn: async () => {
      const response = await fetch('/api/performance/by-action');
      if (!response.ok) {
        throw new Error(`Failed to fetch action performance: ${response.statusText}`);
      }
      return response.json();
    },
    refetchInterval: 60000,
  });

  // Fetch daily history
  const { data: dailyHistory = [], isLoading: historyLoading } = useQuery<DailyPerformance[]>({
    queryKey: ['performance-history'],
    queryFn: async () => {
      const response = await fetch('/api/performance/history?days=30');
      if (!response.ok) {
        throw new Error(`Failed to fetch history: ${response.statusText}`);
      }
      return response.json();
    },
    refetchInterval: 60000,
  });

  // Fetch top sessions
  const { data: topSessions = [], isLoading: sessionsLoading } = useQuery<SessionPerformance[]>({
    queryKey: ['top-sessions', sessionView],
    queryFn: async () => {
      const response = await fetch(`/api/performance/top-sessions?order=${sessionView}&limit=10`);
      if (!response.ok) {
        throw new Error(`Failed to fetch top sessions: ${response.statusText}`);
      }
      return response.json();
    },
    refetchInterval: 60000,
  });

  // ============================================================================
  // Helper Functions
  // ============================================================================

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'BUY':
        return '#10b981';
      case 'SELL':
        return '#ef4444';
      case 'HOLD':
        return '#f59e0b';
      default:
        return '#6b7280';
    }
  };

  // ============================================================================
  // Render
  // ============================================================================

  if (summaryLoading || actionsLoading || historyLoading || sessionsLoading) {
    return (
      <div className="performance-page">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading performance data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="performance-page">
      <div className="performance-header">
        <h1>📊 Agent Performance Dashboard</h1>
        <p className="subtitle">24-hour prediction accuracy and return tracking</p>
      </div>

      {/* Overall Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card">
          <div className="card-icon">🎯</div>
          <div className="card-content">
            <h3>Overall Accuracy</h3>
            <div className="card-value">{summary?.accuracy.toFixed(1)}%</div>
            <div className="card-detail">
              {summary?.correct_predictions} / {summary?.total_predictions} correct
            </div>
          </div>
        </div>

        <div className="summary-card">
          <div className="card-icon">📈</div>
          <div className="card-content">
            <h3>Avg Return</h3>
            <div className={`card-value ${(summary?.avg_return ?? 0) >= 0 ? 'positive' : 'negative'}`}>
              {formatPercent(summary?.avg_return ?? 0)}
            </div>
            <div className="card-detail">Per prediction</div>
          </div>
        </div>

        <div className="summary-card">
          <div className="card-icon">⭐</div>
          <div className="card-content">
            <h3>Avg Performance</h3>
            <div className={`card-value ${(summary?.avg_performance_score ?? 0) >= 0 ? 'positive' : 'negative'}`}>
              {(summary?.avg_performance_score ?? 0).toFixed(4)}
            </div>
            <div className="card-detail">Weighted score</div>
          </div>
        </div>

        <div className="summary-card">
          <div className="card-icon">🏆</div>
          <div className="card-content">
            <h3>Best Action</h3>
            <div className="card-value" style={{ color: getActionColor(summary?.best_action ?? '') }}>
              {summary?.best_action ?? 'N/A'}
            </div>
            <div className="card-detail">Highest accuracy</div>
          </div>
        </div>
      </div>

      {/* Action-Based Performance */}
      <div className="performance-section">
        <h2>📊 Performance by Action</h2>
        <div className="action-performance-grid">
          {actionPerformance.map((action) => (
            <div key={action.action} className="action-card">
              <div className="action-header">
                <span className="action-badge" style={{ backgroundColor: getActionColor(action.action) }}>
                  {action.action}
                </span>
                <span className="action-accuracy">{action.accuracy.toFixed(1)}%</span>
              </div>
              <div className="action-stats">
                <div className="stat-row">
                  <span className="stat-label">Total Predictions:</span>
                  <span className="stat-value">{action.total}</span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">Correct:</span>
                  <span className="stat-value">{action.correct}</span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">Avg Return:</span>
                  <span className={`stat-value ${action.avg_return >= 0 ? 'positive' : 'negative'}`}>
                    {formatPercent(action.avg_return)}
                  </span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">Performance Score:</span>
                  <span className={`stat-value ${action.avg_performance_score >= 0 ? 'positive' : 'negative'}`}>
                    {action.avg_performance_score.toFixed(4)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Daily Performance Trend */}
      <div className="performance-section">
        <h2>📈 Daily Performance Trend (Last 30 Days)</h2>
        <div className="daily-history-table">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Total</th>
                <th>Correct</th>
                <th>Accuracy</th>
                <th>Avg Return</th>
              </tr>
            </thead>
            <tbody>
              {dailyHistory.length === 0 ? (
                <tr>
                  <td colSpan={5} className="no-data">No historical data yet</td>
                </tr>
              ) : (
                dailyHistory.map((day) => (
                  <tr key={day.date}>
                    <td>{formatDate(day.date)}</td>
                    <td>{day.total}</td>
                    <td>{day.correct}</td>
                    <td className={day.accuracy >= 60 ? 'positive' : 'negative'}>
                      {day.accuracy.toFixed(1)}%
                    </td>
                    <td className={day.avg_return >= 0 ? 'positive' : 'negative'}>
                      {formatPercent(day.avg_return)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Top/Bottom Sessions */}
      <div className="performance-section">
        <div className="section-header">
          <h2>🏆 Top Sessions</h2>
          <div className="session-view-toggle">
            <button
              className={sessionView === 'best' ? 'active' : ''}
              onClick={() => setSessionView('best')}
            >
              Best
            </button>
            <button
              className={sessionView === 'worst' ? 'active' : ''}
              onClick={() => setSessionView('worst')}
            >
              Worst
            </button>
          </div>
        </div>

        <div className="sessions-table">
          <table>
            <thead>
              <tr>
                <th>Session</th>
                <th>Ticker</th>
                <th>Action</th>
                <th>Confidence</th>
                <th>Return</th>
                <th>Correct</th>
                <th>Score</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {topSessions.length === 0 ? (
                <tr>
                  <td colSpan={8} className="no-data">No sessions yet</td>
                </tr>
              ) : (
                topSessions.map((session) => (
                  <tr key={session.session_id}>
                    <td>#{session.session_id}</td>
                    <td className="ticker-cell">{session.ticker}</td>
                    <td>
                      <span className="action-badge small" style={{ backgroundColor: getActionColor(session.consensus_action) }}>
                        {session.consensus_action}
                      </span>
                    </td>
                    <td>{(session.consensus_confidence * 100).toFixed(1)}%</td>
                    <td className={session.return_pct >= 0 ? 'positive' : 'negative'}>
                      {formatPercent(session.return_pct)}
                    </td>
                    <td>{session.is_correct ? '✅' : '❌'}</td>
                    <td className={session.performance_score >= 0 ? 'positive' : 'negative'}>
                      {session.performance_score.toFixed(4)}
                    </td>
                    <td>{formatDate(session.initial_timestamp)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Performance;
