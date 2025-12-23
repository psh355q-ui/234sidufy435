/**
 * Portfolio Dashboard - 포트폴리오 현황 대시보드
 *
 * Phase 27: REAL MODE UI
 * Date: 2025-12-23
 */

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import './Portfolio.css';

interface Position {
    symbol: string;
    quantity: number;
    avg_price: number;
    current_price: number;
    market_value: number;
    profit_loss: number;
    profit_loss_pct: number;
    daily_pnl: number;
    daily_return_pct: number;
}

interface PortfolioData {
    total_value: number;
    cash: number;
    invested: number;
    total_pnl: number;
    total_pnl_pct: number;
    daily_pnl: number;
    daily_return_pct: number;
    positions: Position[];
}

// Mock data for development
const MOCK_PORTFOLIO: PortfolioData = {
    total_value: 127580.50,
    cash: 45200.00,
    invested: 82380.50,
    total_pnl: 7380.50,
    total_pnl_pct: 9.84,
    daily_pnl: 1250.30,
    daily_return_pct: 0.98,
    positions: [
        {
            symbol: 'AAPL',
            quantity: 100,
            avg_price: 175.20,
            current_price: 178.50,
            market_value: 17850.00,
            profit_loss: 330.00,
            profit_loss_pct: 1.88,
            daily_pnl: 150.00,
            daily_return_pct: 0.84
        },
        {
            symbol: 'NVDA',
            quantity: 50,
            avg_price: 480.00,
            current_price: 495.20,
            market_value: 24760.00,
            profit_loss: 760.00,
            profit_loss_pct: 3.17,
            daily_pnl: 380.00,
            daily_return_pct: 1.56
        },
        {
            symbol: 'MSFT',
            quantity: 75,
            avg_price: 385.00,
            current_price: 392.10,
            market_value: 29407.50,
            profit_loss: 532.50,
            profit_loss_pct: 1.84,
            daily_pnl: 225.00,
            daily_return_pct: 0.77
        },
        {
            symbol: 'GOOGL',
            quantity: 80,
            avg_price: 138.50,
            current_price: 132.90,
            market_value: 10632.00,
            profit_loss: -448.00,
            profit_loss_pct: -4.04,
            daily_pnl: -160.00,
            daily_return_pct: -1.48
        }
    ]
};

