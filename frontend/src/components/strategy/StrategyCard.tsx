/**
 * Strategy Card Component
 *
 * Phase 5, T5.3: Strategy Dashboard UI
 *
 * Displays individual strategy information with:
 * - Persona icon and name
 * - Priority badge
 * - Active/Inactive status toggle
 * - Position count
 */

import React from 'react';
import type { Strategy } from '../../types/strategy';
import {
  PERSONA_ICONS,
  PERSONA_NAMES,
  getPriorityColor,
  STRATEGY_COLORS
} from '../../types/strategy';
import { useToggleStrategy } from '../../hooks/useStrategies';

interface StrategyCardProps {
  strategy: Strategy;
  positionCount?: number;
  onCardClick?: () => void;
}

export function StrategyCard({ strategy, positionCount = 0, onCardClick }: StrategyCardProps) {
  const toggleMutation = useToggleStrategy();

  const handleToggleActive = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click event

    toggleMutation.mutate({
      strategyId: strategy.id,
      activate: !strategy.is_active
    });
  };

  const priorityColorClass = getPriorityColor(strategy.priority);
  const strategyColorClass = STRATEGY_COLORS[strategy.persona_type];
  const personaIcon = PERSONA_ICONS[strategy.persona_type];
  const personaName = PERSONA_NAMES[strategy.persona_type];

  return (
    <div
      className={`bg-white rounded-lg shadow-md p-6 border-2 transition-all duration-200 hover:shadow-lg cursor-pointer ${
        strategy.is_active ? 'border-blue-200' : 'border-gray-200 opacity-75'
      }`}
      onClick={onCardClick}
      role="button"
      tabIndex={0}
      aria-label={`${personaName} strategy card`}
    >
      {/* Header: Icon + Name + Priority */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-4xl" role="img" aria-label={`${personaName} icon`}>
            {personaIcon}
          </span>
          <div>
            <h3 className="text-lg font-bold text-gray-800">{personaName}</h3>
            <p className="text-sm text-gray-500">{strategy.name}</p>
          </div>
        </div>
      </div>

      {/* Priority Badge */}
      <div className="mb-4">
        <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${priorityColorClass}`}>
          <span className="mr-1">Priority</span>
          <span className="font-bold">{strategy.priority}</span>
        </div>
      </div>

      {/* Divider */}
      <div className="border-t border-gray-200 my-4"></div>

      {/* Stats */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
            strategy.is_active
              ? 'bg-green-100 text-green-800'
              : 'bg-gray-100 text-gray-600'
          }`}>
            {strategy.is_active ? '✓ Active' : '○ Inactive'}
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-gray-800">{positionCount}</div>
          <div className="text-xs text-gray-500">Positions</div>
        </div>
      </div>

      {/* Toggle Switch */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-100">
        <span className="text-sm text-gray-600">
          {strategy.is_active ? 'Deactivate' : 'Activate'}
        </span>
        <button
          onClick={handleToggleActive}
          disabled={toggleMutation.isPending}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
            strategy.is_active ? 'bg-blue-600' : 'bg-gray-300'
          } ${toggleMutation.isPending ? 'opacity-50 cursor-not-allowed' : ''}`}
          role="switch"
          aria-checked={strategy.is_active}
          aria-label={`Toggle ${personaName} strategy`}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              strategy.is_active ? 'translate-x-6' : 'translate-x-1'
            }`}
          />
        </button>
      </div>

      {/* Time Horizon Badge (optional) */}
      <div className="mt-3">
        <span className="text-xs text-gray-400">
          Time Horizon: <span className="font-medium capitalize">{strategy.time_horizon}</span>
        </span>
      </div>
    </div>
  );
}
