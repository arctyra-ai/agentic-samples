"use client";

import { colors } from "../lib/brand";

interface ScorecardLandingProps {
  onStart: () => void;
}

export function ScorecardLanding({ onStart }: ScorecardLandingProps) {
  return (
    <div className="max-w-2xl mx-auto px-6 py-16">
      {/* Headline */}
      <h1
        className="font-display text-4xl sm:text-5xl md:text-6xl font-light mb-6 text-center"
        style={{ color: colors.white }}
      >
        How Ready Is Your Organization for AI?
      </h1>

      {/* Subheadline */}
      <p
        className="text-lg sm:text-xl leading-relaxed mb-8 text-center"
        style={{ color: colors.slate }}
      >
        This assessment evaluates your organization across five dimensions of AI readiness. It was designed for technology leaders and business executives at organizations evaluating AI adoption.
      </p>

      {/* Body paragraphs */}
      <div className="space-y-4 mb-10 text-center">
        <p className="text-base leading-relaxed" style={{ color: colors.slate }}>
          Most AI readiness tools measure intent. This scorecard measures capability: whether your data, governance, security, and strategy can support AI adoption today.
        </p>
        <p className="text-base leading-relaxed" style={{ color: colors.slate }}>
          The scorecard was built by practitioners who have led AI adoption, security architecture, and platform modernization. It is independent of any cloud vendor or platform.
        </p>
      </div>

      {/* Details box */}
      <div
        className="rounded-lg p-8 mb-10"
        style={{
          backgroundColor: colors.navyLight,
          borderLeft: `3px solid ${colors.gold}`,
        }}
      >
        <div
          className="text-base leading-relaxed whitespace-pre-line"
          style={{ color: colors.white }}
        >
          17 questions. 6 to 8 minutes.
          <br />
          Immediate results with dimensional scoring.
          <br />
          PDF report delivered to your inbox.
          <br />
          Free. No sales call required to see your results.
        </div>
      </div>

      {/* CTA button */}
      <div className="text-center mb-6">
        <button
          onClick={onStart}
          className="px-10 py-4 rounded-md text-base font-semibold transition-colors"
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
          Get Your AI Readiness Score
        </button>
      </div>

      {/* Privacy text */}
      <p className="text-xs text-center" style={{ color: colors.slateDark }}>
        Your results are confidential and used only to deliver your report.
      </p>
    </div>
  );
}
