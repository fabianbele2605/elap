"""Tool registry for agent execution."""

from typing import Optional, Any, Callable
from dataclasses import dataclass


@dataclass
class Tool:
    """Definition of an executable tool."""

    name: str
    description: str
    parameters: dict[str, Any]  # OpenAI schema
    func: Callable


class ToolRegistry:
    """Registry of available tools for agents."""

    def __init__(self):
        """Initialize tool registry."""
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, parameters: dict, func: Callable) -> None:
        """
        Register a tool.

        Args:
            name: Tool name
            description: Human description
            parameters: JSON schema for parameters
            func: Callable function
        """
        self._tools[name] = Tool(
            name=name,
            description=description,
            parameters=parameters,
            func=func,
        )

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[dict]:
        """
        List all registered tools in OpenAI format.

        Returns:
            List of tool definitions
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
            }
            for tool in self._tools.values()
        ]

    def execute_tool(self, name: str, **kwargs) -> Any:
        """
        Execute a tool.

        Args:
            name: Tool name
            **kwargs: Tool arguments

        Returns:
            Tool result
        """
        tool = self.get_tool(name)
        if tool is None:
            raise ValueError(f"Tool not found: {name}")

        return tool.func(**kwargs)


# Global registry
_global_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Get global tool registry."""
    return _global_registry


def register_document_tools(registry: ToolRegistry) -> None:
    """Register all document-related tools."""
    from .documents.readers import DocumentReader
    from .documents.writers import DocumentGenerator
    from .documents.charts import ChartGenerator

    # Document reading tools
    registry.register(
        name="read_pdf",
        description="Read and extract text from PDF files",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to PDF file"
                }
            },
            "required": ["file_path"],
        },
        func=DocumentReader.read_pdf,
    )

    registry.register(
        name="read_excel",
        description="Read Excel spreadsheet",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to Excel file"
                }
            },
            "required": ["file_path"],
        },
        func=DocumentReader.read_excel,
    )

    registry.register(
        name="read_word",
        description="Read Word document (.docx)",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to Word document"
                }
            },
            "required": ["file_path"],
        },
        func=DocumentReader.read_word,
    )

    # Document generation tools
    registry.register(
        name="generate_pdf_report",
        description="Generate professional PDF report",
        parameters={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Report title"
                },
                "company_name": {
                    "type": "string",
                    "description": "Company name for header"
                },
                "sections": {
                    "type": "array",
                    "description": "Report sections",
                }
            },
            "required": ["title", "sections"],
        },
        func=DocumentGenerator.generate_pdf_report,
    )

    registry.register(
        name="generate_excel_report",
        description="Generate Excel workbook with data",
        parameters={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Data to include"
                },
                "title": {
                    "type": "string",
                    "description": "Workbook title"
                }
            },
            "required": ["data"],
        },
        func=DocumentGenerator.generate_excel_report,
    )

    # Chart tools
    registry.register(
        name="bar_chart",
        description="Generate bar chart",
        parameters={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Data for chart"
                },
                "title": {
                    "type": "string",
                    "description": "Chart title"
                }
            },
            "required": ["data", "title"],
        },
        func=ChartGenerator.bar_chart,
    )
