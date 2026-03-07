#!/usr/bin/env npx tsx
/**
 * Business Plan Generator — Multi-Agent Pipeline Orchestrator
 *
 * Executes the agent pipeline defined in pipeline-prompt.md.
 * Handles: sequential execution, parallel D1/D2, blocking agent
 * verdicts, retry loops, token tracking, and structured output.
 *
 * Usage:
 *   npx tsx run-pipeline.ts --provider anthropic --model claude-sonnet-4-20250514 --api-key $ANTHROPIC_API_KEY
 *   npx tsx run-pipeline.ts --provider openai --model gpt-4o --api-key $OPENAI_API_KEY
 *   npx tsx run-pipeline.ts --provider custom --model my-model --api-key $API_KEY --base-url https://my-api.example.com/v1
 *
 * Requirements:
 *   - Node.js 18+ (native fetch)
 *   - npx tsx (TypeScript execution)
 */

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

// ============================================================
// TYPES
// ============================================================

type Provider = "anthropic" | "openai" | "custom";
type Verdict = "PASS" | "CONDITIONAL PASS" | "FAIL";

interface CLIConfig {
  provider: Provider;
  model: string;
  apiKey: string;
  baseUrl?: string;
  promptFile: string;
}

interface LLMResponse {
  text: string;
  inputTokens: number;
  outputTokens: number;
}

interface TokenCall {
  agent: string;
  attempt: number;
  input_tokens: number;
  output_tokens: number;
  model: string;
  duration_ms: number;
}

interface TokenUsageLog {
  calls: TokenCall[];
  total_input_tokens: number;
  total_output_tokens: number;
  total_cost_usd: number;
}

interface PipelineLogEntry {
  agent: string;
  start_time: string;
  end_time: string;
  verdict: Verdict | null;
  retry_count: number;
  status: "success" | "fail" | "halt";
}

// ============================================================
// CONSTANTS
// ============================================================

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));

const MAX_GATE_RETRIES = 3;
const MAX_NETWORK_RETRIES = 3;
const API_TIMEOUT_MS = 10 * 60 * 1000; // 10 minutes
const MIN_OUTPUT_LENGTH = 100;

const VERDICT_REGEX = /^## VERDICT:\s*(PASS|CONDITIONAL PASS|FAIL)\s*$/m;

const AGENT_LABELS: Record<string, string> = {
  A: "Product Manager & Architect",
  B: "Senior Engineer Reviewer",
  C: "Senior Engineer & Architect",
  D1: "Backend Engineer",
  D2: "Frontend Engineer",
  D3: "Integration Engineer",
  E: "QA & Developer-in-Test",
  F: "Senior Engineer (Code Revision)",
  G: "Security Analyst & Engineer",
  H1: "Senior Engineer — Code",
  H2: "Senior Engineer — Docs",
};

const AGENT_MAX_TOKENS: Record<string, number> = {
  A: 8_000,
  B: 4_000,
  C: 12_000,
  D1: 10_000,
  D2: 16_000,
  D3: 8_000,
  E: 6_000,
  F: 14_000,
  G: 5_000,
  H1: 24_000,
  H2: 12_000,
};

// Per-million-token pricing: [input, output]
// Update these as provider pricing changes.
const MODEL_PRICING: Record<string, [number, number]> = {
  // Anthropic
  "claude-sonnet-4-20250514": [3, 15],
  "claude-opus-4-20250514": [15, 75],
  "claude-haiku-3-5-20241022": [0.8, 4],
  // OpenAI
  "gpt-4o": [2.5, 10],
  "gpt-4o-mini": [0.15, 0.6],
  "gpt-4.1": [2, 8],
  "gpt-4.1-mini": [0.4, 1.6],
};

// ============================================================
// CLI PARSING
// ============================================================

function parseCLI(): CLIConfig {
  const args = process.argv.slice(2);
  const flags: Record<string, string> = {};

  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith("--") && i + 1 < args.length) {
      flags[args[i].slice(2)] = args[i + 1];
      i++;
    }
  }

  const provider = flags["provider"] as Provider | undefined;
  const model = flags["model"];
  const apiKey = flags["api-key"];
  const baseUrl = flags["base-url"];
  const promptFile = flags["prompt-file"] ?? "pipeline-prompt.md";

  if (!provider || !model || !apiKey) {
    console.error(
      `Usage: npx tsx run-pipeline.ts --provider <anthropic|openai|custom> --model <model> --api-key <key> [--base-url <url>] [--prompt-file <path>]`
    );
    process.exit(1);
  }

  if (!["anthropic", "openai", "custom"].includes(provider)) {
    console.error(`Invalid provider: ${provider}. Must be anthropic, openai, or custom.`);
    process.exit(1);
  }

  if (provider === "custom" && !baseUrl) {
    console.error("Custom provider requires --base-url.");
    process.exit(1);
  }

  return { provider, model, apiKey, baseUrl, promptFile };
}

