import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Select, Button, message, Rate, Table, Tag, Divider, Typography } from 'antd';
import { sendFeedback, getFeedbackList } from '../services/api';

const { Option } = Select;
const { TextArea } = Input;
const { Title } = Typography;

const FeedbackDashboard: React.FC = () => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);
    const [feedbacks, setFeedbacks] = useState<any[]>([]);
    const [tableLoading, setTableLoading] = useState(false);

    const fetchFeedbacks = async () => {
        setTableLoading(true);
        try {
            const data = await getFeedbackList(20);
            setFeedbacks(data);
        } catch (error) {
            console.error('Failed to fetch feedbacks:', error);
        } finally {
            setTableLoading(false);
        }
    };

    useEffect(() => {
        fetchFeedbacks();
    }, []);

    const onFinish = async (values: any) => {
        setLoading(true);
        try {
            await sendFeedback({
                target_type: values.target_type,
                target_id: values.target_id || 'general',
                feedback_type: values.rating >= 4 ? 'like' : 'dislike',
                comment: values.comment
            });
            message.success('피드백이 성공적으로 제출되었습니다!');
            form.resetFields();
            fetchFeedbacks(); // Refresh list
        } catch (error) {
            message.error('피드백 제출에 실패했습니다.');
        } finally {
            setLoading(false);
        }
    };

    const columns = [
        {
            title: '날짜',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (text: string) => new Date(text).toLocaleString(),
        },
        {
            title: '카테고리',
            dataIndex: 'target_type',
            key: 'target_type',
            render: (text: string) => {
                const colors: Record<string, string> = {
                    report: 'blue',
                    signal: 'green',
                    briefing: 'purple',
                    app: 'orange'
                };
                return <Tag color={colors[text] || 'default'}>{text.toUpperCase()}</Tag>;
            }
        },
        {
            title: '유형',
            dataIndex: 'feedback_type',
            key: 'feedback_type',
            render: (text: string) => (
                <Tag color={text === 'like' ? 'success' : 'error'}>
                    {text === 'like' ? '좋아요' : '싫어요'}
                </Tag>
            )
        },
        {
            title: '내용',
            dataIndex: 'comment',
            key: 'comment',
        }
    ];

    return (
        <div style={{ padding: '24px', maxWidth: '1000px', margin: '0 auto' }}>
            <Card title="사용자 피드백" variant="borderless" style={{ marginBottom: '24px' }}>
                <Form layout="vertical" form={form} onFinish={onFinish}>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
                        <Form.Item name="target_type" label="피드백 카테고리" rules={[{ required: true, message: '카테고리를 선택해주세요' }]}>
                            <Select placeholder="카테고리 선택">
                                <Option value="report">AI 리포트 품질</Option>
                                <Option value="signal">매매 시그널 정확도</Option>
                                <Option value="briefing">일일 브리핑</Option>
                                <Option value="app">앱 사용 경험</Option>
                            </Select>
                        </Form.Item>

                        <Form.Item name="target_id" label="참조 ID (선택사항)">
                            <Input placeholder="예: 종목코드(NVDA) 또는 리포트 날짜(2025-01-10)" />
                        </Form.Item>
                    </div>

                    <Form.Item name="rating" label="평가" rules={[{ required: true, message: '별점을 입력해주세요' }]}>
                        <Rate count={5} />
                    </Form.Item>

                    <Form.Item name="comment" label="상세 의견">
                        <TextArea rows={3} placeholder="서비스 이용 경험이나 개선할 점을 자유롭게 적어주세요..." />
                    </Form.Item>

                    <Form.Item>
                        <Button type="primary" htmlType="submit" loading={loading} block>
                            피드백 제출
                        </Button>
                    </Form.Item>
                </Form>
            </Card>

            <Card title="최근 피드백 내역" variant="borderless">
                <Table
                    dataSource={feedbacks}
                    columns={columns}
                    rowKey="id"
                    loading={tableLoading}
                    pagination={{ pageSize: 5 }}
                />
            </Card>
        </div>
    );
};

export default FeedbackDashboard;
