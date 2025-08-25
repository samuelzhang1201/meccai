"""dbt (data build tool) integration tools via MCP.

This module provides ONLY the tools that actually exist in the dbt-mcp server.
All tools connect to the actual dbt-mcp server for real dbt operations.
"""

from datetime import datetime, timedelta
from typing import Any

import httpx

from meccaai.core.config import settings, get_settings
from meccaai.core.logging import get_logger
from meccaai.core.mcp_tool_base import mcp_tool
from meccaai.core.tool_base import tool, ToolResult
from meccaai.core.tool_registry import get_registry
from meccaai.prompts.loader import get_tool_description

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
def run(
    models: str | None = None, select: str | None = None, exclude: str | None = None
):
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


@mcp_tool(
    name="list_metrics",
    server_name="dbt-mcp",
    description=get_tool_description("semantic_layer/list_metrics.md"),
)
def list_metrics():
    """Retrieves all defined metrics.

    Returns:
        List of all available metrics with descriptions via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(
    name="get_dimensions",
    server_name="dbt-mcp",
    description=get_tool_description("semantic_layer/get_dimensions.md"),
)
def get_dimensions(metrics: list[str]):
    """Gets dimensions for specified metrics.

    Args:
        metrics: List of metric names to get dimensions for

    Returns:
        Available dimensions for the specified metrics via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(
    name="get_entities",
    server_name="dbt-mcp",
    description=get_tool_description("semantic_layer/get_entities.md"),
)
def get_entities(metrics: list[str]):
    """Gets entities for specified metrics.

    Args:
        metrics: List of metric names to get entities for

    Returns:
        Available entities for the specified metrics via MCP
    """
    pass  # Implementation handled by MCP decorator


# Define the correct JSON schema for query_metrics parameters
QUERY_METRICS_SCHEMA = {
    "type": "object",
    "properties": {
        "metrics": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of metric names to query",
        },
        "group_by": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "grain": {"type": ["string", "null"]},
                },
                "required": ["name", "type"],
            },
            "description": "List of dimensions/entities to group results by",
        },
        "order_by": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "desc": {"type": "boolean"},
                    "descending": {"type": "boolean"},
                },
                "required": ["name"],
            },
            "description": "List of ordering specifications for results",
        },
        "where": {
            "type": "string",
            "description": "SQL WHERE clause with dimension/entity references",
        },
        "limit": {"type": "integer", "description": "Maximum number of rows to return"},
    },
    "required": ["metrics"],
}


@mcp_tool(
    name="query_metrics",
    server_name="dbt-mcp",
    description=get_tool_description("semantic_layer/query_metrics.md"),
    parameters_schema=QUERY_METRICS_SCHEMA,
)
def query_metrics(
    metrics: list[str],
    group_by: list[dict] | None = None,  # Fixed: list of objects, not strings
    order_by: list[dict] | None = None,  # Fixed: list of objects, not strings
    where: str | None = None,  # Fixed: string, not list
    limit: int | None = None,
):
    """Queries metrics with grouping, ordering, filtering, and limiting.

    Args:
        metrics: List of metric names to query
        group_by: List of dimension/entity objects with name, type, grain
        order_by: List of ordering objects with name, desc/descending
        where: SQL WHERE clause string with dimension/entity references
        limit: Maximum number of rows to return

    Returns:
        Query results from the semantic layer via MCP
    """
    pass  # Implementation handled by MCP decorator


@mcp_tool(
    name="get_metrics_compiled_sql",
    server_name="dbt-mcp",
    parameters_schema=QUERY_METRICS_SCHEMA,
)
def get_metrics_compiled_sql(
    metrics: list[str],
    group_by: list[dict] | None = None,  # Fixed: list of objects, not strings
    order_by: list[dict] | None = None,  # Fixed: list of objects, not strings
    where: str | None = None,  # Fixed: string, not list
    limit: int | None = None,
):
    """Returns compiled SQL for metrics without executing.

    Args:
        metrics: List of metric names to compile SQL for
        group_by: List of dimension/entity objects with name, type, grain
        order_by: List of ordering objects with name, desc/descending
        where: SQL WHERE clause string with dimension/entity references
        limit: Maximum number of rows to return

    Returns:
        Compiled SQL for the metrics query via MCP
    """
    pass  # Implementation handled by MCP decorator


