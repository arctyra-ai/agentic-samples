'use client';

import React from 'react';

interface ProgressBarProps {
  current: number;
  total: number;
  showLabels?: boolean;
  className?: string;
}

export function ProgressBar({ current, total, showLabels = false, className = '' }: ProgressBarProps) {
  const percentage = Math.round((current / total) * 100);

  return (
    <div className={className} role="progressbar" aria-valuenow={current} aria-valuemin={0} aria-valuemax={total} aria-label={`Step ${current} of ${total}`}>
      {showLabels && (
        <div className="flex justify-between text-sm text-slate-400 mb-2">
          <span>Step {current} of {total}</span>
          <span>{percentage}%</span>
        </div>
      )}
      <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-blue-600 to-purple-600 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}