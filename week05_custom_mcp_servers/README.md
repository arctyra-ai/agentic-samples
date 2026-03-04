# Week 5: Custom MCP Servers

## Objective
Build a custom MCP server that wraps a SQLite database for project/task management, then connect your agent to it.

## What You Will Learn
- MCP server lifecycle: initialize, handle requests, cleanup
- Tool registration with input schemas
- Input validation and structured error handling
- Testing MCP servers independently of agents

## Files
- `project_mcp_server.py` -- MCP server with 6 tools, SQLite persistence
- `test_mcp_server.py` -- Tests for CRUD operations, validation, persistence

## How to Run
```bash
# Standalone test mode (no MCP SDK needed)
python project_mcp_server.py

# As MCP server (requires: pip install mcp)
# Then connect from an MCP client or Claude Desktop
```

## How to Test
```bash
pytest test_mcp_server.py -v
```

## Success Criteria
- [ ] Server exposes 6 tools with correct schemas
- [ ] Full CRUD cycle works through tool calls
- [ ] Invalid inputs return structured errors (not crashes)
- [ ] Data persists across server restarts
- [ ] Agent can manage projects end-to-end via natural language

## Prerequisites
- Weeks 1-3 completed (especially Week 3 MCP concepts)
