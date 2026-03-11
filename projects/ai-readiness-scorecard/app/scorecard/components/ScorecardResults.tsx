"use client";

import { useState } from "react";
import jsPDF from "jspdf";
import { ScoreGauge } from "./ScoreGauge";
import { DimensionalChart } from "./DimensionalChart";
import { colors } from "../lib/brand";
import { resultBands, getDimensionInsight, BAND_COPY } from "../lib/interpretations";
import { dimensionMetadata } from "../lib/questions";
import { getDimensionBand } from "../lib/scoring";
import { trackEvent } from "../lib/analytics";
import type { ScorecardResults as Results, EmailFormData } from "../lib/types";

interface ScorecardResultsProps {
  results: Results;
  emailData: EmailFormData;
  onRestart?: () => void;
}

export function ScorecardResults({ results, emailData, onRestart }: ScorecardResultsProps) {
  const bandInfo = resultBands[results.band];
  const bandCopy = BAND_COPY[results.band];
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownloadPDF = () => {
    try {
      setIsDownloading(true);
      trackEvent("scorecard_pdf_downloaded", {
        crs: results.overallScore,
        band: results.band,
      });

      // Create PDF using jsPDF with built-in Helvetica
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const leftMargin = 20;
      const rightMargin = 20;
      const maxWidth = pageWidth - leftMargin - rightMargin;

      // Colors (RGB values from brand)
      const navy = [11, 17, 32];
      const gold = [201, 168, 76];
      const gray = [123, 134, 152];
      const red = [196, 75, 75];
      const orange = [212, 136, 60];
      const green = [75, 139, 110];

      // Helper: Get band color
      const getBandColor = (band: string): number[] => {
        if (band === "foundational") return red;
        if (band === "developing") return orange;
        if (band === "progressing") return gold;
        if (band === "advanced" || band === "leading") return green;
        return gold;
      };

      // Helper: Get dimension band color
      const getDimBandColor = (band: string): number[] => {
        if (band === "low") return red;
        if (band === "moderate") return orange;
        return green;
      };

      // Helper: Add page header
      const addPageHeader = (pageNum: number) => {
        doc.setDrawColor(gold[0], gold[1], gold[2]);
        doc.setLineWidth(0.5);
        doc.line(leftMargin, 15, pageWidth - rightMargin, 15);
        doc.setFontSize(8);
        doc.setTextColor(gold[0], gold[1], gold[2]);
        doc.text("AI READINESS SCORECARD", leftMargin, 12);
        doc.text(`${pageNum}`, pageWidth - rightMargin, 12, { align: "right" });
      };

      // Priority actions mapping
      const priorityActions: Record<string, Record<string, string>> = {
        "data-infrastructure": {
          low: "Conduct a formal data quality and governance assessment for your most business-critical datasets",
          moderate: "Prioritize a structured data readiness assessment for your highest-priority AI use cases",
          strong: "Ensure your data pipeline architecture can serve the specific AI systems you plan to deploy",
        },
        "technical-capability": {
          low: "Assess whether your infrastructure can support AI workloads and identify required upgrades",
          moderate: "Evaluate managed AI services and third-party tools that work within your current infrastructure",
          strong: "Design the architecture for your highest-priority AI initiative",
        },
        "organizational-maturity": {
          low: "Build executive understanding and commitment before committing resources to AI projects",
          moderate: "Formalize executive sponsorship with defined metrics, budget, and accountability",
          strong: "Ensure executive engagement remains active as AI initiatives move from strategy to execution",
        },
        "governance-risk": {
          low: "Establish a baseline AI use policy and gain visibility into current AI tool usage",
          moderate: "Strengthen governance before expanding AI usage to prevent accumulation of unmanaged risk",
          strong: "Ensure governance scales with the complexity and scope of your AI program",
        },
        "strategic-alignment": {
          low: "Identify 1 to 3 specific, concrete problems that AI could address and evaluate whether the investment is justified",
          moderate: "Build a structured AI roadmap that translates interest into a defensible plan",
          strong: "Move directly to architecture and implementation for your prioritized use cases",
        },
      };

      const formatDate = new Date(results.timestamp).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });

      // ========== PAGE 1: COVER ==========
      doc.setFont("helvetica", "normal");
      doc.setFontSize(14);
      doc.setTextColor(gold[0], gold[1], gold[2]);
      doc.text("AI READINESS SCORECARD", pageWidth / 2, 40, { align: "center" });

      // Horizontal gold line
      doc.setDrawColor(gold[0], gold[1], gold[2]);
      doc.setLineWidth(0.5);
      doc.line(pageWidth / 2 - 30, 43, pageWidth / 2 + 30, 43);

      doc.setFontSize(24);
      doc.setTextColor(navy[0], navy[1], navy[2]);
      doc.text("AI Readiness Scorecard", pageWidth / 2, 60, { align: "center" });

      doc.setFontSize(14);
      doc.text(`Results for ${emailData.company}`, pageWidth / 2, 72, { align: "center" });

      // Details block (left-aligned)
      let yPos = 100;
      doc.setFontSize(10);
      doc.setTextColor(navy[0], navy[1], navy[2]);
      doc.text(`Prepared for: ${emailData.firstName} ${emailData.lastName}, ${emailData.jobTitle}`, leftMargin, yPos);
      yPos += 6;
      doc.text(`Organization: ${emailData.company}`, leftMargin, yPos);
      yPos += 6;
      doc.text(`Industry: ${emailData.industry}`, leftMargin, yPos);
      yPos += 6;
      doc.text(`Company Size: ${emailData.companySize}`, leftMargin, yPos);
      yPos += 6;
      doc.text(`Date: ${formatDate}`, leftMargin, yPos);

      // Footer
      doc.setFontSize(9);
      doc.setTextColor(gold[0], gold[1], gold[2]);
      doc.text("[your-domain]", pageWidth / 2, pageHeight - 20, { align: "center" });

      doc.setFontSize(8);
      doc.setTextColor(gray[0], gray[1], gray[2]);
      doc.text("Confidential", pageWidth - rightMargin, pageHeight - 15, { align: "right" });

      // ========== PAGE 2: COMPOSITE SCORE + DIMENSIONAL OVERVIEW ==========
      doc.addPage();
      addPageHeader(2);

      yPos = 25;
      doc.setFontSize(10);
      doc.setTextColor(gold[0], gold[1], gold[2]);
      doc.text("COMPOSITE READINESS SCORE", leftMargin, yPos);

      yPos += 10;
      doc.setFontSize(48);
      doc.setTextColor(navy[0], navy[1], navy[2]);
      doc.text(`${results.overallScore}`, pageWidth / 2, yPos, { align: "center" });

      yPos += 3;
      doc.setFontSize(10);
      doc.setTextColor(gray[0], gray[1], gray[2]);
      doc.text("out of 100", pageWidth / 2, yPos, { align: "center" });

      yPos += 8;
      const bandColor = getBandColor(results.band);
      doc.setFontSize(12);
      doc.setTextColor(bandColor[0], bandColor[1], bandColor[2]);
      doc.text(bandInfo.label.toUpperCase(), pageWidth / 2, yPos, { align: "center" });

      // Band interpretation paragraph
      yPos += 10;
      doc.setFontSize(10);
      doc.setTextColor(navy[0], navy[1], navy[2]);
      const bandBodyLines = doc.splitTextToSize(bandCopy.body.split("\n\n")[0], maxWidth);
      doc.text(bandBodyLines, leftMargin, yPos);
      yPos += bandBodyLines.length * 5;

      // Divider line
      yPos += 5;
      doc.setDrawColor(gold[0], gold[1], gold[2]);
      doc.setLineWidth(0.3);
      doc.line(leftMargin, yPos, pageWidth - rightMargin, yPos);
      yPos += 8;

      // Dimensional Scores section
      doc.setFontSize(10);
      doc.setTextColor(gold[0], gold[1], gold[2]);
      doc.text("DIMENSIONAL SCORES", leftMargin, yPos);
      yPos += 8;

      // Draw dimensional bars
      results.dimensionScores.forEach((dimScore) => {
        const metadata = dimensionMetadata[dimScore.dimension];
        const band = getDimensionBand(dimScore.score);
        const barColor = getDimBandColor(band);
        const isSignal = ["technical-capability", "organizational-maturity"].includes(dimScore.dimension);
        const weight = metadata.weight;

        doc.setFontSize(9);
        doc.setTextColor(navy[0], navy[1], navy[2]);
        doc.text(metadata.label, leftMargin, yPos);

        const scoreText = `${dimScore.score.toFixed(1)} / 5.0`;
        doc.text(scoreText, pageWidth - rightMargin, yPos, { align: "right" });

        yPos += 4;

        // Draw bar (filled + unfilled)
        const barWidth = maxWidth * 0.8;
        const barHeight = 4;
        const fillWidth = (dimScore.score / 5.0) * barWidth;

        // Filled portion
        doc.setFillColor(barColor[0], barColor[1], barColor[2]);
        doc.rect(leftMargin, yPos, fillWidth, barHeight, "F");

        // Unfilled portion
        doc.setDrawColor(gray[0], gray[1], gray[2]);
        doc.setLineWidth(0.3);
        doc.rect(leftMargin, yPos, barWidth, barHeight, "S");

        yPos += barHeight + 3;

        // Weight label
        doc.setFontSize(8);
        doc.setTextColor(gray[0], gray[1], gray[2]);
        const weightLabel = isSignal ? `Weight: ${weight}% (signal assessment)` : `Weight: ${weight}%`;
        doc.text(weightLabel, leftMargin, yPos);

        yPos += 7;
      });

      // Methodology note
      yPos += 3;
      doc.setFontSize(8);
      doc.setTextColor(gray[0], gray[1], gray[2]);
      const methodologyText = "Scoring methodology: Dimensions are weighted. Data Infrastructure and Governance & Risk Readiness each carry 25%. Technical Capability carries 20%. Organizational Maturity carries 15%. Strategic Alignment carries 15%.";
      const methodologyLines = doc.splitTextToSize(methodologyText, maxWidth);
      doc.text(methodologyLines, leftMargin, yPos);

      // ========== PAGE 3: DIMENSION ANALYSIS ==========
      doc.addPage();
      addPageHeader(3);

      yPos = 25;
      doc.setFontSize(10);
      doc.setTextColor(gold[0], gold[1], gold[2]);
      doc.text("DIMENSION ANALYSIS", leftMargin, yPos);
      yPos += 10;

      let pageNum = 3;
      results.dimensionScores.forEach((dimScore, index) => {
        const metadata = dimensionMetadata[dimScore.dimension];
        const band = getDimensionBand(dimScore.score);
        const insight = getDimensionInsight(dimScore.dimension, dimScore.score);
        const priorityAction = priorityActions[dimScore.dimension]?.[band] || "";

        // Check if we need a new page
        if (yPos > pageHeight - 60) {
          doc.addPage();
          pageNum++;
          addPageHeader(pageNum);
          yPos = 25;
        }

        // Dimension name and score
        doc.setFontSize(11);
        doc.setFont("helvetica", "bold");
        doc.setTextColor(navy[0], navy[1], navy[2]);
        doc.text(metadata.label, leftMargin, yPos);

        const scoreLine = `${dimScore.score.toFixed(1)} / 5.0 — ${band.charAt(0).toUpperCase() + band.slice(1)}`;
        doc.text(scoreLine, pageWidth - rightMargin, yPos, { align: "right" });
        yPos += 6;

        // Interpretation paragraph
        doc.setFont("helvetica", "normal");
        doc.setFontSize(10);
        doc.setTextColor(navy[0], navy[1], navy[2]);
        const insightLines = doc.splitTextToSize(insight, maxWidth);
        doc.text(insightLines, leftMargin, yPos);
        yPos += insightLines.length * 5 + 3;

        // Priority action
        doc.setFont("helvetica", "bold");
        doc.setFontSize(9);
        doc.setTextColor(navy[0], navy[1], navy[2]);
        doc.text("Priority action:", leftMargin, yPos);
        yPos += 4;

        doc.setFont("helvetica", "normal");
        const actionLines = doc.splitTextToSize(priorityAction, maxWidth);
        doc.text(actionLines, leftMargin, yPos);
        yPos += actionLines.length * 4 + 4;

        // Gray divider line (except after last dimension)
        if (index < results.dimensionScores.length - 1) {
          doc.setDrawColor(gray[0], gray[1], gray[2]);
          doc.setLineWidth(0.3);
          doc.line(leftMargin, yPos, pageWidth - rightMargin, yPos);
          yPos += 6;
        }
      });

      // ========== PAGE 4: RECOMMENDED NEXT STEP + UPGRADE ==========
      doc.addPage();
      pageNum++;
      addPageHeader(pageNum);

      yPos = 25;
      doc.setFontSize(10);
      doc.setTextColor(gold[0], gold[1], gold[2]);
      doc.text("RECOMMENDED NEXT STEP", leftMargin, yPos);
      yPos += 8;

      doc.setFontSize(14);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(navy[0], navy[1], navy[2]);
      doc.text(bandCopy.service, leftMargin, yPos);
      yPos += 8;

      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      const serviceLines = doc.splitTextToSize(bandCopy.serviceDesc, maxWidth);
      doc.text(serviceLines, leftMargin, yPos);
      yPos += serviceLines.length * 5 + 6;

      doc.setFont("helvetica", "bold");
      doc.text("Book a 30-Minute Discovery Call", leftMargin, yPos);
      yPos += 5;

      doc.setFont("helvetica", "normal");
      doc.text("No pitch. A structured conversation about your specific situation.", leftMargin, yPos);
      yPos += 5;

      doc.setTextColor(gold[0], gold[1], gold[2]);
      doc.text("[Your booking link]", leftMargin, yPos);
      yPos += 10;

      // Divider line
      doc.setDrawColor(gold[0], gold[1], gold[2]);
      doc.setLineWidth(0.3);
      doc.line(leftMargin, yPos, pageWidth - rightMargin, yPos);
      yPos += 8;

      // GO DEEPER section
      doc.setFontSize(10);
      doc.setTextColor(gold[0], gold[1], gold[2]);
      doc.text("GO DEEPER: FULL AI READINESS ASSESSMENT", leftMargin, yPos);
      yPos += 8;

      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(navy[0], navy[1], navy[2]);
      const upgradeIntro = "This scorecard assessed all five dimensions, with detailed scoring on three and directional scoring on two. The full assessment provides:";
      const upgradeIntroLines = doc.splitTextToSize(upgradeIntro, maxWidth);
      doc.text(upgradeIntroLines, leftMargin, yPos);
      yPos += upgradeIntroLines.length * 5 + 4;

      // Bulleted list (use dashes)
      const bullets = [
        "27 questions across all 5 dimensions in full detail",
        "Peer benchmarking against organizations of your size and industry",
        "Sub-dimensional analysis with per-question scoring",
        "15 prioritized actions, sequenced by urgency",
        "12-month action plan with quarterly milestones",
        "Board-ready executive summary",
      ];

      bullets.forEach((bullet) => {
        doc.text(`- ${bullet}`, leftMargin + 3, yPos);
        yPos += 5;
      });

      yPos += 3;
      const closingText = "This scorecard shows where you stand. The full assessment provides the specific, sequenced actions to move forward.";
      const closingLines = doc.splitTextToSize(closingText, maxWidth);
      doc.text(closingLines, leftMargin, yPos);
      yPos += closingLines.length * 5 + 4;

      doc.setFont("helvetica", "bold");
      doc.text("Contact us: [your-domain]/contact", leftMargin, yPos);

      // Footer
      yPos = pageHeight - 25;
      doc.setFontSize(9);
      doc.setTextColor(gray[0], gray[1], gray[2]);
      doc.text("Generated by AI Readiness Scorecard", leftMargin, yPos);
      yPos += 5;
      doc.text(`Confidential — prepared exclusively for ${emailData.company}`, leftMargin, yPos);

      // Save PDF
      const filename = `ai-readiness-scorecard-${emailData.company.replace(/[^a-z0-9]/gi, "-").toLowerCase()}.pdf`;
      doc.save(filename);
    } catch (error) {
      console.error("PDF generation error:", error);
      alert("Failed to generate PDF. Please try again.");
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      {/* Header */}
      <div className="text-center mb-12">
        <h1
          className="font-display text-3xl sm:text-4xl font-light mb-2"
          style={{ color: colors.white }}
        >
          Your AI Readiness Results
        </h1>

        {/* PDF Download Button */}
        <button
          onClick={handleDownloadPDF}
          disabled={isDownloading}
          className="inline-flex items-center gap-2 px-6 py-2.5 rounded-md text-sm font-medium transition-colors mt-4"
          style={{
            backgroundColor: isDownloading ? colors.navyMid : colors.navyLight,
            color: isDownloading ? colors.slateDark : colors.gold,
            border: `1px solid ${colors.gold}`,
            cursor: isDownloading ? "not-allowed" : "pointer",
          }}
          onMouseEnter={(e) => {
            if (!isDownloading) {
              e.currentTarget.style.backgroundColor = colors.navyMid;
            }
          }}
          onMouseLeave={(e) => {
            if (!isDownloading) {
              e.currentTarget.style.backgroundColor = colors.navyLight;
            }
          }}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          {isDownloading ? "Downloading..." : "Download PDF Report"}
        </button>
      </div>

      {/* Score Display */}
      <div
        className="rounded-lg p-8 sm:p-12 mb-8"
        style={{ backgroundColor: colors.navyLight }}
      >
        <ScoreGauge score={results.overallScore} band={results.band} />
      </div>

      {/* Band Interpretation */}
      <div
        className="rounded-lg p-6 sm:p-8 mb-8"
        style={{
          backgroundColor: colors.navyLight,
          borderLeft: `4px solid ${bandInfo.color}`,
        }}
      >
        <h2
          className="font-display text-2xl font-light mb-4"
          style={{ color: colors.white }}
        >
          {bandCopy.headline}
        </h2>
        <div
          className="text-base leading-relaxed whitespace-pre-line"
          style={{ color: colors.slate }}
        >
          {bandCopy.body}
        </div>
      </div>

      {/* Dimensional Chart */}
      <div
        className="rounded-lg p-6 sm:p-8 mb-8"
        style={{ backgroundColor: colors.navyLight }}
      >
        <h3
          className="text-lg font-semibold mb-6"
          style={{ color: colors.white }}
        >
          Dimensional Breakdown
        </h3>
        <DimensionalChart scores={results.dimensionScores} />
      </div>

      {/* Per-Dimension Interpretations */}
      <div className="space-y-4 mb-10">
        {results.dimensionScores.map((score) => {
          const metadata = dimensionMetadata[score.dimension];
          const band = getDimensionBand(score.score);
          const insight = getDimensionInsight(score.dimension, score.score);

          const borderColor =
            band === "low"
              ? colors.red
              : band === "moderate"
                ? colors.orange
                : colors.green;

          return (
            <div
              key={score.dimension}
              className="rounded-lg p-5"
              style={{
                backgroundColor: colors.navyLight,
                borderLeft: `3px solid ${borderColor}`,
              }}
            >
              <div className="flex items-center justify-between mb-2">
                <h3
                  className="font-semibold"
                  style={{ color: colors.white }}
                >
                  {metadata.label}
                </h3>
                <span
                  className="text-xs font-medium uppercase tracking-wider px-2 py-1 rounded"
                  style={{
                    backgroundColor: `${borderColor}20`,
                    color: borderColor,
                  }}
                >
                  {band}
                </span>
              </div>
              <p className="text-sm leading-relaxed" style={{ color: colors.slate }}>
                {insight}
              </p>
            </div>
          );
        })}
      </div>

      {/* Recommended Next Step */}
      <div
        className="rounded-lg p-6 sm:p-8 mb-8"
        style={{
          backgroundColor: colors.navyMid,
        }}
      >
        <h3
          className="text-sm font-medium uppercase tracking-wider mb-3"
          style={{ color: colors.gold }}
        >
          Recommended Next Step
        </h3>
        <h4
          className="font-display text-xl font-semibold mb-2"
          style={{ color: colors.white }}
        >
          {bandCopy.service}
        </h4>
        <p
          className="text-base leading-relaxed mb-6"
          style={{ color: colors.slate }}
        >
          {bandCopy.serviceDesc}
        </p>

        {/* Primary CTA */}
        <a
          href="#"
          onClick={() => trackEvent("scorecard_cta_discovery_call", { location: "recommended_step" })}
          className="inline-block px-8 py-3 rounded-md font-semibold transition-colors mb-3"
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
          Discuss your results with a qualified AI advisor
        </a>

        <p className="text-sm" style={{ color: colors.slateDark }}>
          No pitch. A structured conversation about your specific situation.
        </p>
      </div>

      {/* Scoring Methodology */}
      <div
        className="rounded-lg p-6 mb-8 text-xs leading-relaxed"
        style={{
          backgroundColor: colors.navyLight,
          color: colors.slateDark,
        }}
      >
        <h4
          className="font-semibold mb-2 uppercase tracking-wider"
          style={{ color: colors.slate }}
        >
          Scoring Methodology
        </h4>
        <p>
          Your Composite Readiness Score is calculated across all five dimensions
          using weighted scoring. Data Infrastructure and Governance & Risk
          Readiness each carry 25% weight; Technical Capability carries 20%;
          Organizational Maturity carries 15%; Strategic Alignment carries 15%.
          Technical Capability and Organizational Maturity are assessed at signal
          level (one question each) in this version. Industry benchmarks are
          based on published research data.
        </p>
      </div>

      {/* Footer */}
      <div className="text-center pt-8 pb-4">
        <div
          className="font-display text-xl mb-2"
          style={{ color: colors.white }}
        >
          AI Readiness Scorecard
        </div>

        {/* Retake option */}
        {onRestart && (
          <div className="mt-6">
            <button
              onClick={onRestart}
              className="text-sm underline"
              style={{ color: colors.slateDark }}
            >
              Retake Assessment
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
