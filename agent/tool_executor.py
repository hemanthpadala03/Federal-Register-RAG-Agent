from tools.sql_tools import SQLTools
import json
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ToolExecutor:
    def __init__(self):
        self.available_tools = {
            "search_documents": SQLTools.search_documents,
            "get_recent_documents": SQLTools.get_recent_documents,
            "filter_by_agency": SQLTools.filter_by_agency,
            "get_document_stats": SQLTools.get_document_stats
        }
        
        self.tool_schemas = [
            {
                "type": "function",
                "function": {
                    "name": "search_documents",
                    "description": "Search federal documents by keyword in title or abstract",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search keyword or phrase"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "get_recent_documents",
                    "description": "Get recent federal documents from the last N days",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "days": {
                                "type": "integer",
                                "description": "Number of days back to search (default: 7)",
                                "default": 7
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 20)",
                                "default": 20
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "filter_by_agency",
                    "description": "Filter federal documents by specific agency name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "agency": {
                                "type": "string",
                                "description": "The agency name to filter by (e.g., 'Environmental Protection Agency', 'FDA')"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 15)",
                                "default": 15
                            }
                        },
                        "required": ["agency"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_document_stats",
                    "description": "Get statistics about the document database including total count, document types, and recent activity",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool with given arguments"""
        if tool_name not in self.available_tools:
            logger.error(f"Tool {tool_name} not found")
            return f"Tool {tool_name} not found"
        
        try:
            logger.info(f"Executing tool: {tool_name} with args: {arguments}")
            tool_function = self.available_tools[tool_name]
            result = await tool_function(**arguments)
            logger.info(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            error_msg = f"Error executing tool {tool_name}: {e}"
            logger.error(error_msg)
            return error_msg
    
    def get_tool_schemas(self) -> List[Dict]:
        """Return tool schemas for LLM"""
        return self.tool_schemas
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.available_tools.keys())
