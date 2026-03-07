#!/usr/bin/env npx tsx
/**
 * Extract code files from pipeline agent markdown output.
 *
 * Parses agent_h1.md (code) and agent_h2.md (docs) for fenced code blocks
 * labeled with file paths, and writes them to the project directory.
 *
 * Expected format in agent output:
 *   ### FILE: `src/app/page.tsx`
 *   ```typescript
 *   [code]
 *   ```
 *
 * Usage:
 *   npx tsx extract-files.ts [--dry-run]
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const OUTPUT_DIR = join(SCRIPT_DIR, "pipeline-outputs");
const PROJECT_DIR = SCRIPT_DIR;

const DRY_RUN = process.argv.includes("--dry-run");

interface ExtractedFile {
  path: string;
  content: string;
  source: string;
  lineNumber: number;
}

/**
 * Line-by-line parser. Much more reliable than regex over large markdown files.
 *
 * State machine:
 *   SCANNING → found FILE header → AWAITING_FENCE
 *   AWAITING_FENCE → found opening ``` → CAPTURING
 *   CAPTURING → found closing ``` → SCANNING (file saved)
 */
function extractFiles(markdown: string, sourceName: string): ExtractedFile[] {
  const files: ExtractedFile[] = [];
  const lines = markdown.split("\n");

  // Pattern to match file path headers
  // Matches: ### FILE: `path/file.ext`
  //          ### FILE: path/file.ext
  //          #### FILE: `path/file.ext`
  //          **FILE: path/file.ext**
  const fileHeaderPattern = /^#{1,4}\s+FILE:\s*`?([^`\n*]+?)`?\s*\**\s*$/;

  let state: "SCANNING" | "AWAITING_FENCE" | "CAPTURING" = "SCANNING";
  let currentPath = "";
  let currentContent: string[] = [];
  let currentLineNum = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    switch (state) {
      case "SCANNING": {
        const match = line.match(fileHeaderPattern);
        if (match) {
          currentPath = match[1].trim();
          currentLineNum = i + 1;
          state = "AWAITING_FENCE";
        }
        break;
      }

      case "AWAITING_FENCE": {
        if (line.startsWith("```")) {
          currentContent = [];
          state = "CAPTURING";
        } else if (line.trim() === "" || line.startsWith("<!--")) {
          // Skip blank lines and comments between header and fence
        } else {
          // Not a code fence after the header — false match, go back to scanning
          state = "SCANNING";
        }
        break;
      }

      case "CAPTURING": {
        if (line.startsWith("```")) {
          // End of code block — save the file
          const content = currentContent.join("\n");

          // Skip if it does not look like a real file path
          if (currentPath.includes("/") || currentPath.includes(".")) {
            const entry: ExtractedFile = {
              path: currentPath,
              content,
              source: sourceName,
              lineNumber: currentLineNum,
            };

            // Deduplicate — keep last occurrence
            const existingIdx = files.findIndex((f) => f.path === currentPath);
            if (existingIdx !== -1) {
              files[existingIdx] = entry;
            } else {
              files.push(entry);
            }
          }

          state = "SCANNING";
        } else {
          currentContent.push(line);
        }
        break;
      }
    }
  }

  return files;
}

/**
 * Extract documentation files from agent_h2.md.
 *
 * Documentation may be in fenced blocks (### FILE: INSTALL.md + ```)
 * or as raw markdown sections between headers.
 */
