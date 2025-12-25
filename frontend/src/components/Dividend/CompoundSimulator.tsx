import React, { useState } from 'react';
import { Card, Form, InputNumber, Switch, Button, message } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { RiseOutlined } from '@ant-design/icons';

const CompoundSimulator: React.FC = () => {
    const [results, setResults] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);

    const onFinish = async (values: any) => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8001/api/dividend/simulate/drip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    initial_usd: values.initial || 100000,
                    monthly_contribution_usd: values.monthly || 1000,
                    years: values.years || 10,
                    cagr: values.cagr || 7,
                    dividend_yield: values.yield || 4,
                    reinvest: values.reinvest !== false
                })
            });

            if (!response.ok) throw new Error('Failed to simulate');

            const data = await response.json();
            setResults(data.results || []);
            message.success(`${values.years}년 시뮬레이션 완료!`);
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
                    <RiseOutlined style={{ marginRight: '8px' }} />
                    DRIP 복리 시뮬레이터
                </h3>
                <p style={{ color: '#8c8c8c', fontSize: '13px' }}>
                    배당 재투자 시 포트폴리오 성장 예측
                </p>
            </div>

            <Card style={{ background: '#1a1f3a', border: '1px solid #2d3748' }}>
                <Form
                    layout="inline"
                    onFinish={onFinish}
                    initialValues={{ initial: 100000, monthly: 1000, years: 10, cagr: 7, yield: 4, reinvest: true }}
                >
                    <Form.Item label={<span style={{ color: '#fff' }}>초기 투자</span>} name="initial">
                        <InputNumber min={0} step={10000} addonAfter="USD" style={{ width: 150 }} />
                    </Form.Item>
                    <Form.Item label={<span style={{ color: '#fff' }}>월 적립</span>} name="monthly">
                        <InputNumber min={0} step={100} addonAfter="USD" style={{ width: 150 }} />
                    </Form.Item>
                    <Form.Item label={<span style={{ color: '#fff' }}>기간</span>} name="years">
                        <InputNumber min={1} max={30} addonAfter="년" style={{ width: 120 }} />
                    </Form.Item>
                    <Form.Item label={<span style={{ color: '#fff' }}>CAGR</span>} name="cagr">
                        <InputNumber min={0} max={20} step={0.5} addonAfter="%" style={{ width: 120 }} />
                    </Form.Item>
                    <Form.Item label={<span style={{ color: '#fff' }}>배당률</span>} name="yield">
                        <InputNumber min={0} max={15} step={0.5} addonAfter="%" style={{ width: 120 }} />
                    </Form.Item>
                    <Form.Item label={<span style={{ color: '#fff' }}>재투자</span>} name="reinvest" valuePropName="checked">
                        <Switch />
                    </Form.Item>
                    <Form.Item>
                        <Button type="primary" htmlType="submit" loading={loading}>
                            시뮬레이션
                        </Button>
                    </Form.Item>
                </Form>
            </Card>

            {results.length > 0 && (
                <Card style={{ background: '#1a1f3a', border: '1px solid #2d3748', marginTop: '24px' }}>
                    <ResponsiveContainer width="100%" height={400}>
                        <LineChart data={results}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
                            <XAxis dataKey="year" stroke="#8c8c8c" label={{ value: 'Year', position: 'insideBottom', offset: -5 }} />
                            <YAxis stroke="#8c8c8c" tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`} />
                            <Tooltip
                                contentStyle={{ background: '#1a1f3a', border: '1px solid #2d3748' }}
                                labelStyle={{ color: '#fff' }}
                                formatter={(value: any) => `$${value.toLocaleString()}`}
                            />
                            <Legend />
                            <Line type="monotone" dataKey="portfolio_value_usd" stroke="#52c41a" name="Portfolio Value" strokeWidth={2} />
                            <Line type="monotone" dataKey="cumulative_dividends_usd" stroke="#1890ff" name="Cumulative Dividends" strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                </Card>
            )}
        </div>
    );
};

export default CompoundSimulator;
