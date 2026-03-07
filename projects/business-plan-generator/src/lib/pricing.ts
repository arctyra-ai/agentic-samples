import { LLMProvider, TokenUsage } from '@/lib/types';

interface PricingTier {
  inputPer1K: number;
  outputPer1K: number;
}

const PRICING: Record<string, PricingTier> = {
  // OpenAI
  'gpt-4o': { inputPer1K: 0.005, outputPer1K: 0.015 },
  'gpt-4o-mini': { inputPer1K: 0.00015, outputPer1K: 0.0006 },
  'gpt-4-turbo': { inputPer1K: 0.01, outputPer1K: 0.03 },
  'gpt-3.5-turbo': { inputPer1K: 0.0005, outputPer1K: 0.0015 },
  // Anthropic
  'claude-sonnet-4-20250514': { inputPer1K: 0.003, outputPer1K: 0.015 },
  'claude-3-5-sonnet-20241022': { inputPer1K: 0.003, outputPer1K: 0.015 },
  'claude-3-haiku-20240307': { inputPer1K: 0.00025, outputPer1K: 0.00125 },
  // Google
  'gemini-1.5-pro': { inputPer1K: 0.00125, outputPer1K: 0.005 },
  'gemini-1.5-flash': { inputPer1K: 0.000075, outputPer1K: 0.0003 },
};

export function estimateCost(model: string, usage: TokenUsage): number {
  const pricing = PRICING[model];
  if (!pricing) return 0;

  const inputCost = (usage.inputTokens / 1000) * pricing.inputPer1K;
  const outputCost = (usage.outputTokens / 1000) * pricing.outputPer1K;

  return inputCost + outputCost;
}

export function formatCost(cost: number): string {
  if (cost < 0.01) {
    return `$${cost.toFixed(4)}`;
  }
  return `$${cost.toFixed(2)}`;
}

export function estimatePipelineCost(model: string): { low: string; high: string } {
  const pricing = PRICING[model];
  if (!pricing) return { low: 'N/A', high: 'N/A' };

  // Estimate 8 stages, ~2000 input + ~3000 output tokens each (low)
  // High estimate: ~4000 input + ~6000 output tokens each
  const lowInput = 8 * 2000;
  const lowOutput = 8 * 3000;
  const highInput = 8 * 4000;
  const highOutput = 8 * 6000;

  const lowCost = (lowInput / 1000) * pricing.inputPer1K + (lowOutput / 1000) * pricing.outputPer1K;
  const highCost = (highInput / 1000) * pricing.inputPer1K + (highOutput / 1000) * pricing.outputPer1K;

  return { low: formatCost(lowCost), high: formatCost(highCost) };
}

export function getModelPricing(model: string): PricingTier | null {
  return PRICING[model] || null;
}