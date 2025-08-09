# Lumos AI Multi-Agent System

The Lumos AI system is a multi-agent framework built on top of the MeccaAI platform, designed to handle complex data workflows involving Tableau, dbt, and automated reporting.

## Architecture

The system consists of four specialized agents:

1. **Lumos AI Manager** - Central orchestrator
2. **Tableau Analyst** - Data visualization specialist
3. **DBT Build Agent** - Data engineering specialist  
4. **Reporting Analyst** - Data analysis and reporting specialist

## Agents Overview

### 1. Lumos AI Manager
**Role**: Central orchestrator who coordinates between specialized agents, generates comprehensive reports, and manages communication workflows.

**Capabilities**:
- Orchestrates multi-agent workflows
- Sends emails via Zapier integration
- Posts to Slack channels
- Creates Google Sheet rows
- Triggers custom webhooks

**Tools**: `send_email`, `create_slack_message`, `create_google_sheet_row`, `trigger_webhook`

### 2. Tableau Analyst
**Role**: Expert data visualization specialist who helps users work with Tableau dashboards, views, and reports.

**Capabilities**:
- List and manage Personal Access Tokens (PATs)
- Query Tableau views and get detailed information
- Export views to PDF format with filtering
- List all views in a site or workbook

**Tools**: `list_all_pats`, `get_view`, `query_view_pdf`, `list_views`

### 3. DBT Build Agent
**Role**: Data engineering specialist who helps with dbt model building, testing, and deployment.

**Capabilities**:
- Run dbt models with selection criteria
- Execute dbt tests
- Generate dbt documentation

**Tools**: `dbt_run`, `dbt_test`, `dbt_docs_generate`

### 4. Reporting Analyst
**Role**: Experienced data analyst who helps analyze data patterns, create insights, and generate comprehensive reports.

**Capabilities**:
- Data pattern analysis
- Trend identification
- Report generation and insights
- Data interpretation and communication

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Tableau Configuration
TABLEAU_TOKEN_VALUE=your_tableau_token_value_here

# Optional
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ENVIRONMENT=dev
```

### Tableau Configuration

The system is pre-configured with the following Tableau settings:
- **Server URL**: `https://prod-apsoutheast-a.online.tableau.com`
- **Site Content URL**: `meccalumos`
- **Token Name**: `Agent`
- **API Version**: `3.25`

These can be overridden via YAML configuration files in the `config/` directory.

## Usage

### Command Line Interface

The Lumos system provides a CLI tool accessible via the `lumos` command:

```bash
# Install the package
uv add -e .

# Basic chat with any agent
lumos chat "List all Tableau PATs in our site"

# Use specific agent
lumos chat --agent tableau "Export view xyz123 to PDF"

# Use orchestrated workflow (multiple agents)
lumos chat --workflow "Create a comprehensive data report with Tableau insights"

# List available agents
lumos list-agents

# Tableau-specific commands
lumos tableau-pats
lumos tableau-view <view_id>
lumos tableau-pdf <view_id> --filters '{"region": "north"}'
```

### Programmatic Usage

```python
from meccaai.apps.lumos_agents import LumosAgentSystem
from meccaai.core.types import Message

# Initialize the system
system = LumosAgentSystem()

# Use specific agent
messages = [Message(role="user", content="List all PATs")]
result = await system.process_request(messages, agent="tableau")

# Use orchestrated workflow
workflow_messages = [Message(role="user", content="Generate weekly report")]
results = await system.process_request(workflow_messages, workflow=True)
```

## Tableau Tools

### Authentication
All Tableau tools automatically handle authentication using Personal Access Tokens (PAT). The system:
1. Signs in using the configured PAT before making API calls
2. Automatically signs out after completing operations
3. Handles session management and error cleanup

### Available Tools

#### `list_all_pats`
Lists all Personal Access Tokens in the Tableau site with pagination support.

#### `get_view`
Retrieves detailed information about a specific Tableau view by ID.

#### `query_view_pdf`
Exports a Tableau view to PDF format with optional filtering parameters.

#### `list_views`
Lists all views in the site, optionally filtered by workbook ID.

### Error Handling
- Automatic session cleanup on errors
- Comprehensive error logging
- Graceful fallback for API timeouts
- Pagination support for large datasets

## Integration Points

### MCP (Model Context Protocol)
The system is designed to integrate with MCP servers for:
- **dbt-mcp**: Advanced dbt operations and model management
- **zapier-mcp**: Enhanced automation and workflow triggers

### OpenAI Integration
- Uses GPT-4 as the default model for all agents
- Supports function calling for tool execution
- Configurable temperature and token limits

## Security

### Credential Management
- API keys and tokens stored as environment variables
- No hardcoded secrets in source code
- Automatic session cleanup for Tableau authentication
- Secure token-based authentication for all external APIs

### Best Practices
- All API communications use HTTPS
- Session tokens are scoped and temporary
- Error messages sanitized to prevent information leakage

## Development

### Adding New Tools
1. Create tool functions using the `@tool` decorator
2. Add them to the appropriate agent's tool list
3. Import the module in `meccaai/tools/__init__.py`

### Adding New Agents
1. Extend the `LumosAgent` base class
2. Define the agent's role and available tools
3. Register the agent in the `LumosAgentSystem`

### Testing
```bash
# Run all tests
uv run pytest

# Test specific functionality
uv run pytest tests/test_tableau_tools.py
```

## Troubleshooting

### Common Issues

**Tableau Authentication Errors**
- Verify `TABLEAU_TOKEN_VALUE` is correctly set
- Check that the PAT is active and has necessary permissions
- Ensure the site content URL matches your Tableau site

**Tool Not Found Errors**
- Verify all tool modules are imported in `__init__.py`
- Check that the tool is registered with the correct name
- Ensure the agent has the tool in its tools list

**API Timeout Errors**
- PDF export operations may take longer - timeout is set to 120s
- Large datasets with pagination may take time to complete
- Check network connectivity to external APIs

### Logging
The system uses structured logging. Enable debug mode for detailed operation logs:

```bash
export LOG_LEVEL=DEBUG
lumos chat "your command"
```

## Future Enhancements

- Real MCP integration for dbt and Zapier tools
- Support for additional visualization platforms
- Enhanced workflow orchestration capabilities
- Real-time data streaming and alerts
- Advanced analytics and ML model integration