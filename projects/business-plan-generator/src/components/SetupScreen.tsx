'use client';

import React, { useState, useCallback } from 'react';
import { useAppContext } from '@/context/AppContext';
import { LLMProvider, LLMConfig, MODEL_OPTIONS, PROVIDER_ENDPOINTS } from '@/lib/types';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { estimatePipelineCost } from '@/lib/pricing';
// SECURITY FIX: G-1 — Import URL validation for custom endpoint
import { validateExternalUrl } from '@/lib/url-validation';

const PROVIDER_OPTIONS = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'google', label: 'Google AI' },
  { value: 'openrouter', label: 'OpenRouter' },
  { value: 'custom', label: 'Custom Endpoint' },
];

export function SetupScreen() {
  const { setLLMConfig, setApiKey, setCurrentStep, setError, errors, clearError } = useAppContext();

  const [provider, setProvider] = useState<LLMProvider>('openai');
  const [model, setModel] = useState<string>('gpt-4o');
  const [apiKeyInput, setApiKeyInput] = useState<string>('');
  const [customEndpoint, setCustomEndpoint] = useState<string>('');
  const [customModel, setCustomModel] = useState<string>('');
  const [maxTokens, setMaxTokens] = useState<number>(4096);
  const [temperature, setTemperature] = useState<number>(0.7);
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [isValidated, setIsValidated] = useState<boolean>(false);
  // SECURITY FIX: G-2 — State for API key visibility toggle
  const [showApiKey, setShowApiKey] = useState<boolean>(false);

  const availableModels = MODEL_OPTIONS.filter(m => m.provider === provider);

  const handleProviderChange = useCallback((value: string) => {
    const p = value as LLMProvider;
    setProvider(p);
    setIsValidated(false);
    clearError('apiKey');
    clearError('customEndpoint');

    const models = MODEL_OPTIONS.filter(m => m.provider === p);
    if (models.length > 0) {
      setModel(models[0].value);
      setMaxTokens(Math.min(4096, models[0].maxTokens));
    } else {
      setModel('');
    }
  }, [clearError]);

  const handleValidateKey = useCallback(async () => {
    if (!apiKeyInput.trim()) {
      setError('apiKey', 'API key is required');
      return;
    }

    // SECURITY FIX: G-1 — Validate custom endpoint URL before sending to backend
    if (provider === 'custom') {
      if (!customEndpoint.trim()) {
        setError('customEndpoint', 'Custom endpoint URL is required');
        return;
      }
      const urlValidation = validateExternalUrl(customEndpoint);
      if (!urlValidation.valid) {
        setError('customEndpoint', urlValidation.error || 'Invalid endpoint URL');
        return;
      }
      if (!customModel.trim()) {
        setError('customModel', 'Model name is required for custom endpoints');
        return;
      }
    }

    setIsValidating(true);
    clearError('apiKey');
    clearError('customEndpoint');
    clearError('customModel');

    try {
      const config: LLMConfig = {
        provider,
        model: provider === 'custom' ? customModel : model,
        endpoint: provider === 'custom' ? customEndpoint : undefined,
        maxTokens,
        temperature,
      };

      const response = await fetch('/api/validate-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config, apiKey: apiKeyInput }),
      });

      const data = await response.json();

      if (data.valid) {
        setIsValidated(true);
        clearError('apiKey');
      } else {
        setError('apiKey', data.error || 'Invalid API key');
        setIsValidated(false);
      }
    } catch (error) {
      setError('apiKey', 'Failed to validate API key. Please check your network connection.');
      setIsValidated(false);
    } finally {
      setIsValidating(false);
    }
  }, [apiKeyInput, provider, model, customEndpoint, customModel, maxTokens, temperature, setError, clearError]);

  const handleContinue = useCallback(() => {
    if (!isValidated) return;

    const config: LLMConfig = {
      provider,
      model: provider === 'custom' ? customModel : model,
      endpoint: provider === 'custom' ? customEndpoint : undefined,
      maxTokens,
      temperature,
    };

    setLLMConfig(config);
    setApiKey(apiKeyInput);
    setCurrentStep('wizard');
  }, [isValidated, provider, model, customEndpoint, customModel, maxTokens, temperature, apiKeyInput, setLLMConfig, setApiKey, setCurrentStep]);

  const selectedModel = MODEL_OPTIONS.find(m => m.value === model);
  const costEstimate = selectedModel ? estimatePipelineCost(model) : null;

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
      <div className="max-w-xl w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gradient mb-3">
            Business Plan Generator
          </h1>
          <p className="text-slate-400 text-lg">
            AI-powered business plan generation with multi-stage pipeline
          </p>
        </div>

        {/* Setup Card */}
        <div className="card space-y-6">
          <h2 className="text-xl font-semibold text-slate-100">
            LLM Configuration
          </h2>

          {/* Provider Selection */}
          <Select
            label="Provider"
            options={PROVIDER_OPTIONS}
            value={provider}
            onChange={handleProviderChange}
          />

          {/* Model Selection */}
          {provider !== 'custom' ? (
            <Select
              label="Model"
              options={availableModels.map(m => ({ value: m.value, label: m.label }))}
              value={model}
              onChange={(val) => {
                setModel(val);
                setIsValidated(false);
                const m = MODEL_OPTIONS.find(opt => opt.value === val);
                if (m) setMaxTokens(Math.min(4096, m.maxTokens));
              }}
            />
          ) : (
            <>
              <Input
                label="Custom Endpoint URL"
                type="url"
                value={customEndpoint}
                onChange={(e) => {
                  setCustomEndpoint(e.target.value);
                  setIsValidated(false);
                  clearError('customEndpoint');
                }}
                placeholder="https://your-api-endpoint.com/v1/chat/completions"
                error={errors.customEndpoint}
              />
              <Input
                label="Model Name"
                type="text"
                value={customModel}
                onChange={(e) => {
                  setCustomModel(e.target.value);
                  setIsValidated(false);
                  clearError('customModel');
                }}
                placeholder="e.g., gpt-4, llama-3"
                error={errors.customModel}
              />
            </>
          )}

          {/* API Key */}
          <div className="w-full">
            <label htmlFor="api-key-input" className="label">API Key</label>
            {/* SECURITY FIX: G-2 — Mask API key input with toggle visibility */}
            <div className="relative">
              <input
                id="api-key-input"
                type={showApiKey ? 'text' : 'password'}
                value={apiKeyInput}
                onChange={(e) => {
                  setApiKeyInput(e.target.value);
                  setIsValidated(false);
                  clearError('apiKey');
                }}
                placeholder="Enter your API key"
                className={`input pr-10 ${errors.apiKey ? 'input-error' : ''}`}
                aria-invalid={!!errors.apiKey}
                aria-describedby={errors.apiKey ? 'api-key-error' : undefined}
                autoComplete="off"
              />
              <button
                type="button"
                onClick={() => setShowApiKey(!showApiKey)}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
                aria-label={showApiKey ? 'Hide API key' : 'Show API key'}
              >
                {showApiKey ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
            </div>
            {errors.apiKey && (
              <p id="api-key-error" className="error-message" role="alert">
                {errors.apiKey}
              </p>
            )}
            <p className="text-xs text-slate-500 mt-1">
              Your API key is sent directly to the provider and is never stored on our servers.
            </p>
          </div>

          {/* Advanced Settings */}
          <details className="group">
            <summary className="text-sm text-slate-400 cursor-pointer hover:text-slate-300 transition-colors">
              Advanced Settings
            </summary>
            <div className="mt-4 space-y-4 pl-4 border-l-2 border-slate-800">
              <div>
                <label htmlFor="max-tokens" className="label">Max Tokens per Request</label>
                <input
                  id="max-tokens"
                  type="number"
                  value={maxTokens}
                  onChange={(e) => {
                    setMaxTokens(Number(e.target.value));
                    setIsValidated(false);
                  }}
                  min={256}
                  max={selectedModel?.maxTokens || 128000}
                  className="input"
                />
              </div>
              <div>
                <label htmlFor="temperature" className="label">Temperature: {temperature}</label>
                <input
                  id="temperature"
                  type="range"
                  value={temperature}
                  onChange={(e) => {
                    setTemperature(Number(e.target.value));
                    setIsValidated(false);
                  }}
                  min={0}
                  max={2}
                  step={0.1}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
                <div className="flex justify-between text-xs text-slate-500 mt-1">
                  <span>Precise (0)</span>
                  <span>Creative (2)</span>
                </div>
              </div>
            </div>
          </details>

          {/* Cost Estimate */}
          {costEstimate && (
            <div className="bg-slate-800 rounded-lg p-3">
              <p className="text-sm text-slate-400">
                Estimated pipeline cost: <span className="text-green-400 font-medium">{costEstimate.low} – {costEstimate.high}</span>
              </p>
            </div>
          )}

          {/* Validation Status */}
          {isValidated && (
            <div className="bg-green-900/20 border border-green-500/20 rounded-lg p-3">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-green-400 text-sm">API key validated successfully</span>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <Button
              onClick={handleValidateKey}
              loading={isValidating}
              disabled={!apiKeyInput.trim() || isValidating}
              variant="secondary"
              className="flex-1"
            >
              {isValidating ? 'Validating...' : 'Validate Key'}
            </Button>
            <Button
              onClick={handleContinue}
              disabled={!isValidated}
              className="flex-1"
            >
              Continue to Wizard →
            </Button>
          </div>
        </div>

        {/* Footer Note */}
        <p className="text-center text-xs text-slate-600">
          All API calls are made directly from this application to your chosen provider.
          No data is stored or transmitted to third parties.
        </p>
      </div>
    </div>
  );
}