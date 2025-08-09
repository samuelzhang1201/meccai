# MeccaAI

AI tool framework with MCP (Model Context Protocol) support for building flexible AI agents.

## Features

- **Multi-framework Support**: Works with OpenAI SDK, CrewAI, and LangGraph
- **MCP Integration**: Native Model Context Protocol support for tool discovery
- **Extensible Architecture**: Plugin-based tool system
- **Type Safety**: Full type hints and validation with Pydantic
- **Configuration Management**: YAML-based configuration with environment overrides
- **Structured Logging**: Built-in structured logging with OpenTelemetry support

## Quick Start

### Installation

```bash
uv add meccaai
```

### Development Setup

```bash
# Clone and setup
git clone <repository-url>
cd meccaai
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Format and lint
uv run ruff format .
uv run ruff check .
uv run pyright
```

### Basic Usage

```python
from meccaai.apps.openai_app import create_app

# Create an AI app with your tools
app = create_app()
response = app.run("What tools are available?")
print(response)
```

## Architecture

- **Core**: Framework-agnostic components (config, tools, MCP client)
- **Tools**: Native Python tools and MCP tool wrappers
- **Adapters**: Framework-specific adapters (OpenAI, CrewAI, LangGraph)
- **Apps**: Runnable applications for each framework

## Configuration

Place configuration files in the `config/` directory:

- `base.yaml`: Non-secret defaults
- `dev.yaml`: Development overrides  
- `prod.yaml`: Production overrides
- `logging.yaml`: Structured logging configuration

## MCP Integration

Configure MCP servers in `config/mcp/cursor.mcp.json` or add custom endpoints in `config/mcp/endpoints.yaml`.

## Development

See [CLAUDE.md](./CLAUDE.md) for detailed development guidelines.

## License

MIT