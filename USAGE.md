# MeccaAI System - Usage Guide

The MeccaAI system is a comprehensive data management platform with multi-agent coordination capabilities. Here's how to use it:

## Setup

1. **Install dependencies**:
   ```bash
   uv add -e .
   ```

2. **Configure environment**:
   Create a `.env` file with your API keys:
   ```bash
   # AWS Bedrock Configuration (Primary AI Provider)
   AWS_ACCESS_KEY_ID=your_aws_access_key_id
   AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
   AWS_SESSION_TOKEN=your_aws_session_token (optional)
   AWS_REGION=ap-southeast-2
   
   # Tableau Configuration
   TABLEAU_TOKEN_VALUE=your_tableau_personal_access_token
   
   # CloudWatch Logging (optional - see config for control)
   CLOUDWATCH_LOG_GROUP=your_log_group_name
   ```

3. **Local Logging**:
   Logs are automatically stored in the `logs/` directory with rotation and JSON formatting.

## Command Line Usage

### Basic Commands

```bash
# Run the Bedrock-based agent application
uv run python meccaai/apps/lumos_bedrock_agents.py

# Run the main Lumos Bedrock application
uv run python meccaai/apps/lumos_bedrock_app.py

# Test individual Tableau functions
uv run python tests/test_tableau_functions.py
```

### Testing Tools

```bash
# Run all tests
uv run pytest

# Test specific modules
uv run pytest tests/test_tableau_functions.py -v

# Format code
uv run ruff format .

# Type checking
uv run pyright
```

## Programmatic Usage

```python
import asyncio
from meccaai.tools.tableau_tools import (
    get_datasources,
    get_workbooks, 
    get_views_on_site,
    get_content_usage
)

async def main():
    # Get all datasources
    result = await get_datasources.call(page_size=100)
    if result.success:
        data = result.result
        print(f"Found {data['total_datasources']} datasources")
    
    # Get workbooks with filtering
    result = await get_workbooks.call(
        filter_expression="createdAt:gt:2023-01-01T00:00:00Z",
        page_size=50
    )
    if result.success:
        data = result.result  
        print(f"Found {data['total_workbooks']} recent workbooks")
    
    # Get views for usage analysis
    result = await get_views_on_site.call(page_size=500)
    if result.success:
        data = result.result
        print(f"Found {data['total_views']} views")

asyncio.run(main())
```

## Available Agents

### 1. **Data Manager** (`data_manager`)
- **Role**: Central orchestrator and primary interface for users
- **Capabilities**: Coordinates tasks across different agents, provides comprehensive data reporting with both summaries and detailed lists (up to 500 rows)
- **Use for**: Workflow orchestration, project management, comprehensive reporting

### 2. **Data Analyst** (`data_analyst`)  
- **Role**: Semantic layer queries and data insights specialist
- **Tools**: dbt metrics, data analysis, business intelligence
- **Use for**: Query execution, metrics analysis, trend identification

### 3. **Data Engineer** (`data_engineer`)
- **Role**: dbt project management and data pipeline specialist
- **Tools**: dbt model building, testing, documentation, discovery
- **Use for**: Data transformations, model management, pipeline health

### 4. **Tableau Admin** (`tableau_admin`)
- **Role**: Tableau user management and site administration
- **Tools**: User management, permissions, site administration, content management
- **Use for**: Tableau administration, user lifecycle, permissions management

### 5. **Data Admin** (`data_admin`)
- **Role**: Jira project management and team coordination
- **Tools**: Issue tracking, project management, team coordination
- **Use for**: Project management, issue resolution, team coordination

## Tableau Integration

The system includes comprehensive Tableau REST API integration:

- **Authentication**: Automatic sign-in/sign-out with Personal Access Tokens
- **API Version**: 3.25 (latest)
- **Server**: `https://prod-apsoutheast-a.online.tableau.com`
- **Site**: `meccalumos`
- **Pagination**: Automatic handling for large datasets (up to 500 records per request)

### Available Tableau Operations

#### Content Management:
1. **get_content_usage**: Get usage statistics for workbooks, views, data sources
2. **get_datasources**: List published data sources with filtering and sorting
3. **get_workbooks**: List workbooks with filtering and sorting
4. **get_views_on_site**: List all views with filtering options

#### User Management:
5. **get_users_on_site**: List site users with filtering and pagination
6. **add_user_to_site**: Add new users to the site
7. **update_user**: Update user information and roles
8. **get_users_in_group**: Get users in specific groups

#### Access Management:
9. **list_all_personal_access_tokens**: List Personal Access Tokens
10. **get_group_set**: List all groups with filtering and sorting

## Security Features

- **Secure Credentials**: API keys stored as environment variables
- **Session Management**: Automatic Tableau session cleanup
- **Token-based Auth**: Uses Personal Access Tokens for Tableau API
- **AWS Integration**: Bedrock for AI models with proper IAM credentials
- **Local Logging**: Logs stored locally in `logs/` directory with rotation
- **CloudWatch Control**: Optional CloudWatch logging with configurable parameters
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

- **Multi-Agent System**: Specialized agents for different data domains
- **Tool-based Architecture**: Modular tools that can be mixed and matched
- **AWS Bedrock Integration**: Uses Claude Sonnet for intelligent responses
- **Comprehensive Reporting**: Provides both summary statistics and detailed lists (up to 500 rows)
- **Async/Await**: Fully asynchronous for high performance
- **Configuration Management**: YAML + environment variable configuration
- **Structured Logging**: JSON formatted logs with local storage and optional CloudWatch
- **Type Safety**: Full type hints throughout the codebase
- **Testing**: Comprehensive test suite for reliability

## Logging Configuration

The system now supports:
- **Local Logging**: Automatically stores logs in `logs/meccaai.log` with rotation (10MB files, 5 backups)
- **Console Logging**: Real-time console output for development
- **JSON Format**: Structured logging for better parsing and analysis
- **CloudWatch Integration**: Optional upload to AWS CloudWatch (configurable)

To control CloudWatch logging, see the configuration section for the new parameter.

The MeccaAI system is now fully implemented and ready for production use!