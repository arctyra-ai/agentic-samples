# Security Notes

This document covers security considerations for the curriculum code. These exercises are learning tools, not production software. However, they demonstrate real security patterns that matter in production.

---

## API Key Protection

- **Never commit `.env` files.** The `.gitignore` excludes `.env` by default.
- **Use `.env.example` as a template.** It contains placeholder values only (`sk-ant-your-key-here`).
- **If you accidentally commit a key:** Rotate it immediately at the provider's dashboard, then use `git filter-branch` or `git-filter-repo` to remove it from history. GitHub's push protection may catch this before it reaches the remote.

## Path Traversal Protection (Week 1)

The file operations agent restricts all file access to the specified working directory using path sandboxing (`_validate_path`). This prevents the LLM from requesting access to files outside the target directory (e.g., `/etc/passwd`, `../../sensitive_file`).

If you modify the agent or build your own file tools, always validate that resolved paths are within the expected directory before performing any read or write operation.

## SQL Injection (Week 5 vs Week 7/9)

**Week 5 (project_mcp_server.py)** uses parameterized queries (`?` placeholders) throughout. This is the correct pattern.

**Week 7 and Week 9** contain intentionally vulnerable code samples (f-string SQL queries) as test data for the code review agents to detect. These samples are:
- `week07_multi_agent_systems/code_review_agents.py` line 227 (demo input)
- `week09_evaluation_and_observability/evaluation.py` ground truth dataset

These are not executed against any database. They exist solely as examples of what the review agents should flag.

## Fake Secrets in Test Data (Week 9)

The ground truth dataset in `evaluation.py` contains a fake API key (`sk-abc123secret`) as an intentionally insecure code sample for the agents to detect. It is annotated with comments and `# noqa: S105` to suppress secret scanner warnings. This key is not real and connects to nothing.

## Dependency Versions

All dependencies use bounded version ranges (`>=X.Y.Z,<NEXT_MAJOR`) to prevent breaking changes from upstream packages while still allowing patch updates. If you encounter version conflicts, pin exact versions with `pip freeze > requirements.lock`.

## LLM-Controlled Actions

A general security principle for all exercises: **the LLM decides which tools to call and with what arguments.** This means any tool that performs a side effect (writing files, executing queries, making API calls) is a potential attack surface if the LLM is manipulated via prompt injection.

Mitigations used in this curriculum:
- **Path sandboxing** (Week 1): File tools reject paths outside the working directory
- **Parameterized SQL** (Week 5): Database queries use placeholders, not string formatting
- **Input validation** (Week 5): Tool inputs are validated before execution
- **Budget enforcement** (shared/llm_client.py): Cost limits prevent runaway API usage
- **Max iterations** (all agents): Agent loops have hard limits to prevent infinite execution

For production systems, add:
- Human approval for destructive operations (delete, overwrite, send)
- Rate limiting on tool calls
- Audit logging for all tool executions
- Principle of least privilege (agents should have minimal permissions)

## Reporting Issues

If you find a security issue in this curriculum, open a GitHub issue or contact the repository maintainer.
