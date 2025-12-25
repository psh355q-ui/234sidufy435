import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Tabs, message, Spin } from 'antd';
import {
    DollarOutlined,
    CalendarOutlined,
    RiseOutlined,
    SafetyOutlined,
    PlusCircleOutlined,
    TrophyOutlined
} from '@ant-design/icons';
import DividendSummaryCards from '../components/Dividend/DividendSummaryCards';
import DividendCalendar from '../components/Dividend/DividendCalendar';
import CompoundSimulator from '../components/Dividend/CompoundSimulator';
import RiskScoreTable from '../components/Dividend/RiskScoreTable';
import CashInjectionSlider from '../components/Dividend/CashInjectionSlider';
import AristocratsTable from '../components/Dividend/AristocratsTable';

const { TabPane } = Tabs;

const DividendDashboard: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const [portfolioIncome, setPortfolioIncome] = useState<any>(null);

    // 포트폴리오 배당 수입 조회
    const fetchPortfolioIncome = async () => {
        setLoading(true);
        try {
            // 예시 포지션 (실제로는 KIS API에서 가져와야 함)
            const positions = [
                { ticker: 'JNJ', shares: 100, avg_price: 150 },
                { ticker: 'PG', shares: 50, avg_price: 145 },
                { ticker: 'KO', shares: 150, avg_price: 60 }
            ];

            const response = await fetch('http://localhost:8001/api/dividend/portfolio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(positions)
            });

            if (!response.ok) throw new Error('Failed to fetch portfolio income');

            const data = await response.json();
            setPortfolioIncome(data);
        } catch (error: any) {
            message.error(`배당 수입 조회 실패: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPortfolioIncome();
    }, []);

    return (
        <div style={{ padding: '24px', background: '#0a0e27', minHeight: '100vh' }}>
            {/* 헤더 */}
            <div style={{ marginBottom: '24px' }}>
                <h1 style={{
                    color: '#fff',
                    fontSize: '28px',
                    fontWeight: 'bold',
                    marginBottom: '8px'
                }}>
                    <DollarOutlined style={{ marginRight: '12px', color: '#52c41a' }} />
                    배당 인텔리전스
                </h1>
                <p style={{ color: '#8c8c8c', fontSize: '14px' }}>
                    미국 배당주 포트폴리오 분석 및 시뮬레이션
                </p>
            </div>

            {/* 요약 카드 */}
            {loading ? (
                <div style={{ textAlign: 'center', padding: '40px' }}>
                    <Spin size="large" />
                </div>
            ) : (
                <DividendSummaryCards portfolioIncome={portfolioIncome} />
            )}

            {/* 탭 컨텐츠 */}
            <Card
                style={{
                    background: 'linear-gradient(135deg, #1a1f3a 0%, #0f1729 100%)',
                    border: '1px solid #2d3748',
                    borderRadius: '12px',
                    marginTop: '24px'
                }}
                bodyStyle={{ padding: '24px' }}
            >
                <Tabs
                    defaultActiveKey="calendar"
                    type="card"
                    tabBarStyle={{
                        borderBottom: '1px solid #2d3748',
                        marginBottom: '24px'
                    }}
                >
                    {/* 배당 캘린더 */}
                    <TabPane
                        tab={
                            <span>
                                <CalendarOutlined />
                                배당 캘린더
                            </span>
                        }
                        key="calendar"
                    >
                        <DividendCalendar />
                    </TabPane>

                    {/* 복리 시뮬레이션 */}
                    <TabPane
                        tab={
                            <span>
                                <RiseOutlined />
                                복리 시뮬레이션
                            </span>
                        }
                        key="drip"
                    >
                        <CompoundSimulator />
                    </TabPane>

                    {/* 리스크 분석 */}
                    <TabPane
                        tab={
                            <span>
                                <SafetyOutlined />
                                리스크 분석
                            </span>
                        }
                        key="risk"
                    >
                        <RiskScoreTable />
                    </TabPane>

                    {/* 예수금 추가 */}
                    <TabPane
                        tab={
                            <span>
                                <PlusCircleOutlined />
                                예수금 추가
                            </span>
                        }
                        key="injection"
                    >
                        <CashInjectionSlider portfolioIncome={portfolioIncome} />
                    </TabPane>

                    {/* 배당 귀족주 */}
                    <TabPane
                        tab={
                            <span>
                                <TrophyOutlined />
                                배당 귀족주
                            </span>
                        }
                        key="aristocrats"
                    >
                        <AristocratsTable />
                    </TabPane>
                </Tabs>
            </Card>
        </div>
    );
};

export default DividendDashboard;