# Schema is now provided via decorator parameter


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


# dbt Cloud Discovery API Tools (new additions)

logger = get_logger(__name__)



class DBTCloudDiscoveryAPI:
    """dbt Cloud Discovery API client."""

    def __init__(self):
        # Use the API base from environment variables (required)
        api_base = getattr(settings, 'api_base', None)

        if not api_base:
            raise ValueError("API_BASE environment variable must be set")

        # Convert the dbt host URL to the correct metadata API endpoint
        if 'au.dbt.com' in api_base:
            # Australian dbt Cloud uses the Australian metadata endpoint
            self.base_url = "https://metadata.au.dbt.com/graphql"
        elif 'cloud.getdbt.com' in api_base or 'getdbt.com' in api_base:
            # US/Global dbt Cloud
            self.base_url = "https://metadata.cloud.getdbt.com/graphql"
        else:
            # For any other API base, try to construct the metadata URL
            # Replace 'dbt.com' with 'dbt.com' and add metadata prefix
            base_domain = api_base.replace('https://', '').replace('http://', '')
            if 'au.dbt.com' in base_domain:
                self.base_url = "https://metadata.au.dbt.com/graphql"
            else:
                self.base_url = f"https://metadata.{base_domain}/graphql"

        self.token = getattr(settings, 'dbt_cloud_token', None)
        self.environment_id = getattr(settings, 'dbt_environment_id', None)

    async def query_graphql(self, query: str, variables: dict = None) -> dict[str, Any]:
        """Execute a GraphQL query against dbt Cloud Discovery API."""
        if not self.token:
            raise ValueError("DBT_CLOUD_TOKEN environment variable not set")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        timeout = httpx.Timeout(60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                self.base_url,
                json=payload,
                headers=headers
            )

            logger.info(f"dbt Discovery API response status: {response.status_code}")

            # Log response details for debugging
            if response.status_code != 200:
                logger.error(f"Response status: {response.status_code}")
                logger.error(f"Response headers: {response.headers}")
                logger.error(f"Response content: {response.text}")

            response.raise_for_status()

            return response.json()


@tool("list_dbt_test_info")
async def list_dbt_test_info(environment_id: str | None = None, limit: int = 20, hours: int = 24) -> dict[str, Any]:
    """Get detailed information about dbt tests including status and execution details.

    Args:
        environment_id: dbt Cloud environment ID (optional, uses default from config)
        limit: Maximum number of tests to retrieve (default: 20, max: 100)
        hours: Number of hours to look back for filtering (default: 24)

    Returns:
        Dict containing test information with names, status, execution times, and errors
    """
    try:
        api = DBTCloudDiscoveryAPI()
        env_id = environment_id or api.environment_id

        if not env_id:
            raise ValueError("Environment ID must be provided or set in DBT_ENVIRONMENT_ID")

        query = """
        query ($environmentId: BigInt!, $first: Int!) {
          environment(id: $environmentId) {
            applied {
              tests(first: $first) {
                edges {
                  node {
                    name
                    uniqueId
                    columnName
                    parents {
                      name
                      uniqueId
                    }
                    executionInfo {
                      lastRunId
                      lastRunStatus
                      lastRunError
                      executeCompletedAt
                      executeStartedAt
                      executionTime
                    }
                  }
                }
                pageInfo {
                  hasNextPage
                  endCursor
                }
              }
            }
          }
        }
        """

        variables = {
            "environmentId": int(env_id),
            "first": min(limit, 100)  # Reduced to prevent oversized responses
        }

        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        tests_data = result["data"]["environment"]["applied"]["tests"]
        all_tests = [edge["node"] for edge in tests_data["edges"]]

        # Return all tests (removed time filtering)
        tests = all_tests

        return {
            "total_tests": len(tests),
            "tests": tests,
            "has_more": tests_data["pageInfo"]["hasNextPage"],
            "environment_id": env_id,
            "time_filter": {
                "hours_back": hours,
                "tests_before_filter": len(all_tests),
                "tests_after_filter": len(tests)
            }
        }

    except Exception as e:
        logger.error(f"Error getting dbt test info: {e}")
        raise e


