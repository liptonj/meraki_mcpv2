"""
Tools package for Meraki MCP server.

This package contains modules that implement various MCP tools for interacting
with the Meraki Dashboard API. Tools are organized by functional area.
"""

import importlib
import inspect
import logging
import pkgutil
import sys
from typing import Dict, List, Type

from meraki_mcp.tools.base import ToolBase

logger = logging.getLogger(__name__)

# We don't need to import modules explicitly - they'll be discovered dynamically

__all__ = [
    "discover_tool_classes",
]

def discover_tool_classes() -> Dict[str, Type[ToolBase]]:
    """Discover all tool classes in the tools package.
    
    This function dynamically discovers all classes that inherit from ToolBase
    within the tools package. It can be used to automatically load tool classes
    without having to manually import and instantiate each one.
    
    Returns:
        A dictionary mapping tool class names to tool class types
    """
    tool_classes = {}
    
    # Get the package object
    package = sys.modules[__name__]
    
    # Iterate through all modules in the package
    for _, module_name, _ in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
        # Skip the base module to avoid importing the base class itself
        if module_name.endswith('base'):
            continue
            
        # Import the module
        try:
            module = importlib.import_module(module_name)
            
            # Find all classes in the module that inherit from ToolBase
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, ToolBase) and 
                    obj is not ToolBase and 
                    obj.__module__ == module_name):
                    tool_classes[name] = obj
                    logger.debug(f"Discovered tool class: {name}")
        except ImportError as e:
            logger.warning(f"Failed to import module {module_name}: {e}")
    
    logger.info(f"Discovered {len(tool_classes)} tool classes: {', '.join(tool_classes.keys())}")
    return tool_classes
