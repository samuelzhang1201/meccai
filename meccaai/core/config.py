"""Configuration management with Pydantic settings and YAML support."""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    """Application configuration."""

    name: str = "meccaai"
    version: str = "0.1.0"
    debug: bool = False


class MCPConfig(BaseModel):
    """MCP (Model Context Protocol) configuration."""

    config_path: str = "config/mcp/cursor.mcp.json"
    timeout: int = 30
    max_retries: int = 3
    endpoints_path: str = "config/mcp/endpoints.yaml"


class ModelConfig(BaseModel):
    """AI model configuration."""

    model: str
    temperature: float = 0.1
    max_tokens: int = 4096


class ModelsConfig(BaseModel):
    """Multi-provider model configuration."""

    default_provider: str = "openai"
    openai: ModelConfig = Field(default_factory=lambda: ModelConfig(model="gpt-4o-mini"))
    anthropic: ModelConfig = Field(
        default_factory=lambda: ModelConfig(model="claude-3-sonnet-20240229")
    )


class ToolsConfig(BaseModel):
    """Tools configuration."""

    auto_discover: bool = True
    registry_paths: list[str] = Field(default_factory=lambda: ["meccaai.tools"])
    mcp_enabled: bool = True


class MemoryConfig(BaseModel):
    """Memory/vector storage configuration."""

    enabled: bool = False
    provider: str = "chromadb"
    persist_directory: str = "./data/chroma"


class TelemetryConfig(BaseModel):
    """Telemetry configuration."""

    enabled: bool = False
    service_name: str = "meccaai"
    traces_endpoint: str | None = None
    metrics_endpoint: str | None = None


class TableauConfig(BaseModel):
    """Tableau API configuration."""

    server_url: str = Field(default="https://prod-apsoutheast-a.online.tableau.com")
    site_content_url: str = Field(default="meccalumos")
    token_name: str = Field(default="Agent")
    api_version: str = Field(default="3.25")


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    # Environment
    environment: str = Field(default="dev", alias="ENVIRONMENT")

    # API Keys
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    tableau_token_value: str | None = Field(default=None, alias="TABLEAU_TOKEN_VALUE")

    # Configuration sections
    app: AppConfig = Field(default_factory=AppConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    models: ModelsConfig = Field(default_factory=ModelsConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    telemetry: TelemetryConfig = Field(default_factory=TelemetryConfig)
    tableau: TableauConfig = Field(default_factory=TableauConfig)


def load_yaml_config(config_dir: Path, environment: str = "dev") -> dict[str, Any]:
    """Load configuration from YAML files with environment overrides."""
    config_data = {}

    # Load base configuration
    base_config_path = config_dir / "base.yaml"
    if base_config_path.exists():
        with open(base_config_path) as f:
            config_data.update(yaml.safe_load(f) or {})

    # Load environment-specific overrides
    env_config_path = config_dir / f"{environment}.yaml"
    if env_config_path.exists():
        with open(env_config_path) as f:
            env_config = yaml.safe_load(f) or {}
            # Deep merge environment config
            _deep_merge(config_data, env_config)

    return config_data


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> None:
    """Deep merge override into base dictionary."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def get_settings() -> Settings:
    """Get application settings with YAML config loaded."""
    config_dir = Path("config")
    environment = os.getenv("ENVIRONMENT", "dev")

    # Load YAML configuration
    yaml_config = load_yaml_config(config_dir, environment)

    # Create settings with YAML config as defaults
    return Settings(**yaml_config)


# Global settings instance
settings = get_settings()
