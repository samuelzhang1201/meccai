"""Export tools for data analysis and reporting."""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union

from meccaai.core.logging import get_logger
from meccaai.core.tool_base import tool

logger = get_logger(__name__)


@tool("export_tableau_users_to_csv")
async def export_tableau_users_to_csv(
    filename: str = "tableau_users",
    include_timestamp: bool = True,
    output_dir: str = "exports"
) -> Dict[str, Any]:
    """Export Tableau users directly to CSV by calling the tableau API.
    
    Args:
        filename: Custom filename for the export
        include_timestamp: Whether to include timestamp in filename
        output_dir: Directory to save the file
    
    Returns:
        Dict containing export details including file path and record count
    """
    try:
        # Import here to avoid circular imports
        from meccaai.core.tool_registry import get_registry
        
        # Get the tableau users tool directly
        registry = get_registry()
        tableau_tool = None
        
        for tool in registry.list_tools():
            if tool.name == 'get_users_on_site':
                tableau_tool = tool
                break
        
        if not tableau_tool:
            raise ValueError("Tableau users tool not found")
        
        # Call the tool directly to get structured data
        result = await tableau_tool.call()
        
        if not result.success:
            raise ValueError(f"Failed to get tableau users: {result.error}")
        
        # Use the structured data directly
        data = result.result
        
        if not data or not isinstance(data, dict):
            raise ValueError("No valid user data received from Tableau")
        
        # Extract users from the result
        users = data.get('users', [])
        if not users:
            return {
                "success": False,
                "message": "No users found in Tableau data",
                "file_path": None,
                "record_count": 0
            }
        
        # Call the generic export function with the actual data
        return await _export_data_to_csv(
            data=users,
            filename=filename,
            include_timestamp=include_timestamp,
            output_dir=output_dir,
            data_type="tableau_users"
        )
        
    except Exception as e:
        logger.error(f"Error exporting Tableau users to CSV: {e}")
        raise e


@tool("export_result_to_csv") 
async def export_result_to_csv(
    data: Union[str, Dict[str, Any], List[Dict[str, Any]]],
    filename: str = "",
    include_timestamp: bool = True,
    output_dir: str = "exports"
) -> Dict[str, Any]:
    """Export data results to a CSV file.
    
    Args:
        data: The data to export. Can be JSON string, dict, or list of dicts
        filename: Custom filename (optional, will auto-generate if not provided)
        include_timestamp: Whether to include timestamp in filename
        output_dir: Directory to save the file (relative to current working directory)
    
    Returns:
        Dict containing export details including file path and record count
    """
    try:
        # Parse data if it's a JSON string
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                # If not valid JSON, treat as plain text
                data = {"content": data}
        
        # Ensure we have a list of dictionaries
        if isinstance(data, dict):
            # Check if it's a response with nested data
            if "users" in data:
                records = data["users"]
                data_type = "users"
            elif "groups" in data:
                records = data["groups"] 
                data_type = "groups"
            elif "tokens" in data:
                records = data["tokens"]
                data_type = "tokens"
            elif "models" in data:
                records = data["models"]
                data_type = "models"
            elif "metrics" in data:
                records = data["metrics"]
                data_type = "metrics"
            else:
                # Convert single dict to list
                records = [data]
                data_type = "data"
        elif isinstance(data, list):
            records = data
            data_type = "data"
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
        
        if not records:
            return {
                "success": False,
                "message": "No data to export",
                "file_path": None,
                "record_count": 0
            }
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
            filename = f"{data_type}_export_{timestamp}.csv" if timestamp else f"{data_type}_export.csv"
        elif include_timestamp and not filename.endswith(".csv"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}.csv"
        elif not filename.endswith(".csv"):
            filename = f"{filename}.csv"
        
        file_path = output_path / filename
        
        # Flatten nested dictionaries for CSV export
        flattened_records = []
        for record in records:
            if isinstance(record, dict):
                flattened = _flatten_dict(record)
                flattened_records.append(flattened)
            else:
                flattened_records.append({"value": str(record)})
        
        # Get all unique keys for CSV headers
        all_keys = set()
        for record in flattened_records:
            all_keys.update(record.keys())
        
        # Sort keys for consistent column order
        sorted_keys = sorted(all_keys)
        
        # Write to CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted_keys)
            writer.writeheader()
            writer.writerows(flattened_records)
        
        logger.info(f"Exported {len(flattened_records)} records to {file_path}")
        
        return {
            "success": True,
            "message": f"Successfully exported {len(flattened_records)} records",
            "file_path": str(file_path.absolute()),
            "record_count": len(flattened_records),
            "columns": sorted_keys,
            "data_type": data_type
        }
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        raise e


