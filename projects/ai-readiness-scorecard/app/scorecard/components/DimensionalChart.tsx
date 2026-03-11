"use client";

import { dimensionMetadata } from "../lib/questions";
import { colors } from "../lib/brand";
import type { DimensionScore } from "../lib/types";

interface DimensionalChartProps {
  scores: DimensionScore[];
}

export function DimensionalChart({ scores }: DimensionalChartProps) {
  // Signal dimensions (1 question each)
  const signalDimensions = ["technical-capability", "organizational-maturity"];

  return (
    <div className="space-y-6">
      {scores.map((score) => {
        const metadata = dimensionMetadata[score.dimension];
        const percentage = Math.round(score.percentage);
        const isSignal = signalDimensions.includes(score.dimension);

        return (
          <div key={score.dimension}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span
                  className="text-sm font-medium"
                  style={{ color: colors.white }}
                >
                  {metadata.label}
                </span>
                {isSignal && (
                  <span
                    className="text-xs font-medium uppercase tracking-wider px-2 py-0.5 rounded"
                    style={{
                      backgroundColor: colors.navyMid,
                      color: colors.slateDark,
                      fontSize: "10px",
                    }}
                  >
                    signal
                  </span>
                )}
              </div>
              <div className="flex items-center gap-3">
                <span
                  className="text-xs"
                  style={{ color: colors.slateDark }}
                >
                  {metadata.weight}% weight
                </span>
                <span
                  className="text-sm font-mono tabular-nums font-semibold"
                  style={{ color: metadata.color }}
                >
                  {percentage}%
                </span>
              </div>
            </div>

            {/* Progress bar */}
            <div
              className="h-2.5 rounded-full overflow-hidden"
              style={{ backgroundColor: colors.navyMid }}
            >
              <div
                className="h-full rounded-full transition-all duration-700 ease-out"
                style={{
                  width: `${percentage}%`,
                  backgroundColor: metadata.color,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
