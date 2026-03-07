'use client';

import React, { useState, useEffect } from 'react';
import { useAppContext } from '@/context/AppContext';
import { usePipeline } from '@/hooks/usePipeline';
import { BusinessInfo, RESEARCH_REFINABLE_FIELDS } from '@/lib/types';
import { Button } from '@/components/ui/Button';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Modal } from '@/components/ui/Modal';

export function PipelineScreen() {
  const {
    businessInfo,
    llmConfig,
    apiKey,
    executionMode,
    setExecutionMode,
    setCurrentStep,
  } = useAppContext();

  const {
    stages,
    currentStageId,
    isRunning,
    error,
    totalTokenUsage,
    pendingResearchReview,
    researchSuggestions,
    run,
    approve,
    regenerate,
    submitResearchRefinements,
    cancel,
    reset,
  } = usePipeline();

  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [regenerateNotes, setRegenerateNotes] = useState('');

  // Research review form state
  const [refinementValues, setRefinementValues] = useState<Record<string, string | number>>({});
  const [showResearchReview, setShowResearchReview] = useState(false);

  // Initialize refinement values when research review becomes pending
  useEffect(() => {
    if (pendingResearchReview) {
      const initial: Record<string, string | number> = {};
      for (const field of RESEARCH_REFINABLE_FIELDS) {
        const currentVal = businessInfo[field];
        const suggestion = researchSuggestions[field as keyof typeof researchSuggestions];

        if (field === 'year1RevenueGoal') {
          // Use suggestion if field was blank (0), otherwise keep user's value
          const numVal = Number(currentVal);
          initial[field] = numVal > 0 ? numVal : (suggestion as number) || 0;
        } else {
          const strVal = String(currentVal || '').trim();
          initial[field] = strVal || (suggestion as string) || '';
        }
      }
      setRefinementValues(initial);
      setShowResearchReview(true);
    }
  }, [pendingResearchReview, businessInfo, researchSuggestions]);

  const handleResearchReviewSubmit = () => {
    const refinements: Partial<BusinessInfo> = {};
    for (const field of RESEARCH_REFINABLE_FIELDS) {
      const value = refinementValues[field];
      if (field === 'year1RevenueGoal') {
        (refinements as any)[field] = Number(value) || 0;
      } else {
        (refinements as any)[field] = String(value || '');
      }
    }
    setShowResearchReview(false);
    submitResearchRefinements(refinements);
  };

  const canStart = businessInfo.companyName &&
                  businessInfo.tagline &&
                  businessInfo.primaryIndustry &&
                  llmConfig &&
                  apiKey;

  const handleStart = async () => {
    if (!canStart) return;

    await run(
      businessInfo as any,
      llmConfig!,
      apiKey,
      executionMode
    );
  };

  const currentStage = stages.find(s => s.id === currentStageId);
  const waitingForApproval = currentStage?.status === 'completed' &&
                            currentStage?.requiresApproval &&
                            executionMode === 'step-by-step' &&
                            !isRunning &&
                            !pendingResearchReview;

  useEffect(() => {
    if (waitingForApproval) {
      setShowApprovalModal(true);
    }
  }, [waitingForApproval]);

  const handleApprove = async () => {
    if (currentStage) {
      await approve(currentStage.id);
      setShowApprovalModal(false);
    }
  };

  const handleRegenerate = async () => {
    if (currentStage) {
      await regenerate(currentStage.id, regenerateNotes);
      setRegenerateNotes('');
      setShowApprovalModal(false);
    }
  };

  const allStagesComplete = stages.every(stage =>
    stage.status === 'approved' || stage.status === 'completed'
  );

  useEffect(() => {
    if (allStagesComplete && !isRunning && !pendingResearchReview && stages[0]?.status !== 'queued') {
      setCurrentStep('output');
    }
  }, [allStagesComplete, isRunning, pendingResearchReview, stages, setCurrentStep]);

  /** Labels for research-refinable fields */
  const FIELD_LABELS: Record<string, string> = {
    keyDifferentiators: 'Key Differentiators',
    knownCompetitors: 'Known Competitors',
    year1RevenueGoal: 'Year 1 Revenue Goal ($)',
  };

  return (
    <div className="min-h-screen bg-slate-950 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-slate-100 mb-2">
            Pipeline Execution
          </h1>
          <p className="text-slate-400">
            Generate your business plan using AI-powered analysis
          </p>
        </div>

        {/* Mode Selection */}
        {!isRunning && !pendingResearchReview && stages[0]?.status === 'queued' && (
          <div className="bg-slate-900 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-slate-100 mb-4">
              Execution Mode
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6" role="radiogroup" aria-label="Execution mode">
              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="radio"
                  value="step-by-step"
                  checked={executionMode === 'step-by-step'}
                  onChange={(e) => setExecutionMode(e.target.value as any)}
                  className="w-4 h-4 text-blue-600 bg-slate-800 border-slate-600 focus:ring-blue-500 mt-1"
                />
                <div>
                  <span className="text-slate-200 font-medium">Step-by-Step</span>
                  <p className="text-sm text-slate-400 mt-1">
                    Review and approve each stage before continuing
                  </p>
                </div>
              </label>
              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="radio"
                  value="full-auto"
                  checked={executionMode === 'full-auto'}
                  onChange={(e) => setExecutionMode(e.target.value as any)}
                  className="w-4 h-4 text-blue-600 bg-slate-800 border-slate-600 focus:ring-blue-500 mt-1"
                />
                <div>
                  <span className="text-slate-200 font-medium">Full Auto</span>
                  <p className="text-sm text-slate-400 mt-1">
                    Run all stages automatically without interruption
                  </p>
                </div>
              </label>
            </div>

            <Button
              onClick={handleStart}
              disabled={!canStart || isRunning}
              loading={isRunning}
              size="lg"
              className="w-full"
            >
              {isRunning ? 'Starting Pipeline...' : 'Start Business Plan Generation'}
            </Button>
          </div>
        )}

        {/* Pipeline Progress */}
        {(isRunning || pendingResearchReview || stages.some(s => s.status !== 'queued')) && (
          <div className="bg-slate-900 rounded-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-slate-100">
                Pipeline Progress
              </h2>
              <div className="text-sm text-slate-400">
                Tokens: {totalTokenUsage.totalTokens.toLocaleString()}
              </div>
            </div>

            <div aria-live="polite" className="sr-only">
              {pendingResearchReview
                ? 'Research complete. Reviewing research-informed fields.'
                : currentStage && isRunning
                  ? `Currently running: ${currentStage.name}`
                  : ''
              }
            </div>

            <div className="space-y-4">
              {stages.map((stage, index) => (
                <div
                  key={stage.id}
                  className={`border rounded-lg p-4 ${
                    stage.status === 'running'
                      ? 'border-blue-500 bg-blue-900/10'
                      : stage.status === 'completed' || stage.status === 'approved'
                      ? 'border-green-500 bg-green-900/10'
                      : stage.status === 'error'
                      ? 'border-red-500 bg-red-900/10'
                      : 'border-slate-700 bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                        stage.status === 'running'
                          ? 'bg-blue-600 text-white'
                          : stage.status === 'completed' || stage.status === 'approved'
                          ? 'bg-green-600 text-white'
                          : stage.status === 'error'
                          ? 'bg-red-600 text-white'
                          : 'bg-slate-600 text-slate-300'
                      }`}>
                        {stage.status === 'running' ? (
                          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                        ) : stage.status === 'completed' || stage.status === 'approved' ? (
                          <span aria-hidden="true">&#10003;</span>
                        ) : stage.status === 'error' ? (
                          <span aria-hidden="true">&#10007;</span>
                        ) : (
                          index + 1
                        )}
                      </div>
                      <div>
                        <h3 className="text-lg font-medium text-slate-100">
                          {stage.name}
                        </h3>
                        <p className="text-sm text-slate-400">
                          {stage.description}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        stage.status === 'queued'
                          ? 'bg-slate-700 text-slate-300'
                          : stage.status === 'running'
                          ? 'bg-blue-700 text-blue-100'
                          : stage.status === 'completed'
                          ? 'bg-green-700 text-green-100'
                          : stage.status === 'approved'
                          ? 'bg-green-700 text-green-100'
                          : stage.status === 'error'
                          ? 'bg-red-700 text-red-100'
                          : 'bg-slate-700 text-slate-300'
                      }`}>
                        {stage.status.charAt(0).toUpperCase() + stage.status.slice(1)}
                      </span>

                      {stage.tokenUsage && (
                        <span className="text-xs text-slate-400">
                          {stage.tokenUsage.totalTokens.toLocaleString()} tokens
                        </span>
                      )}
                    </div>
                  </div>

                  {stage.output && (
                    <div className="mt-3 p-3 bg-slate-800 rounded border border-slate-700">
                      <div className="text-sm text-slate-300 whitespace-pre-wrap">
                        {stage.output.length > 200
                          ? `${stage.output.substring(0, 200)}...`
                          : stage.output
                        }
                        {stage.status === 'running' && (
                          <span className="typing-cursor ml-1" aria-hidden="true">|</span>
                        )}
                      </div>
                    </div>
                  )}

                  {stage.error && (
                    <div className="mt-3 p-3 bg-red-900/20 border border-red-500/20 rounded">
                      <div className="text-sm text-red-400" role="alert">
                        Error: {stage.error}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Research Review Banner */}
            {pendingResearchReview && (
              <div className="mt-6 bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-blue-200">Research Complete</h3>
                    <p className="text-sm text-blue-300/70 mt-1">
                      Review the research findings and confirm the fields you left blank before the pipeline continues.
                    </p>
                  </div>
                  <Button onClick={() => setShowResearchReview(true)}>
                    Review & Continue
                  </Button>
                </div>
              </div>
            )}

            {/* Pipeline Controls */}
            {(isRunning || error) && !pendingResearchReview && (
              <div className="flex justify-center mt-6 space-x-4">
                <Button
                  variant="secondary"
                  onClick={isRunning ? cancel : reset}
                >
                  {isRunning ? 'Cancel' : 'Reset'}
                </Button>

                {error && !isRunning && (
                  <Button
                    onClick={handleStart}
                    disabled={isRunning}
                  >
                    Retry Pipeline
                  </Button>
                )}
              </div>
            )}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-900/20 border border-red-500/20 rounded-lg p-4" role="alert">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span className="text-red-400">{error}</span>
            </div>
          </div>
        )}

        {/* Approval Modal */}
        <Modal
          isOpen={showApprovalModal}
          onClose={() => setShowApprovalModal(false)}
          title={`Approve: ${currentStage?.name || ''}`}
          size="xl"
        >
          {currentStage && (
            <div className="space-y-4">
              <div className="bg-slate-800 rounded-lg p-4 max-h-96 overflow-y-auto">
                <h4 className="text-lg font-medium text-slate-100 mb-2">
                  Stage Output
                </h4>
                <div className="text-sm text-slate-300 whitespace-pre-wrap">
                  {currentStage.output}
                </div>
              </div>

              <div className="space-y-3">
                <label htmlFor="regenerate-notes" className="label">
                  Regeneration Notes (Optional)
                </label>
                <textarea
                  id="regenerate-notes"
                  className="textarea"
                  value={regenerateNotes}
                  onChange={(e) => setRegenerateNotes(e.target.value)}
                  placeholder="Enter specific feedback or changes you'd like to see..."
                  rows={3}
                />
              </div>

              <div className="flex space-x-3">
                <Button
                  variant="secondary"
                  onClick={handleApprove}
                  className="flex-1"
                >
                  Approve & Continue
                </Button>
                <Button
                  variant="ghost"
                  onClick={handleRegenerate}
                  className="flex-1"
                >
                  Regenerate
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* Research Review Modal */}
        <Modal
          isOpen={showResearchReview}
          onClose={() => {}} // Cannot dismiss — must confirm
          title="Refine Your Business Information"
          size="xl"
        >
          <div className="space-y-6">
            <p className="text-slate-400 text-sm">
              The research phase has completed. Below are the fields you left blank, now pre-filled
              with suggestions based on the research findings. Review and edit each field, then confirm
              to continue the pipeline.
            </p>

            {RESEARCH_REFINABLE_FIELDS.map((field) => {
              const label = FIELD_LABELS[field] || field;
              const currentValue = refinementValues[field] ?? '';
              const suggestion = researchSuggestions[field as keyof typeof researchSuggestions];
              const originalValue = businessInfo[field];
              const wasBlank = field === 'year1RevenueGoal'
                ? !originalValue || Number(originalValue) === 0
                : !originalValue || (typeof originalValue === 'string' && !originalValue.trim());

              return (
                <div key={field} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label htmlFor={`refinement-${field}`} className="label">
                      {label}
                    </label>
                    {wasBlank && suggestion && (
                      <span className="text-xs text-blue-400">AI-suggested from research</span>
                    )}
                    {!wasBlank && (
                      <span className="text-xs text-green-400">You provided this</span>
                    )}
                  </div>

                  {field === 'year1RevenueGoal' ? (
                    <input
                      id={`refinement-${field}`}
                      type="number"
                      className="input"
                      value={currentValue}
                      onChange={(e) => setRefinementValues(prev => ({
                        ...prev,
                        [field]: Number(e.target.value),
                      }))}
                      min={0}
                    />
                  ) : (
                    <textarea
                      id={`refinement-${field}`}
                      className="textarea"
                      value={currentValue as string}
                      onChange={(e) => setRefinementValues(prev => ({
                        ...prev,
                        [field]: e.target.value,
                      }))}
                      rows={3}
                    />
                  )}
                </div>
              );
            })}

            <div className="flex space-x-3">
              <Button
                variant="secondary"
                onClick={() => {
                  // Reset to blank — user wants to proceed without filling these
                  const empty: Record<string, string | number> = {};
                  for (const field of RESEARCH_REFINABLE_FIELDS) {
                    empty[field] = field === 'year1RevenueGoal' ? 0 : '';
                  }
                  setRefinementValues(empty);
                }}
                className="flex-shrink-0"
              >
                Clear All
              </Button>
              <Button
                onClick={handleResearchReviewSubmit}
                className="flex-1"
              >
                Confirm & Continue Pipeline
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </div>
  );
}
