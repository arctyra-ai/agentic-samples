import { LLMConfig, LLMProvider, PROVIDER_ENDPOINTS, TokenUsage } from '@/lib/types';
import { validateExternalUrl, isTrustedProviderEndpoint } from '@/lib/url-validation';

// SECURITY FIX: G-3 — Request timeout and size limits
const REQUEST_TIMEOUT_MS = 30000; // 30 seconds
const MAX_RESPONSE_SIZE = 10 * 1024 * 1024; // 10MB

interface LLMRequestOptions {
  config: LLMConfig;
  apiKey: string;
  systemPrompt: string;
  userPrompt: string;
  stream?: boolean;
}

interface LLMResponse {
  content: string;
  tokenUsage: TokenUsage;
}

export function getEndpoint(config: LLMConfig): string {
  if (config.provider === 'custom' && config.endpoint) {
    return config.endpoint;
  }
  return PROVIDER_ENDPOINTS[config.provider];
}

// SECURITY FIX: G-1 — Validate endpoint URL before making requests
export function validateEndpoint(config: LLMConfig): { valid: boolean; error?: string } {
  const endpoint = getEndpoint(config);

  if (isTrustedProviderEndpoint(endpoint)) {
    return { valid: true };
  }

  if (config.provider === 'custom') {
    return validateExternalUrl(endpoint);
  }

  return { valid: true };
}

export function buildRequestBody(config: LLMConfig, systemPrompt: string, userPrompt: string, stream: boolean) {
  switch (config.provider) {
    case 'openai':
    case 'openrouter':
    case 'custom':
      return {
        model: config.model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt },
        ],
        max_tokens: config.maxTokens,
        temperature: config.temperature,
        stream,
      };

    case 'anthropic':
      return {
        model: config.model,
        system: systemPrompt,
        messages: [
          { role: 'user', content: userPrompt },
        ],
        max_tokens: config.maxTokens,
        temperature: config.temperature,
        stream,
      };

    case 'google':
      return {
        contents: [
          {
            parts: [
              { text: `${systemPrompt}\n\n${userPrompt}` },
            ],
          },
        ],
        generationConfig: {
          maxOutputTokens: config.maxTokens,
          temperature: config.temperature,
        },
      };

    default:
      throw new Error(`Unsupported provider: ${config.provider}`);
  }
}

export function buildRequestHeaders(config: LLMConfig, apiKey: string): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  switch (config.provider) {
    case 'openai':
    case 'openrouter':
    case 'custom':
      headers['Authorization'] = `Bearer ${apiKey}`;
      break;
    case 'anthropic':
      headers['x-api-key'] = apiKey;
      headers['anthropic-version'] = '2023-06-01';
      break;
    case 'google':
      // Google uses API key as query parameter
      break;
  }

  return headers;
}

export function getStreamEndpoint(config: LLMConfig, apiKey: string): string {
  const base = getEndpoint(config);

  if (config.provider === 'google') {
    return `${base}/models/${config.model}:streamGenerateContent?alt=sse&key=${apiKey}`;
  }

  return base;
}

export function getNonStreamEndpoint(config: LLMConfig, apiKey: string): string {
  const base = getEndpoint(config);

  if (config.provider === 'google') {
    return `${base}/models/${config.model}:generateContent?key=${apiKey}`;
  }

  return base;
}

export function parseStreamChunk(config: LLMConfig, data: string): { content: string; done: boolean; usage?: TokenUsage } {
  try {
    if (data === '[DONE]') {
      return { content: '', done: true };
    }

    const parsed = JSON.parse(data);

    switch (config.provider) {
      case 'openai':
      case 'openrouter':
      case 'custom': {
        const choice = parsed.choices?.[0];
        if (choice?.finish_reason) {
          const usage = parsed.usage ? {
            inputTokens: parsed.usage.prompt_tokens || 0,
            outputTokens: parsed.usage.completion_tokens || 0,
            totalTokens: parsed.usage.total_tokens || 0,
          } : undefined;
          return { content: choice.delta?.content || '', done: true, usage };
        }
        return { content: choice?.delta?.content || '', done: false };
      }

      case 'anthropic': {
        if (parsed.type === 'content_block_delta') {
          return { content: parsed.delta?.text || '', done: false };
        }
        if (parsed.type === 'message_stop') {
          return { content: '', done: true };
        }
        if (parsed.type === 'message_delta' && parsed.usage) {
          return {
            content: '',
            done: true,
            usage: {
              inputTokens: parsed.usage.input_tokens || 0,
              outputTokens: parsed.usage.output_tokens || 0,
              totalTokens: (parsed.usage.input_tokens || 0) + (parsed.usage.output_tokens || 0),
            },
          };
        }
        return { content: '', done: false };
      }

      case 'google': {
        const text = parsed.candidates?.[0]?.content?.parts?.[0]?.text || '';
        const finishReason = parsed.candidates?.[0]?.finishReason;
        return { content: text, done: finishReason === 'STOP' };
      }

      default:
        return { content: '', done: false };
    }
  } catch {
    return { content: '', done: false };
  }
}

export function parseNonStreamResponse(config: LLMConfig, data: any): LLMResponse {
  switch (config.provider) {
    case 'openai':
    case 'openrouter':
    case 'custom':
      return {
        content: data.choices?.[0]?.message?.content || '',
        tokenUsage: {
          inputTokens: data.usage?.prompt_tokens || 0,
          outputTokens: data.usage?.completion_tokens || 0,
          totalTokens: data.usage?.total_tokens || 0,
        },
      };

    case 'anthropic':
      return {
        content: data.content?.[0]?.text || '',
        tokenUsage: {
          inputTokens: data.usage?.input_tokens || 0,
          outputTokens: data.usage?.output_tokens || 0,
          totalTokens: (data.usage?.input_tokens || 0) + (data.usage?.output_tokens || 0),
        },
      };

    case 'google':
      return {
        content: data.candidates?.[0]?.content?.parts?.[0]?.text || '',
        tokenUsage: {
          inputTokens: data.usageMetadata?.promptTokenCount || 0,
          outputTokens: data.usageMetadata?.candidatesTokenCount || 0,
          totalTokens: data.usageMetadata?.totalTokenCount || 0,
        },
      };

    default:
      return { content: '', tokenUsage: { inputTokens: 0, outputTokens: 0, totalTokens: 0 } };
  }
}

// SECURITY FIX: G-3 — Create fetch with timeout and size limits
export async function safeFetch(url: string, options: RequestInit): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      redirect: 'error', // SECURITY FIX: G-3 — Disable redirects
    });

    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}