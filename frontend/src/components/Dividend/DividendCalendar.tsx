import React, { useState, useEffect } from 'react';
import { Card, message, Empty } from 'antd';
import { Calendar as AntCalendar } from 'antd';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';

const DividendCalendar: React.FC = () => {
    const [upcomingDividends, setUpcomingDividends] = useState<any[]>([]);

    useEffect(() => {
        fetchUpcomingDividends();
    }, []);

    const fetchUpcomingDividends = async () => {
        try {
            const response = await fetch('http://localhost:8001/api/dividend/calendar');
            if (!response.ok) throw new Error('Failed to fetch calendar');

            const data = await response.json();
            setUpcomingDividends(data.events || []);
        } catch (error) {
            console.error('Calendar fetch error:', error);
        }
    };

    const dateCellRender = (value: Dayjs) => {
        const dateStr = value.format('YYYY-MM-DD');
        const events = upcomingDividends.filter(e => e.ex_dividend_date === dateStr);

        return (
            <ul style={{ listStyle: 'none', padding: 0 }}>
                {events.map((event, index) => (
                    <li key={index} style={{
                        fontSize: '11px',
                        color: '#52c41a',
                        background: '#f0f9ff',
                        padding: '2px 4px',
                        borderRadius: '4px',
                        marginBottom: '2px'
                    }}>
                        {event.ticker}: ${event.amount}
                    </li>
                ))}
            </ul>
        );
    };

    return (
        <div>
            <div style={{ marginBottom: '16px', color: '#fff' }}>
                <h3 style={{ color: '#fff', marginBottom: '8px' }}>배당락일 달력</h3>
                <p style={{ color: '#8c8c8c', fontSize: '13px' }}>
                    다가오는 배당락일 ({upcomingDividends.length}개)
                </p>
            </div>

            <Card style={{ background: '#fff' }}>
                <AntCalendar
                    dateCellRender={dateCellRender}
                    style={{ border: 'none' }}
                />
            </Card>
        </div>
    );
};

export default DividendCalendar;