// ============================================================
// PROMPT FILE PARSER
// ============================================================

/**
 * Parses pipeline-prompt.md into a map of agent ID → full prompt text.
 *
 * Identifies agent sections by headers matching `# AGENT X —` (top-level)
 * and `## AGENT DX —` (D sub-agents). Skips the parent `# AGENT D` section
 * since D1, D2, D3 are extracted individually.
 *
 * Stops at `## AUTOMATED ORCHESTRATION` (not an agent section).
 */
function parsePromptFile(filePath: string): Map<string, string> {
  const content = readFileSync(filePath, "utf-8");
  const sections = new Map<string, string>();

  // Find all agent headers: # AGENT X — ... or ## AGENT D1 — ...
  const headerPattern = /^(#{1,3}) AGENT ([\w]+)\s*—/gm;
  const headers: Array<{ id: string; level: number; index: number }> = [];

  let match: RegExpExecArray | null;
  while ((match = headerPattern.exec(content)) !== null) {
    headers.push({
      id: match[2],
      level: match[1].length,
      index: match.index,
    });
  }

  if (headers.length === 0) {
    throw new Error(`No agent sections found in ${filePath}. Expected headers like "# AGENT A —".`);
  }

  for (let i = 0; i < headers.length; i++) {
    const header = headers[i];

    // Skip parent D section — we use D1, D2, D3 individually
    if (header.id === "D" && header.level === 1) continue;

    // Determine end position
    let endIdx = content.length;

    if (header.level >= 2) {
      // D sub-agents: end at the very next agent header
      if (i + 1 < headers.length) endIdx = headers[i + 1].index;
    } else {
      // Top-level agents: end at the next top-level agent header
      for (let j = i + 1; j < headers.length; j++) {
        if (headers[j].level <= header.level) {
          endIdx = headers[j].index;
          break;
        }
      }
    }

    // Also stop at AUTOMATED ORCHESTRATION section if it comes first
    const orchIdx = content.indexOf("## AUTOMATED ORCHESTRATION", header.index);
    if (orchIdx !== -1 && orchIdx < endIdx) endIdx = orchIdx;

    // Extract and clean up separator lines at boundaries
    let section = content.slice(header.index, endIdx);
    section = section.replace(/\n---\s*\n?$/g, "").trim();

    sections.set(header.id, section);
  }

  // Validate all expected agents were found
  const expected = ["A", "B", "C", "D1", "D2", "D3", "E", "F", "G", "H1", "H2"];
  const missing = expected.filter((id) => !sections.has(id));
  if (missing.length > 0) {
    throw new Error(`Missing agent sections in prompt file: ${missing.join(", ")}`);
  }

  return sections;
}

// ============================================================
// LLM CLIENT
// ============================================================

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Calls the configured LLM provider with the given prompt.
 * Handles Anthropic and OpenAI/compatible response formats.
 * Retries on network errors with exponential backoff (1s, 2s, 4s).
 */
async function callLLM(
  config: CLIConfig,
  prompt: string,
  maxTokens: number
): Promise<LLMResponse> {
  const { provider, model, apiKey, baseUrl } = config;

  let url: string;
  let headers: Record<string, string>;
  let body: Record<string, unknown>;

  if (provider === "anthropic") {
    url = "https://api.anthropic.com/v1/messages";
    headers = {
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
    };
    body = {
      model,
      max_tokens: maxTokens,
      messages: [{ role: "user", content: prompt }],
    };
  } else {
    // OpenAI or custom (OpenAI-compatible)
    url =
      provider === "openai"
        ? "https://api.openai.com/v1/chat/completions"
        : `${baseUrl!.replace(/\/+$/, "")}/chat/completions`;
    headers = {
      Authorization: `Bearer ${apiKey}`,
      "content-type": "application/json",
    };
    body = {
      model,
      max_tokens: maxTokens,
      messages: [{ role: "user", content: prompt }],
    };
  }

  for (let attempt = 0; attempt < MAX_NETWORK_RETRIES; attempt++) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), API_TIMEOUT_MS);

      const response = await fetch(url, {
        method: "POST",
        headers,
        body: JSON.stringify(body),
        signal: controller.signal,
      });

      clearTimeout(timeout);

      if (!response.ok) {
        const errorBody = await response.text().catch(() => "");
        throw new Error(`API ${response.status}: ${errorBody.slice(0, 200)}`);
      }

      const data = (await response.json()) as Record<string, unknown>;

      if (provider === "anthropic") {
        const content = data.content as Array<{ type: string; text: string }>;
        const usage = data.usage as { input_tokens: number; output_tokens: number };
        return {
          text: content
            .filter((c) => c.type === "text")
            .map((c) => c.text)
            .join(""),
          inputTokens: usage.input_tokens,
          outputTokens: usage.output_tokens,
        };
      } else {
        const choices = data.choices as Array<{ message: { content: string } }>;
        const usage = data.usage as
          | { prompt_tokens: number; completion_tokens: number }
          | undefined;
        return {
          text: choices[0].message.content,
          inputTokens: usage?.prompt_tokens ?? 0,
          outputTokens: usage?.completion_tokens ?? 0,
        };
      }
    } catch (err) {
      const isLast = attempt >= MAX_NETWORK_RETRIES - 1;
      if (isLast) throw err;

      const delay = Math.pow(2, attempt) * 1000; // 1s, 2s, 4s
      logLine(
        "NET",
        `Retry ${attempt + 1}/${MAX_NETWORK_RETRIES} in ${delay}ms — ${(err as Error).message}`
      );
      await sleep(delay);
    }
  }

  // Unreachable — loop either returns or throws
  throw new Error("Network retry loop exited unexpectedly");
}

