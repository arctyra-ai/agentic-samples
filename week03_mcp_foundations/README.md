# Week 3: MCP Foundations

## Objective
Refactor the Week 1 agent to use MCP for tool discovery and execution, then connect to multiple MCP servers.

## What You Will Learn
- MCP architecture: client, server, transport
- Dynamic tool discovery (no hardcoded tool lists)
- Multi-server routing
- How MCP replaces custom tool integrations

## Files
- `mcp_agent.py` -- Agent with MCP tool router, mock servers for testing
- `test_mcp.py` -- Tests for router, tool discovery, multi-server routing

## How to Run
```bash
# With mock servers (no MCP packages needed)
python mcp_agent.py

# Custom request
python mcp_agent.py "List all files and show me the database tables"
```

## How to Test
```bash
pytest test_mcp.py -v
```

## Success Criteria
- [ ] Agent works identically to Week 1 but tools are provided via MCP
- [ ] Agent can use tools from both filesystem and SQLite servers
- [ ] Adding a new MCP server requires zero changes to agent code
- [ ] Tool discovery is dynamic (reads tool list from server at startup)

## Prerequisites
- Weeks 1-2 completed
- `shared/mcp_utils.py` understood
