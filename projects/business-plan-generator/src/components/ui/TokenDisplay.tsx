'use client';

import React from 'react';
import { TokenUsage } from '@/lib/types';
import { formatNumber } from '@/lib/utils';
import { estimateCost, formatCost } from '@/lib/pricing';

interface TokenDisplayProps {
  usage: TokenUsage;
  model?: string;
  className?: string;
  compact?: boolean;
}

export function TokenDisplay({ usage, model, className = '', compact = false }: TokenDisplayProps) {
  const cost = model ? estimateCost(model, usage) : 0;

  if (compact) {
    return (
      <div className={`flex items-center space-x-2 text-xs text-slate-400 ${className}`}>
        <span>{formatNumber(usage.totalTokens)} tokens</span>
        {model && cost > 0 && (
          <>
            <span>•</span>
            <span>{formatCost(cost)}</span>
          </>
        )}
      </div>
    );
  }

  return (
    <div className={`bg-slate-800 rounded-lg p-3 ${className}`}>
      <h4 className="text-sm font-medium text-slate-300 mb-2">Token Usage</h4>
      <div className="grid grid-cols-3 gap-3 text-center">
        <div>
          <div className="text-lg font-semibold text-slate-100">
            {formatNumber(usage.inputTokens)}
          </div>
          <div className="text-xs text-slate-400">Input</div>
        </div>
        <div>
          <div className="text-lg font-semibold text-slate-100">
            {formatNumber(usage.outputTokens)}
          </div>
          <div className="text-xs text-slate-400">Output</div>
        </div>
        <div>
          <div className="text-lg font-semibold text-slate-100">
            {formatNumber(usage.totalTokens)}
          </div>
          <div className="text-xs text-slate-400">Total</div>
        </div>
      </div>
      {model && cost > 0 && (
        <div className="mt-2 pt-2 border-t border-slate-700 text-center">
          <span className="text-sm text-slate-300">Estimated Cost: </span>
          <span className="text-sm font-semibold text-green-400">{formatCost(cost)}</span>
        </div>
      )}
    </div>
  );
}