// ============================================================
// ORCHESTRATION UTILITIES
// ============================================================

/** Replace all {{variable_name}} markers with stored values. */
function replaceVariables(template: string, variables: Map<string, string>): string {
  return template.replace(/\{\{(\w+)\}\}/g, (_match, varName: string) => {
    return variables.get(varName) ?? `{{${varName}}}`;
  });
}

/** Parse verdict from blocking agent output. */
function parseVerdict(output: string): Verdict {
  const match = output.match(VERDICT_REGEX);
  if (!match) return "FAIL"; // No parseable verdict treated as FAIL
  return match[1] as Verdict;
}

/** Calculate cost in USD for a given model and token counts. */
function calculateCost(model: string, inputTokens: number, outputTokens: number): number {
  const pricing = MODEL_PRICING[model];
  if (!pricing) return 0;
  const [inputPer1M, outputPer1M] = pricing;
  return (inputTokens / 1_000_000) * inputPer1M + (outputTokens / 1_000_000) * outputPer1M;
}

/** Format a number with commas: 12345 → "12,345" */
function fmt(n: number): string {
  return n.toLocaleString("en-US");
}

/** Console log with agent tag and timestamp. */
function logLine(agentId: string, message: string): void {
  const label = AGENT_LABELS[agentId] ?? agentId;
  console.log(`[${agentId}] ${label} — ${message}`);
}

// ============================================================
// PIPELINE RUNNER
// ============================================================

