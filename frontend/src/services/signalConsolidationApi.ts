/**
 * Signal Consolidation API Service
 * 
 * Type-safe API client for consolidated signal endpoints
 * 
 * Created: 2025-12-21
 * Phase: 4 (Frontend Integration)
 */

const API_BASE_URL = '/api';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

export interface ConsolidatedSignal {
    id: number;
    ticker: string;
    action: 'BUY' | 'SELL' | 'HOLD';
    confidence: number;
    source: 'war_room' | 'deep_reasoning' | 'manual_analysis' | 'news_analysis';
    reasoning: string;
    generated_at: string;
    timestamp: string; // Alias for frontend compatibility
    priority: number;
}

export interface SignalsByTicker {
    ticker: string;
    total_signals: number;
    by_source: Record<string, ConsolidatedSignal[]>;
    conflict_detected: boolean;
}

export interface ConsolidationStats {
    total_signals: number;
    by_source: Record<string, number>;
    by_action: Record<string, number>;
    avg_confidence: number;
}

export interface GetSignalsParams {
    source?: string;
    action?: string;
    confidence_min?: number;
    limit?: number;
}

export interface GetSignalsResponse {
    signals: ConsolidatedSignal[];
    total_count: number;
}

// ============================================================================
// API Client
// ============================================================================

export const signalConsolidationApi = {
    /**
     * Get consolidated signals with optional filters
     * GET /api/consolidated-signals
     */
    getConsolidatedSignals: async (params: GetSignalsParams = {}): Promise<GetSignalsResponse> => {
        const queryParams = new URLSearchParams();

        if (params.source) queryParams.append('source', params.source);
        if (params.action) queryParams.append('action', params.action);
        if (params.confidence_min !== undefined) {
            queryParams.append('confidence_min', params.confidence_min.toString());
        }
        if (params.limit) queryParams.append('limit', params.limit.toString());

        const url = `${API_BASE_URL}/consolidated-signals${queryParams.toString() ? `?${queryParams}` : ''}`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Failed to fetch consolidated signals: ${response.statusText}`);
        }

        return response.json();
    },

    /**
     * Get signals grouped by ticker
     * GET /api/consolidated-signals/by-ticker/{ticker}
     */
    getSignalsByTicker: async (ticker: string): Promise<SignalsByTicker> => {
        const response = await fetch(`${API_BASE_URL}/consolidated-signals/by-ticker/${ticker}`);

        if (!response.ok) {
            throw new Error(`Failed to fetch signals for ${ticker}: ${response.statusText}`);
        }

        return response.json();
    },

    /**
     * Get consolidation statistics
     * GET /api/consolidated-signals/stats
     */
    getStats: async (days: number = 7): Promise<ConsolidationStats> => {
        const response = await fetch(`${API_BASE_URL}/consolidated-signals/stats?days=${days}`);

        if (!response.ok) {
            throw new Error(`Failed to fetch consolidation stats: ${response.statusText}`);
        }

        return response.json();
    },
};

export default signalConsolidationApi;
