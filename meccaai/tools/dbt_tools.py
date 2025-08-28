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


# dbt Cloud Discovery API Tools

logger = get_logger(__name__)


class DBTCloudDiscoveryAPI:
    """dbt Cloud Discovery API client."""

    def __init__(self):
        # Use the API base from environment variables (required)
        api_base = getattr(settings, "api_base", None)

        if not api_base:
            raise ValueError("API_BASE environment variable must be set")

        # Convert the dbt host URL to the correct metadata API endpoint
        if "au.dbt.com" in api_base:
            # Australian dbt Cloud uses the Australian metadata endpoint
            self.base_url = "https://metadata.au.dbt.com/graphql"
        elif "cloud.getdbt.com" in api_base or "getdbt.com" in api_base:
            # US/Global dbt Cloud
            self.base_url = "https://metadata.cloud.getdbt.com/graphql"
        else:
            # For any other API base, try to construct the metadata URL
            # Replace 'dbt.com' with 'dbt.com' and add metadata prefix
            base_domain = api_base.replace("https://", "").replace("http://", "")
            if "au.dbt.com" in base_domain:
                self.base_url = "https://metadata.au.dbt.com/graphql"
            else:
                self.base_url = f"https://metadata.{base_domain}/graphql"

        self.token = getattr(settings, "dbt_cloud_token", None)
        self.environment_id = getattr(settings, "dbt_environment_id", None)

    async def query_graphql(
        self, query: str, variables: dict | None = None
    ) -> dict[str, Any]:
        """Execute a GraphQL query against dbt Cloud Discovery API."""
        if not self.token:
            raise ValueError("DBT_CLOUD_TOKEN environment variable not set")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        timeout = httpx.Timeout(60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(self.base_url, json=payload, headers=headers)

            logger.info(f"dbt Discovery API response status: {response.status_code}")

            # Log response details for debugging
            if response.status_code != 200:
                logger.error(f"Response status: {response.status_code}")
                logger.error(f"Response headers: {response.headers}")
                logger.error(f"Response content: {response.text}")

            response.raise_for_status()

            return response.json()


# Category 1: Job ID Based Tools


@tool("list_jobs")
async def list_jobs(job_id: str) -> dict[str, Any]:
    """List job information including exposures, models, seeds, snapshots, sources, and tests.

    Args:
        job_id: dbt Cloud job ID to query

    Returns:
        Dict containing job information with all resources
    """
    try:
        api = DBTCloudDiscoveryAPI()

        query = """
        query ($jobId: BigInt!) {
          job(id: $jobId) {
            id
            runId
            exposures {
              name
              uniqueId
            }
            models {
              name
              uniqueId
            }
            seeds {
              name
              uniqueId  
            }
            snapshots {
              name
              uniqueId
            }
            sources {
              name
              uniqueId
            }
            tests {
              uniqueId
            }
          }
        }
        """

        variables = {"jobId": int(job_id)}
        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        return result["data"]["job"]

    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise e


@tool("list_dbt_tests")
async def list_dbt_tests(job_id: str, first: int = 500) -> dict[str, Any]:
    """List all tests for a specific job.

    Args:
        job_id: dbt Cloud job ID to query
        first: Number of tests to return (default: 1000)

    Returns:
        Dict containing test information
    """
    try:
        api = DBTCloudDiscoveryAPI()

        query = """
        query ($jobId: BigInt!, $first: Int!) {
          job(id: $jobId) {
            tests(first: $first) {
              columnName
              compileStartedAt
              dependsOn
              description
              error
              executeCompletedAt
              executeStartedAt
              executionTime
              fail
              jobId
              runId
              state
              status
              tags
              uniqueId
              warn
            }
          }
        }
        """

        variables = {"jobId": int(job_id), "first": first}
        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        return {"job_id": job_id, "tests": result["data"]["job"]["tests"]}

    except Exception as e:
        logger.error(f"Error listing dbt tests: {e}")
        raise e


@tool("list_dbt_test")
async def list_dbt_test(job_id: str, unique_id: str) -> dict[str, Any]:
    """Get detailed information for a specific test.

    Args:
        job_id: dbt Cloud job ID to query
        unique_id: Unique identifier for the test

    Returns:
        Dict containing detailed test information
    """
    try:
        api = DBTCloudDiscoveryAPI()

        query = """
        query ($jobId: BigInt!, $uniqueId: String!) {
          job(id: $jobId) {
            test(uniqueId: $uniqueId) {
              columnName
              compileStartedAt
              dependsOn
              description
              error
              executeCompletedAt
              executeStartedAt
              executionTime
              fail
              jobId
              runId
              state
              status
              tags
              uniqueId
              warn
            }
          }
        }
        """

        variables = {"jobId": int(job_id), "uniqueId": unique_id}
        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        return {"job_id": job_id, "test": result["data"]["job"]["test"]}

    except Exception as e:
        logger.error(f"Error getting dbt test: {e}")
        raise e


@tool("list_dbt_model")
async def list_dbt_model(job_id: str, unique_id: str) -> dict[str, Any]:
    """Get detailed information for a specific model.

    Args:
        job_id: dbt Cloud job ID to query
        unique_id: Unique identifier for the model

    Returns:
        Dict containing detailed model information
    """
    try:
        api = DBTCloudDiscoveryAPI()

        query = """
        query ($jobId: BigInt!, $uniqueId: String!) {
          job(id: $jobId) {
            model(uniqueId: $uniqueId) {
              access
              catalog
              columns
              compiledSql
              compileCompletedAt
              compileStartedAt
              database
              dependsOn
              description
              error
              executeCompletedAt
              executeStartedAt
              executionTime
              jobId
              materializedType
              name
              rawSql
              runElapsedTime
              runId
              schema
              stats
              status
              tags
              uniqueId
            }
          }
        }
        """

        variables = {"jobId": int(job_id), "uniqueId": unique_id}
        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        return {"job_id": job_id, "model": result["data"]["job"]["model"]}

    except Exception as e:
        logger.error(f"Error getting dbt model: {e}")
        raise e


@tool("list_dbt_models")
async def list_dbt_models(
    job_id: str, schema: str | None = None, first: int = 500
) -> dict[str, Any]:
    """List all models for a specific job with optional schema filter.

    Args:
        job_id: dbt Cloud job ID to query
        schema: Optional schema filter
        first: Number of models to return (default: 1000)

    Returns:
        Dict containing model information
    """
    try:
        api = DBTCloudDiscoveryAPI()

        # Build filter clause if schema is provided
        filter_clause = f', filter: {{schema: "{schema}"}}' if schema else ""

        query = f"""
        query ($jobId: BigInt!, $first: Int!) {{
          job(id: $jobId) {{
            models(first: $first{filter_clause}) {{
              access
              childrenL1
              columns
              compileCompletedAt
              compileStartedAt
              dependsOn
              description
              error
              executeCompletedAt
              executeStartedAt
              executionTime
              invocationId
              jobId
              name
              owner
              parentsModels
              parentsSources
              runElapsedTime
              runId
              runResults
              schema
              tags
              uniqueId
              tests
              status
              stats
            }}
          }}
        }}
        """

        variables = {"jobId": int(job_id), "first": first}
        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        return {
            "job_id": job_id,
            "schema_filter": schema,
            "models": result["data"]["job"]["models"],
        }

    except Exception as e:
        logger.error(f"Error listing dbt models: {e}")
        raise e


# Category 2: Environment Level Tools (Latest State)


@tool("model_execution_time")
async def model_execution_time(
    environment_id: str | None = None, first: int = 100
) -> dict[str, Any]:
    """Get execution time for each model in the environment.

    Args:
        environment_id: dbt Cloud environment ID (optional)
        first: Number of models to return (default: 1000)

    Returns:
        Dict containing model execution times
    """
    try:
        api = DBTCloudDiscoveryAPI()
        env_id = environment_id or api.environment_id

        if not env_id:
            raise ValueError("Environment ID must be provided or set in settings")

        query = """
        query ($environmentId: BigInt!, $first: Int!) {
          environment(id: $environmentId) {
            applied {
              models(first: $first) {
                edges {
                  node {
                    name
                    uniqueId
                    executionInfo {
                      executionTime
                      executeStartedAt
                      executeCompletedAt
                      lastRunStatus
                    }
                  }
                }
              }
            }
          }
        }
        """

        variables = {"environmentId": int(env_id), "first": min(first, 500)}
        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        models = [
            edge["node"]
            for edge in result["data"]["environment"]["applied"]["models"]["edges"]
        ]

        return {"environment_id": env_id, "models": models}

    except Exception as e:
        logger.error(f"Error getting model execution time: {e}")
        raise e


@tool("model_status")
async def model_status(
    environment_id: str | None = None, first: int = 100
) -> dict[str, Any]:
    """Get the latest state of each model in the environment.

    Args:
        environment_id: dbt Cloud environment ID (optional)
        first: Number of models to return (default: 1000)

    Returns:
        Dict containing model status information
    """
    try:
        api = DBTCloudDiscoveryAPI()
        env_id = environment_id or api.environment_id

        if not env_id:
            raise ValueError("Environment ID must be provided or set in settings")

        query = """
        query ($environmentId: BigInt!, $first: Int!) {
          environment(id: $environmentId) {
            applied {
              models(first: $first) {
                edges {
                  node {
                    name
                    uniqueId
                    materializedType
                    executionInfo {
                      lastSuccessRunId
                      lastRunStatus
                      lastRunError
                      executeCompletedAt
                    }
                  }
                }
              }
            }
          }
        }
        """

        variables = {"environmentId": int(env_id), "first": min(first, 500)}
        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        models = [
            edge["node"]
            for edge in result["data"]["environment"]["applied"]["models"]["edges"]
        ]

        return {"environment_id": env_id, "models": models}

    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        raise e


@tool("model_lineage")
async def model_lineage(
    environment_id: str | None = None, first: int = 100
) -> dict[str, Any]:
    """Get the full data lineage at model level.

    Args:
        environment_id: dbt Cloud environment ID (optional)
        first: Number of models to return (default: 1000)

    Returns:
        Dict containing model lineage information
    """
    try:
        api = DBTCloudDiscoveryAPI()
        env_id = environment_id or api.environment_id

        if not env_id:
            raise ValueError("Environment ID must be provided or set in settings")

        query = """
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
                      resourceType
                    }
                    children {
                      name
                      uniqueId
                      resourceType
                    }
                  }
                }
              }
            }
          }
        }
        """

        variables = {"environmentId": int(env_id), "first": min(first, 500)}
        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        models = [
            edge["node"]
            for edge in result["data"]["environment"]["applied"]["models"]["edges"]
        ]

        return {"environment_id": env_id, "models": models}

    except Exception as e:
        logger.error(f"Error getting model lineage: {e}")
        raise e


@tool("failed_models_and_tests")
async def failed_models_and_tests(
    environment_id: str | None = None, first: int = 500
) -> dict[str, Any]:
    """Get models and tests that failed to run.

    Args:
        environment_id: dbt Cloud environment ID (optional)
        first: Number of items to return (default: 1000)

    Returns:
        Dict containing failed models and tests
    """
    try:
        api = DBTCloudDiscoveryAPI()
        env_id = environment_id or api.environment_id

        if not env_id:
            raise ValueError("Environment ID must be provided or set in settings")

        query = """
        query ($environmentId: BigInt!, $first: Int!) {
          environment(id: $environmentId) {
            applied {
              models(first: $first, filter: {lastRunStatus: error}) {
                edges {
                  node {
                    name
                    uniqueId
                    executionInfo {
                      lastRunStatus
                      lastRunError
                      executeCompletedAt
                    }
                  }
                }
              }
              tests(first: $first, filter: {status: "fail"}) {
                edges {
                  node {
                    name
                    uniqueId
                    executionInfo {
                      lastRunStatus
                      lastRunError
                      executeCompletedAt
                    }
                  }
                }
              }
            }
          }
        }
        """

        variables = {"environmentId": int(env_id), "first": min(first, 500)}
        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        failed_models = [
            edge["node"]
            for edge in result["data"]["environment"]["applied"]["models"]["edges"]
        ]
        failed_tests = [
            edge["node"]
            for edge in result["data"]["environment"]["applied"]["tests"]["edges"]
        ]

        return {
            "environment_id": env_id,
            "failed_models": failed_models,
            "failed_tests": failed_tests,
        }

    except Exception as e:
        logger.error(f"Error getting failed models and tests: {e}")
        raise e


@tool("list_test_result")
async def list_test_result(
    environment_id: str | None = None, first: int = 500
) -> dict[str, Any]:
    """Get test coverage and status information.

    Args:
        environment_id: dbt Cloud environment ID (optional)
        first: Number of tests to return (default: 1000)

    Returns:
        Dict containing test coverage and status
    """
    try:
        api = DBTCloudDiscoveryAPI()
        env_id = environment_id or api.environment_id

        if not env_id:
            raise ValueError("Environment ID must be provided or set in settings")

        query = """
        query ($environmentId: BigInt!, $first: Int!) {
          environment(id: $environmentId) {
            applied {
              tests(first: $first) {
                edges {
                  node {
                    uniqueId
                    columnName
                    parents {
                      uniqueId
                    }
                    executionInfo {
                      lastRunStatus
                      lastRunError
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

        variables = {"environmentId": int(env_id), "first": min(first, 500)}
        result = await api.query_graphql(query, variables)

        if "errors" in result:
            raise ValueError(f"GraphQL errors: {result['errors']}")

        tests = [
            edge["node"]
            for edge in result["data"]["environment"]["applied"]["tests"]["edges"]
        ]

        return {"environment_id": env_id, "tests": tests}

    except Exception as e:
        logger.error(f"Error getting test results: {e}")
        raise e
