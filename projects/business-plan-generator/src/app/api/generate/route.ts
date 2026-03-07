import { NextRequest, NextResponse } from 'next/server';
import {
  buildRequestBody,
  buildRequestHeaders,
  getStreamEndpoint,
  parseStreamChunk,
  validateEndpoint,
  safeFetch,
} from '@/lib/llm';
import { LLMConfig } from '@/lib/types';

// SECURITY FIX: G-4 — Server-side input length limits
const MAX_PROMPT_LENGTH = 50000;
const MAX_SYSTEM_PROMPT_LENGTH = 10000;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { config, apiKey, prompt, systemPrompt } = body as {
      config: LLMConfig;
      apiKey: string;
      prompt: string;
      systemPrompt: string;
    };

    // Validate required fields
    if (!config || !apiKey || !prompt) {
      return NextResponse.json(
        { error: 'Missing required fields: config, apiKey, prompt' },
        { status: 400 }
      );
    }

    // SECURITY FIX: G-4 — Enforce server-side input length validation
    if (prompt.length > MAX_PROMPT_LENGTH) {
      return NextResponse.json(
        { error: `Prompt exceeds maximum length of ${MAX_PROMPT_LENGTH} characters` },
        { status: 400 }
      );
    }

    if (systemPrompt && systemPrompt.length > MAX_SYSTEM_PROMPT_LENGTH) {
      return NextResponse.json(
        { error: `System prompt exceeds maximum length of ${MAX_SYSTEM_PROMPT_LENGTH} characters` },
        { status: 400 }
      );
    }

    // SECURITY FIX: G-1 — Validate endpoint URL before making requests
    const endpointValidation = validateEndpoint(config);
    if (!endpointValidation.valid) {
      return NextResponse.json(
        { error: `Invalid endpoint: ${endpointValidation.error}` },
        { status: 400 }
      );
    }

    const endpoint = getStreamEndpoint(config, apiKey);
    const headers = buildRequestHeaders(config, apiKey);
    const requestBody = buildRequestBody(config, systemPrompt || 'You are a helpful assistant.', prompt, true);

    // SECURITY FIX: G-3 — Use safeFetch with timeout and redirect protection
    const response = await safeFetch(endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      return NextResponse.json(
        { error: `LLM API error (${response.status}): ${errorText.substring(0, 500)}` },
        { status: response.status }
      );
    }

    // Create a TransformStream for SSE forwarding
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        const reader = response.body?.getReader();
        if (!reader) {
          controller.close();
          return;
        }

        const decoder = new TextDecoder();
        let buffer = '';
        // SECURITY FIX: G-3 — Track response size to enforce limits
        let totalSize = 0;
        const MAX_SIZE = 10 * 1024 * 1024; // 10MB

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            totalSize += chunk.length;

            // SECURITY FIX: G-3 — Enforce response size limit
            if (totalSize > MAX_SIZE) {
              const errorEvent = `data: ${JSON.stringify({ type: 'error', content: 'Response exceeded maximum size limit' })}\n\n`;
              controller.enqueue(encoder.encode(errorEvent));
              break;
            }

            buffer += chunk;
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
              const trimmed = line.trim();
              if (trimmed.startsWith('data: ')) {
                const data = trimmed.slice(6);

                if (data === '[DONE]') {
                  const doneEvent = `data: ${JSON.stringify({ type: 'done' })}\n\n`;
                  controller.enqueue(encoder.encode(doneEvent));
                  continue;
                }

                try {
                  const parsed = parseStreamChunk(config, data);
                  if (parsed.content) {
                    const tokenEvent = `data: ${JSON.stringify({ type: 'token', content: parsed.content })}\n\n`;
                    controller.enqueue(encoder.encode(tokenEvent));
                  }
                  if (parsed.done && parsed.usage) {
                    const usageEvent = `data: ${JSON.stringify({ type: 'usage', ...parsed.usage })}\n\n`;
                    controller.enqueue(encoder.encode(usageEvent));
                  }
                } catch {
                  // Skip unparseable chunks
                }
              }
            }
          }
        } catch (error: any) {
          if (error.name === 'AbortError') {
            const errorEvent = `data: ${JSON.stringify({ type: 'error', content: 'Request timed out' })}\n\n`;
            controller.enqueue(encoder.encode(errorEvent));
          } else {
            const errorEvent = `data: ${JSON.stringify({ type: 'error', content: 'Stream processing error' })}\n\n`;
            controller.enqueue(encoder.encode(errorEvent));
          }
        } finally {
          controller.close();
        }
      },
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  } catch (error: any) {
    if (error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Request timed out' },
        { status: 504 }
      );
    }
    console.error('Generate API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}