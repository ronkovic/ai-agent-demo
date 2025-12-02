# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI agent demo project with MCP (Model Context Protocol) server integrations configured.

## MCP Servers

The project has the following MCP servers configured in `.mcp.json`:

- **filesystem**: Access to Desktop, Downloads, and workspace directories
- **context7**: Documentation retrieval via @upstash/context7-mcp
- **kiri**: Code indexing with DuckDB (index stored in `.kiri/`)
- **chrome-devtools**: Browser automation and DevTools integration
- **next-devtools**: Next.js development tools
- **aws-mcp**: AWS services integration (configured for ap-northeast-1 region)
- **serena**: IDE assistant functionality
