'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import {
  PipelineStage,
  PipelineMode,
  BusinessInfo,
  LLMConfig,
  TokenUsage,
  StageStatus,
  ResearchSuggestions,
  RESEARCH_REFINABLE_FIELDS,
} from '@/lib/types';
import { useAppContext } from '@/context/AppContext';
import { getStagePrompt } from '@/lib/prompts';

interface UsePipelineReturn {
  stages: PipelineStage[];
  currentStageId: number;
  isRunning: boolean;
  error?: string;
  totalTokenUsage: TokenUsage;
  sessionId?: string;
  pendingResearchReview: boolean;
  researchSuggestions: ResearchSuggestions;
  run: (businessInfo: BusinessInfo, llmConfig: LLMConfig, apiKey: string, mode: PipelineMode) => Promise<void>;
  approve: (stageId: number) => Promise<void>;
  regenerate: (stageId: number, notes?: string) => Promise<void>;
  submitResearchRefinements: (refinements: Partial<BusinessInfo>) => void;
  cancel: () => void;
  reset: () => void;
}

const INITIAL_STAGES: PipelineStage[] = [
  {
    id: 1,
    name: 'Industry & Market Research',
    role: 'Researcher',
    description: 'Analyzing industry landscape, competitive environment, and market opportunities',
    status: 'queued',
    output: '',
    requiresApproval: true,
  },
  {
    id: 2,
    name: 'Strategic Synthesis',
    role: 'Researcher',
    description: 'Synthesizing research insights into strategic positioning and market opportunities',
    status: 'queued',
    output: '',
    requiresApproval: true,
  },
  {
    id: 3,
    name: 'Service Portfolio Development',
    role: 'Writer',
    description: 'Crafting detailed service offerings, pricing strategy, and value propositions',
    status: 'queued',
    output: '',
    requiresApproval: true,
  },
  {
    id: 4,
    name: 'Service Portfolio Refinement',
    role: 'Editor',
    description: 'Refining service descriptions for clarity, market fit, and professional presentation',
    status: 'queued',
    output: '',
    requiresApproval: false,
  },
  {
    id: 5,
    name: 'Service Portfolio Finalization',
    role: 'Editor',
    description: 'Final review and formatting of service portfolio for business plan integration',
    status: 'queued',
    output: '',
    requiresApproval: true,
  },
  {
    id: 6,
    name: 'Business Plan Development',
    role: 'Writer',
    description: 'Creating comprehensive business plan with all required sections',
    status: 'queued',
    output: '',
    requiresApproval: true,
  },
  {
    id: 7,
    name: 'Quality Assurance Review',
    role: 'Editor',
    description: 'Comprehensive review for consistency, completeness, and professional quality',
    status: 'queued',
    output: '',
    requiresApproval: false,
  },
  {
    id: 8,
    name: 'Final Document Assembly',
    role: 'Editor',
    description: 'Incorporating QA feedback into polished, professional business plan',
    status: 'queued',
    output: '',
    requiresApproval: false,
  },
];

// Stage 2 is the research synthesis — after it completes, we pause for refinement
const RESEARCH_REVIEW_AFTER_STAGE = 2;

/**
 * Parse research synthesis output to extract suggestions for refinable fields.
 * Looks for competitive information, differentiators, and revenue data in the text.
 */
