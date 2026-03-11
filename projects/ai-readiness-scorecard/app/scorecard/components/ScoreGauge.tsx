"use client";

import { colors } from "../lib/brand";
import { resultBands } from "../lib/interpretations";
import type { ResultBand } from "../lib/types";

interface ScoreGaugeProps {
  score: number;
  band: ResultBand;
}

export function ScoreGauge({ score, band }: ScoreGaugeProps) {
  const bandInfo = resultBands[band];

  // Calculate position on gradient bar (0-100%)
  const position = score;

  return (
    <div className="text-center">
      {/* Large CRS Number */}
      <div className="mb-6">
        <div
          className="font-sans font-light"
          style={{
            fontSize: "72px",
            lineHeight: "1",
            color: bandInfo.color,
          }}
        >
          {score}
        </div>
        <div className="text-sm mt-2" style={{ color: colors.slate }}>
          out of 100
        </div>
      </div>

      {/* Band Label Pill */}
      <div className="mb-6">
        <span
          className="inline-block px-4 py-2 rounded-md text-sm font-semibold uppercase tracking-wider"
          style={{
            backgroundColor: colors.navyMid,
            color: bandInfo.color,
            border: `2px solid ${bandInfo.color}`,
          }}
        >
          {bandInfo.label}
        </span>
      </div>

      {/* 5-Segment Gradient Bar */}
      <div className="max-w-xl mx-auto">
        <div
          className="h-3 rounded-full relative overflow-hidden"
          style={{
            background: `linear-gradient(to right,
              ${colors.red} 0%,
              ${colors.red} 25%,
              ${colors.orange} 25%,
              ${colors.orange} 45%,
              ${colors.gold} 45%,
              ${colors.gold} 65%,
              ${colors.green} 65%,
              ${colors.green} 80%,
              ${colors.greenLight} 80%,
              ${colors.greenLight} 100%)`,
          }}
        >
          {/* Score Position Indicator */}
          <div
            className="absolute top-1/2 transform -translate-y-1/2 -translate-x-1/2"
            style={{
              left: `${position}%`,
            }}
          >
            <div
              className="w-1 h-6 rounded-full"
              style={{ backgroundColor: colors.white }}
            />
          </div>
        </div>

        {/* Band Labels */}
        <div className="flex justify-between text-xs mt-2">
          <span style={{ color: colors.slateDark }}>0</span>
          <span style={{ color: colors.slateDark }}>25</span>
          <span style={{ color: colors.slateDark }}>45</span>
          <span style={{ color: colors.slateDark }}>65</span>
          <span style={{ color: colors.slateDark }}>80</span>
          <span style={{ color: colors.slateDark }}>100</span>
        </div>
      </div>
    </div>
  );
}
