'use client';

import { useState, useCallback, useRef } from 'react';
import { LLMConfig, TokenUsage } from '@/lib/types';

interface UseLLMStreamOptions {
  onToken?: (token: string) => void;
  onComplete?: (fullText: string, usage?: TokenUsage) => void;
  onError?: (error: string) => void;
}

interface UseLLMStreamReturn {
  isStreaming: boolean;
  content: string;
  error: string | null;
  tokenUsage: TokenUsage | null;
  startStream: (config: LLMConfig, apiKey: string, prompt: string, systemPrompt?: string) => Promise<void>;
  stopStream: () => void;
  reset: () => void;
}

export function useLLMStream(options: UseLLMStreamOptions = {}): UseLLMStreamReturn {
  const [isStreaming, setIsStreaming] = useState(false);
  const [content, setContent] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [tokenUsage, setTokenUsage] = useState<TokenUsage | null>(null);

  const abortControllerRef = useRef<AbortController>();
  const contentRef = useRef('');

  const stopStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = undefined;
    }
    setIsStreaming(false);
  }, []);

  const reset = useCallback(() => {
    stopStream();
    setContent('');
    setError(null);
    setTokenUsage(null);
    contentRef.current = '';
  }, [stopStream]);

  const startStream = useCallback(async (
    config: LLMConfig,
    apiKey: string,
    prompt: string,
    systemPrompt?: string
  ) => {
    // Reset state
    reset();
    setIsStreaming(true);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          config,
          apiKey,
          prompt,
          systemPrompt: systemPrompt || 'You are a helpful business planning assistant.',
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

      while (true) {
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
                contentRef.current += data.content;
                setContent(contentRef.current);
                options.onToken?.(data.content);
                break;

              case 'usage':
                const usage: TokenUsage = {
                  inputTokens: data.inputTokens || 0,
                  outputTokens: data.outputTokens || 0,
                  totalTokens: data.totalTokens || 0,
                };
                setTokenUsage(usage);
                break;

              case 'done':
                options.onComplete?.(contentRef.current, tokenUsage || undefined);
                break;

              case 'error':
                throw new Error(data.content || 'Stream error');
            }
          } catch (parseError: any) {
            if (parseError.message && parseError.message !== 'Stream error') {
              // JSON parse error — skip
              continue;
            }
            throw parseError;
          }
        }
      }

      options.onComplete?.(contentRef.current, tokenUsage || undefined);
    } catch (err: any) {
      if (err.name === 'AbortError') {
        // Stream was intentionally stopped
        return;
      }
      const errorMsg = err.message || 'Stream failed';
      setError(errorMsg);
      options.onError?.(errorMsg);
    } finally {
      setIsStreaming(false);
    }
  }, [reset, options, tokenUsage]);

  return {
    isStreaming,
    content,
    error,
    tokenUsage,
    startStream,
    stopStream,
    reset,
  };
}