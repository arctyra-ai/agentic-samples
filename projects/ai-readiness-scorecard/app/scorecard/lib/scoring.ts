// Scoring engine for AI Readiness Scorecard

import type {
  Answer,
  DimensionScore,
  ScorecardResults,
  ResultBand,
} from "./types";
import { questions, dimensionMetadata } from "./questions";

// Calculate dimensional scores
// Questions are scored 1-5
// Dimension score = average of all questions in that dimension (1.0 to 5.0)
export function calculateDimensionScores(answers: Answer[]): DimensionScore[] {
  const dimensionGroups = new Map<
    string,
    { total: number; count: number }
  >();

  // Initialize dimension groups
  questions.forEach((q) => {
    if (!dimensionGroups.has(q.dimension)) {
      dimensionGroups.set(q.dimension, { total: 0, count: 0 });
    }
  });

  // Sum actual scores
  answers.forEach((answer) => {
    const question = questions.find((q) => q.id === answer.questionId);
    if (!question) return;

    const group = dimensionGroups.get(question.dimension);
    if (group) {
      group.total += answer.value;
      group.count += 1;
    }
  });

  // Convert to DimensionScore array with averages
  const scores: DimensionScore[] = [];
  dimensionGroups.forEach((value, dimension) => {
    const average = value.count > 0 ? value.total / value.count : 0;
    const percentage = ((average - 1) / 4) * 100; // Convert 1-5 scale to 0-100%

    scores.push({
      dimension: dimension as any,
      score: average, // Store as 1.0-5.0
      maxScore: 5,
      percentage: Math.round(percentage * 10) / 10, // Round to 1 decimal
    });
  });

  return scores;
}

// Calculate overall Composite Readiness Score (CRS)
// Weighted average based on dimension weights
// Formula: rawCRS = ((data * 0.25) + (technical * 0.20) + (organizational * 0.15) + (governance * 0.25) + (strategic * 0.15)) * 20
// displayCRS = Math.round(((rawCRS - 20) / 80) * 100), clamped to 0-100
export function calculateOverallScore(
  dimensionScores: DimensionScore[]
): number {
  const scoreMap = new Map<string, number>();
  dimensionScores.forEach((ds) => {
    scoreMap.set(ds.dimension, ds.score);
  });

  // Get scores for each dimension (defaults to 1.0 if missing)
  const data = scoreMap.get("data-infrastructure") ?? 1.0;
  const technical = scoreMap.get("technical-capability") ?? 1.0;
  const organizational = scoreMap.get("organizational-maturity") ?? 1.0;
  const governance = scoreMap.get("governance-risk") ?? 1.0;
  const strategic = scoreMap.get("strategic-alignment") ?? 1.0;

  // Calculate raw CRS (range: 20 to 100)
  const rawCRS =
    (data * 0.25 +
      technical * 0.2 +
      organizational * 0.15 +
      governance * 0.25 +
      strategic * 0.15) *
    20;

  // Convert to display CRS (range: 0 to 100)
  const displayCRS = Math.round(((rawCRS - 20) / 80) * 100);

  // Clamp to 0-100
  return Math.max(0, Math.min(100, displayCRS));
}

// Determine result band based on overall score
// Band assignments:
// 0-25: Foundational (red)
// 26-45: Developing (orange)
// 46-65: Progressing (gold)
// 66-80: Advanced (green)
// 81-100: Leading (greenLight)
export function determineResultBand(score: number): ResultBand {
  if (score <= 25) return "foundational";
  if (score <= 45) return "developing";
  if (score <= 65) return "progressing";
  if (score <= 80) return "advanced";
  return "leading";
}

// Determine dimension band
// 1.0-2.0: Low
// 2.1-3.5: Moderate
// 3.6-5.0: Strong
export function getDimensionBand(score: number): "low" | "moderate" | "strong" {
  if (score <= 2.0) return "low";
  if (score <= 3.5) return "moderate";
  return "strong";
}

// Identify the lowest-scoring dimension for HubSpot workflow targeting
export function getLowestScoringDimension(
  dimensionScores: DimensionScore[]
): string {
  if (dimensionScores.length === 0) return "data-infrastructure";

  let lowest = dimensionScores[0];
  for (const ds of dimensionScores) {
    if (ds.score < lowest.score) {
      lowest = ds;
    }
  }

  return lowest.dimension;
}

// Main scoring function
export function calculateResults(answers: Answer[]): ScorecardResults {
  const dimensionScores = calculateDimensionScores(answers);
  const overallScore = calculateOverallScore(dimensionScores);
  const band = determineResultBand(overallScore);
  const lowestDimension = getLowestScoringDimension(dimensionScores);

  return {
    overallScore,
    dimensionScores,
    band,
    lowestDimension,
    timestamp: new Date().toISOString(),
  };
}