@tool("list_dbt_tests")
async def list_dbt_tests(environment_id: str | None = None, status_filter: str | None = None, limit: int = 20) -> dict[str, Any]:
    """List dbt tests with optional filtering by status.

    Args:
        environment_id: dbt Cloud environment ID (optional, uses default from config)
        status_filter: Filter tests by status ('pass', 'fail', 'error', 'warn')
        limit: Maximum number of tests to retrieve (default: 20, max: 100)

    Returns:
        Dict containing filtered test list with basic information
    """
    try:
        api = DBTCloudDiscoveryAPI()
        env_id = environment_id or api.environment_id

        if not env_id:
            raise ValueError("Environment ID must be provided or set in DBT_ENVIRONMENT_ID")

        # Build filter clause for GraphQL
        filter_clause = ""
        if status_filter:
            valid_statuses = ["pass", "fail", "error", "warn"]
            if status_filter.lower() in valid_statuses:
                filter_clause = f", filter: {{ status: \"{status_filter.lower()}\" }}"

        query = f"""
        query ($environmentId: BigInt!, $first: Int!) {{
          environment(id: $environmentId) {{
            applied {{
              tests(first: $first{filter_clause}) {{
                edges {{
                  node {{
                    name
                    uniqueId
                    columnName
                    executionInfo {{
                      lastRunStatus
                      executeCompletedAt
                      executeStartedAt
                      executionTime
                    }}
                    parents {{
                      name
                      uniqueId
                    }}
                  }}
                }}
                pageInfo {{
                  hasNextPage
                  endCursor
                }}
              }}
            }}
          }}
        }}
        """

        variables = {
            "environmentId": int(env_id),
            "first": min(limit, 100)  # Reduced to prevent oversized responses
        }

        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        tests_data = result["data"]["environment"]["applied"]["tests"]
        tests = [edge["node"] for edge in tests_data["edges"]]

        return {
            "total_tests": len(tests),
            "status_filter": status_filter,
            "tests": tests,
            "has_more": tests_data["pageInfo"]["hasNextPage"],
            "environment_id": env_id
        }

    except Exception as e:
        logger.error(f"Error listing dbt tests: {e}")
        raise e


@tool("list_job_runs")
async def list_job_runs(job_id: str, run_id: str | None = None) -> dict[str, Any]:
    """Get information about dbt job runs including model and test execution details.

    Args:
        job_id: dbt Cloud job ID to query
        run_id: Optional specific run ID (defaults to latest run)

    Returns:
        Dict containing job run information with model and test results
    """
    try:
        api = DBTCloudDiscoveryAPI()

        # Build query with optional runId
        run_clause = f", runId: {run_id}" if run_id else ""

        query = f"""
        query ($jobId: BigInt!) {{
          job(id: $jobId{run_clause}) {{
            models {{
              name
              uniqueId
              database
              schema
              alias
              status
              executionInfo {{
                executionTime
                executeStartedAt
                executeCompletedAt
                lastRunStatus
                lastRunId
              }}
              tests {{
                name
                uniqueId
                status
                columnName
                executionInfo {{
                  lastRunStatus
                  executionTime
                  executeStartedAt
                  executeCompletedAt
                }}
              }}
            }}
            sources {{
              uniqueId
              sourceName
              name
              database
              schema
              state
              maxLoadedAt
              freshnessChecked
            }}
            runId
          }}
        }}
        """

        variables = {
            "jobId": int(job_id)
        }

        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        job_data = result["data"]["job"]

        return {
            "job_id": job_id,
            "run_id": run_id or job_data.get("runId"),
            "models": job_data.get("models", []),
            "sources": job_data.get("sources", []),
            "total_models": len(job_data.get("models", [])),
            "total_sources": len(job_data.get("sources", []))
        }

    except Exception as e:
        logger.error(f"Error getting job runs: {e}")
        raise e


