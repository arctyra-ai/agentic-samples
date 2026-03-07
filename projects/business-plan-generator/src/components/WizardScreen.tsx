'use client';

import React, { useState, useCallback } from 'react';
import { useAppContext } from '@/context/AppContext';
import { BusinessInfo, WizardStep, WizardField, IndustryType, CompanySize, GeographyFocus } from '@/lib/types';
import { validateBusinessInfo } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Modal } from '@/components/ui/Modal';

// Helper text shown on research-refinable fields
const REFINABLE_HINT = 'Leave blank to let the research phase inform this.';

// Define wizard steps
const WIZARD_STEPS: WizardStep[] = [
  {
    id: 1,
    title: 'Company Basics',
    description: 'Tell us about your company foundation',
    fields: [
      {
        name: 'companyName',
        label: 'Company Name',
        type: 'text',
        required: true,
        helpPrompt: 'Suggest a professional company name for a business in this industry',
        validation: (value) => !value?.trim() ? 'Company name is required' : null,
        maxLength: 100,
      },
      {
        name: 'tagline',
        label: 'Company Tagline',
        type: 'text',
        required: true,
        helpPrompt: 'Create a compelling tagline that captures the essence of this business',
        validation: (value) => !value?.trim() ? 'Tagline is required' : null,
        maxLength: 200,
      },
    ],
  },
  {
    id: 2,
    title: 'Industry & Market',
    description: 'Define your market and industry focus',
    fields: [
      {
        name: 'primaryIndustry',
        label: 'Primary Industry',
        type: 'select',
        required: true,
        helpPrompt: 'Help me choose the best industry classification for my business',
        validation: (value) => !value ? 'Primary industry is required' : null,
        options: [
          { value: 'technology', label: 'Technology' },
          { value: 'healthcare', label: 'Healthcare' },
          { value: 'finance', label: 'Finance' },
          { value: 'retail', label: 'Retail' },
          { value: 'manufacturing', label: 'Manufacturing' },
          { value: 'consulting', label: 'Consulting' },
          { value: 'education', label: 'Education' },
          { value: 'real-estate', label: 'Real Estate' },
          { value: 'food-beverage', label: 'Food & Beverage' },
          { value: 'other', label: 'Other' },
        ],
      },
      {
        name: 'geographyFocus',
        label: 'Geographic Focus',
        type: 'select',
        required: true,
        helpPrompt: 'Recommend the optimal geographic scope for this type of business',
        validation: (value) => !value ? 'Geographic focus is required' : null,
        options: [
          { value: 'local', label: 'Local' },
          { value: 'regional', label: 'Regional' },
          { value: 'national', label: 'National' },
          { value: 'international', label: 'International' },
          { value: 'global', label: 'Global' },
        ],
      },
      {
        name: 'secondaryIndustries',
        label: 'Secondary Industries (Optional)',
        type: 'multiselect',
        required: false,
        helpPrompt: 'Select related industries that complement your primary focus',
        validation: (value) => {
          if (value && Array.isArray(value) && value.length > 3) {
            return 'Please select no more than 3 secondary industries';
          }
          return null;
        },
        options: [
          { value: 'technology', label: 'Technology' },
          { value: 'healthcare', label: 'Healthcare' },
          { value: 'finance', label: 'Finance' },
          { value: 'retail', label: 'Retail' },
          { value: 'manufacturing', label: 'Manufacturing' },
          { value: 'consulting', label: 'Consulting' },
          { value: 'education', label: 'Education' },
          { value: 'real-estate', label: 'Real Estate' },
          { value: 'food-beverage', label: 'Food & Beverage' },
        ],
      },
    ],
  },
  {
    id: 3,
    title: 'Founder Background',
    description: 'Share your experience and expertise',
    fields: [
      {
        name: 'founderBackground',
        label: 'Founder Background & Experience',
        type: 'textarea',
        required: true,
        helpPrompt: 'Help me describe my professional background and relevant experience',
        validation: (value) => !value?.trim() ? 'Founder background is required' : null,
        maxLength: 1000,
      },
    ],
  },
  {
    id: 4,
    title: 'Services & Offerings',
    description: 'Describe what you offer to customers',
    fields: [
      {
        name: 'servicesDescription',
        label: 'Services Description',
        type: 'textarea',
        required: true,
        helpPrompt: 'Help me articulate our core services and value proposition',
        validation: (value) => !value?.trim() ? 'Services description is required' : null,
        maxLength: 1000,
      },
      {
        name: 'keyDifferentiators',
        label: 'Key Differentiators',
        type: 'textarea',
        required: false,
        researchRefinable: true,
        helpPrompt: 'Identify unique competitive advantages and differentiators',
        validation: () => null, // Optional — research will inform if blank
        maxLength: 500,
      },
    ],
  },
  {
    id: 5,
    title: 'Competition & IP',
    description: 'Market positioning and intellectual property',
    fields: [
      {
        name: 'knownCompetitors',
        label: 'Known Competitors',
        type: 'textarea',
        required: false,
        researchRefinable: true,
        helpPrompt: 'Identify potential competitors and market alternatives',
        validation: () => null, // Optional — research will identify competitors
        maxLength: 500,
      },
      {
        name: 'existingIP',
        label: 'Existing Intellectual Property',
        type: 'textarea',
        required: true,
        helpPrompt: 'Describe any patents, trademarks, or proprietary assets',
        validation: (value) => !value?.trim() ? 'Please describe existing IP or enter "None"' : null,
        maxLength: 500,
      },
    ],
  },
  {
    id: 6,
    title: 'Business Goals',
    description: 'Revenue targets and team size',
    fields: [
      {
        name: 'year1RevenueGoal',
        label: 'Year 1 Revenue Goal ($)',
        type: 'number',
        required: false,
        researchRefinable: true,
        helpPrompt: 'Suggest a realistic first-year revenue target for this business model',
        validation: (value) => {
          // Optional — 0 or empty means research will inform
          const num = Number(value);
          if (num < 0) return 'Revenue goal cannot be negative';
          return null;
        },
      },
      {
        name: 'currentTeamSize',
        label: 'Current Team Size',
        type: 'number',
        required: true,
        helpPrompt: 'What is the optimal starting team size for this business?',
        validation: (value) => {
          const num = Number(value);
          if (num < 0) return 'Team size cannot be negative';
          return null;
        },
      },
      {
        name: 'targetCompanySize',
        label: 'Target Company Size',
        type: 'select',
        required: true,
        helpPrompt: 'Recommend the ideal long-term company size for this business model',
        validation: (value) => !value ? 'Target company size is required' : null,
        options: [
          { value: 'solopreneur', label: 'Solopreneur' },
          { value: 'small-team-2-10', label: 'Small Team (2-10)' },
          { value: 'medium-team-11-50', label: 'Medium Team (11-50)' },
          { value: 'large-team-51-200', label: 'Large Team (51-200)' },
          { value: 'enterprise-200+', label: 'Enterprise (200+)' },
        ],
      },
    ],
  },
];

