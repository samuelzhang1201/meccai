"""dbt (data build tool) integration tools via MCP.

This module provides ONLY the tools that actually exist in the dbt-mcp server.
All tools connect to the actual dbt-mcp server for real dbt operations.
"""

from meccaai.core.mcp_tool_base import mcp_tool

# ONLY actual dbt-mcp server tools (verified from dbt-labs/dbt-mcp repository)


# dbt CLI Tools (8 tools)

@mcp_tool(name="build", server_name="dbt-mcp")
def build(models: str | None = None, select: str | None = None):
    """Executes models, tests, snapshots, and seeds in dependency order.

    Args:
        models: Specific models to build
        select: dbt select syntax for choosing models

    Returns:
        Results of the dbt build command via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="compile", server_name="dbt-mcp")
def compile(models: str | None = None, select: str | None = None):
    """Generates executable SQL without running.

    Args:
        models: Specific models to compile
        select: dbt select syntax for choosing models

    Returns:
        Compilation results via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="docs", server_name="dbt-mcp")
def docs():
    """Generates documentation for the dbt project.

    Returns:
        Documentation generation status via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="list", server_name="dbt-mcp")
def list_resources(select: str | None = None, resource_type: str | None = None):
    """Lists resources in the dbt project.

    Args:
        select: Resource selection criteria
        resource_type: Type of resource to list (model, test, source, etc.)

    Returns:
        List of dbt resources via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="parse", server_name="dbt-mcp")
def parse():
    """Validates project files.

    Returns:
        Parse operation results via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="run", server_name="dbt-mcp")
def run(models: str | None = None, select: str | None = None, exclude: str | None = None):
    """Executes models in the database.

    Args:
        models: Specific models to run (comma-separated)
        select: dbt select syntax for choosing models  
        exclude: Models to exclude from the run

    Returns:
        Results of the dbt run command via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="test", server_name="dbt-mcp")
def test(models: str | None = None, select: str | None = None):
    """Validates data and model integrity.

    Args:
        models: Specific models to test (comma-separated)
        select: dbt select syntax for choosing models to test

    Returns:
        Results of the dbt test command via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="show", server_name="dbt-mcp")
def show(select: str, limit: int = 5):
    """Runs a query against the data warehouse.

    Args:
        select: Model selection criteria
        limit: Number of rows to show

    Returns:
        Query results from the model via MCP
    """
    pass  # Implementation handled by MCP decorator


# Semantic Layer Tools (5 tools)

@mcp_tool(name="list_metrics", server_name="dbt-mcp")
def list_metrics():
    """Retrieves all defined metrics.

    Returns:
        List of all available metrics with descriptions via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="get_dimensions", server_name="dbt-mcp")
def get_dimensions(metrics: list[str]):
    """Gets dimensions for specified metrics.

    Args:
        metrics: List of metric names to get dimensions for

    Returns:
        Available dimensions for the specified metrics via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="get_entities", server_name="dbt-mcp")
def get_entities(metrics: list[str]):
    """Gets entities for specified metrics.

    Args:
        metrics: List of metric names to get entities for

    Returns:
        Available entities for the specified metrics via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="query_metrics", server_name="dbt-mcp")
def query_metrics(
    metrics: list[str],
    group_by: list[str] | None = None,
    order_by: list[str] | None = None,
    where: list[str] | None = None,
    limit: int | None = None,
):
    """Queries metrics with grouping, ordering, filtering, and limiting.

    Args:
        metrics: List of metric names to query
        group_by: Dimensions to group results by
        order_by: Ordering specifications for results
        where: Filter conditions to apply
        limit: Maximum number of rows to return

    Returns:
        Query results from the semantic layer via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="get_metrics_compiled_sql", server_name="dbt-mcp")
def get_metrics_compiled_sql(
    metrics: list[str],
    group_by: list[str] | None = None,
    order_by: list[str] | None = None,
    where: list[str] | None = None,
    limit: int | None = None,
):
    """Returns compiled SQL for metrics without executing.

    Args:
        metrics: List of metric names to compile SQL for
        group_by: Dimensions to group results by
        order_by: Ordering specifications for results
        where: Filter conditions to apply
        limit: Maximum number of rows to return

    Returns:
        Compiled SQL for the metrics query via MCP
    """
    pass  # Implementation handled by MCP decorator


# Discovery Tools (5 tools)

@mcp_tool(name="get_mart_models", server_name="dbt-mcp")
def get_mart_models():
    """Gets all mart models.

    Returns:
        List of all mart models via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="get_all_models", server_name="dbt-mcp")
def get_all_models():
    """Gets all models.

    Returns:
        List of all dbt models via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="get_model_details", server_name="dbt-mcp")
def get_model_details(model_name: str):
    """Gets details for a specific model.

    Args:
        model_name: Name of the model to get details for

    Returns:
        Detailed model information via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="get_model_parents", server_name="dbt-mcp")
def get_model_parents(model_name: str):
    """Gets parent nodes of a model.

    Args:
        model_name: Name of the model to get parents for

    Returns:
        List of parent models and dependencies via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="get_model_children", server_name="dbt-mcp")
def get_model_children(model_name: str):
    """Gets children models.

    Args:
        model_name: Name of the model to get children for

    Returns:
        List of child models that depend on this model via MCP
    """
    pass  # Implementation handled by MCP decorator


# SQL Tools (2 tools)

@mcp_tool(name="text_to_sql", server_name="dbt-mcp")
def text_to_sql(query_text: str):
    """Generates SQL from natural language.

    Args:
        query_text: Natural language description of the desired SQL query

    Returns:
        Generated SQL query via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(name="execute_sql", server_name="dbt-mcp")
def execute_sql(sql_query: str):
    """Executes SQL on dbt Cloud's backend.

    Args:
        sql_query: SQL query to execute

    Returns:
        Query execution results via MCP
    """
    pass  # Implementation handled by MCP decorator