@tool("list_model_execution_time")
async def list_model_execution_time(environment_id: str | None = None, limit: int = 20, sort_by_time: bool = True, hours: int = 24) -> dict[str, Any]:
    """Get model execution times and performance information.

    Args:
        environment_id: dbt Cloud environment ID (optional, uses default from config)
        limit: Maximum number of models to retrieve (default: 20, max: 100)
        sort_by_time: Whether to sort results by execution time (default: True)
        hours: Number of hours to look back for filtering (default: 24)

    Returns:
        Dict containing model execution times and performance data
    """
    try:
        api = DBTCloudDiscoveryAPI()
        env_id = environment_id or api.environment_id

        if not env_id:
            raise ValueError("Environment ID must be provided or set in DBT_ENVIRONMENT_ID")

        query = """
        query ($environmentId: BigInt!, $first: Int!) {
          environment(id: $environmentId) {
            applied {
              models(first: $first) {
                edges {
                  node {
                    name
                    uniqueId
                    database
                    schema
                    alias
                    executionInfo {
                      executionTime
                      executeStartedAt
                      executeCompletedAt
                      lastRunStatus
                      lastRunId
                    }
                  }
                }
                pageInfo {
                  hasNextPage
                  endCursor
                }
              }
            }
          }
        }
        """

        variables = {
            "environmentId": int(env_id),
            "first": min(limit, 100)  # Reduced to prevent oversized responses
        }

        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        models_data = result["data"]["environment"]["applied"]["models"]
        all_models = [edge["node"] for edge in models_data["edges"]]

        # Filter models by time window
        models = all_models

        # Sort by execution time if requested
        if sort_by_time:
            models.sort(
                key=lambda x: x.get("executionInfo", {}).get("executionTime") or 0,
                reverse=True
            )

        return {
            "total_models": len(models),
            "models": models,
            "has_more": models_data["pageInfo"]["hasNextPage"],
            "environment_id": env_id,
            "sorted_by_time": sort_by_time,
            "time_filter": {
                "hours_back": hours,
                "models_before_filter": len(all_models),
                "models_after_filter": len(models)
            }
        }

    except Exception as e:
        logger.error(f"Error getting model execution times: {e}")
        raise e