async function runPipeline(): Promise<void> {
  const config = parseCLI();
  const promptFilePath = join(SCRIPT_DIR, config.promptFile);
  const agentPrompts = parsePromptFile(promptFilePath);
  const variables = new Map<string, string>();
  const outputDir = join(SCRIPT_DIR, "pipeline-outputs");

  mkdirSync(outputDir, { recursive: true });

  const tokenLog: TokenUsageLog = {
    calls: [],
    total_input_tokens: 0,
    total_output_tokens: 0,
    total_cost_usd: 0,
  };
  const pipelineLog: PipelineLogEntry[] = [];
  const pipelineStart = Date.now();

  // ----------------------------------------------------------
  // Helper: execute a single agent
  // ----------------------------------------------------------
  async function execAgent(
    agentId: string,
    attempt: number = 1,
    failureReport?: string
  ): Promise<string> {
    let prompt = agentPrompts.get(agentId)!;
    prompt = replaceVariables(prompt, variables);

    if (failureReport) {
      prompt +=
        "\n\n## FAILURE REPORT FROM REVIEW AGENT — ADDRESS ALL ITEMS BEFORE RESUBMITTING\n\n" +
        failureReport;
    }

    const maxTokens = AGENT_MAX_TOKENS[agentId] ?? 8_000;
    const startTime = Date.now();
    const startISO = new Date(startTime).toISOString();

    logLine(agentId, attempt > 1 ? `running (retry ${attempt - 1})...` : "running...");

    const result = await callLLM(config, prompt, maxTokens);
    const duration = Date.now() - startTime;

    // Validate output length
    if (result.text.length < MIN_OUTPUT_LENGTH) {
      throw new Error(
        `Agent ${agentId} returned truncated output (${result.text.length} chars, minimum ${MIN_OUTPUT_LENGTH})`
      );
    }

    // Store in variables map
    const varName = `agent_${agentId.toLowerCase()}_output`;
    variables.set(varName, result.text);

    // Write to file
    const suffix = attempt > 1 ? `_retry_${attempt - 1}` : "";
    const filename = `agent_${agentId.toLowerCase()}${suffix}.md`;
    writeFileSync(join(outputDir, filename), result.text, "utf-8");

    // Token tracking
    const cost = calculateCost(config.model, result.inputTokens, result.outputTokens);
    tokenLog.calls.push({
      agent: agentId,
      attempt,
      input_tokens: result.inputTokens,
      output_tokens: result.outputTokens,
      model: config.model,
      duration_ms: duration,
    });
    tokenLog.total_input_tokens += result.inputTokens;
    tokenLog.total_output_tokens += result.outputTokens;
    tokenLog.total_cost_usd += cost;

    const totalTokens = result.inputTokens + result.outputTokens;
    logLine(agentId, `done (${fmt(totalTokens)} tokens, ${Math.round(duration / 1000)}s)`);

    return result.text;
  }

  // ----------------------------------------------------------
  // Helper: run a blocking gate with retry loop
  // ----------------------------------------------------------
  async function execBlockingGate(
    blockerId: string,
    rerunPredecessor: (failureReport: string, attempt: number) => Promise<void>
  ): Promise<void> {
    for (let attempt = 1; attempt <= MAX_GATE_RETRIES + 1; attempt++) {
      const startISO = new Date().toISOString();

      // Run the blocking agent
      const output = await execAgent(blockerId, attempt);
      const verdict = parseVerdict(output);

      const endISO = new Date().toISOString();
      pipelineLog.push({
        agent: blockerId,
        start_time: startISO,
        end_time: endISO,
        verdict,
        retry_count: attempt - 1,
        status: verdict === "FAIL" && attempt > MAX_GATE_RETRIES ? "halt" : "success",
      });

      if (verdict === "PASS" || verdict === "CONDITIONAL PASS") {
        logLine(blockerId, `VERDICT: ${verdict}`);
        return;
      }

      // FAIL
      logLine(blockerId, `VERDICT: FAIL`);

      if (attempt > MAX_GATE_RETRIES) {
        // Max retries exceeded — halt
        const haltReport = [
          `# PIPELINE HALTED`,
          ``,
          `Blocking agent ${blockerId} issued FAIL after ${MAX_GATE_RETRIES} retries.`,
          ``,
          `## Last Failure Report`,
          ``,
          output,
        ].join("\n");

        writeFileSync(join(outputDir, "HALT_REPORT.md"), haltReport, "utf-8");
        writeLogs();

        console.error(
          `\nPipeline halted: Agent ${blockerId} failed ${MAX_GATE_RETRIES} consecutive times.`
        );
        console.error(`See: pipeline-outputs/HALT_REPORT.md`);
        process.exit(1);
      }

      logLine(blockerId, `Retrying predecessor (attempt ${attempt}/${MAX_GATE_RETRIES})...`);
      await rerunPredecessor(output, attempt + 1);
    }
  }

  // ----------------------------------------------------------
  // Helper: run the D development phase (D1‖D2 → D3)
  // ----------------------------------------------------------
  async function execDevelopmentPhase(failureReport?: string, attempt: number = 1): Promise<void> {
    // D1 and D2 in parallel
    const [d1Output, d2Output] = await Promise.all([
      execAgent("D1", attempt, failureReport),
      execAgent("D2", attempt, failureReport),
    ]);

    // D3 runs after both complete — also receives failure report if retrying
    await execAgent("D3", attempt, failureReport);

    // Build combined output
    const combined = [
      "## AGENT D1 OUTPUT — Backend Engineer\n",
      d1Output,
      "\n\n---\n\n",
      "## AGENT D2 OUTPUT — Frontend Engineer\n",
      d2Output,
      "\n\n---\n\n",
      "## AGENT D3 OUTPUT — Integration Engineer\n",
      variables.get("agent_d3_output") ?? "",
    ].join("");

    variables.set("agent_d_combined", combined);
  }

  // ----------------------------------------------------------
  // Helper: write token and pipeline logs
  // ----------------------------------------------------------
  function writeLogs(): void {
    writeFileSync(
      join(outputDir, "token_usage.json"),
      JSON.stringify(tokenLog, null, 2),
      "utf-8"
    );
    writeFileSync(
      join(outputDir, "pipeline_log.json"),
      JSON.stringify(pipelineLog, null, 2),
      "utf-8"
    );
  }

  // ----------------------------------------------------------
  // Pipeline execution
  // ----------------------------------------------------------
  try {
    console.log(`\nPipeline starting — ${config.provider}/${config.model}\n`);

    // === A: Product Manager & Architect ===
    const startA = new Date().toISOString();
    await execAgent("A");
    pipelineLog.push({
      agent: "A",
      start_time: startA,
      end_time: new Date().toISOString(),
      verdict: null,
      retry_count: 0,
      status: "success",
    });

    // === B: Senior Engineer Reviewer (BLOCKING) ===
    await execBlockingGate("B", async (failureReport, attempt) => {
      await execAgent("A", attempt, failureReport);
    });

    // === C: Senior Engineer & Architect ===
    const startC = new Date().toISOString();
    await execAgent("C");
    pipelineLog.push({
      agent: "C",
      start_time: startC,
      end_time: new Date().toISOString(),
      verdict: null,
      retry_count: 0,
      status: "success",
    });

    // === D: Development Phase (D1‖D2 → D3) ===
    const startD = new Date().toISOString();
    await execDevelopmentPhase();
    pipelineLog.push({
      agent: "D",
      start_time: startD,
      end_time: new Date().toISOString(),
      verdict: null,
      retry_count: 0,
      status: "success",
    });

    // === E: QA (BLOCKING) ===
    await execBlockingGate("E", async (failureReport, attempt) => {
      await execDevelopmentPhase(failureReport, attempt);
    });

    // === F: Code Revision ===
    const startF = new Date().toISOString();
    await execAgent("F");
    pipelineLog.push({
      agent: "F",
      start_time: startF,
      end_time: new Date().toISOString(),
      verdict: null,
      retry_count: 0,
      status: "success",
    });

    // === G: Security Audit (BLOCKING) ===
    await execBlockingGate("G", async (failureReport, attempt) => {
      await execAgent("F", attempt, failureReport);
    });

    // === H1: Final Code ===
    const startH1 = new Date().toISOString();
    await execAgent("H1");
    pipelineLog.push({
      agent: "H1",
      start_time: startH1,
      end_time: new Date().toISOString(),
      verdict: null,
      retry_count: 0,
      status: "success",
    });

    // === H2: Documentation ===
    const startH2 = new Date().toISOString();
    await execAgent("H2");
    pipelineLog.push({
      agent: "H2",
      start_time: startH2,
      end_time: new Date().toISOString(),
      verdict: null,
      retry_count: 0,
      status: "success",
    });

    // === Done ===
    writeLogs();

    const totalDuration = Date.now() - pipelineStart;
    const totalTokens = tokenLog.total_input_tokens + tokenLog.total_output_tokens;
    const minutes = Math.floor(totalDuration / 60_000);
    const seconds = Math.round((totalDuration % 60_000) / 1000);

    console.log(`\nPipeline complete.`);
    console.log(
      `  Total: ${fmt(totalTokens)} tokens, $${tokenLog.total_cost_usd.toFixed(2)}, ${minutes}m ${seconds}s`
    );
    console.log(`  Output: ${outputDir}/`);
    console.log();
  } catch (err) {
    writeLogs();
    console.error(`\nPipeline failed: ${(err as Error).message}`);
    process.exit(1);
  }
}

// ============================================================
// ENTRY POINT
// ============================================================

runPipeline();