export function WizardScreen() {
  const {
    businessInfo,
    updateBusinessInfo,
    wizardStep,
    setWizardStep,
    setCurrentStep,
    llmConfig,
    apiKey,
    setError,
    clearError,
    errors,
  } = useAppContext();

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [aiSuggestion, setAiSuggestion] = useState<string>('');
  const [isLoadingAI, setIsLoadingAI] = useState(false);
  const [showAIModal, setShowAIModal] = useState(false);
  const [currentField, setCurrentField] = useState<WizardField | null>(null);
  const [showReview, setShowReview] = useState(false);

  const currentStepData = WIZARD_STEPS.find(step => step.id === wizardStep);
  const totalSteps = WIZARD_STEPS.length;

  const getFieldValue = useCallback((fieldName: keyof BusinessInfo) => {
    return businessInfo[fieldName] || '';
  }, [businessInfo]);

  const setFieldValue = useCallback((fieldName: keyof BusinessInfo, value: any) => {
    updateBusinessInfo({ [fieldName]: value });
    clearError(fieldName);
  }, [updateBusinessInfo, clearError]);

  const handleAISuggestion = useCallback(async (field: WizardField) => {
    if (!llmConfig || !apiKey) return;

    setCurrentField(field);
    setIsLoadingAI(true);
    setAiSuggestion('');
    setShowAIModal(true);

    try {
      const context = Object.entries(businessInfo)
        .filter(([_, value]) => value)
        .map(([key, value]) => `${key}: ${value}`)
        .join('\n');

      const prompt = `${field.helpPrompt}

Current business context:
${context}

Please provide a helpful suggestion for the "${field.label}" field.`;

      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          config: llmConfig,
          apiKey,
          prompt,
          systemPrompt: 'You are a business planning assistant. Provide concise, actionable suggestions.',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get AI suggestion');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let suggestion = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.type === 'token') {
                  suggestion += data.content;
                  setAiSuggestion(suggestion);
                }
              } catch {
                // Skip invalid JSON
              }
            }
          }
        }
      }
    } catch (error) {
      setError('ai_suggestion', 'Failed to get AI suggestion. Please try again.');
    } finally {
      setIsLoadingAI(false);
    }
  }, [llmConfig, apiKey, businessInfo, setError]);

  const validateCurrentStep = useCallback(() => {
    if (!currentStepData) return true;

    let hasErrors = false;
    for (const field of currentStepData.fields) {
      const value = getFieldValue(field.name);
      const error = field.validation(value);
      if (error) {
        setError(field.name, error);
        hasErrors = true;
      }
    }
    return !hasErrors;
  }, [currentStepData, getFieldValue, setError]);

  const handleNext = useCallback(() => {
    if (!validateCurrentStep()) return;

    if (wizardStep < totalSteps) {
      setWizardStep(wizardStep + 1);
    } else {
      setShowReview(true);
    }
  }, [validateCurrentStep, wizardStep, totalSteps, setWizardStep]);

  const handlePrevious = useCallback(() => {
    if (wizardStep > 1) {
      setWizardStep(wizardStep - 1);
    }
  }, [wizardStep, setWizardStep]);

  const handleSubmit = useCallback(async () => {
    // Skip validation for research-refinable fields that are blank
    const validation = validateBusinessInfo(businessInfo);
    const nonRefinableErrors = validation.errors.filter(err => {
      const step = WIZARD_STEPS.flatMap(s => s.fields).find(f => f.name === err.field);
      return step && !step.researchRefinable;
    });

    if (nonRefinableErrors.length > 0) {
      for (const error of nonRefinableErrors) {
        setError(error.field, error.message);
      }
      setShowReview(false);
      const firstErrorStep = WIZARD_STEPS.find(step =>
        step.fields.some(field => nonRefinableErrors.some(e => e.field === field.name))
      );
      if (firstErrorStep) {
        setWizardStep(firstErrorStep.id);
      }
      return;
    }

    setIsSubmitting(true);
    try {
      setCurrentStep('pipeline');
    } catch (error) {
      setError('submit', 'Failed to proceed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }, [businessInfo, setError, setCurrentStep, setWizardStep]);

  /** Check if a field was left blank and is research-refinable */
  const isBlankRefinable = useCallback((field: WizardField): boolean => {
    if (!field.researchRefinable) return false;
    const value = getFieldValue(field.name);
    if (field.type === 'number') return !value || Number(value) === 0;
    return !value || (typeof value === 'string' && !value.trim());
  }, [getFieldValue]);

  const renderField = useCallback((field: WizardField) => {
    const value = getFieldValue(field.name);
    const error = errors[field.name];

    switch (field.type) {
      case 'text':
        return (
          <Input
            type="text"
            value={value as string}
            onChange={(e) => setFieldValue(field.name, e.target.value)}
            placeholder={field.label}
            error={error}
            maxLength={field.maxLength}
            required={field.required}
          />
        );

      case 'textarea':
        return (
          <div>
            <textarea
              className={`textarea ${error ? 'input-error' : ''}`}
              value={value as string}
              onChange={(e) => setFieldValue(field.name, e.target.value)}
              placeholder={field.researchRefinable ? `${field.label} (optional — research will inform)` : field.label}
              maxLength={field.maxLength}
              required={field.required}
              rows={4}
              aria-invalid={!!error}
            />
            {error && <p className="error-message" role="alert">{error}</p>}
          </div>
        );

      case 'number':
        return (
          <Input
            type="number"
            value={value as number}
            onChange={(e) => setFieldValue(field.name, Number(e.target.value))}
            error={error}
            required={field.required}
            min={0}
          />
        );

      case 'select':
        return (
          <Select
            options={field.options || []}
            value={value as string}
            onChange={(val) => setFieldValue(field.name, val)}
            error={error}
            required={field.required}
          />
        );

      case 'multiselect':
        return (
          <div className="space-y-2" role="group" aria-label={field.label}>
            {field.options?.map((option) => (
              <label key={option.value} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={(value as string[] || []).includes(option.value)}
                  onChange={(e) => {
                    const current = (value as string[]) || [];
                    if (e.target.checked) {
                      setFieldValue(field.name, [...current, option.value]);
                    } else {
                      setFieldValue(field.name, current.filter(v => v !== option.value));
                    }
                  }}
                  className="w-4 h-4 text-blue-600 bg-slate-800 border-slate-600 rounded focus:ring-blue-500"
                />
                <span className="text-slate-200">{option.label}</span>
              </label>
            ))}
            {error && <p className="error-message" role="alert">{error}</p>}
          </div>
        );

      default:
        return null;
    }
  }, [getFieldValue, setFieldValue, errors]);

  if (!currentStepData) {
    return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400">Invalid step</div>;
  }

  if (showReview) {
    // Count how many refinable fields are blank
    const blankRefinableCount = WIZARD_STEPS
      .flatMap(s => s.fields)
      .filter(f => f.researchRefinable && isBlankRefinable(f))
      .length;

    return (
      <div className="min-h-screen bg-slate-950 p-6">
        <div className="max-w-2xl mx-auto space-y-6">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-slate-100 mb-2">
              Review Your Information
            </h1>
            <p className="text-slate-400">
              Please review your business information before proceeding
            </p>
          </div>

          {blankRefinableCount > 0 && (
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
              <p className="text-blue-300 text-sm">
                {blankRefinableCount} field{blankRefinableCount > 1 ? 's' : ''} left blank will be informed by the research phase.
                After stages 1-2 complete, you will review AI-suggested values before the pipeline continues.
              </p>
            </div>
          )}

          <div className="bg-slate-900 rounded-lg p-6 space-y-6">
            {WIZARD_STEPS.map((step) => (
              <div key={step.id} className="border-b border-slate-800 pb-4 last:border-b-0">
                <h3 className="text-lg font-semibold text-slate-100 mb-3">
                  {step.title}
                </h3>
                <div className="space-y-3">
                  {step.fields.map((field) => {
                    const blank = isBlankRefinable(field);
                    return (
                      <div key={field.name} className="flex justify-between">
                        <span className="text-slate-400">{field.label}:</span>
                        <span className={`max-w-md text-right ${blank ? 'text-blue-400 italic text-sm' : 'text-slate-200'}`}>
                          {blank
                            ? 'Will be informed by research'
                            : Array.isArray(getFieldValue(field.name))
                              ? (getFieldValue(field.name) as string[]).join(', ')
                              : String(getFieldValue(field.name) || 'Not specified')
                          }
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="flex space-x-4">
            <Button
              variant="secondary"
              onClick={() => setShowReview(false)}
              disabled={isSubmitting}
              className="flex-1"
            >
              Back to Edit
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting}
              loading={isSubmitting}
              className="flex-1"
            >
              Start Pipeline
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 p-6">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-slate-100 mb-2">
            {currentStepData.title}
          </h1>
          <p className="text-slate-400">
            {currentStepData.description}
          </p>
        </div>

        {/* Progress */}
        <ProgressBar
          current={wizardStep}
          total={totalSteps}
          showLabels
          className="mb-8"
        />

        {/* Fields */}
        <fieldset className="bg-slate-900 rounded-lg p-6 space-y-6">
          <legend className="sr-only">{currentStepData.title} Fields</legend>

          {currentStepData.fields.map((field) => (
            <div key={field.name}>
              <div className="flex items-center justify-between mb-2">
                <div>
                  <label className="label">
                    {field.label}
                    {field.required && <span className="text-red-400"> *</span>}
                    {field.researchRefinable && !field.required && (
                      <span className="text-slate-500 text-sm font-normal ml-1">(optional)</span>
                    )}
                  </label>
                  {field.researchRefinable && (
                    <p className="text-xs text-blue-400/70 mt-0.5">{REFINABLE_HINT}</p>
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleAISuggestion(field)}
                  disabled={!llmConfig || !apiKey}
                  className="text-blue-400 hover:text-blue-300"
                >
                  AI Help
                </Button>
              </div>
              {renderField(field)}
            </div>
          ))}
        </fieldset>

        {/* Navigation */}
        <div className="flex justify-between">
          <Button
            variant="secondary"
            onClick={handlePrevious}
            disabled={wizardStep === 1}
          >
            Previous
          </Button>
          <Button onClick={handleNext}>
            {wizardStep === totalSteps ? 'Review' : 'Next'}
          </Button>
        </div>

        {/* AI Suggestion Modal */}
        <Modal
          isOpen={showAIModal}
          onClose={() => setShowAIModal(false)}
          title={currentField ? `AI Suggestion for ${currentField.label}` : 'AI Suggestion'}
          size="lg"
        >
          <div className="space-y-4">
            <div aria-live="polite">
              {isLoadingAI ? (
                <div className="flex items-center space-x-2 text-slate-400">
                  <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Getting AI suggestion...</span>
                </div>
              ) : aiSuggestion ? (
                <div className="bg-slate-800 rounded-lg p-4">
                  <p className="text-slate-200">{aiSuggestion}</p>
                </div>
              ) : null}
            </div>

            <div className="flex space-x-3">
              <Button
                variant="secondary"
                onClick={() => setShowAIModal(false)}
                className="flex-1"
              >
                Close
              </Button>
              {aiSuggestion && currentField && (
                <Button
                  onClick={() => {
                    setFieldValue(currentField.name, aiSuggestion);
                    setShowAIModal(false);
                  }}
                  className="flex-1"
                >
                  Use Suggestion
                </Button>
              )}
            </div>
          </div>
        </Modal>
      </div>
    </div>
  );
}
