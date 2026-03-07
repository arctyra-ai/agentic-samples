# Business Plan Generator — Developer Guide

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [State Management](#state-management)
5. [Development Commands](#development-commands)
6. [Code Style Conventions](#code-style-conventions)
7. [How to Add a New LLM Provider](#how-to-add-a-new-llm-provider)
8. [How to Add a New Pipeline Stage](#how-to-add-a-new-pipeline-stage)
9. [How to Modify Prompts](#how-to-modify-prompts)
10. [How to Modify the DOCX Output Format](#how-to-modify-the-docx-output-format)
11. [How to Update Model Pricing Data](#how-to-update-model-pricing-data)
12. [Security Architecture](#security-architecture)
13. [Building for Production](#building-for-production)
14. [API Route Reference](#api-route-reference)

---

## Architecture Overview

The application is a single-page Next.js 14 application (App Router) with three API routes. It follows a client-heavy architecture where nearly all application state lives in the browser, and API routes serve as thin proxies to external LLM APIs.

```
┌─────────────────────────────────────────────────────────────┐
│ Browser (Client)                                             │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────┐│
│  │ SetupScreen│→ │WizardScreen│→ │PipelineScreen│→│Output  ││
│  │            │  │            │  │            │  │Screen  ││
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └───┬────┘│
│        │               │               │              │      │
│        └───────────────┼───────────────┼──────────────┘      │
│                        │               │                     │
│              ┌─────────┴──────┐  ┌─────┴─────────┐          │
│              │  AppContext     │  │  usePipeline   │          │
│              │  (global state)│  │  useLLMStream   │          │
│              └────────────────┘  └───────┬────────┘          │
│                                          │                   │
└──────────────────────────────────────────┼───────────────────┘
                                           │ fetch()
┌──────────────────────────────────────────┼───────────────────┐
│ Server (Next.js API Routes)              │                    │
│                                          │                    │
│  /api/validate-key  ← key validation     │                    │
│  /api/generate      ← SSE streaming proxy│                    │
│  /api/export-docx   ← DOCX generation    │                    │
│                                          │                    │
└──────────────────────────────────────────┼───────────────────┘
                                           │ fetch()
                                           ▼
                              ┌─────────────────────┐
                              │ External LLM API     │
                              │ (OpenAI, Anthropic,  │
                              │  Google, OpenRouter,  │
                              │  or Custom)           │
                              └─────────────────────┘
```

### Key design decisions

- **No database.** All state is ephemeral, held in React context and component state.
- **No server-side API key storage.** API keys are sent by the client per-request and never persisted.
- **SSE streaming.** The `/api/generate` route proxies streaming responses from LLM providers to the browser, allowing real-time token display.
- **Provider abstraction.** `src/lib/llm.ts` normalizes the differences between OpenAI, Anthropic, Google, and OpenRouter APIs behind a common interface.
- **Prompt pipeline.** `src/lib/prompts.ts` defines all eight stage prompts. Each stage receives the business context and the outputs of all previous stages.
- **Research-refinable fields.** Three wizard fields (competitors, differentiators, revenue goal) can be left blank. After stage 2, the pipeline pauses for the user to review AI-extracted suggestions before continuing.

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | Next.js 14 (App Router) | Full-stack React framework |
| Language | TypeScript 5.4 | Type safety |
| Styling | Tailwind CSS 3.4 | Utility-first CSS |
| Markdown rendering | react-markdown + remark-gfm + rehype-sanitize | Safe Markdown to HTML |
| DOCX generation | docx (v8.5) | Server-side Word document creation |
| State management | React Context API | Global app state |
| Streaming | Server-Sent Events (SSE) | Real-time LLM output |

---

## Project Structure

```
src/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout, wraps with AppProvider
│   ├── page.tsx                  # Route handler — renders current step
│   ├── globals.css               # Global styles and Tailwind layers
│   └── api/
│       ├── generate/route.ts     # SSE streaming LLM proxy
│       ├── validate-key/route.ts # API key validation endpoint
│       └── export-docx/route.ts  # DOCX file generation
│
├── components/
│   ├── SetupScreen.tsx           # LLM provider/model/key setup
│   ├── WizardScreen.tsx          # Multi-step business info form
│   ├── PipelineScreen.tsx        # Stage execution with progress UI
│   ├── OutputScreen.tsx          # Final plan display and export
│   └── ui/                       # Reusable UI primitives
│       ├── Button.tsx
│       ├── Input.tsx
│       ├── Select.tsx
│       ├── Badge.tsx
│       ├── Modal.tsx
│       ├── ProgressBar.tsx
│       ├── StreamingText.tsx
│       ├── MarkdownRenderer.tsx
│       └── TokenDisplay.tsx
│
├── context/
│   └── AppContext.tsx             # Global React context (state store)
│
├── hooks/
│   ├── useLLMStream.ts           # Hook for streaming LLM requests
│   └── usePipeline.ts            # Hook for multi-stage pipeline orchestration
│
└── lib/
    ├── types.ts                  # All TypeScript types and constants
    ├── prompts.ts                # Stage prompt templates
    ├── llm.ts                    # LLM API abstraction (request building, parsing)
    ├── pricing.ts                # Token cost estimation
    ├── utils.ts                  # Validation, formatting utilities
    ├── url-validation.ts         # SSRF prevention (URL validation)
    └── docx-utils.ts             # Markdown-to-DOCX conversion
```

---

## State Management

All global state is managed through `AppContext` (`src/context/AppContext.tsx`). The context provides:

| State | Type | Description |
|-------|------|-------------|
| `currentStep` | `AppStep` | Which screen is displayed (`'setup'`, `'wizard'`, `'pipeline'`, `'output'`) |
| `llmConfig` | `LLMConfig \| null` | Provider, model, endpoint, maxTokens, temperature |
| `apiKey` | `string` | The user's API key (held in memory only) |
| `businessInfo` | `BusinessInfo` | All wizard form data |
| `wizardStep` | `number` | Current wizard page (1–6) |
| `executionMode` | `PipelineMode` | `'step-by-step'` or `'full-auto'` |
| `pipelineOutputs` | `string[]` | Output text from each completed stage |
| `totalTokenUsage` | `TokenUsage` | Cumulative token counts |
| `finalOutput` | `string` | The final assembled business plan text |
| `errors` | `Record<string, string>` | Field-level error messages |

The pipeline orchestration state (individual stage statuses, streaming state, abort controllers) is managed locally in the `usePipeline` hook using `useState` and `useRef`.

### Research-refinable fields

Three `BusinessInfo` fields are designated as research-refinable: `keyDifferentiators`, `knownCompetitors`, and `year1RevenueGoal`. These are listed in the `RESEARCH_REFINABLE_FIELDS` constant exported from `src/lib/types.ts`.

The `WizardField` type includes an optional `researchRefinable: boolean` flag. When a field has this flag and the user leaves it blank, the pipeline pauses after stage 2 (Strategic Synthesis) to show AI-suggested values.

The `usePipeline` hook manages this with two additional state values:

| State | Type | Description |
|-------|------|-------------|
| `pendingResearchReview` | `boolean` | True when the pipeline is paused for research review |
| `researchSuggestions` | `ResearchSuggestions` | AI-extracted suggestions for blank refinable fields |

The hook also exposes `submitResearchRefinements(refinements: Partial<BusinessInfo>)` which updates the business info, clears the review state, and resumes the pipeline from stage 3.

---

## Development Commands

```bash
# Start development server (with hot reload)
npm run dev

# Run ESLint
npm run lint

# TypeScript type checking (no emit)
npx tsc --noEmit

# Build for production
npm run build

# Start production server (after building)
npm start
```

---

## Code Style Conventions

- **TypeScript strict mode** is enabled (`strict: true` in `tsconfig.json`).
- **Functional components** with hooks only — no class components.
- **Named exports** for all components and hooks (except the default export in `page.tsx`).
- **`'use client'`** directive on all components and hooks that use React state or browser APIs.
- **File naming:** PascalCase for components (`Button.tsx`), camelCase for hooks and utilities (`usePipeline.ts`, `pricing.ts`).
- **Security comments** prefixed with `// SECURITY FIX: G-X` reference the original security audit finding number.
- **ESLint configuration** extends `next/core-web-vitals` (see `.eslintrc.json`).

---

## How to Add a New LLM Provider

Adding a new provider requires changes in five files. Here is the step-by-step process, using a hypothetical provider called "Mistral" as an example.

### Step 1: Add the provider to types (`src/lib/types.ts`)

1. Add the provider to the `LLMProvider` union type:

```typescript
export type LLMProvider = 'openai' | 'anthropic' | 'google' | 'openrouter' | 'custom' | 'mistral';
```

2. Add models to `MODEL_OPTIONS`:

```typescript
export const MODEL_OPTIONS: ModelOption[] = [
  // ... existing models ...
  // Mistral
  { value: 'mistral-large-latest', label: 'Mistral Large', provider: 'mistral', maxTokens: 128000 },
  { value: 'mistral-small-latest', label: 'Mistral Small', provider: 'mistral', maxTokens: 128000 },
];
```

3. Add the base endpoint to `PROVIDER_ENDPOINTS`:

```typescript
export const PROVIDER_ENDPOINTS: Record<LLMProvider, string> = {
  // ... existing providers ...
  mistral: 'https://api.mistral.ai/v1/chat/completions',
};
```

### Step 2: Update the LLM abstraction (`src/lib/llm.ts`)

1. Update `buildRequestBody()` to handle the new provider's API format. If the provider uses the OpenAI-compatible format (as Mistral does), add it to the existing `case`:

```typescript
case 'openai':
case 'openrouter':
case 'custom':
case 'mistral':   // ← Add here
  return { /* ... same OpenAI format ... */ };
```

2. Update `buildRequestHeaders()`:

```typescript
case 'openai':
case 'openrouter':
case 'custom':
case 'mistral':   // ← Add here
  headers['Authorization'] = `Bearer ${apiKey}`;
  break;
```

3. Update `parseStreamChunk()` and `parseNonStreamResponse()` similarly if the provider uses a non-OpenAI response format.

### Step 3: Update the UI (`src/components/SetupScreen.tsx`)

Add the provider to `PROVIDER_OPTIONS`:

```typescript
const PROVIDER_OPTIONS = [
  // ... existing ...
  { value: 'mistral', label: 'Mistral AI' },
];
```

### Step 4: Update CSP headers (`next.config.js`)

Add the provider's API domain to the `connect-src` directive:

```javascript
"connect-src 'self' https://api.openai.com https://api.anthropic.com https://generativelanguage.googleapis.com https://openrouter.ai https://api.mistral.ai",
```

### Step 5: Update pricing (`src/lib/pricing.ts`)

Add pricing for the new models:

```typescript
const PRICING: Record<string, PricingTier> = {
  // ... existing ...
  'mistral-large-latest': { inputPer1K: 0.002, outputPer1K: 0.006 },
  'mistral-small-latest': { inputPer1K: 0.0002, outputPer1K: 0.0006 },
};
```

### Step 6: Update URL validation (`src/lib/url-validation.ts`)

Add the new domain to the trusted provider list:

```typescript
export function isTrustedProviderEndpoint(urlString: string): boolean {
  const trustedPrefixes = [
    // ... existing ...
    'https://api.mistral.ai/',
  ];
  return trustedPrefixes.some(prefix => urlString.startsWith(prefix));
}
```

---

## How to Add a New Pipeline Stage

### Step 1: Define the stage in `usePipeline.ts`

Add a new entry to the `INITIAL_STAGES` array in `src/hooks/usePipeline.ts`:

```typescript
const INITIAL_STAGES: PipelineStage[] = [
  // ... existing 8 stages ...
  {
    id: 9,
    name: 'Financial Model Deep Dive',
    role: 'Writer',
    description: 'Creating detailed financial projections with multiple scenarios',
    status: 'queued',
    output: '',
    requiresApproval: true, // Set to true if you want step-by-step review
  },
];
```

### Step 2: Add the stage prompt in `prompts.ts`

Add a new entry to the `STAGE_PROMPTS` object in `src/lib/prompts.ts`:

```typescript
export const STAGE_PROMPTS: Record<number, { system: string; user: (context: string, previousOutputs: string[]) => string }> = {
  // ... existing stages 1-8 ...
  9: {
    system: `You are an expert financial modeler...`,
    user: (context, previousOutputs) => `Create detailed financial projections...

${context}

=== BUSINESS PLAN ===
${previousOutputs[7] || ''}
===

Include:
1. ...
2. ...`,
  },
};
```

The `previousOutputs` array is zero-indexed, so `previousOutputs[0]` is Stage 1's output, `previousOutputs[7]` is Stage 8's output.

### Step 3: Update stage names in the output screen

In `src/components/OutputScreen.tsx`, add the stage name to the `stageNames` array:

```typescript
const stageNames = [
  'Industry & Market Research',
  'Strategic Synthesis',
  // ... existing ...
  'Final Document Assembly',
  'Financial Model Deep Dive',  // ← New
];
```

### Step 4: Adjust final output logic

In `src/hooks/usePipeline.ts`, the pipeline's final output is always the last stage's output. If your new stage should produce the final output, no changes are needed. If it should produce supplementary content (not the main plan), you may want to adjust the `setFinalOutput` call in the `run()` function to specify which stage's output to use.

---

## How to Modify Prompts

All prompts are centralized in `src/lib/prompts.ts`.

### Prompt structure

Each stage prompt has two parts:

```typescript
{
  system: `...`,  // Sets the AI's persona and behavior
  user: (context: string, previousOutputs: string[]) => `...`,  // The actual task
}
```

- `context` is automatically built from `BusinessInfo` by `buildContextBlock()`.
- `previousOutputs` is an array of strings, one per prior stage (zero-indexed).
- If the user requests regeneration with notes, those notes are automatically appended to the user prompt by `getStagePrompt()`.

### Modifying the business context block

Edit `buildContextBlock()` in `src/lib/prompts.ts` to add or remove fields from the context that is sent to every stage:

```typescript
export function buildContextBlock(info: BusinessInfo): string {
  return `
=== BUSINESS CONTEXT ===
Company Name: ${info.companyName}
// Add new fields here
===
`.trim();
}
```

If you add new fields, also update the `BusinessInfo` interface in `src/lib/types.ts` and the wizard in `src/components/WizardScreen.tsx`.

### Research-refinable fields in prompts

The `buildContextBlock()` function handles research-refinable fields specially. When `keyDifferentiators`, `knownCompetitors`, or `year1RevenueGoal` are blank, the context block shows "Not yet specified — to be determined from research" instead of empty values. This signals to stages 1 and 2 that they should specifically address these areas in their research.

If you add a new research-refinable field:

1. Add it to the `RESEARCH_REFINABLE_FIELDS` array in `src/lib/types.ts`
2. Add handling for the blank case in `buildContextBlock()` in `src/lib/prompts.ts`
3. Mark the corresponding wizard field with `researchRefinable: true` in `src/components/WizardScreen.tsx`
4. Update the `extractSuggestionsFromResearch()` function in `src/hooks/usePipeline.ts` with a regex pattern to extract the new field's value from research output
5. Add the field to the Research Review modal in `src/components/PipelineScreen.tsx`

### Tips for effective prompts

- Be explicit about the output format you want (Markdown headers, bullet points, tables).
- Reference specific previous stage outputs when they are relevant.
- Use numbered lists for required sections to ensure completeness.
- The system prompt sets the persona; the user prompt sets the task. Keep them separate.

---

## How to Modify the DOCX Output Format

DOCX generation uses two files:

1. **`src/lib/docx-utils.ts`** — Contains the Markdown-to-DOCX parsing logic. This is where heading styles, paragraph formatting, table rendering, and inline formatting (bold, italic, code) are defined.

2. **`src/app/api/export-docx/route.ts`** — The API route that assembles the final document, including the optional cover page and table of contents.

### Changing heading styles

In `docx-utils.ts`, modify `createHeading()`:

```typescript
function createHeading(text: string, level: number): Paragraph {
  return new Paragraph({
    text,
    heading: headingLevels[Math.min(level - 1, 5)],
    // Add spacing, color, or other formatting here
    spacing: { before: 400, after: 200 },
  });
}
```

### Changing the cover page

In `export-docx/route.ts`, modify the cover page section. You can change fonts, sizes, colors, and layout:

```typescript
new Paragraph({
  children: [
    new TextRun({
      text: sanitizedCompanyName,
      bold: true,
      size: 56,          // Size in half-points (56 = 28pt)
      color: '2563EB',   // Hex color without '#'
      font: 'Arial',     // Font family
    }),
  ],
  alignment: AlignmentType.CENTER,
}),
```

### Adding page breaks between sections

Insert a page break paragraph in your DOCX children:

```typescript
new Paragraph({
  children: [new PageBreak()],
})
```

### Reference documentation

The `docx` library documentation is at [https://docx.js.org](https://docx.js.org). Key classes: `Document`, `Paragraph`, `TextRun`, `Table`, `TableRow`, `TableCell`, `HeadingLevel`, `AlignmentType`.

---

## How to Update Model Pricing Data

Pricing data is in `src/lib/pricing.ts`. The `PRICING` object maps model IDs to per-1K-token costs:

```typescript
const PRICING: Record<string, PricingTier> = {
  'gpt-4o': { inputPer1K: 0.005, outputPer1K: 0.015 },
  // ...
};
```

### To update prices

1. Find the current pricing on your provider's website:
   - OpenAI: [https://openai.com/pricing](https://openai.com/pricing)
   - Anthropic: [https://www.anthropic.com/pricing](https://www.anthropic.com/pricing)
   - Google: [https://ai.google.dev/pricing](https://ai.google.dev/pricing)

2. Convert prices to **per 1,000 tokens.** Provider websites usually list prices per million tokens. Divide by 1,000.

3. Update the corresponding entry in the `PRICING` object.

### To add pricing for a new model

Add a new key-value pair where the key exactly matches the model's `value` field in `MODEL_OPTIONS`:

```typescript
'new-model-id': { inputPer1K: 0.001, outputPer1K: 0.003 },
```

If a model is not in the `PRICING` object, the cost estimate will show as $0.00 — it will not break the app.

### Pipeline cost estimates

The `estimatePipelineCost()` function assumes 8 stages with estimated token ranges:
- Low: ~2,000 input + ~3,000 output tokens per stage
- High: ~4,000 input + ~6,000 output tokens per stage

If you add stages or change prompt verbosity significantly, update these estimates.

---

## Security Architecture

The application implements the following security measures, all originating from the security audit by Agent G:

### G-1: SSRF Prevention

**File:** `src/lib/url-validation.ts`

Custom LLM endpoints are validated before any outbound request. The validation blocks:
- Localhost addresses (127.0.0.1, ::1, and variants including octal/decimal/hex encoding)
- Private IP ranges (10.x.x.x, 172.16-31.x.x, 192.168.x.x)
- Link-local addresses (169.254.x.x, fe80::)
- Cloud metadata endpoints (169.254.169.254, metadata.google.internal)
- Internal domain TLDs (.internal, .local, .localhost)

Validation is enforced at three levels:
1. Client-side in `SetupScreen.tsx` (immediate feedback)
2. Server-side in `/api/generate/route.ts` (before any fetch)
3. Server-side in `/api/validate-key/route.ts` (before any fetch)

Known provider endpoints (OpenAI, Anthropic, Google, OpenRouter) bypass validation via `isTrustedProviderEndpoint()`.

### G-2: API Key Masking

**File:** `src/components/SetupScreen.tsx`

The API key input uses `type="password"` by default with a toggle button to reveal/hide.

### G-3: Request Hardening

**File:** `src/lib/llm.ts`

All outbound requests use `safeFetch()` which enforces:
- 30-second timeout via `AbortController`
- Redirect disabled (`redirect: 'error'`)
- 10MB response size limit (tracked during stream reading)

### G-4: Input Length Validation

**File:** `src/app/api/generate/route.ts`

Server-side limits:
- User prompt: 50,000 characters
- System prompt: 10,000 characters
- Export content: 500,000 characters
- Company name: 100 characters

### G-5: Security Headers

**File:** `next.config.js`

Headers applied to all routes:
- Content-Security-Policy (restrictive CSP with explicit connect-src allowlist)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer-Policy: strict-origin-when-cross-origin
- Strict-Transport-Security (HSTS)
- Permissions-Policy (restricts camera, microphone, geolocation)

### G-6: Markdown Sanitization

**File:** `src/components/ui/MarkdownRenderer.tsx`

Uses `rehype-sanitize` with a strict schema that:
- Strips `<script>`, `<style>`, `<iframe>`, `<object>`, `<embed>`, `<form>`, `<input>`
- Only allows `className` attribute
- Explicitly allows table-related HTML elements for GFM tables

---

## Building for Production

### Build

```bash
npm run build
```

This creates an optimized production build in the `.next/` directory.

### Run

```bash
npm start
```

By default, this starts the production server on port 3000. To change the port:

```bash
PORT=8080 npm start
```

### Deploy to Vercel

The app is designed for Vercel deployment:

```bash
npx vercel
```

Or connect the Git repository to Vercel's dashboard for automatic deployments.

### Deploy to other platforms

The app requires a Node.js runtime for the API routes. Suitable platforms include:
- **Vercel** (recommended, zero-config for Next.js)
- **Railway**
- **Render**
- **AWS EC2/ECS** (with Node.js installed)
- **Docker** (create a `Dockerfile` based on the official Next.js Docker example)

Static export is **not** supported because the app requires server-side API routes.

### Environment variables

The app does not require any environment variables to run. Optional overrides can be set in `.env.local`:

```bash
REQUEST_TIMEOUT_MS=30000     # Request timeout in milliseconds (default: 30000)
MAX_RESPONSE_SIZE=10485760   # Max response size in bytes (default: 10MB)
```

---

## API Route Reference

### `POST /api/validate-key`

Validates an API key by sending a minimal test request to the provider.

**Request body:**
```json
{
  "config": {
    "provider": "openai",
    "model": "gpt-4o",
    "maxTokens": 4096,
    "temperature": 0.7
  },
  "apiKey": "sk-..."
}
```

**Success response (200):**
```json
{
  "valid": true,
  "model": "gpt-4o",
  "provider": "openai",
  "testResponse": "API key validated successfully."
}
```

**Error response (200 with valid: false, or 4xx/5xx):**
```json
{
  "valid": false,
  "error": "Invalid API key. Please check your key and try again."
}