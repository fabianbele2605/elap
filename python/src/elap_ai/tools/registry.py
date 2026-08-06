"""Tool Registry for Agent Execution."""

from typing import Any, Callable, Optional
from dataclasses import dataclass


@dataclass
class Tool:
    """Tool definition."""

    name: str
    description: str
    func: Callable
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


class ToolRegistry:
    """Registry for managing agent tools."""

    def __init__(self) -> None:
        """Initialize tool registry."""
        self.tools: dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        func: Callable,
        input_schema: dict[str, Any],
        output_schema: dict[str, Any],
    ) -> None:
        """Register a tool.

        Args:
            name: Tool name
            description: Tool description
            func: Callable tool function
            input_schema: Input parameter schema
            output_schema: Output value schema
        """
        tool = Tool(
            name=name,
            description=description,
            func=func,
            input_schema=input_schema,
            output_schema=output_schema,
        )
        self.tools[name] = tool

    async def execute(self, tool_name: str, **kwargs: Any) -> Any:
        """Execute a tool.

        Args:
            tool_name: Name of tool to execute
            **kwargs: Tool parameters

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")

        tool = self.tools[tool_name]
        result = tool.func(**kwargs)

        # Handle async functions
        if hasattr(result, "__await__"):
            return await result

        return result

    def list_tools(self) -> list[dict[str, Any]]:
        """List all registered tools."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
                "output_schema": tool.output_schema,
            }
            for tool in self.tools.values()
        ]

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool by name."""
        return self.tools.get(name)
