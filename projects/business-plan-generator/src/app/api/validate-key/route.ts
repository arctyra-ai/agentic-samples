import { NextRequest, NextResponse } from 'next/server';
import { LLMConfig } from '@/lib/types';
import {
  buildRequestHeaders,
  getNonStreamEndpoint,
  buildRequestBody,
  parseNonStreamResponse,
  validateEndpoint,
  safeFetch,
} from '@/lib/llm';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { config, apiKey } = body as {
      config: LLMConfig;
      apiKey: string;
    };

    if (!config || !apiKey) {
      return NextResponse.json(
        { valid: false, error: 'Missing config or API key' },
        { status: 400 }
      );
    }

    // SECURITY FIX: G-1 — Validate endpoint URL before making requests
    const endpointValidation = validateEndpoint(config);
    if (!endpointValidation.valid) {
      return NextResponse.json(
        { valid: false, error: `Invalid endpoint: ${endpointValidation.error}` },
        { status: 400 }
      );
    }

    const endpoint = getNonStreamEndpoint(config, apiKey);
    const headers = buildRequestHeaders(config, apiKey);
    const requestBody = buildRequestBody(
      config,
      'You are a helpful assistant.',
      'Respond with exactly: "API key validated successfully."',
      false
    );

    // SECURITY FIX: G-3 — Use safeFetch with timeout and redirect protection
    const response = await safeFetch(endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');

      if (response.status === 401 || response.status === 403) {
        return NextResponse.json({
          valid: false,
          error: 'Invalid API key. Please check your key and try again.',
        });
      }

      return NextResponse.json({
        valid: false,
        error: `API error (${response.status}): ${errorText.substring(0, 200)}`,
      });
    }

    const data = await response.json();
    const parsed = parseNonStreamResponse(config, data);

    return NextResponse.json({
      valid: true,
      model: config.model,
      provider: config.provider,
      testResponse: parsed.content.substring(0, 100),
    });
  } catch (error: any) {
    if (error.name === 'AbortError') {
      return NextResponse.json(
        { valid: false, error: 'Request timed out. Please check your endpoint and try again.' },
        { status: 504 }
      );
    }
    console.error('Validate key error:', error);
    return NextResponse.json(
      { valid: false, error: 'Failed to validate API key. Please try again.' },
      { status: 500 }
    );
  }
}