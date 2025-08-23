"""dbt (data build tool) integration tools via MCP.

This module provides ONLY the tools that actually exist in the dbt-mcp server.
All tools connect to the actual dbt-mcp server for real dbt operations.
"""

from meccaai.core.mcp_tool_base import mcp_tool
from meccaai.core.tool_base import tool
from meccaai.core.logging import get_logger
from meccaai.core.config import settings
from meccaai.prompts.loader import get_tool_description
import httpx
import json
from typing import Dict, Any, List, Optional

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
        self.base_url = "https://metadata.cloud.getdbt.com/graphql"
        self.token = getattr(settings, 'dbt_cloud_token', None)
        self.environment_id = getattr(settings, 'dbt_environment_id', None)
    
    async def query_graphql(self, query: str, variables: dict = None) -> Dict[str, Any]:
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
            response.raise_for_status()
            
            return response.json()


@tool("list_dbt_test_info")
async def list_dbt_test_info(environment_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    """Get detailed information about dbt tests including status and execution details.
    
    Args:
        environment_id: dbt Cloud environment ID (optional, uses default from config)
        limit: Maximum number of tests to retrieve (default: 50, max: 500)
    
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
                    description
                    parents {
                      name
                      resourceType
                    }
                    executionInfo {
                      lastRunId
                      lastRunStatus
                      lastRunError
                      executeCompletedAt
                      executeStartedAt
                      executionTime
                    }
                    tags {
                      value
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
            "first": min(limit, 500)  # Cap at API limit
        }
        
        result = await api.query_graphql(query, variables)
        
        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")
        
        tests_data = result["data"]["environment"]["applied"]["tests"]
        tests = [edge["node"] for edge in tests_data["edges"]]
        
        return {
            "total_tests": len(tests),
            "tests": tests,
            "has_more": tests_data["pageInfo"]["hasNextPage"],
            "environment_id": env_id
        }
        
    except Exception as e:
        logger.error(f"Error getting dbt test info: {e}")
        raise e


@tool("list_dbt_tests")
async def list_dbt_tests(environment_id: Optional[str] = None, status_filter: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    """List dbt tests with optional filtering by status.
    
    Args:
        environment_id: dbt Cloud environment ID (optional, uses default from config)
        status_filter: Filter tests by status ('pass', 'fail', 'error', 'warn') 
        limit: Maximum number of tests to retrieve (default: 50, max: 500)
    
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
                    }}
                    parents {{
                      name
                      resourceType
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
            "first": min(limit, 500)
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
async def list_job_runs(job_id: str, run_id: Optional[str] = None) -> Dict[str, Any]:
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
              status
              executionTime
              executeStartedAt
              executeCompletedAt
              tests {{
                name
                uniqueId
                status
                columnName
              }}
            }}
            sources {{
              uniqueId
              sourceName
              state
              maxLoadedAt
              freshnessChecked
            }}
            runId
            accountId
            jobId
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
            "account_id": job_data.get("accountId"),
            "models": job_data.get("models", []),
            "sources": job_data.get("sources", []),
            "total_models": len(job_data.get("models", [])),
            "total_sources": len(job_data.get("sources", []))
        }
        
    except Exception as e:
        logger.error(f"Error getting job runs: {e}")
        raise e


@tool("list_model_execution_time")
async def list_model_execution_time(environment_id: Optional[str] = None, limit: int = 50, sort_by_time: bool = True) -> Dict[str, Any]:
    """Get model execution times and performance information.
    
    Args:
        environment_id: dbt Cloud environment ID (optional, uses default from config)
        limit: Maximum number of models to retrieve (default: 50, max: 500)
        sort_by_time: Whether to sort results by execution time (default: True)
    
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
                    stats {
                      label
                      value
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
            "first": min(limit, 500)
        }
        
        result = await api.query_graphql(query, variables)
        
        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")
        
        models_data = result["data"]["environment"]["applied"]["models"]
        models = [edge["node"] for edge in models_data["edges"]]
        
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
            "sorted_by_time": sort_by_time
        }
        
    except Exception as e:
        logger.error(f"Error getting model execution times: {e}")
        raise e