function extractDocs(markdown: string): ExtractedFile[] {
  // First try: use the same FILE: pattern extraction
  const fenced = extractFiles(markdown, "agent_h2.md");
  const docFiles = fenced.filter((f) =>
    /^(INSTALL|USER_GUIDE|DEVELOPER_GUIDE|INTEGRATION_CHECKLIST)\.md$/.test(f.path)
  );

  if (docFiles.length > 0) return docFiles;

  // Second try: look for top-level section headers
  const docs: ExtractedFile[] = [];
  const docNames = [
    "INSTALL.md",
    "USER_GUIDE.md",
    "DEVELOPER_GUIDE.md",
    "INTEGRATION_CHECKLIST.md",
  ];

  for (const docName of docNames) {
    const baseName = docName.replace(".md", "").replace(/_/g, "[_ ]");
    const headerRe = new RegExp(
      `^#{1,3}\\s+(?:Part \\d+[:\\s]*)?${baseName}(?:\\.md)?\\s*$`,
      "im"
    );

    const match = markdown.match(headerRe);
    if (!match || match.index === undefined) continue;

    const startIdx = markdown.indexOf("\n", match.index) + 1;

    // Find end: next doc header or end of file
    let endIdx = markdown.length;
    for (const other of docNames) {
      if (other === docName) continue;
      const otherBase = other.replace(".md", "").replace(/_/g, "[_ ]");
      const otherRe = new RegExp(
        `^#{1,3}\\s+(?:Part \\d+[:\\s]*)?${otherBase}(?:\\.md)?\\s*$`,
        "im"
      );
      const otherMatch = markdown.slice(startIdx).match(otherRe);
      if (otherMatch && otherMatch.index !== undefined) {
        const idx = startIdx + otherMatch.index;
        if (idx < endIdx) endIdx = idx;
      }
    }

    const content = markdown.slice(startIdx, endIdx).trim();
    if (content.length > 50) {
      docs.push({
        path: docName,
        content,
        source: "agent_h2.md",
        lineNumber: 0,
      });
    }
  }

  return docs;
}

// ============================================================
// MAIN
// ============================================================

function main(): void {
  const h1Path = join(OUTPUT_DIR, "agent_h1.md");
  const h2Path = join(OUTPUT_DIR, "agent_h2.md");

  if (!existsSync(h1Path)) {
    console.error(`Missing: ${h1Path}`);
    console.error("Run the pipeline first: npx tsx run-pipeline.ts ...");
    process.exit(1);
  }

  const h1Content = readFileSync(h1Path, "utf-8");
  const allFiles: ExtractedFile[] = [];

  // Extract code files from H1
  const codeFiles = extractFiles(h1Content, "agent_h1.md");
  allFiles.push(...codeFiles);

  // Extract from H2
  if (existsSync(h2Path)) {
    const h2Content = readFileSync(h2Path, "utf-8");

    // Code files from H2
    const h2Code = extractFiles(h2Content, "agent_h2.md");
    for (const file of h2Code) {
      const existing = allFiles.findIndex((f) => f.path === file.path);
      if (existing === -1) allFiles.push(file);
    }

    // Documentation files
    const docFiles = extractDocs(h2Content);
    for (const file of docFiles) {
      const existing = allFiles.findIndex((f) => f.path === file.path);
      if (existing === -1) allFiles.push(file);
    }
  }

  if (allFiles.length === 0) {
    console.error("No files extracted.");
    console.error("Check agent_h1.md for '### FILE: `path/to/file.ext`' headers above code blocks.");
    process.exit(1);
  }

  // Separate into categories for display
  const srcFiles = allFiles.filter((f) => f.path.startsWith("src/"));
  const configFiles = allFiles.filter(
    (f) => !f.path.startsWith("src/") && !f.path.endsWith(".md")
  );
  const docFilesOut = allFiles.filter(
    (f) => f.path.endsWith(".md") && !f.path.startsWith("src/")
  );

  console.log(`\nExtracted ${allFiles.length} files:\n`);

  if (configFiles.length > 0) {
    console.log("  Config:");
    for (const f of configFiles) {
      console.log(`    ${f.path} (${f.content.split("\n").length} lines)`);
    }
  }

  if (srcFiles.length > 0) {
    console.log("  Source:");
    for (const f of srcFiles) {
      console.log(`    ${f.path} (${f.content.split("\n").length} lines)`);
    }
  }

  if (docFilesOut.length > 0) {
    console.log("  Docs:");
    for (const f of docFilesOut) {
      console.log(`    ${f.path} (${f.content.split("\n").length} lines)`);
    }
  }

  if (!DRY_RUN) {
    for (const file of allFiles) {
      const targetPath = join(PROJECT_DIR, file.path);
      mkdirSync(dirname(targetPath), { recursive: true });
      writeFileSync(targetPath, file.content, "utf-8");
    }
    console.log(`\nFiles written to: ${PROJECT_DIR}/`);
    console.log("\nNext steps:");
    console.log("  npm install");
    console.log("  npm run dev");
  } else {
    console.log("\n[DRY RUN] No files written. Remove --dry-run to write files.");
  }
}

main();