def _flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """Flatten a nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert lists to string representation
            items.append((new_key, '; '.join(str(item) for item in v)))
        else:
            items.append((new_key, v))
    return dict(items)


async def _export_data_to_csv(
    data: Union[List[Dict[str, Any]], Dict[str, Any]],
    filename: str,
    include_timestamp: bool,
    output_dir: str,
    data_type: str
) -> Dict[str, Any]:
    """Helper function to export data to CSV."""
    # Ensure we have a list of dictionaries
    if isinstance(data, dict):
        records = [data]
    elif isinstance(data, list):
        records = data
    else:
        raise ValueError(f"Unsupported data type: {type(data)}")
    
    if not records:
        return {
            "success": False,
            "message": "No data to export",
            "file_path": None,
            "record_count": 0
        }
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        filename = f"{data_type}_export_{timestamp}.csv" if timestamp else f"{data_type}_export.csv"
    elif include_timestamp and not filename.endswith(".csv"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename}_{timestamp}.csv"
    elif not filename.endswith(".csv"):
        filename = f"{filename}.csv"
    
    file_path = output_path / filename
    
    # Flatten nested dictionaries for CSV export
    flattened_records = []
    for record in records:
        if isinstance(record, dict):
            flattened = _flatten_dict(record)
            flattened_records.append(flattened)
        else:
            flattened_records.append({"value": str(record)})
    
    # Get all unique keys for CSV headers
    all_keys = set()
    for record in flattened_records:
        all_keys.update(record.keys())
    
    # Sort keys for consistent column order
    sorted_keys = sorted(all_keys)
    
    # Write to CSV
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted_keys)
        writer.writeheader()
        writer.writerows(flattened_records)
    
    logger.info(f"Exported {len(flattened_records)} records to {file_path}")
    
    return {
        "success": True,
        "message": f"Successfully exported {len(flattened_records)} records",
        "file_path": str(file_path.absolute()),
        "record_count": len(flattened_records),
        "columns": sorted_keys,
        "data_type": data_type
    }


@tool("list_export_files")
async def list_export_files(output_dir: str = "exports") -> Dict[str, Any]:
    """List all exported CSV files in the output directory.
    
    Args:
        output_dir: Directory to search for export files
        
    Returns:
        Dict containing list of export files with details
    """
    try:
        output_path = Path(output_dir)
        
        if not output_path.exists():
            return {
                "success": True,
                "message": "Export directory does not exist",
                "files": [],
                "total_files": 0
            }
        
        # Find all CSV files
        csv_files = list(output_path.glob("*.csv"))
        
        file_details = []
        for file_path in csv_files:
            stat = file_path.stat()
            file_details.append({
                "filename": file_path.name,
                "full_path": str(file_path.absolute()),
                "size_bytes": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
        
        # Sort by modification time (newest first)
        file_details.sort(key=lambda x: x["modified"], reverse=True)
        
        return {
            "success": True,
            "message": f"Found {len(file_details)} export files",
            "files": file_details,
            "total_files": len(file_details),
            "directory": str(output_path.absolute())
        }
        
    except Exception as e:
        logger.error(f"Error listing export files: {e}")
        raise e


@tool("delete_export_file")
async def delete_export_file(filename: str, output_dir: str = "exports") -> Dict[str, Any]:
    """Delete a specific export file.
    
    Args:
        filename: Name of the file to delete
        output_dir: Directory containing the export files
        
    Returns:
        Dict containing deletion status
    """
    try:
        output_path = Path(output_dir)
        file_path = output_path / filename
        
        if not file_path.exists():
            return {
                "success": False,
                "message": f"File '{filename}' not found in {output_dir}",
                "deleted": False
            }
        
        file_path.unlink()  # Delete the file
        
        logger.info(f"Deleted export file: {file_path}")
        
        return {
            "success": True,
            "message": f"Successfully deleted '{filename}'",
            "deleted": True,
            "file_path": str(file_path.absolute())
        }
        
    except Exception as e:
        logger.error(f"Error deleting export file: {e}")
        raise e