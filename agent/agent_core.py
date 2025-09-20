from .llm_client import OllamaClient
from .tool_executor import ToolExecutor
import json
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RAGAgent:
    def __init__(self):
        self.llm_client = OllamaClient()
        self.tool_executor = ToolExecutor()
        self.system_prompt = """You are a helpful Federal Register document assistant. You have access to a database of federal documents, regulations, and government publications.

You can help users by:
- Searching for documents by keywords
- Finding recent documents from specific time periods
- Filtering documents by government agency
- Providing statistics about the document database

Always use the appropriate tools to find current, accurate information from the database before responding. When presenting results, summarize the key information clearly and mention the source (Federal Register database).

Be helpful, accurate, and informative in your responses."""
        
        self.max_iterations = 5  # Prevent infinite loops
    
    async def process_query(self, user_query: str, chat_history: List[Dict] = None) -> str:
        """Process user query using agent logic with tool calling"""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add chat history if provided (keep it reasonable)
        if chat_history:
            # Keep only last 6 messages to avoid context overflow
            recent_history = chat_history[-6:] if len(chat_history) > 6 else chat_history
            messages.extend(recent_history)
        
        messages.append({"role": "user", "content": user_query})
        
        iteration = 0
        while iteration < self.max_iterations:
            try:
                # Request LLM response with tools
                response = await self.llm_client.chat_completion(
                    messages=messages,
                    tools=self.tool_executor.get_tool_schemas()
                )
                
                if not response:
                    return "I'm sorry, I'm having trouble connecting to the AI service right now. Please try again."
                
                assistant_message = response.choices[0].message
                
                # Check if LLM wants to use tools
                if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
                    logger.info(f"LLM requested {len(assistant_message.tool_calls)} tool calls")
                    
                    # Add assistant message with tool calls
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message.content,
                        "tool_calls": [tc.model_dump() for tc in assistant_message.tool_calls]
                    })
                    
                    # Execute each tool call
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        try:
                            tool_args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            tool_args = {}
                        
                        # Execute tool
                        tool_result = await self.tool_executor.execute_tool(tool_name, tool_args)
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": tool_result
                        })
                    
                    # Continue to next iteration for final response
                    iteration += 1
                    continue
                
                else:
                    # No tools needed, return direct response
                    final_response = assistant_message.content or "I'm not sure how to help with that query."
                    logger.info("Query processed successfully without tools")
                    return final_response
                    
            except Exception as e:
                logger.error(f"Error in agent processing: {e}")
                return f"I encountered an error while processing your request: {str(e)[:100]}..."
        
        return "I tried to help but ran into some complexity issues. Could you please rephrase your question?"
    
    async def test_agent(self) -> Dict[str, Any]:
        """Test agent functionality"""
        tests = {
            "llm_connection": False,
            "tool_execution": False,
            "full_query": False
        }
        
        try:
            # Test LLM connection
            if await self.llm_client.test_connection():
                tests["llm_connection"] = True
            
            # Test tool execution
            try:
                result = await self.tool_executor.execute_tool("get_document_stats", {})
                if result and not result.startswith("Error"):
                    tests["tool_execution"] = True
            except:
                pass
            
            # Test full query processing
            try:
                response = await self.process_query("Hello, can you help me?")
                if response and len(response) > 0:
                    tests["full_query"] = True
            except:
                pass
                
        except Exception as e:
            logger.error(f"Agent test failed: {e}")
        
        return tests
