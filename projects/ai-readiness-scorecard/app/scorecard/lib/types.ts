// Scorecard type definitions

export type ScorecardStep =
  | "landing"
  | "email-gate"
  | "questions"
  | "calculating"
  | "results";

export interface EmailFormData {
  firstName: string;
  lastName: string;
  email: string;
  company: string;
  jobTitle: string;
  industry: string;
  companySize: string;
  isPersonalEmail?: boolean; // For HubSpot workflow targeting
}

export interface Question {
  id: string;
  dimension: Dimension;
  text: string;
  description?: string;
  options: QuestionOption[];
}

export interface QuestionOption {
  value: number;
  label: string;
  description?: string;
}

export type Dimension =
  | "data-infrastructure"
  | "technical-capability"
  | "organizational-maturity"
  | "governance-risk"
  | "strategic-alignment";

export interface DimensionMetadata {
  id: Dimension;
  label: string;
  description: string;
  color: string;
  weight: number; // Percentage weight in overall score
}

export interface Answer {
  questionId: string;
  value: number;
}

export interface DimensionScore {
  dimension: Dimension;
  score: number;
  maxScore: number;
  percentage: number;
}

export interface ScorecardResults {
  overallScore: number; // Composite Readiness Score (CRS)
  dimensionScores: DimensionScore[];
  band: ResultBand;
  lowestDimension: string; // For HubSpot workflow targeting
  timestamp: string;
}

export type ResultBand =
  | "foundational"
  | "developing"
  | "progressing"
  | "advanced"
  | "leading";

export interface ResultBandInfo {
  band: ResultBand;
  label: string;
  range: [number, number];
  color: string;
  description: string;
  recommendations: string[];
}

export interface ScorecardState {
  step: ScorecardStep;
  emailData: EmailFormData | null;
  answers: Answer[];
  currentQuestionIndex: number;
  results: ScorecardResults | null;
}
