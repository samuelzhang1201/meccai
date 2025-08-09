# Development Guidelines

This document contains critical information about working with this codebase. Follow these guidelines precisely.

## Core Development Rules

1. Package Management
   - ONLY use uv, NEVER pip
   - Installation: `uv add package`
   - Running tools: `uv run tool`
   - Upgrading: `uv add --dev package --upgrade-package package`
   - FORBIDDEN: `uv pip install`, `@latest` syntax

2. Code Quality
   - Type hints required for all code
   - Public APIs must have docstrings
   - Functions must be focused and small
   - Follow existing patterns exactly
   - Line length: 88 chars maximum

3. Testing Requirements
   - Framework: `uv run pytest`
   - Async testing: use anyio, not asyncio
   - Coverage: test edge cases and errors
   - New features require tests
   - Bug fixes require regression tests

4. Code Style
    - PEP 8 naming (snake_case for functions/variables)
    - Class names in PascalCase
    - Constants in UPPER_SNAKE_CASE
    - Document with docstrings
    - Use f-strings for formatting

- For commits fixing bugs or adding features based on user reports add:
  ```bash
  git commit --trailer "Reported-by:<name>"
  ```
  Where `<name>` is the name of the user.

- For commits related to a Github issue, add
  ```bash
  git commit --trailer "Github-Issue:#<number>"
  ```
- NEVER ever mention a `co-authored-by` or similar aspects. In particular, never
  mention the tool used to create the commit message or PR.

## Development Philosophy

- **Simplicity**: Write simple, straightforward code
- **Readability**: Make code easy to understand
- **Performance**: Consider performance without sacrificing readability
- **Maintainability**: Write code that's easy to update
- **Testability**: Ensure code is testable
- **Reusability**: Create reusable components and functions
- **Less Code = Less Debt**: Minimize code footprint

## Coding Best Practices

- **Early Returns**: Use to avoid nested conditions
- **Descriptive Names**: Use clear variable/function names (prefix handlers with "handle")
- **Constants Over Functions**: Use constants where possible
- **DRY Code**: Don't repeat yourself
- **Functional Style**: Prefer functional, immutable approaches when not verbose
- **Minimal Changes**: Only modify code related to the task at hand
- **Function Ordering**: Define composing functions before their components
- **TODO Comments**: Mark issues in existing code with "TODO:" prefix
- **Simplicity**: Prioritize simplicity and readability over clever solutions
- **Build Iteratively** Start with minimal functionality and verify it works before adding complexity
- **Run Tests**: Test your code frequently with realistic inputs and validate outputs
- **Build Test Environments**: Create testing environments for components that are difficult to validate directly
- **Functional Code**: Use functional and stateless approaches where they improve clarity
- **Clean logic**: Keep core logic clean and push implementation details to the edges
- **File Organsiation**: Balance file organization with simplicity - use an appropriate number of files for the project scale

## System Architecture

