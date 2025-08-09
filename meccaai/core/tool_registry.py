"""Tool registry for managing and discovering tools."""

import importlib
import pkgutil

from meccaai.core.logging import get_logger
from meccaai.core.types import Tool

logger = get_logger(__name__)


class ToolRegistryImpl:
    """Implementation of the tool registry."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())

    def unregister(self, name: str) -> None:
        """Unregister a tool by name."""
        if name in self._tools:
            del self._tools[name]
            logger.info(f"Unregistered tool: {name}")

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
        logger.info("Cleared all registered tools")


def discover_tools_in_module(module_name: str, registry: ToolRegistryImpl) -> None:
    """Discover and register tools in a Python module."""
    try:
        module = importlib.import_module(module_name)

        # Walk through the module and its submodules
        if hasattr(module, "__path__"):
            for _, name, _ in pkgutil.walk_packages(
                module.__path__, module.__name__ + "."
            ):
                try:
                    submodule = importlib.import_module(name)
                    _register_tools_from_module(submodule, registry)
                except Exception as e:
                    logger.warning(f"Failed to load submodule {name}: {e}")
        else:
            _register_tools_from_module(module, registry)

    except ImportError as e:
        logger.warning(f"Failed to import module {module_name}: {e}")


def _register_tools_from_module(module, registry: ToolRegistryImpl) -> None:
    """Register tools found in a module."""
    for attr_name in dir(module):
        attr = getattr(module, attr_name)

        # Check if it's a tool (implements Tool protocol)
        if hasattr(attr, "name") and hasattr(attr, "call") and callable(attr.call):
            try:
                registry.register(attr)
            except Exception as e:
                logger.warning(f"Failed to register tool {attr_name}: {e}")


# Global registry instance
registry = ToolRegistryImpl()


def get_registry() -> ToolRegistryImpl:
    """Get the global tool registry."""
    return registry
