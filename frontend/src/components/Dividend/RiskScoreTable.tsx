import React, { useState, useEffect } from 'react';
import { Table, Tag, Input, message } from 'antd';
import { SearchOutlined, SafetyOutlined } from '@ant-design/icons';

const RiskScoreTable: React.FC = () => {
    const [tickers, setTickers] = useState(['JNJ', 'PG', 'KO', 'T', 'O']);
    const [riskData, setRiskData] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchRiskScores();
    }, [tickers]);

    const fetchRiskScores = async () => {
        setLoading(true);
        try {
            const promises = tickers.map(ticker =>
                fetch(`http://localhost:8001/api/dividend/risk/${ticker}`)
                    .then(res => res.ok ? res.json() : null)
            );

            const results = await Promise.all(promises);
            setRiskData(results.filter(Boolean));
        } catch (error) {
            console.error('Risk fetch error:', error);
        } finally {
            setLoading(false);
        }
    };

    const getRiskColor = (level: string) => {
        switch (level) {
            case 'Safe': return 'green';
            case 'Warning': return 'orange';
            case 'Danger': return 'red';
            default: return 'default';
        }
    };

    const columns = [
        {
            title: 'Ticker',
            dataIndex: 'ticker',
            key: 'ticker',
            render: (text: string) => <strong style={{ color: '#1890ff' }}>{text}</strong>
        },
        {
            title: '리스크 점수',
            dataIndex: 'risk_score',
            key: 'risk_score',
            sorter: (a: any, b: any) => a.risk_score - b.risk_score,
            render: (score: number) => <span style={{ color: score > 60 ? '#ff4d4f' : score > 30 ? '#faad14' : '#52c41a' }}>{score}</span>
        },
        {
            title: '레벨',
            dataIndex: 'risk_level',
            key: 'risk_level',
            render: (level: string) => <Tag color={getRiskColor(level)}>{level}</Tag>
        },
        {
            title: 'Payout Ratio',
            dataIndex: ['metrics', 'payout_ratio'],
            key: 'payout_ratio',
            render: (ratio: number) => ratio ? `${ratio.toFixed(1)}%` : 'N/A'
        },
        {
            title: 'Debt/Equity',
            dataIndex: ['metrics', 'debt_to_equity'],
            key: 'debt_to_equity',
            render: (de: number) => de ? de.toFixed(2) : 'N/A'
        },
        {
            title: 'Sector',
            dataIndex: 'sector',
            key: 'sector',
            render: (sector: string) => <Tag>{sector}</Tag>
        },
        {
            title: '경고',
            dataIndex: 'warnings',
            key: 'warnings',
            render: (warnings: string[]) => warnings?.length || 0
        }
    ];

    return (
        <div>
            <div style={{ marginBottom: '16px' }}>
                <h3 style={{ color: '#fff', marginBottom: '8px' }}>
                    <SafetyOutlined style={{ marginRight: '8px' }} />
                    배당주 리스크 분석
                </h3>
                <p style={{ color: '#8c8c8c', fontSize: '13px' }}>
                    배당 지속 가능성 평가 (0-100, 낮을수록 안전)
                </p>
            </div>

            <Table
                dataSource={riskData}
                columns={columns}
                loading={loading}
                rowKey="ticker"
                pagination={false}
                style={{ background: '#1a1f3a' }}
            />
        </div>
    );
};

export default RiskScoreTable;