meccaai/
├─ pyproject.toml
├─ README.md
├─ .env.example
├─ .gitignore
├─ Makefile
├─ docker/
│  ├─ Dockerfile
│  └─ gunicorn.conf.py
├─ scripts/                 # helper scripts (lint, format, seed, etc.)
├─ config/
│  ├─ base.yaml             # non-secret defaults
│  ├─ dev.yaml              # dev overrides
│  ├─ prod.yaml             # prod overrides
│  ├─ logging.yaml          # struct logging config
│  └─ mcp/
│     ├─ cursor.mcp.json    # your Cursor MCP server config (source of truth)
│     └─ endpoints.yaml     # optional: extra MCP endpoints/services
├─ meccaai/                 # Python package root
│  ├─ __init__.py
│  ├─ core/                 # framework-agnostic code
│  │  ├─ config.py          # pydantic settings loader (env + yaml)
│  │  ├─ logging.py         # logger init from config/logging.yaml
│  │  ├─ types.py           # shared dataclasses / typing Protocols
│  │  ├─ tool_base.py       # Tool interface + registry
│  │  ├─ tool_registry.py   # loads python tools + MCP tools
│  │  ├─ mcp_client.py      # minimal MCP client (JSON-RPC/HTTP)
│  │  ├─ memory.py          # vector/store adapters (optional)
│  │  ├─ io.py              # file/kv/cache abstractions
│  │  └─ tracing.py         # OpenTelemetry hooks (optional)
│  ├─ tools/                # native Python tools (your custom ones)
│  │  ├─ __init__.py
│  │  ├─ data_tools.py      # e.g., Snowflake/dbt utilities
│  │  ├─ reporting_tools.py # e.g., Tableau/report generators
│  │  ├─ mcp_tools.py       # wrappers that present MCP endpoints as Tools
│  │  └─ examples/
│  │     └─ hello.py
│  ├─ adapters/             # framework adapters (translate tools <-> framework)
│  │  ├─ openai_sdk/
│  │  │  ├─ __init__.py
│  │  │  ├─ tool_adapter.py     # tools -> OpenAI "tools"/"functions"
│  │  │  └─ runner.py           # conversation loop, state mgmt
│  │  ├─ crewai/
│  │  │  ├─ __init__.py
│  │  │  ├─ tool_adapter.py     # tools -> CrewAI Tool
│  │  │  └─ runner.py
│  │  └─ langgraph/
│  │     ├─ __init__.py
│  │     ├─ nodes.py            # node defs (call_tool, plan, reflect, etc.)
│  │     ├─ edges.py
│  │     └─ runner.py           # build graph and execute
│  ├─ apps/                 # runnable entrypoints per framework
│  │  ├─ openai_app.py
│  │  ├─ crewai_app.py
│  │  └─ langgraph_app.py
│  └─ mcp/                  # optional: local mcp helpers/clients
│     └─ schemas/           # JSON Schemas if you validate MCP tool IO
└─ tests/
   ├─ test_tools.py
   ├─ test_mcp_integration.py
   └─ test_adapters.py

## Core Components

- `config.py`: Configuration management
- `daemon.py`: Main daemon
[etc... fill in here]

## Pull Requests

- Create a detailed message of what changed. Focus on the high level description of
  the problem it tries to solve, and how it is solved. Don't go into the specifics of the
  code unless it adds clarity.

- Always add `ArthurClune` as reviewer.

- NEVER ever mention a `co-authored-by` or similar aspects. In particular, never
  mention the tool used to create the commit message or PR.

## Python Tools

## Code Formatting

1. Ruff
   - Format: `uv run ruff format .`
   - Check: `uv run ruff check .`
   - Fix: `uv run ruff check . --fix`
   - Critical issues:
     - Line length (88 chars)
     - Import sorting (I001)
     - Unused imports
   - Line wrapping:
     - Strings: use parentheses
     - Function calls: multi-line with proper indent
     - Imports: split into multiple lines

2. Type Checking
   - Tool: `uv run pyright`
   - Requirements:
     - Explicit None checks for Optional
     - Type narrowing for strings
     - Version warnings can be ignored if checks pass

3. Pre-commit
   - Config: `.pre-commit-config.yaml`
   - Runs: on git commit
   - Tools: Prettier (YAML/JSON), Ruff (Python)
   - Ruff updates:
     - Check PyPI versions
     - Update config rev
     - Commit config first

## Error Resolution

1. CI Failures
   - Fix order:
     1. Formatting
     2. Type errors
     3. Linting
   - Type errors:
     - Get full line context
     - Check Optional types
     - Add type narrowing
     - Verify function signatures

2. Common Issues
   - Line length:
     - Break strings with parentheses
     - Multi-line function calls
     - Split imports
   - Types:
     - Add None checks
     - Narrow string types
     - Match existing patterns

3. Best Practices
   - Check git status before commits
   - Run formatters before type checks
   - Keep changes minimal
   - Follow existing patterns
   - Document public APIs
   - Test thoroughly