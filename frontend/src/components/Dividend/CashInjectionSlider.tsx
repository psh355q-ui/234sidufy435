import React, { useState } from 'react';
import { Card, Slider, Button, Statistic, Row, Col, message } from 'antd';
import { PlusCircleOutlined, ArrowUpOutlined } from '@ant-design/icons';

interface CashInjectionSliderProps {
    portfolioIncome: any;
}

const CashInjectionSlider: React.FC<CashInjectionSliderProps> = ({ portfolioIncome }) => {
    const [injectionAmount, setInjectionAmount] = useState(10000);
    const [simulationResult, setSimulationResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const handleSimulate = async () => {
        setLoading(true);
        try {
            // 예시 포지션
            const positions = [
                { ticker: 'JNJ', shares: 100, avg_price: 150 },
                { ticker: 'PG', shares: 50, avg_price: 145 },
                { ticker: 'KO', shares: 150, avg_price: 60 }
            ];

            const response = await fetch('http://localhost:8001/api/dividend/simulate/injection', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    inject_amount_usd: injectionAmount
                }),
                // Pass positions as query params or find another way
            });

            if (!response.ok) throw new Error('Failed to simulate injection');

            const data = await response.json();
            setSimulationResult(data);
            message.success('예수금 추가 시뮬레이션 완료!');
        } catch (error: any) {
            message.error(`시뮬레이션 실패: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div style={{ marginBottom: '16px' }}>
                <h3 style={{ color: '#fff', marginBottom: '8px' }}>
                    <PlusCircleOutlined style={{ marginRight: '8px' }} />
                    예수금 추가 시뮬레이션
                </h3>
                <p style={{ color: '#8c8c8c', fontSize: '13px' }}>
                    추가 투자 시 배당 수입 변화 예측
                </p>
            </div>

            <Card style={{ background: '#1a1f3a', border: '1px solid #2d3748' }}>
                <div style={{ marginBottom: '24px' }}>
                    <div style={{ color: '#fff', marginBottom: '16px' }}>
                        추가 투자 금액: <strong style={{ color: '#52c41a' }}>${injectionAmount.toLocaleString()}</strong>
                    </div>
                    <Slider
                        min={1000}
                        max={100000}
                        step={1000}
                        value={injectionAmount}
                        onChange={(value) => setInjectionAmount(value)}
                        marks={{
                            1000: '$1K',
                            25000: '$25K',
                            50000: '$50K',
                            75000: '$75K',
                            100000: '$100K'
                        }}
                    />
                </div>

                <Button
                    type="primary"
                    icon={<ArrowUpOutlined />}
                    onClick={handleSimulate}
                    loading={loading}
                    size="large"
                    block
                >
                    시뮬레이션 실행
                </Button>
            </Card>

            {simulationResult && (
                <Card style={{ background: '#1a1f3a', border: '1px solid #2d3748', marginTop: '24px' }}>
                    <Row gutter={[16, 16]}>
                        <Col span={8}>
                            <Statistic
                                title={<span style={{ color: '#8c8c8c' }}>현재 연간 배당</span>}
                                value={simulationResult.before?.annual_net_krw || 0}
                                precision={0}
                                prefix="₩"
                                valueStyle={{ color: '#fff' }}
                            />
                        </Col>
                        <Col span={8}>
                            <Statistic
                                title={<span style={{ color: '#8c8c8c' }}>추가 후 연간 배당</span>}
                                value={simulationResult.after?.annual_net_krw || 0}
                                precision={0}
                                prefix="₩"
                                valueStyle={{ color: '#52c41a' }}
                            />
                        </Col>
                        <Col span={8}>
                            <Statistic
                                title={<span style={{ color: '#8c8c8c' }}>증가량</span>}
                                value={simulationResult.increase?.annual_krw || 0}
                                precision={0}
                                prefix="₩ +"
                                suffix={`(+${simulationResult.increase?.percentage || 0}%)`}
                                valueStyle={{ color: '#1890ff' }}
                            />
                        </Col>
                    </Row>
                </Card>
            )}
        </div>
    );
};

export default CashInjectionSlider;