function extractSuggestionsFromResearch(
  researchOutput: string,
  synthesisOutput: string
): ResearchSuggestions {
  const combined = researchOutput + '\n' + synthesisOutput;
  const suggestions: ResearchSuggestions = {};

  // Extract competitors: look for sections mentioning competitors, competitive landscape, etc.
  const competitorPatterns = [
    /(?:competitors?|competitive landscape|key players|market players)[\s:]*\n([\s\S]*?)(?:\n\n|\n#|\n\*\*)/i,
    /(?:compete with|competing against|main competitors?)[\s:]+([^\n]+(?:\n[^\n#]+)*)/i,
  ];
  for (const pattern of competitorPatterns) {
    const match = combined.match(pattern);
    if (match) {
      suggestions.knownCompetitors = match[1].trim().slice(0, 500);
      break;
    }
  }

  // Extract differentiators: look for positioning, unique value, differentiation sections
  const diffPatterns = [
    /(?:differentiat|unique value|competitive advantage|positioning strategy)[\s:]*\n([\s\S]*?)(?:\n\n|\n#|\n\*\*)/i,
    /(?:stand out|distinguish|unique selling)[\s:]+([^\n]+(?:\n[^\n#]+)*)/i,
  ];
  for (const pattern of diffPatterns) {
    const match = combined.match(pattern);
    if (match) {
      suggestions.keyDifferentiators = match[1].trim().slice(0, 500);
      break;
    }
  }

  // Extract revenue: look for revenue targets, market sizing, revenue potential
  const revenuePatterns = [
    /(?:revenue target|year.?1 revenue|first.year revenue|revenue goal|revenue potential)[\s:]*\$?([\d,]+(?:\.\d+)?)\s*(?:k|K|thousand|million|M)?/i,
    /\$?([\d,]+(?:\.\d+)?)\s*(?:k|K|thousand|million|M)?\s*(?:in (?:year|first|initial)|annual|revenue target)/i,
  ];
  for (const pattern of revenuePatterns) {
    const match = combined.match(pattern);
    if (match) {
      let value = parseFloat(match[1].replace(/,/g, ''));
      const text = match[0].toLowerCase();
      if (text.includes('million') || text.includes('m')) value *= 1_000_000;
      if (text.includes('thousand') || text.includes('k')) value *= 1_000;
      if (value > 0 && value < 1_000_000_000) {
        suggestions.year1RevenueGoal = Math.round(value);
      }
      break;
    }
  }

  return suggestions;
}

export function usePipeline(): UsePipelineReturn {
  const { setPipelineOutputs, updatePipelineOutput, setFinalOutput, updateBusinessInfo } = useAppContext();

  const [stages, setStages] = useState<PipelineStage[]>(INITIAL_STAGES.map(s => ({ ...s })));
  const [currentStageId, setCurrentStageId] = useState<number>(0);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [error, setError] = useState<string>();
  const [totalTokenUsage, setTotalTokenUsage] = useState<TokenUsage>({
    inputTokens: 0,
    outputTokens: 0,
    totalTokens: 0,
  });
  const [sessionId, setSessionId] = useState<string>();
  const [pendingResearchReview, setPendingResearchReview] = useState(false);
  const [researchSuggestions, setResearchSuggestions] = useState<ResearchSuggestions>({});

  const abortControllerRef = useRef<AbortController>();
  const stageOutputsRef = useRef<string[]>([]);
  const cancelledRef = useRef<boolean>(false);
  // Store pipeline run context for resuming after research review
  const runContextRef = useRef<{
    businessInfo: BusinessInfo;
    llmConfig: LLMConfig;
    apiKey: string;
    mode: PipelineMode;
    resumeFromStage: number;
  } | null>(null);

  const updateStage = useCallback((stageId: number, updates: Partial<PipelineStage>) => {
    setStages(prevStages => prevStages.map(stage =>
      stage.id === stageId ? { ...stage, ...updates } : stage
    ));
  }, []);

  const updateTotalTokens = useCallback((usage: TokenUsage) => {
    setTotalTokenUsage(prev => ({
      inputTokens: prev.inputTokens + usage.inputTokens,
      outputTokens: prev.outputTokens + usage.outputTokens,
      totalTokens: prev.totalTokens + usage.totalTokens,
    }));
  }, []);

  const cancel = useCallback(() => {
    cancelledRef.current = true;
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = undefined;
    }
    setIsRunning(false);
    setCurrentStageId(0);
    setPendingResearchReview(false);
  }, []);

  const reset = useCallback(() => {
    cancel();
    setStages(INITIAL_STAGES.map(s => ({ ...s })));
    setCurrentStageId(0);
    setError(undefined);
    setTotalTokenUsage({ inputTokens: 0, outputTokens: 0, totalTokens: 0 });
    setSessionId(undefined);
    setPendingResearchReview(false);
    setResearchSuggestions({});
    stageOutputsRef.current = [];
    cancelledRef.current = false;
    runContextRef.current = null;
  }, [cancel]);

  const runStage = useCallback(async (
    stageId: number,
    businessInfo: BusinessInfo,
    llmConfig: LLMConfig,
    apiKey: string,
    regenerationNotes?: string
  ): Promise<string> => {
    if (cancelledRef.current) throw new Error('Pipeline cancelled');

    const prompts = getStagePrompt(stageId, businessInfo, stageOutputsRef.current, regenerationNotes);

    updateStage(stageId, { status: 'running', output: '', startedAt: Date.now() });
    setCurrentStageId(stageId);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        config: llmConfig,
        apiKey,
        prompt: prompts.user,
        systemPrompt: prompts.system,
      }),
      signal: controller.signal,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || `HTTP ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let buffer = '';
    let fullOutput = '';
    let stageUsage: TokenUsage | undefined;

    while (true) {
      if (cancelledRef.current) {
        reader.cancel();
        throw new Error('Pipeline cancelled');
      }

      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith('data: ')) continue;

        try {
          const data = JSON.parse(trimmed.slice(6));

          switch (data.type) {
            case 'token':
              fullOutput += data.content;
              updateStage(stageId, { output: fullOutput });
              break;

            case 'usage':
              stageUsage = {
                inputTokens: data.inputTokens || 0,
                outputTokens: data.outputTokens || 0,
                totalTokens: data.totalTokens || 0,
              };
              break;

            case 'error':
              throw new Error(data.content || 'Stream error');
          }
        } catch (parseError: any) {
          if (parseError.message === 'Stream error' || parseError.message === 'Pipeline cancelled') {
            throw parseError;
          }
        }
      }
    }

    if (stageUsage) {
      updateStage(stageId, {
        status: 'completed',
        output: fullOutput,
        tokenUsage: stageUsage,
        completedAt: Date.now(),
      });
      updateTotalTokens(stageUsage);
    } else {
      updateStage(stageId, {
        status: 'completed',
        output: fullOutput,
        completedAt: Date.now(),
      });
    }

    stageOutputsRef.current[stageId - 1] = fullOutput;
    updatePipelineOutput(stageId - 1, fullOutput);

    return fullOutput;
  }, [updateStage, updateTotalTokens, updatePipelineOutput]);

  /**
   * Check if any research-refinable fields were left blank.
   */
  const hasBlankRefinableFields = useCallback((businessInfo: BusinessInfo): boolean => {
    for (const field of RESEARCH_REFINABLE_FIELDS) {
      const value = businessInfo[field];
      if (field === 'year1RevenueGoal') {
        if (!value || Number(value) === 0) return true;
      } else {
        if (!value || (typeof value === 'string' && !value.trim())) return true;
      }
    }
    return false;
  }, []);

  /**
   * Run the pipeline stages, starting from a given stage index.
   */
  const runStages = useCallback(async (
    businessInfo: BusinessInfo,
    llmConfig: LLMConfig,
    apiKey: string,
    mode: PipelineMode,
    startFromStageIdx: number = 0
  ) => {
    for (let i = startFromStageIdx; i < INITIAL_STAGES.length; i++) {
      const stage = INITIAL_STAGES[i];
      if (cancelledRef.current) break;

      await runStage(stage.id, businessInfo, llmConfig, apiKey);

      // After stage 2 (Research Synthesis), pause for research review if fields are blank
      if (
        stage.id === RESEARCH_REVIEW_AFTER_STAGE &&
        hasBlankRefinableFields(businessInfo)
      ) {
        // Extract suggestions from research output
        const researchOutput = stageOutputsRef.current[0] || '';
        const synthesisOutput = stageOutputsRef.current[1] || '';
        const suggestions = extractSuggestionsFromResearch(researchOutput, synthesisOutput);
        setResearchSuggestions(suggestions);

        // Save context for resuming
        runContextRef.current = {
          businessInfo,
          llmConfig,
          apiKey,
          mode,
          resumeFromStage: i + 1, // Resume from stage 3
        };

        // Pause — PipelineScreen will show the research review form
        setPendingResearchReview(true);
        setIsRunning(false);
        return;
      }

      // In step-by-step mode, pause at stages requiring approval
      if (mode === 'step-by-step' && stage.requiresApproval) {
        setIsRunning(false);
        return;
      }

      // In full-auto mode, auto-approve
      if (mode === 'full-auto') {
        updateStage(stage.id, { status: 'approved' });
      }
    }

    // Pipeline complete
    const lastOutput = stageOutputsRef.current[stageOutputsRef.current.length - 1];
    if (lastOutput) {
      setFinalOutput(lastOutput);
    }
    setPipelineOutputs([...stageOutputsRef.current]);
  }, [runStage, updateStage, hasBlankRefinableFields, setFinalOutput, setPipelineOutputs]);

  const run = useCallback(async (
    businessInfo: BusinessInfo,
    llmConfig: LLMConfig,
    apiKey: string,
    mode: PipelineMode
  ) => {
    setIsRunning(true);
    setError(undefined);
    cancelledRef.current = false;
    stageOutputsRef.current = [];

    const newSessionId = `pipeline_${Date.now()}`;
    setSessionId(newSessionId);

    try {
      await runStages(businessInfo, llmConfig, apiKey, mode, 0);
    } catch (err: any) {
      if (err.name === 'AbortError' || err.message === 'Pipeline cancelled') {
        return;
      }
      const errorMsg = err.message || 'Pipeline failed';
      setError(errorMsg);

      if (currentStageId) {
        updateStage(currentStageId, { status: 'error', error: errorMsg });
      }
    } finally {
      if (!pendingResearchReview) {
        setIsRunning(false);
      }
    }
  }, [runStages, updateStage, currentStageId, pendingResearchReview]);

  /**
   * Called by PipelineScreen after user reviews and confirms research-informed fields.
   * Updates businessInfo and resumes the pipeline from stage 3.
   */
  const submitResearchRefinements = useCallback((refinements: Partial<BusinessInfo>) => {
    // Update business info in app context
    updateBusinessInfo(refinements);

    // Clear the review state
    setPendingResearchReview(false);
    setResearchSuggestions({});

    // Resume pipeline
    const ctx = runContextRef.current;
    if (!ctx) return;

    // Merge refinements into the business info for remaining stages
    const updatedInfo = { ...ctx.businessInfo, ...refinements };
    runContextRef.current = null;

    setIsRunning(true);
    runStages(updatedInfo, ctx.llmConfig, ctx.apiKey, ctx.mode, ctx.resumeFromStage)
      .catch((err: any) => {
        if (err.name === 'AbortError' || err.message === 'Pipeline cancelled') return;
        const errorMsg = err.message || 'Pipeline failed';
        setError(errorMsg);
      })
      .finally(() => {
        setIsRunning(false);
      });
  }, [updateBusinessInfo, runStages]);

  const approve = useCallback(async (stageId: number) => {
    updateStage(stageId, { status: 'approved' });
  }, [updateStage]);

  const regenerate = useCallback(async (stageId: number, notes?: string) => {
    updateStage(stageId, { status: 'queued', output: '', error: undefined });
  }, [updateStage]);

  return {
    stages,
    currentStageId,
    isRunning,
    error,
    totalTokenUsage,
    sessionId,
    pendingResearchReview,
    researchSuggestions,
    run,
    approve,
    regenerate,
    submitResearchRefinements,
    cancel,
    reset,
  };
}
