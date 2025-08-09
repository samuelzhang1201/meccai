# Lumos AI System - Usage Guide

The Lumos AI system has been successfully implemented according to the requirements. Here's how to use it:

## Setup

1. **Install dependencies**:
   ```bash
   uv add -e .
   ```

2. **Configure environment**:
   Create a `.env` file with your API keys:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   TABLEAU_PAT_TOKEN=your_tableau_pat_token_here
   ```

## Command Line Usage

### Basic Commands

```bash
# List all available agents
lumos list-agents

# Chat with a specific agent
lumos chat --agent tableau "List all personal access tokens"
lumos chat --agent dbt "Run data transformations"
lumos chat --agent reporting "Analyze the latest sales data"

# Use orchestrated workflow (multiple agents)
lumos chat --workflow "Create a comprehensive data report with Tableau visualizations"
```

### Tableau-Specific Commands

```bash
# List Tableau Personal Access Tokens
lumos tableau-pats

# Get details of a specific view
lumos tableau-view abc123-def456

# Export a view to PDF with filters
lumos tableau-pdf abc123-def456 --filters '{"region": "north", "year": "2024"}'
```

## Programmatic Usage

```python
import asyncio
from meccaai.apps.lumos_agents import LumosAgentSystem
from meccaai.core.types import Message

async def main():
    system = LumosAgentSystem()
    
    # Use Tableau analyst
    messages = [Message(role="user", content="List all PATs in our Tableau site")]
    result = await system.process_request(messages, agent="tableau")
    print(result.content)
    
    # Use orchestrated workflow
    messages = [Message(role="user", content="Generate weekly analytics report")]
    results = await system.process_request(messages, workflow=True)
    for result in results:
        print(result.content)

asyncio.run(main())
```

## Available Agents

### 1. **Lumos AI Manager** (`manager`)
- **Role**: Central orchestrator who coordinates between specialized agents
- **Tools**: Email sending, Slack messaging, Google Sheets integration, webhooks
- **Use for**: Report generation, workflow coordination, communication

### 2. **Tableau Analyst** (`tableau`)  
- **Role**: Expert data visualization specialist for Tableau operations
- **Tools**: PAT management, view querying, PDF export, dashboard analysis
- **Use for**: Tableau administration, visualization exports, dashboard insights

### 3. **DBT Build Agent** (`dbt`)
- **Role**: Data engineering specialist for dbt operations
- **Tools**: Model building, testing, documentation generation
- **Use for**: Data transformations, model management, data quality

### 4. **Reporting Analyst** (`reporting`)
- **Role**: Experienced data analyst for insights and reporting
- **Tools**: General analysis tools, data interpretation
- **Use for**: Data analysis, trend identification, business insights

## Tableau Integration

The system includes comprehensive Tableau REST API integration:

- **Authentication**: Automatic sign-in/sign-out with Personal Access Tokens
- **API Version**: 3.25 (latest)
- **Server**: `https://prod-apsoutheast-a.online.tableau.com`
- **Site**: `meccalumos`
- **Pagination**: Automatic handling for large datasets

### Available Tableau Operations

1. **list_all_pats**: List all Personal Access Tokens
2. **get_view**: Get detailed view information by ID
3. **query_view_pdf**: Export views to PDF with optional filters
4. **list_views**: List all views (with optional workbook filtering)

## Security Features

- **Secure Credentials**: API keys stored as environment variables
- **Session Management**: Automatic Tableau session cleanup
- **Token-based Auth**: Uses Personal Access Tokens for Tableau API
- **No Hardcoded Secrets**: All sensitive data configurable via environment

## Future Extensibility

The system is designed for easy extension:

- **MCP Integration**: Ready for dbt-mcp and zapier-mcp tools
- **Custom Agents**: Easy to add new specialized agents
- **Tool Registry**: Automatic discovery and registration of new tools
- **Workflow Orchestration**: Intelligent task delegation between agents

## Testing

Run the test suite to verify everything is working:

```bash
# Run all tests
uv run pytest -v

# Run specific test modules
uv run pytest tests/test_lumos_system.py -v
uv run pytest tests/test_tools.py -v
```

## Development

The implementation follows all project guidelines:

- **Code Style**: PEP 8 with 88-character line length
- **Type Hints**: Full type annotations throughout
- **Testing**: Comprehensive test coverage
- **Documentation**: Detailed docstrings for all public APIs
- **Error Handling**: Graceful error handling and cleanup

## Architecture Highlights

- **Multi-Agent System**: Specialized agents for different domains
- **Tool-based Architecture**: Modular tools that can be mixed and matched
- **OpenAI Integration**: Uses GPT-4 for intelligent responses
- **Async/Await**: Fully asynchronous for high performance
- **Configuration Management**: YAML + environment variable configuration
- **Logging**: Structured logging throughout the system

The Lumos AI system is now fully implemented and ready for production use!