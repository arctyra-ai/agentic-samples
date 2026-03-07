// ============================================================
// Core business information types
// ============================================================

export type IndustryType =
  | 'technology'
  | 'healthcare'
  | 'finance'
  | 'retail'
  | 'manufacturing'
  | 'consulting'
  | 'education'
  | 'real-estate'
  | 'food-beverage'
  | 'other';

export type CompanySize =
  | 'solopreneur'
  | 'small-team-2-10'
  | 'medium-team-11-50'
  | 'large-team-51-200'
  | 'enterprise-200+';

export type GeographyFocus =
  | 'local'
  | 'regional'
  | 'national'
  | 'international'
  | 'global';

export interface BusinessInfo {
  companyName: string;
  tagline: string;
  primaryIndustry: IndustryType | '';
  secondaryIndustries: string[];
  geographyFocus: GeographyFocus | '';
  founderBackground: string;
  servicesDescription: string;
  keyDifferentiators: string;
  knownCompetitors: string;
  existingIP: string;
  year1RevenueGoal: number;
  currentTeamSize: number;
  targetCompanySize: CompanySize | '';
  errors?: Record<string, string>;
}

// Fields that can be left blank in the wizard and refined after research
export const RESEARCH_REFINABLE_FIELDS: (keyof BusinessInfo)[] = [
  'keyDifferentiators',
  'knownCompetitors',
  'year1RevenueGoal',
];

// Suggestions extracted from research output for refinable fields
export interface ResearchSuggestions {
  keyDifferentiators?: string;
  knownCompetitors?: string;
  year1RevenueGoal?: number;
}

// ============================================================
// LLM configuration types
// ============================================================

export type LLMProvider = 'openai' | 'anthropic' | 'google' | 'openrouter' | 'custom';

export interface LLMConfig {
  provider: LLMProvider;
  model: string;
  endpoint?: string;
  maxTokens: number;
  temperature: number;
}

export interface TokenUsage {
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
}

// ============================================================
// Pipeline types
// ============================================================

export type StageStatus = 'queued' | 'running' | 'completed' | 'approved' | 'error' | 'cancelled';
export type PipelineMode = 'step-by-step' | 'full-auto';

export interface PipelineStage {
  id: number;
  name: string;
  role: 'Researcher' | 'Writer' | 'Editor';
  description: string;
  status: StageStatus;
  output: string;
  error?: string;
  tokenUsage?: TokenUsage;
  requiresApproval: boolean;
  startedAt?: number;
  completedAt?: number;
}

export type SSEEventType = 'stage_start' | 'token' | 'stage_complete' | 'stage_error' | 'pipeline_complete' | 'pipeline_error';

export interface SSEEvent {
  type: SSEEventType;
  stageId?: number;
  content?: string;
  tokenUsage?: TokenUsage;
  error?: string;
}

// ============================================================
// Wizard types
// ============================================================

export interface WizardFieldOption {
  value: string;
  label: string;
}

export interface WizardField {
  name: keyof BusinessInfo;
  label: string;
  type: 'text' | 'textarea' | 'number' | 'select' | 'multiselect';
  required: boolean;
  researchRefinable?: boolean; // If true, field can be left blank and refined after research stages
  helpPrompt: string;
  validation: (value: any) => string | null;
  options?: WizardFieldOption[];
  maxLength?: number;
}

export interface WizardStep {
  id: number;
  title: string;
  description: string;
  fields: WizardField[];
}

// ============================================================
// Application step types
// ============================================================

export type AppStep = 'setup' | 'wizard' | 'pipeline' | 'output';

// ============================================================
// Export types
// ============================================================

export type ExportFormat = 'docx' | 'markdown' | 'pdf';

export interface ExportOptions {
  format: ExportFormat;
  includeTableOfContents: boolean;
  includeCoverPage: boolean;
  companyName: string;
}

// ============================================================
// Model definitions for provider dropdowns
// ============================================================

export interface ModelOption {
  value: string;
  label: string;
  provider: LLMProvider;
  maxTokens: number;
}

export const MODEL_OPTIONS: ModelOption[] = [
  // OpenAI
  { value: 'gpt-4o', label: 'GPT-4o', provider: 'openai', maxTokens: 128000 },
  { value: 'gpt-4o-mini', label: 'GPT-4o Mini', provider: 'openai', maxTokens: 128000 },
  { value: 'gpt-4-turbo', label: 'GPT-4 Turbo', provider: 'openai', maxTokens: 128000 },
  { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo', provider: 'openai', maxTokens: 16385 },
  // Anthropic
  { value: 'claude-sonnet-4-20250514', label: 'Claude Sonnet 4', provider: 'anthropic', maxTokens: 200000 },
  { value: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet', provider: 'anthropic', maxTokens: 200000 },
  { value: 'claude-3-haiku-20240307', label: 'Claude 3 Haiku', provider: 'anthropic', maxTokens: 200000 },
  // Google
  { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro', provider: 'google', maxTokens: 1048576 },
  { value: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash', provider: 'google', maxTokens: 1048576 },
];

export const PROVIDER_ENDPOINTS: Record<LLMProvider, string> = {
  openai: 'https://api.openai.com/v1/chat/completions',
  anthropic: 'https://api.anthropic.com/v1/messages',
  google: 'https://generativelanguage.googleapis.com/v1beta',
  openrouter: 'https://openrouter.ai/api/v1/chat/completions',
  custom: '',
};
