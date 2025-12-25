import React, { useState, useEffect } from 'react';
import { Table, Tag, message } from 'antd';
import { TrophyOutlined } from '@ant-design/icons';

const AristocratsTable: React.FC = () => {
    const [aristocrats, setAristocrats] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchAristocrats();
    }, []);

    const fetchAristocrats = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8001/api/dividend/aristocrats');
            if (!response.ok) throw new Error('Failed to fetch aristocrats');

            const data = await response.json();
            setAristocrats(data.aristocrats || []);
        } catch (error: any) {
            message.error(`귀족주 조회 실패: ${error.message}`);
        } finally {
            setLoading(false);
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
            title: 'Company',
            dataIndex: 'company_name',
            key: 'company_name'
        },
        {
            title: '연속 배당 증가',
            dataIndex: 'consecutive_years',
            key: 'consecutive_years',
            sorter: (a: any, b: any) => b.consecutive_years - a.consecutive_years,
            render: (years: number) => (
                <Tag color="green">{years}년</Tag>
            )
        },
        {
            title: '현재 배당률',
            dataIndex: 'current_yield',
            key: 'current_yield',
            render: (yield_val: number) => yield_val ? `${yield_val.toFixed(2)}%` : 'N/A'
        },
        {
            title: 'Sector',
            dataIndex: 'sector',
            key: 'sector',
            render: (sector: string) => <Tag>{sector}</Tag>
        }
    ];

    return (
        <div>
            <div style={{ marginBottom: '16px' }}>
                <h3 style={{ color: '#fff', marginBottom: '8px' }}>
                    <TrophyOutlined style={{ marginRight: '8px', color: '#faad14' }} />
                    배당 귀족주 (Dividend Aristocrats)
                </h3>
                <p style={{ color: '#8c8c8c', fontSize: '13px' }}>
                    25년 이상 연속 배당금을 증가시킨 우량 배당주 ({aristocrats.length}개)
                </p>
            </div>

            <Table
                dataSource={aristocrats}
                columns={columns}
                loading={loading}
                rowKey="ticker"
                pagination={{ pageSize: 10 }}
                style={{ background: '#1a1f3a' }}
            />
        </div>
    );
};

export default AristocratsTable;