const Portfolio: React.FC = () => {
    // Fetch portfolio from API
    const { data: portfolio, isLoading, error } = useQuery({
        queryKey: ['portfolio'],
        queryFn: async () => {
            const response = await fetch('/api/portfolio');
            if (!response.ok) {
                throw new Error(`Failed to fetch portfolio: ${response.statusText}`);
            }
            return response.json();
        },
        refetchInterval: 30000, // Refresh every 30 seconds
        // Fallback to mock data if API fails (development mode)
        placeholderData: MOCK_PORTFOLIO
    });

    if (isLoading) {
        return (
            <div className="portfolio-page">
                <div className="loading-state">
                    <div className="spinner">🔄</div>
                    <p>포트폴리오 로딩 중...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="portfolio-page">
                <div className="error-state">
                    <p>⚠️ 포트폴리오를 불러올 수 없습니다</p>
                    <p style={{ fontSize: '14px', opacity: 0.7 }}>{(error as Error).message}</p>
                </div>
            </div>
        );
    }

    const allocation_pct = (portfolio.invested / portfolio.total_value) * 100;
    const cash_pct = (portfolio.cash / portfolio.total_value) * 100;

    return (
        <div className="portfolio-page">
            {/* Header */}
            <div className="page-header">
                <h1>💼 포트폴리오</h1>
            </div>

            {/* Summary Cards */}
            <div className="summary-cards">
                <div className="summary-card total-value">
                    <div className="card-icon">💰</div>
                    <div className="card-content">
                        <div className="card-label">총 자산</div>
                        <div className="card-value">${portfolio.total_value.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
                        <div className={`card-change ${portfolio.daily_pnl >= 0 ? 'positive' : 'negative'}`}>
                            {portfolio.daily_pnl >= 0 ? '+' : ''}${portfolio.daily_pnl.toFixed(2)} ({portfolio.daily_return_pct >= 0 ? '+' : ''}{portfolio.daily_return_pct.toFixed(2)}%)
                            <span className="change-label">오늘</span>
                        </div>
                    </div>
                </div>

                <div className="summary-card invested">
                    <div className="card-icon">📈</div>
                    <div className="card-content">
                        <div className="card-label">투자 금액</div>
                        <div className="card-value">${portfolio.invested.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
                        <div className="card-change neutral">
                            {allocation_pct.toFixed(1)}% <span className="change-label">배분</span>
                        </div>
                    </div>
                </div>

                <div className="summary-card cash">
                    <div className="card-icon">💵</div>
                    <div className="card-content">
                        <div className="card-label">현금</div>
                        <div className="card-value">${portfolio.cash.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
                        <div className="card-change neutral">
                            {cash_pct.toFixed(1)}% <span className="change-label">보유</span>
                        </div>
                    </div>
                </div>

                <div className="summary-card pnl">
                    <div className="card-icon">{portfolio.total_pnl >= 0 ? '🎯' : '📉'}</div>
                    <div className="card-content">
                        <div className="card-label">총 손익</div>
                        <div className={`card-value ${portfolio.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                            {portfolio.total_pnl >= 0 ? '+' : ''}${portfolio.total_pnl.toFixed(2)}
                        </div>
                        <div className={`card-change ${portfolio.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                            {portfolio.total_pnl_pct >= 0 ? '+' : ''}{portfolio.total_pnl_pct.toFixed(2)}%
                        </div>
                    </div>
                </div>
            </div>

            {/* Positions Table */}
            <div className="positions-section">
                <div className="section-header">
                    <h2>📊 보유 종목 ({portfolio.positions.length})</h2>
                </div>

                <div className="positions-table-container">
                    {portfolio.positions.length > 0 ? (
                        <table className="positions-table">
                            <thead>
                                <tr>
                                    <th>티커</th>
                                    <th className="text-right">수량</th>
                                    <th className="text-right">평균 단가</th>
                                    <th className="text-right">현재가</th>
                                    <th className="text-right">평가액</th>
                                    <th className="text-right">손익</th>
                                    <th className="text-right">수익률</th>
                                    <th className="text-right">일일 손익</th>
                                    <th className="text-right">일일 수익률</th>
                                </tr>
                            </thead>
                            <tbody>
                                {portfolio.positions.map(position => (
                                    <tr key={position.symbol}>
                                        <td className="ticker">{position.symbol}</td>
                                        <td className="text-right mono">{position.quantity}</td>
                                        <td className="text-right mono">${position.avg_price.toFixed(2)}</td>
                                        <td className="text-right mono">${position.current_price.toFixed(2)}</td>
                                        <td className="text-right mono">${position.market_value.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                                        <td className={`text-right mono ${position.profit_loss >= 0 ? 'positive' : 'negative'}`}>
                                            {position.profit_loss >= 0 ? '+' : ''}${position.profit_loss.toFixed(2)}
                                        </td>
                                        <td className={`text-right mono ${position.profit_loss_pct >= 0 ? 'positive' : 'negative'}`}>
                                            {position.profit_loss_pct >= 0 ? '+' : ''}{position.profit_loss_pct.toFixed(2)}%
                                        </td>
                                        <td className={`text-right mono ${position.daily_pnl >= 0 ? 'positive' : 'negative'}`}>
                                            {position.daily_pnl >= 0 ? '+' : ''}${position.daily_pnl.toFixed(2)}
                                        </td>
                                        <td className={`text-right mono ${position.daily_return_pct >= 0 ? 'positive' : 'negative'}`}>
                                            {position.daily_return_pct >= 0 ? '+' : ''}{position.daily_return_pct.toFixed(2)}%
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <div className="empty-state">
                            <p>보유 종목이 없습니다</p>
                            <p className="hint">War Room에서 토론을 시작해보세요</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Allocation Chart (Placeholder) */}
            <div className="allocation-section">
                <div className="section-header">
                    <h2>📊 자산 배분</h2>
                </div>
                <div className="allocation-chart">
                    <div className="allocation-bar">
                        <div
                            className="allocation-invested"
                            style={{ width: `${allocation_pct}%` }}
                        >
                            <span>{allocation_pct.toFixed(1)}%</span>
                        </div>
                        <div
                            className="allocation-cash"
                            style={{ width: `${cash_pct}%` }}
                        >
                            <span>{cash_pct.toFixed(1)}%</span>
                        </div>
                    </div>
                    <div className="allocation-legend">
                        <div className="legend-item">
                            <div className="legend-color invested"></div>
                            <span>투자 중 (${portfolio.invested.toLocaleString('en-US')})</span>
                        </div>
                        <div className="legend-item">
                            <div className="legend-color cash"></div>
                            <span>현금 (${portfolio.cash.toLocaleString('en-US')})</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Portfolio;
