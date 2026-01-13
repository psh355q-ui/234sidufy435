/**
 * Strategy Card Grid Component
 *
 * Phase 5, T5.3: Strategy Dashboard UI
 *
 * Displays a grid of strategy cards with responsive layout
 */

import React from 'react';
import { StrategyCard } from './StrategyCard';
import type { Strategy } from '../../types/strategy';

interface StrategyCardGridProps {
  strategies: Strategy[];
  positionCounts?: Record<string, number>;
  onStrategyClick?: (strategy: Strategy) => void;
}

export function StrategyCardGrid({
  strategies,
  positionCounts = {},
  onStrategyClick
}: StrategyCardGridProps) {
  if (strategies.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-gray-400 text-4xl mb-4">🤷</div>
        <p className="text-gray-600">전략이 없습니다</p>
        <p className="text-sm text-gray-400 mt-2">
          전략을 생성하여 시작하세요
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {strategies.map((strategy) => (
        <StrategyCard
          key={strategy.id}
          strategy={strategy}
          positionCount={positionCounts[strategy.id] || 0}
          onCardClick={() => onStrategyClick?.(strategy)}
        />
      ))}
    </div>
  );
}
