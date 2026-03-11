"use client";

import { useEffect } from "react";
import { dimensionMetadata } from "../lib/questions";
import { colors } from "../lib/brand";
import { trackEvent } from "../lib/analytics";
import type { Dimension } from "../lib/types";

interface DimensionIntroProps {
  dimension: Dimension;
  onContinue: () => void;
}

export function DimensionIntro({ dimension, onContinue }: DimensionIntroProps) {
  const metadata = dimensionMetadata[dimension];

  // Track dimension start
  useEffect(() => {
    trackEvent(`scorecard_dim_started_${dimension}`);
  }, [dimension]);

  return (
    <div className="max-w-xl mx-auto px-6 py-16 text-center">
      <div className="mb-6">
        <span
          className="text-xs font-medium uppercase tracking-wider"
          style={{ color: metadata.color }}
        >
          Next Section
        </span>
      </div>

      <h2
        className="font-display text-3xl sm:text-4xl font-light mb-4"
        style={{ color: colors.white }}
      >
        {metadata.label}
      </h2>

      <p
        className="text-base sm:text-lg leading-relaxed mb-8"
        style={{ color: colors.slate }}
      >
        {metadata.description}
      </p>

      <button
        onClick={onContinue}
        className="px-8 py-3 rounded-md font-medium transition-colors"
        style={{
          backgroundColor: colors.gold,
          color: colors.navy,
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = colors.goldLight;
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = colors.gold;
        }}
      >
        Continue
      </button>
    </div>
  );
}
