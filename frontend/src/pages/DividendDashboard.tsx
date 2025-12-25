import React, { useState, useEffect } from 'react';
import { DollarSign, Calendar, TrendingUp, Shield, PlusCircle, Trophy } from 'lucide-react';
import { Card } from '../components/common/Card';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { getPortfolio } from '../services/api';
import DividendSummaryCards from '../components/Dividend/DividendSummaryCards';
import DividendCalendar from '../components/Dividend/DividendCalendar';
import CompoundSimulator from '../components/Dividend/CompoundSimulator';
import RiskScoreTable from '../components/Dividend/RiskScoreTable';
import CashInjectionSlider from '../components/Dividend/CashInjectionSlider';
import AristocratsTable from '../components/Dividend/AristocratsTable';

type TabType = 'holdings' | 'calendar' | 'drip' | 'risk' | 'injection' | 'aristocrats';

const DividendDashboard: React.FC = () => {
    const [activeTab, setActiveTab] = useState<TabType>('holdings');
    const [loading, setLoading] = useState(false);
    const [portfolioIncome, setPortfolioIncome] = useState<any>(null);
    const [portfolio, setPortfolio] = useState<any>(null);

    // KIS 포트폴리오 데이터 및 배당 수입 조회
    const fetchPortfolioIncome = async () => {
        setLoading(true);
        try {
            // KIS API에서 실제 포트폴리오 데이터 가져오기
            const portfolioData = await getPortfolio();
            setPortfolio(portfolioData);

            // 포지션 데이터를 배당 API 형식으로 변환
            const positions = portfolioData.positions.map((pos: any) => ({
                ticker: pos.symbol,
                shares: pos.quantity,
                avg_price: pos.avg_price
            }));

            const response = await fetch('http://localhost:8001/api/dividend/portfolio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(positions)
            });

            if (!response.ok) throw new Error('Failed to fetch portfolio income');

            const data = await response.json();
            setPortfolioIncome(data);
        } catch (error: any) {
            console.error('Failed to fetch portfolio income:', error.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPortfolioIncome();
    }, []);

    const renderTabContent = () => {
        switch (activeTab) {
            case 'holdings':
                return portfolio ? renderHoldingsTable() : <div className="text-center py-12 text-gray-500">포트폴리오 데이터를 불러오는 중...</div>;
            case 'calendar':
                return <DividendCalendar />;
            case 'drip':
                return <CompoundSimulator />;
            case 'risk':
                return <RiskScoreTable />;
            case 'injection':
                return <CashInjectionSlider portfolioIncome={portfolioIncome} />;
            case 'aristocrats':
                return <AristocratsTable />;
            default:
                return portfolio ? renderHoldingsTable() : <div className="text-center py-12 text-gray-500">포트폴리오 데이터를 불러오는 중...</div>;
        }
    };

    // 보유 종목 배당 정보 테이블
    const renderHoldingsTable = () => (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-gray-200 bg-gray-50">
                            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">티커</th>
                            <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">보유 수량</th>
                            <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">현재가</th>
                            <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">평가액</th>
                            <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">배당률</th>
                            <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">연간 배당금</th>
                            <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">다음 배당일</th>
                        </tr>
                    </thead>
                    <tbody>
                        {portfolio.positions.map((position: any) => {
                            const annualDividend = position.market_value * 0.03; // 임시 3% 가정
                            return (
                                <tr key={position.symbol} className="border-b border-gray-100 hover:bg-gray-50">
                                    <td className="py-3 px-4 font-semibold text-gray-900">{position.symbol}</td>
                                    <td className="text-right py-3 px-4 font-mono text-sm text-gray-700">
                                        {position.quantity.toLocaleString()}
                                    </td>
                                    <td className="text-right py-3 px-4 font-mono text-sm text-gray-700">
                                        ${position.current_price.toFixed(2)}
                                    </td>
                                    <td className="text-right py-3 px-4 font-mono text-sm text-gray-700">
                                        ${position.market_value.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                                    </td>
                                    <td className="text-right py-3 px-4 font-mono text-sm text-blue-600">
                                        ~3.0%
                                    </td>
                                    <td className="text-right py-3 px-4 font-mono text-sm font-semibold text-green-600">
                                        ${annualDividend.toFixed(2)}
                                    </td>
                                    <td className="text-right py-3 px-4 text-sm text-gray-600">
                                        2025-03-15
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                    <tfoot className="bg-gray-50 border-t-2 border-gray-300">
                        <tr>
                            <td className="py-3 px-4 font-bold text-gray-900" colSpan={3}>합계</td>
                            <td className="text-right py-3 px-4 font-mono font-bold text-gray-900">
                                ${portfolio.total_value.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                            </td>
                            <td className="text-right py-3 px-4"></td>
                            <td className="text-right py-3 px-4 font-mono font-bold text-green-600">
                                ${(portfolio.total_value * 0.03).toFixed(2)}
                            </td>
                            <td className="text-right py-3 px-4"></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
            <div className="p-4 bg-blue-50 border-t border-blue-100">
                <p className="text-sm text-blue-800">
                    💡 <strong>참고:</strong> 배당률과 배당금은 예상 수치입니다. 실제 배당은 각 기업의 정책에 따라 달라질 수 있습니다.
                </p>
            </div>
        </div>
    );

    return (
        <div className="space-y-6 p-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                    <DollarSign className="text-green-600" size={32} />
                    배당 인텔리전스
                </h1>
                <p className="text-gray-600 mt-1">미국 배당주 포트폴리오 분석 및 시뮬레이션</p>
            </div>

            {/* Summary Cards */}
            {loading ? (
                <div className="flex justify-center items-center py-12">
                    <LoadingSpinner size="lg" />
                </div>
            ) : (
                <DividendSummaryCards portfolioIncome={portfolioIncome} />
            )}

            {/* Tabs and Content */}
            <div className="space-y-6">
                <Card>
                    <div className="mb-6 border-b">
                        <h2 className="text-xl font-semibold text-gray-800 mb-4">배당 분석 도구</h2>
                        {/* Compact tab grid for mobile, flex for desktop */}
                        <div className="grid grid-cols-3 md:flex md:flex-wrap gap-2 pb-2">
                            <button
                                onClick={() => setActiveTab('holdings')}
                                className={`px-2 py-2 md:px-4 md:py-2 rounded-md text-xs md:text-sm font-medium transition-colors flex flex-col md:flex-row items-center justify-center gap-1 md:gap-2 ${activeTab === 'holdings'
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'text-gray-600 hover:bg-gray-100'
                                    }`}
                            >
                                <DollarSign size={14} className="md:w-4 md:h-4" />
                                <span className="text-center leading-tight">보유<br className="md:hidden" />종목</span>
                            </button>
                            <button
                                onClick={() => setActiveTab('calendar')}
                                className={`px-2 py-2 md:px-4 md:py-2 rounded-md text-xs md:text-sm font-medium transition-colors flex flex-col md:flex-row items-center justify-center gap-1 md:gap-2 ${activeTab === 'calendar'
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'text-gray-600 hover:bg-gray-100'
                                    }`}
                            >
                                <Calendar size={14} className="md:w-4 md:h-4" />
                                <span className="text-center leading-tight">배당<br className="md:hidden" />캘린더</span>
                            </button>
                            <button
                                onClick={() => setActiveTab('drip')}
                                className={`px-2 py-2 md:px-4 md:py-2 rounded-md text-xs md:text-sm font-medium transition-colors flex flex-col md:flex-row items-center justify-center gap-1 md:gap-2 ${activeTab === 'drip'
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'text-gray-600 hover:bg-gray-100'
                                    }`}
                            >
                                <TrendingUp size={14} className="md:w-4 md:h-4" />
                                <span className="text-center leading-tight">복리<br className="md:hidden" />시뮬레이션</span>
                            </button>
                            <button
                                onClick={() => setActiveTab('risk')}
                                className={`px-2 py-2 md:px-4 md:py-2 rounded-md text-xs md:text-sm font-medium transition-colors flex flex-col md:flex-row items-center justify-center gap-1 md:gap-2 ${activeTab === 'risk'
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'text-gray-600 hover:bg-gray-100'
                                    }`}
                            >
                                <Shield size={14} className="md:w-4 md:h-4" />
                                <span className="text-center leading-tight">리스크<br className="md:hidden" />분석</span>
                            </button>
                            <button
                                onClick={() => setActiveTab('injection')}
                                className={`px-2 py-2 md:px-4 md:py-2 rounded-md text-xs md:text-sm font-medium transition-colors flex flex-col md:flex-row items-center justify-center gap-1 md:gap-2 ${activeTab === 'injection'
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'text-gray-600 hover:bg-gray-100'
                                    }`}
                            >
                                <PlusCircle size={14} className="md:w-4 md:h-4" />
                                <span className="text-center leading-tight">예수금<br className="md:hidden" />추가</span>
                            </button>
                            <button
                                onClick={() => setActiveTab('aristocrats')}
                                className={`px-2 py-2 md:px-4 md:py-2 rounded-md text-xs md:text-sm font-medium transition-colors flex flex-col md:flex-row items-center justify-center gap-1 md:gap-2 ${activeTab === 'aristocrats'
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'text-gray-600 hover:bg-gray-100'
                                    }`}
                            >
                                <Trophy size={14} className="md:w-4 md:h-4" />
                                <span className="text-center leading-tight">배당<br className="md:hidden" />귀족주</span>
                            </button>
                        </div>
                    </div>

                    <div className="min-h-[400px]">
                        {renderTabContent()}
                    </div>
                </Card>
            </div>
        </div>
    );
};

export default DividendDashboard;
