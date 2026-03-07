'use client';

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { BusinessInfo, LLMConfig, AppStep, PipelineMode, TokenUsage } from '@/lib/types';

interface AppContextValue {
  // Current app step
  currentStep: AppStep;
  setCurrentStep: (step: AppStep) => void;

  // LLM configuration
  llmConfig: LLMConfig | null;
  setLLMConfig: (config: LLMConfig) => void;
  apiKey: string;
  setApiKey: (key: string) => void;

  // Business information
  businessInfo: BusinessInfo;
  updateBusinessInfo: (updates: Partial<BusinessInfo>) => void;
  resetBusinessInfo: () => void;

  // Wizard state
  wizardStep: number;
  setWizardStep: (step: number) => void;

  // Pipeline state
  executionMode: PipelineMode;
  setExecutionMode: (mode: PipelineMode) => void;

  // Pipeline outputs
  pipelineOutputs: string[];
  setPipelineOutputs: (outputs: string[]) => void;
  updatePipelineOutput: (index: number, output: string) => void;

  // Total token usage
  totalTokenUsage: TokenUsage;
  setTotalTokenUsage: (usage: TokenUsage) => void;

  // Error handling
  errors: Record<string, string>;
  setError: (field: string, message: string) => void;
  clearError: (field: string) => void;
  clearAllErrors: () => void;

  // Final output
  finalOutput: string;
  setFinalOutput: (output: string) => void;
}

const DEFAULT_BUSINESS_INFO: BusinessInfo = {
  companyName: '',
  tagline: '',
  primaryIndustry: '',
  secondaryIndustries: [],
  geographyFocus: '',
  founderBackground: '',
  servicesDescription: '',
  keyDifferentiators: '',
  knownCompetitors: '',
  existingIP: '',
  year1RevenueGoal: 0,
  currentTeamSize: 0,
  targetCompanySize: '',
};

const AppContext = createContext<AppContextValue | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [currentStep, setCurrentStep] = useState<AppStep>('setup');
  const [llmConfig, setLLMConfig] = useState<LLMConfig | null>(null);
  const [apiKey, setApiKey] = useState<string>('');
  const [businessInfo, setBusinessInfo] = useState<BusinessInfo>(DEFAULT_BUSINESS_INFO);
  const [wizardStep, setWizardStep] = useState<number>(1);
  const [executionMode, setExecutionMode] = useState<PipelineMode>('step-by-step');
  const [pipelineOutputs, setPipelineOutputs] = useState<string[]>([]);
  const [totalTokenUsage, setTotalTokenUsage] = useState<TokenUsage>({
    inputTokens: 0,
    outputTokens: 0,
    totalTokens: 0,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [finalOutput, setFinalOutput] = useState<string>('');

  const updateBusinessInfo = useCallback((updates: Partial<BusinessInfo>) => {
    setBusinessInfo(prev => ({ ...prev, ...updates }));
  }, []);

  const resetBusinessInfo = useCallback(() => {
    setBusinessInfo(DEFAULT_BUSINESS_INFO);
  }, []);

  const setError = useCallback((field: string, message: string) => {
    setErrors(prev => ({ ...prev, [field]: message }));
  }, []);

  const clearError = useCallback((field: string) => {
    setErrors(prev => {
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }, []);

  const clearAllErrors = useCallback(() => {
    setErrors({});
  }, []);

  const updatePipelineOutput = useCallback((index: number, output: string) => {
    setPipelineOutputs(prev => {
      const next = [...prev];
      next[index] = output;
      return next;
    });
  }, []);

  const value: AppContextValue = {
    currentStep,
    setCurrentStep,
    llmConfig,
    setLLMConfig,
    apiKey,
    setApiKey,
    businessInfo,
    updateBusinessInfo,
    resetBusinessInfo,
    wizardStep,
    setWizardStep,
    executionMode,
    setExecutionMode,
    pipelineOutputs,
    setPipelineOutputs,
    updatePipelineOutput,
    totalTokenUsage,
    setTotalTokenUsage,
    errors,
    setError,
    clearError,
    clearAllErrors,
    finalOutput,
    setFinalOutput,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext(): AppContextValue {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}