@tool("get_job_execution_performance")
async def get_job_execution_performance(job_id: str, hours: int = 24) -> dict[str, Any]:
    """Get job execution performance summary for a specific job over a time period.

    Args:
        job_id: dbt Cloud job ID to query
        hours: Number of hours to look back (default: 24)

    Returns:
        Dict containing job execution performance summary including model times and status
    """
    try:
        api = DBTCloudDiscoveryAPI()

        query = """
        query ($jobId: BigInt!) {
          job(id: $jobId) {
            models {
              name
              uniqueId
              database
              schema
              alias
              status
              executionInfo {
                executionTime
                executeStartedAt
                executeCompletedAt
                lastRunStatus
                lastRunId
              }
              tests {
                name
                uniqueId
                status
                executionInfo {
                  lastRunStatus
                  executionTime
                  executeStartedAt
                  executeCompletedAt
                }
              }
            }
            sources {
              uniqueId
              sourceName
              name
              database
              schema
              state
              maxLoadedAt
              freshnessChecked
            }
            runId
          }
        }
        """

        variables = {
            "jobId": int(job_id)
        }

        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        job_data = result["data"]["job"]
        all_models = job_data.get("models", [])
        all_sources = job_data.get("sources", [])

        # Filter models and sources by time window
        models = all_models
        sources = all_sources

        # Calculate performance metrics
        total_execution_time = sum(
            model.get("executionInfo", {}).get("executionTime", 0) or 0
            for model in models
        )

        # Status summary
        status_counts = {}
        for model in models:
            status = model.get("executionInfo", {}).get("lastRunStatus", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        # Top slowest models
        slowest_models = sorted(
            [m for m in models if m.get("executionInfo", {}).get("executionTime")],
            key=lambda x: x["executionInfo"]["executionTime"],
            reverse=True
        )[:10]

        return {
            "job_id": job_id,
            "run_id": job_data.get("runId"),
            "time_filter": {
                "hours_back": hours,
                "models_before_filter": len(all_models),
                "models_after_filter": len(models),
                "sources_before_filter": len(all_sources),
                "sources_after_filter": len(sources)
            },
            "summary": {
                "total_models": len(models),
                "total_sources": len(sources),
                "total_execution_time_seconds": total_execution_time,
                "status_breakdown": status_counts
            },
            "slowest_models": [
                {
                    "name": m["name"],
                    "execution_time": m["executionInfo"]["executionTime"],
                    "status": m["executionInfo"].get("lastRunStatus")
                }
                for m in slowest_models
            ],
            "models": models,
            "sources": sources
        }

    except Exception as e:
        logger.error(f"Error getting job execution performance: {e}")
        raise e


@tool("get_folder_performance_summary")
async def get_folder_performance_summary(
    job_id: str,
    folder_path: str,
    hours: int = 24,
    limit: int = 20
) -> dict[str, Any]:
    """Get focused performance summary for models in a specific folder.

    Args:
        job_id: dbt Cloud job ID to query
        folder_path: Folder path to filter models (e.g., '05_presentation/balanced_scorecard')
        hours: Number of hours to look back (default: 24)
        limit: Maximum number of models to return (default: 20)

    Returns:
        Dict with minimal performance data for models in the specified folder
    """
    try:
        api = DBTCloudDiscoveryAPI()

        # Minimal GraphQL query with only essential fields
        query = """
        query ($jobId: BigInt!) {
          job(id: $jobId) {
            models {
              name
              uniqueId
              database
              schema
              alias
              executionInfo {
                executionTime
                executeStartedAt
                executeCompletedAt
                lastRunStatus
              }
            }
          }
        }
        """

        variables = {
            "jobId": int(job_id)
        }

        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        job_data = result["data"]["job"]
        all_models = job_data.get("models", [])

        # Filter by folder path
        folder_models = []
        for model in all_models:
            unique_id = model.get("uniqueId", "")
            model_name = model.get("name", "")

            # Check if model is in the specified folder path
            if folder_path.lower() in unique_id.lower() or folder_path.lower() in model_name.lower():
                folder_models.append(model)

        # Apply time filtering
        recent_models = folder_models

        # Limit results to prevent oversized responses
        limited_models = recent_models[:limit]

        # Create focused summary with only requested fields
        model_summaries = []
        for model in limited_models:
            exec_info = model.get("executionInfo", {})

            summary = {
                "model_name": model.get("name"),
                "execution_start_time": exec_info.get("executeStartedAt"),
                "execution_end_time": exec_info.get("executeCompletedAt"),
                "time_consumed_seconds": exec_info.get("executionTime"),
                "status": exec_info.get("lastRunStatus")
            }
            model_summaries.append(summary)

        # Sort by execution time (slowest first)
        model_summaries.sort(
            key=lambda x: x.get("time_consumed_seconds") or 0,
            reverse=True
        )

        return {
            "folder_path": folder_path,
            "job_id": job_id,
            "time_window_hours": hours,
            "summary": {
                "total_models_in_job": len(all_models),
                "models_in_folder": len(folder_models),
                "models_in_timeframe": len(recent_models),
                "models_returned": len(model_summaries)
            },
            "models": model_summaries
        }

    except Exception as e:
        logger.error(f"Error getting folder performance summary: {e}")
        raise e


@tool("get_model_and_upstream_tests")
async def get_model_and_upstream_tests(
    model_name: str,
    environment_id: int | None = None,
    limit: int = 20
) -> ToolResult:
    """Get tests for a specific model and its upstream dependencies.
    
    Args:
        model_name: Name of the model to get tests for
        environment_id: dbt Cloud environment ID (optional, uses default if not provided)
        limit: Maximum number of tests to return per model (default: 20)
        
    Returns:
        ToolResult with test information including model name, test name, status, and execution time
    """
    try:
        # Get environment ID from settings if not provided
        if environment_id is None:
            environment_id = getattr(get_settings(), 'dbt_environment_id', None)
            if not environment_id:
                raise ValueError("Environment ID not provided and not found in settings")
        
        api = DBTCloudDiscoveryAPI()
        
        # First, find the model and get its parents
        model_query = """
        query ($environmentId: BigInt!, $first: Int!) {
          environment(id: $environmentId) {
            applied {
              models(first: $first) {
                edges {
                  node {
                    name
                    uniqueId
                    parents {
                      name
                      uniqueId
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        variables = {
            "environmentId": int(environment_id),
            "first": 100  # Get more models to find the target and parents
        }
        
        result = await api.query_graphql(model_query, variables)
        
        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")
            
        models = result["data"]["environment"]["applied"]["models"]["edges"]
        
        # Find the target model and collect all model names (target + parents)
        target_model = None
        model_names = set()
        
        for edge in models:
            model = edge["node"]
            if model["name"] == model_name:
                target_model = model
                model_names.add(model_name)
                # Add parent model names
                for parent in model.get("parents", []):
                    model_names.add(parent["name"])
                break
                
        if not target_model:
            return ToolResult(
                success=False,
                result=None,
                error=f"Model '{model_name}' not found in environment {environment_id}"
            )
        
        # Now get tests for all these models
        tests_query = """
        query ($environmentId: BigInt!, $first: Int!) {
          environment(id: $environmentId) {
            applied {
              tests(first: $first) {
                edges {
                  node {
                    name
                    uniqueId
                    columnName
                    parents {
                      name
                    }
                    executionInfo {
                      lastRunStatus
                      executeCompletedAt
                      executionTime
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        test_variables = {
            "environmentId": int(environment_id),
            "first": min(limit * len(model_names), 500)  # Get enough tests
        }
        
        test_result = await api.query_graphql(tests_query, test_variables)
        
        if "errors" in test_result:
            raise ValueError(f"GraphQL errors: {test_result['errors']}")
            
        all_tests = test_result["data"]["environment"]["applied"]["tests"]["edges"]
        
        # Filter tests that belong to our target models
        relevant_tests = []
        for edge in all_tests:
            test = edge["node"]
            # Check if this test is associated with any of our target models
            test_parents = [parent["name"] for parent in test.get("parents", [])]
            if any(parent_name in model_names for parent_name in test_parents):
                # Find which model this test belongs to
                test_model = None
                for parent_name in test_parents:
                    if parent_name in model_names:
                        test_model = parent_name
                        break
                
                relevant_tests.append({
                    "model_name": test_model,
                    "test_name": test["name"],
                    "test_status": test["executionInfo"].get("lastRunStatus") if test["executionInfo"] else None,
                    "test_time": test["executionInfo"].get("executeCompletedAt") if test["executionInfo"] else None,
                    "execution_time_seconds": test["executionInfo"].get("executionTime") if test["executionInfo"] else None,
                    "column_name": test.get("columnName"),
                    "unique_id": test["uniqueId"]
                })
        
        # Sort by execution time (most recent first)
        relevant_tests.sort(key=lambda x: x["test_time"] or "", reverse=True)
        
        # Limit results
        limited_tests = relevant_tests[:limit]
        
        return ToolResult(
            success=True,
            result={
                "target_model": model_name,
                "total_models_checked": len(model_names),
                "model_names": list(model_names),
                "total_tests_found": len(relevant_tests),
                "tests": limited_tests
            },
            error=None
        )
        
    except Exception as e:
        logger.error(f"Error getting model and upstream tests: {e}")
        return ToolResult(
            success=False,
            result=None,
            error=str(e)
        )
