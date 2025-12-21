/**
 * War Room API Service
 * 
 * Type-safe API client for War Room debate endpoints
 * 
 * Created: 2025-12-21
 * Phase: 4 (Frontend Integration)
 */

const API_BASE_URL = '/api';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

export interface WarRoomVote {
    agent: string;
    action: 'BUY' | 'SELL' | 'HOLD';
    confidence: number;
    reasoning: string;
    risk_factors?: Record<string, any>;
    technical_factors?: Record<string, any>;
    macro_factors?: Record<string, any>;
    institutional_factors?: Record<string, any>;
    fundamental_factors?: Record<string, any>;
}

export interface WarRoomConsensus {
    action: 'BUY' | 'SELL' | 'HOLD';
    confidence: number;
    summary: string;
}

export interface WarRoomDebateResponse {
    session_id: number;
    ticker: string;
    votes: WarRoomVote[];
    consensus: WarRoomConsensus;
    constitutional_valid: boolean;
    signal_id: number | null;
    timestamp: string;
}

export interface DebateSession {
    id: number;
    ticker: string;
    consensus_action: 'BUY' | 'SELL' | 'HOLD';
    consensus_confidence: number;
    constitutional_valid: boolean;
    agent_votes: Record<string, any>;
    signal_generated: boolean;
    created_at: string;
}

export interface WarRoomHealthResponse {
    agents: string[];
    healthy: boolean;
    total_agents: number;
}

// ============================================================================
// API Client
// ============================================================================

export const warRoomApi = {
    /**
     * Run War Room debate for a ticker
     * POST /api/war-room/debate
     */
    runDebate: async (ticker: string): Promise<WarRoomDebateResponse> => {
        const response = await fetch(`${API_BASE_URL}/war-room/debate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ticker }),
        });

        if (!response.ok) {
            throw new Error(`War Room debate failed: ${response.statusText}`);
        }

        return response.json();
    },

    /**
     * Get War Room debate session history
     * GET /api/war-room/sessions
     */
    getSessions: async (params: { limit?: number } = {}): Promise<DebateSession[]> => {
        const queryParams = new URLSearchParams();
        if (params.limit) {
            queryParams.append('limit', params.limit.toString());
        }

        const url = `${API_BASE_URL}/war-room/sessions${queryParams.toString() ? `?${queryParams}` : ''}`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Failed to fetch War Room sessions: ${response.statusText}`);
        }

        return response.json();
    },

    /**
     * Get War Room health status
     * GET /api/war-room/health
     */
    getHealth: async (): Promise<WarRoomHealthResponse> => {
        const response = await fetch(`${API_BASE_URL}/war-room/health`);

        if (!response.ok) {
            throw new Error(`Failed to fetch War Room health: ${response.statusText}`);
        }

        return response.json();
    },
};

export default warRoomApi;
