import React from 'react';
import { Card, Row, Col, Statistic } from 'antd';
import {
    DollarOutlined,
    RiseOutlined,
    CalendarOutlined,
    SafetyOutlined
} from '@ant-design/icons';

interface DividendSummaryCardsProps {
    portfolioIncome: any;
}

const DividendSummaryCards: React.FC<DividendSummaryCardsProps> = ({ portfolioIncome }) => {
    const cards = [
        {
            title: '연간 배당 수입 (세후)',
            value: portfolioIncome?.annual_net_krw || 0,
            prefix: '₩',
            suffix: '',
            icon: <DollarOutlined style={{ color: '#52c41a', fontSize: '32px' }} />,
            color: '#1a1f3a'
        },
        {
            title: '월평균 배당금',
            value: portfolioIncome?.monthly_avg_krw || 0,
            prefix: '₩',
            suffix: '/월',
            icon: <CalendarOutlined style={{ color: '#13c2c2', fontSize: '32px' }} />,
            color: '#1a1f3a'
        },
        {
            title: 'YOC (Yield on Cost)',
            value: portfolioIncome?.yoc || 0,
            prefix: '',
            suffix: '%',
            icon: <RiseOutlined style={{ color: '#faad14', fontSize: '32px' }} />,
            color: '#1a1f3a'
        },
        {
            title: '실효 세율',
            value: portfolioIncome?.effective_tax_rate || 0,
            prefix: '',
            suffix: '%',
            icon: <SafetyOutlined style={{ color: '#eb2f96', fontSize: '32px' }} />,
            color: '#1a1f3a'
        }
    ];

    return (
        <Row gutter={[16, 16]}>
            {cards.map((card, index) => (
                <Col xs={24} sm={12} lg={6} key={index}>
                    <Card
                        style={{
                            background: `linear-gradient(135deg, ${card.color} 0%, #0f1729 100%)`,
                            border: '1px solid #2d3748',
                            borderRadius: '12px'
                        }}
                        bodyStyle={{ padding: '20px' }}
                    >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <div style={{ flex: 1 }}>
                                <div style={{ color: '#8c8c8c', fontSize: '12px', marginBottom: '8px' }}>
                                    {card.title}
                                </div>
                                <Statistic
                                    value={card.value}
                                    precision={0}
                                    prefix={card.prefix}
                                    suffix={card.suffix}
                                    valueStyle={{
                                        color: '#fff',
                                        fontSize: '24px',
                                        fontWeight: 'bold'
                                    }}
                                />
                            </div>
                            <div>{card.icon}</div>
                        </div>
                    </Card>
                </Col>
            ))}
        </Row>
    );
};

export default DividendSummaryCards;
