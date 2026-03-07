# Business Plan Generator — User Guide

---

## Table of Contents

1. [Overview](#overview)
2. [Step 1: LLM Setup](#step-1-llm-setup)
3. [Step 2: Business Information Wizard](#step-2-business-information-wizard)
4. [Step 3: Pipeline Execution](#step-3-pipeline-execution)
5. [Step 4: Viewing and Exporting Your Business Plan](#step-4-viewing-and-exporting-your-business-plan)
6. [Starting Over](#starting-over)
7. [Tips for Best Results](#tips-for-best-results)

---

## Overview

The Business Plan Generator walks you through four screens:

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  1.Setup │ →  │ 2.Wizard │ →  │3.Pipeline│ →  │ 4.Output │
│  (LLM)   │    │ (Info)   │    │(Generate)│    │(Download) │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

1. **Setup** — Choose your AI provider, enter your API key, and validate it.
2. **Wizard** — Fill in six pages of information about your business.
3. **Pipeline** — Watch as eight AI stages research, write, and polish your plan.
4. **Output** — Read, review, and download your finished business plan.

---

## Step 1: LLM Setup

When you first open the app at `http://localhost:3000`, you will see the setup screen.

```
┌─────────────────────────────────────────────────┐
│         Business Plan Generator                  │
│   AI-powered business plan generation            │
│                                                  │
│  ┌─────────────────────────────────────────┐     │
│  │ LLM Configuration                       │     │
│  │                                         │     │
│  │ Provider:    [OpenAI          ▾]        │     │
│  │ Model:       [GPT-4o          ▾]        │     │
│  │ API Key:     [••••••••••••••••] 👁      │     │
│  │                                         │     │
│  │ ▸ Advanced Settings                     │     │
│  │                                         │     │
│  │ Estimated cost: $0.18 – $0.54           │     │
│  │                                         │     │
│  │ [Validate Key]     [Continue to Wizard] │     │
│  └─────────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
```

### How to complete this screen

1. **Select a Provider.** Click the "Provider" dropdown and choose from:
   - **OpenAI** — For GPT-4o, GPT-4o Mini, GPT-4 Turbo, or GPT-3.5 Turbo
   - **Anthropic** — For Claude Sonnet 4, Claude 3.5 Sonnet, or Claude 3 Haiku
   - **Google AI** — For Gemini 1.5 Pro or Gemini 1.5 Flash
   - **OpenRouter** — For access to multiple models through one key
   - **Custom Endpoint** — For self-hosted or alternative API-compatible services

2. **Select a Model.** The dropdown updates to show models available for your chosen provider. Select the one you want to use.

3. **Enter your API Key.** Paste your key into the API Key field. The key is hidden by default (shown as dots). Click the eye icon (👁) to toggle visibility if you need to verify what you pasted.

4. **Click "Validate Key."** The app sends a small test request to your provider to confirm your key works. If successful, you will see a green checkmark with "API key validated successfully."

5. **Click "Continue to Wizard →"** to proceed. This button is only enabled after your key is validated.

### Understanding the cost estimate

Below the Advanced Settings section, you will see an estimated cost range (e.g., "$0.18 – $0.54"). This is the approximate cost of running the full eight-stage pipeline with your selected model:

| Model | Typical Cost |
|-------|-------------|
| GPT-3.5 Turbo | $0.01 – $0.04 |
| GPT-4o Mini | $0.01 – $0.02 |
| Claude 3 Haiku | $0.01 – $0.03 |
| Gemini 1.5 Flash | < $0.01 |
| GPT-4o | $0.18 – $0.54 |
| Claude 3.5 Sonnet / Claude Sonnet 4 | $0.11 – $0.33 |
| Gemini 1.5 Pro | $0.05 – $0.14 |
| GPT-4 Turbo | $0.36 – $1.08 |

More expensive models generally produce higher-quality, more detailed output.

### Advanced Settings

Click "Advanced Settings" to expand additional options:

- **Max Tokens per Request** — Controls how long each AI response can be. Default is 4,096 tokens (~3,000 words). Increase this if your stages are being cut off mid-sentence. Decrease to reduce cost.
- **Temperature** — Controls creativity vs. consistency. Lower values (0.0–0.3) produce more conservative, consistent output. Higher values (0.7–1.0) produce more creative, varied output. Default is 0.7, which is a good balance for business plans.

---

## Step 2: Business Information Wizard

After setup, you enter a six-step wizard that collects information about your business. A progress bar at the top shows where you are.

```
┌─────────────────────────────────────────────────┐
│           Company Basics                         │
│   Tell us about your company foundation          │
│                                                  │
│   Step 1 of 6                       17%          │
│   [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░]        │
│                                                  │
│   Company Name *              [✨ AI Help]       │
│   ┌─────────────────────────────────────────┐    │
│   │ Acme Consulting                         │    │
│   └─────────────────────────────────────────┘    │
│                                                  │
│   Company Tagline *           [✨ AI Help]       │
│   ┌─────────────────────────────────────────┐    │
│   │ Strategic insights for growing businesses│    │
│   └─────────────────────────────────────────┘    │
│                                                  │
│   [Previous]                         [Next]      │
└─────────────────────────────────────────────────┘
```

### The six wizard steps

**Step 1: Company Basics**
- **Company Name** (required) — Your business name. Max 100 characters.
- **Company Tagline** (required) — A one-line summary of what your company does. Max 200 characters.

**Step 2: Industry & Market**
- **Primary Industry** (required) — Select from: Technology, Healthcare, Finance, Retail, Manufacturing, Consulting, Education, Real Estate, Food & Beverage, or Other.
- **Geographic Focus** (required) — Select from: Local, Regional, National, International, or Global.
- **Secondary Industries** (optional) — Check up to 3 related industries that complement your primary focus.

**Step 3: Founder Background**
- **Founder Background & Experience** (required) — Describe your professional experience, relevant skills, and qualifications. Max 1,000 characters. The more detail you provide, the better the AI can tailor the plan.

**Step 4: Services & Offerings**
- **Services Description** (required) — Describe what products or services your business offers. Max 1,000 characters.
- **Key Differentiators** (optional — research-refinable) — What makes your business different from competitors? Max 500 characters. If you are unsure, leave this blank and the research phase will suggest differentiators based on its competitive analysis.

**Step 5: Competition & IP**
- **Known Competitors** (optional — research-refinable) — List any competitors you are aware of. Max 500 characters. If you leave this blank, the research phase will identify competitors for you to review.
- **Existing Intellectual Property** (required) — Describe any patents, trademarks, proprietary technology, or unique assets. If none, type "None." Max 500 characters.

**Step 6: Business Goals**
- **Year 1 Revenue Goal** (optional — research-refinable) — Your target revenue for the first year, in dollars. Enter a number only (e.g., 500000). If you are unsure, leave this as 0 and the research phase will suggest a realistic target based on market analysis.
- **Current Team Size** (required) — How many people currently work on this business. Enter 0 if you are pre-launch.
- **Target Company Size** (required) — Where you want the company to be long-term: Solopreneur, Small Team (2–10), Medium Team (11–50), Large Team (51–200), or Enterprise (200+).

### Research-refinable fields

Three fields are marked "optional — research-refinable": Key Differentiators, Known Competitors, and Year 1 Revenue Goal. These fields are ones where the AI's market research can provide better information than guessing.

If you leave any of these blank, the review screen will show a blue note: "X fields left blank will be informed by the research phase." After stages 1 and 2 complete (Industry Research and Strategic Synthesis), the pipeline pauses and shows you a Research Review form with AI-suggested values based on the research findings. You can accept, edit, or clear each suggestion before the pipeline continues.

If you already know your competitors, differentiators, or revenue target, fill them in during the wizard — the pipeline will use your values directly and skip the research review pause.

### Using the AI Help button

Every field has an "AI Help" button on the right. Click it to get an AI-generated suggestion for that field based on the information you have already provided. A popup will appear with the suggestion:

```
┌─────────────────────────────────────────────────┐
│  AI Suggestion for Company Tagline               │
│                                                  │
│  ┌─────────────────────────────────────────┐     │
│  │ "Empowering mid-market businesses with  │     │
│  │  data-driven strategic consulting for    │     │
│  │  sustainable growth and competitive      │     │
│  │  advantage."                             │     │
│  └─────────────────────────────────────────┘     │
│                                                  │
│  [Close]                    [Use Suggestion]      │
└─────────────────────────────────────────────────┘
```

- Click **"Use Suggestion"** to paste the suggestion into the field.
- Click **"Close"** to dismiss it and keep your own text.

This feature is useful if you are unsure what to write. The suggestion costs a small number of tokens (usually a few cents at most).

### Navigating the wizard

- Click **"Next"** to advance to the next step. The app will validate the current step's required fields and show error messages in red if anything is missing.
- Click **"Previous"** to go back and change earlier answers.
- On the final step, clicking **"Next"** takes you to a **Review** screen where you can see all your answers at once before proceeding.

### Review screen

```
┌─────────────────────────────────────────────────┐
│         Review Your Information                   │
│                                                  │
│  Company Basics                                   │
│    Company Name:       Acme Consulting            │
│    Company Tagline:    Strategic insights for...  │
│                                                  │
│  Industry & Market                                │
│    Primary Industry:   Consulting                 │
│    Geographic Focus:   National                   │
│    ...                                            │
│                                                  │
│  [Back to Edit]              [Start Pipeline]     │
└─────────────────────────────────────────────────┘
```

- Click **"Back to Edit"** to return to the wizard and make changes.
- Click **"Start Pipeline"** to begin generating your business plan.

---

## Step 3: Pipeline Execution

The pipeline screen is where the AI generates your business plan through eight sequential stages. Before it starts, you choose an execution mode.

### Choosing an execution mode

```
┌─────────────────────────────────────────────────┐
│           Execution Mode                          │
│                                                  │
│  ○ Step-by-Step                                   │
│    Review and approve each stage before           │
│    continuing                                     │
│                                                  │
│  ○ Full Auto                                      │
│    Run all stages automatically without           │
│    interruption                                   │
│                                                  │
│  [Start Business Plan Generation]                 │
└─────────────────────────────────────────────────┘
```

**Step-by-Step Mode** (recommended for first-time use):
- The pipeline pauses after certain stages and asks you to review and approve the output before continuing.
- You can provide feedback and ask the AI to regenerate a stage if you are not satisfied.
- This gives you the most control over the quality of your plan.

**Full Auto Mode** (faster, less control):
- All eight stages run one after another without pausing.
- You cannot intervene during generation.
- Best when you trust the AI to produce good results and want the fastest turnaround.

Click **"Start Business Plan Generation"** to begin.

### The eight pipeline stages

| # | Stage | Role | What It Does |
|---|-------|------|-------------|
| 1 | Industry & Market Research | Researcher | Analyzes your industry, competitors, and market opportunities |
| 2 | Strategic Synthesis | Researcher | Converts research into strategic positioning and recommendations |
| 3 | Service Portfolio Development | Writer | Creates detailed service descriptions with pricing |
| 4 | Service Portfolio Refinement | Editor | Improves clarity and consistency of services |
| 5 | Service Portfolio Finalization | Editor | Final polish and formatting of service descriptions |
| 6 | Business Plan Development | Writer | Writes the full business plan with all sections |
| 7 | Quality Assurance Review | Editor | Reviews for completeness, accuracy, and consistency |
| 8 | Final Document Assembly | Editor | Incorporates QA feedback into the polished final document |

### Watching the pipeline

#### Research Review pause

If you left any research-refinable fields blank in the wizard, the pipeline pauses after stage 2 (Strategic Synthesis) and shows a banner: "Research Complete — Review & Continue." Click the button to open a form showing each blank field pre-filled with AI-suggested values extracted from the research.

For each field:
- If the AI found relevant information (e.g., identified competitors or suggested a revenue target), the field is pre-filled.
- Fields you already filled in during the wizard are shown with a "You provided this" label and are not changed.
- You can edit any value before confirming.

Click "Confirm & Continue Pipeline" to resume. The updated values are used by all remaining stages (3 through 8).

If all three refinable fields were filled in during the wizard, this pause does not occur — the pipeline runs straight through.

#### Stage progress

```
┌─────────────────────────────────────────────────┐
│           Pipeline Progress                       │
│                                        Tokens: 12,456 │
│                                                  │
│  ✓  1. Industry & Market Research    [Approved]  │
│  ✓  2. Strategic Synthesis           [Approved]  │
│  ⟳  3. Service Portfolio Dev.        [Running]   │
│     │  ┌─────────────────────────────────────┐   │
│     │  │ ## Service Categories               │   │
│     │  │ Based on the strategic analysis...  |│   │
│     │  └─────────────────────────────────────┘   │
│  ○  4. Service Portfolio Refinement  [Queued]    │
│  ○  5. Service Portfolio Finalization[Queued]    │
│  ○  6. Business Plan Development     [Queued]    │
│  ○  7. Quality Assurance Review      [Queued]    │
│  ○  8. Final Document Assembly       [Queued]    │
│                                                  │
│              [Cancel]                             │
└─────────────────────────────────────────────────┘
```

Each stage shows:
- A **status indicator**: spinning for running, checkmark for completed/approved, number for queued, X for error.
- A **status badge**: Queued, Running, Completed, Approved, or Error.
- A **token count** after completion (e.g., "3,241 tokens").
- A **preview** of the output text while running or after completion.
- The **total token count** for all stages so far is shown in the top-right corner.

### Understanding the token usage display

Tokens are the units AI models use to measure text. Roughly:
- 1 token ≈ 4 characters of English text
- 1 token ≈ ¾ of a word
- 100 tokens ≈ 75 words

The token count shown for each stage includes both the input (your business information + context from previous stages) and the output (what the AI wrote). Higher token counts mean more detailed output but also higher cost.

### Reviewing and approving stages (Step-by-Step mode only)

When a stage that requires approval finishes, a popup appears:

```
┌─────────────────────────────────────────────────┐
│  Approve: Industry & Market Research              │
│                                                  │
│  ┌─────────────────────────────────────────┐     │
│  │ Stage Output                             │     │
│  │                                         │     │
│  │ ## Industry Overview                    │     │
│  │ The consulting industry is a $300B...   │     │
│  │ ...                                     │     │
│  │ (scrollable)                            │     │
│  └─────────────────────────────────────────┘     │
│                                                  │
│  Regeneration Notes (Optional)                    │
│  ┌─────────────────────────────────────────┐     │
│  │                                         │     │
│  └─────────────────────────────────────────┘     │
│                                                  │
│  [Approve & Continue]        [Regenerate]         │
└─────────────────────────────────────────────────┘
```

- **Scroll through the output** to review what the AI produced.
- If you are satisfied, click **"Approve & Continue"** to move to the next stage.
- If you want changes, type feedback in the "Regeneration Notes" field and click **"Regenerate."** The AI will run the stage again, incorporating your notes as additional instructions.

**Examples of useful regeneration notes:**
- "Focus more on the SaaS market segment"
- "Add more specific competitor names in the healthcare space"
- "The pricing is too high — target mid-market companies with budgets under $50K"
- "Include more financial data and statistics"

Stages that do **not** require approval (stages 4, 7, and 8) run automatically even in Step-by-Step mode.

### If something goes wrong

If a stage fails, you will see it highlighted in red with an error message. Common causes:
- **Rate limiting** — You are making too many requests to your AI provider. Wait a minute and retry.
- **Timeout** — The request took too long. Try again; or switch to a faster model.
- **API error** — Check that your API key is still valid and has credit.

Click **"Retry Pipeline"** to attempt the failed stage again, or **"Reset"** to start the entire pipeline over.

---

## Step 4: Viewing and Exporting Your Business Plan

After all eight stages complete, you are automatically taken to the output screen.

```
┌─────────────────────────────────────────────────┐
│  Acme Consulting Business Plan                    │
│  Generated business plan ready for review         │
│                                      [📋 Copy] [📥 Export] │
│                                                  │
│  ┌─ Token Usage ────────────────────────────┐    │
│  │  Input: 24,560  Output: 31,240  Total: 55,800│
│  │  Estimated Cost: $0.42                    │    │
│  └──────────────────────────────────────────┘    │
│                                                  │
│  [Final Business Plan]  [Stage Outputs (8)]       │
│                                                  │
│  ┌─────────────────────────────────────────┐     │
│  │ # Executive Summary                     │     │
│  │                                         │     │
│  │ Acme Consulting is a national strategic │     │
│  │ consulting firm specializing in...      │     │
│  │ ...                                     │     │
│  │ (rendered Markdown — scrollable)        │     │
│  └─────────────────────────────────────────┘     │
│                                                  │
│  [← Back to Pipeline]       [Start New Plan]      │
└─────────────────────────────────────────────────┘
```

### Tabs

- **Final Business Plan** — The complete, polished business plan from the final stage, rendered with formatted headings, tables, bullet points, etc.
- **Stage Outputs (8)** — Expandable sections showing what each individual stage produced. Click any stage name to expand it. This is useful if you want to see the research, strategic synthesis, or QA feedback separately.

### Token usage summary

The token usage panel shows:
- **Input tokens** — Total tokens sent to the AI across all stages.
- **Output tokens** — Total tokens the AI generated across all stages.
- **Total tokens** — Sum of input and output.
- **Estimated Cost** — Approximate dollar cost based on your model's published pricing.

### Copying your plan

Click **"📋 Copy"** to copy the entire business plan text (in Markdown format) to your clipboard. You can then paste it into Google Docs, Notion, or any other document editor.

### Exporting your plan

Click **"📥 Export"** to open the export dialog:

```
┌─────────────────────────────────────────────────┐
│  Export Business Plan                             │
│                                                  │
│  Export Format                                    │
│  ○ Microsoft Word (.docx)                         │
│  ○ Markdown (.md)                                 │
│                                                  │
│  Options (Word only)                              │
│  ☑ Include Cover Page                             │
│  ☑ Include Table of Contents                      │
│                                                  │
│  [Cancel]                     [Export]             │
└─────────────────────────────────────────────────┘
```

**Microsoft Word (.docx):**
- Produces a professionally formatted Word document.
- Optionally includes a cover page with your company name, the title "Business Plan," and the current date.
- Optionally includes a Table of Contents placeholder (update it in Word by right-clicking → "Update Field").
- Bold, italic, headers, tables, and bullet points from the AI output are preserved.

**Markdown (.md):**
- Produces a plain text file in Markdown format.
- Can be opened in any text editor or imported into tools that support Markdown (Notion, Obsidian, GitHub, etc.).

Click **"Export"** to download the file. It will be saved to your browser's default download location.

---

## Starting Over

You have two options on the output screen:

- **"← Back to Pipeline"** — Returns to the pipeline screen. Useful if you want to review the pipeline stages or if the pipeline did not complete.
- **"Start New Plan"** — Returns to the wizard screen so you can enter new business information and generate a different plan. Your LLM configuration (provider, model, API key) is preserved.

To change your API key or provider, you will need to refresh the page (this resets everything) and start from the setup screen.

---

## Tips for Best Results

1. **Be specific.** The more detail you provide in the wizard, the more tailored and useful your business plan will be. Instead of "We offer consulting services," write "We provide data analytics consulting for mid-market retail companies, helping them optimize inventory management and customer segmentation using machine learning."

2. **Use Step-by-Step mode on your first run.** This lets you catch issues early. If the market research misunderstands your industry, you can correct it before the rest of the plan is built on flawed assumptions.

3. **Use regeneration notes strategically.** You do not need to rewrite the entire output. Just tell the AI what to change: "Add more detail about the Asian market," "Lower the pricing tier by 20%," "Remove references to B2C—we are B2B only."

4. **Choose the right model for your budget.** If cost is a concern, start with a cheaper model (GPT-4o Mini, Claude 3 Haiku, or Gemini 1.5 Flash) to see if the quality meets your needs. Upgrade to a more powerful model for the final version.

5. **Review the stage outputs, not just the final plan.** The "Stage Outputs" tab lets you see the research and strategic thinking behind your plan. This can surface insights that did not make it into the final document.

6. **Export to Word, then customize.** The generated plan is a strong starting point, but you will likely want to add your own branding, adjust financial projections, and add specifics that only you know. Export to Word and edit from there.

7. **Run multiple times with different information.** You can generate several plans with different revenue targets, geographic focuses, or service descriptions to explore different business strategies.
