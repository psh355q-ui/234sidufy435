/**
 * Emergency Status Hook
 * 
 * Polls emergency status every 60 seconds
 * Provides real-time emergency detection based on Constitution
 */

import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

export interface EmergencyStatus {
    is_emergency: boolean;
    severity: 'normal' | 'low' | 'medium' | 'high' | 'critical';
    triggers: string[];
    recommend_grounding: boolean;
    grounding_searches_today: number;
    daily_limit: number;
    message: string;
    portfolio_data?: {
        daily_loss_pct: number;
        total_drawdown_pct: number;
    };
    vix?: number;
    last_checked: string;
}

export const useEmergencyStatus = () => {
    const { data, isLoading, error } = useQuery<{ data: EmergencyStatus }>({
        queryKey: ['emergency-status'],
        queryFn: () => axios.get('/api/emergency/status'),
        refetchInterval: 60000, // 60 seconds
        refetchIntervalInBackground: true,
        staleTime: 50000, // Consider stale after 50s
    });

    return {
        isEmergency: data?.data.is_emergency || false,
        severity: data?.data.severity || 'normal',
        triggers: data?.data.triggers || [],
        recommended: data?.data.recommend_grounding || false,
        searchesToday: data?.data.grounding_searches_today || 0,
        dailyLimit: data?.data.daily_limit || 10,
        message: data?.data.message || '',
        vix: data?.data.vix,
        portfolioData: data?.data.portfolio_data,
        lastChecked: data?.data.last_checked,
        isLoading,
        error,
    };
};

export interface GroundingUsage {
    today: {
        searches: number;
        cost: number;
        unique_tickers: number;
    };
    this_month: {
        searches: number;
        cost: number;
        unique_tickers: number;
    };
    daily_limit: number;
    monthly_budget: number;
    remaining_daily: number;
    remaining_budget: number;
}

export const useGroundingUsage = () => {
    const { data, isLoading } = useQuery<{ data: GroundingUsage }>({
        queryKey: ['grounding-usage'],
        queryFn: () => axios.get('/api/emergency/grounding/usage'),
        refetchInterval: 300000, // 5 minutes
    });

    return {
        usage: data?.data,
        isLoading,
    };
};
