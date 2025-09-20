from openai import AsyncOpenAI
from typing import List, Dict, Any
import json
import logging
from config.settings import OLLAMA_CONFIG

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, model: str = None):
        self.client = AsyncOpenAI(
            base_url=OLLAMA_CONFIG['base_url'],
            api_key="ollama"  # Required but unused for local Ollama
        )
        self.model = model or OLLAMA_CONFIG['model']
        logger.info(f"Initialized Ollama client with model: {self.model}")
    
    async def chat_completion(self, messages: List[Dict], tools: List[Dict] = None) -> Dict:
        """Send chat completion request WITHOUT tools support"""
        try:
            logger.debug(f"Sending request to {self.model} with {len(messages)} messages")
            
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            # Remove tools and tool_choice to disable tool calling
            # Commented out:
            # if tools:
            #     request_params["tools"] = tools
            #     request_params["tool_choice"] = "auto"
            
            response = await self.client.chat.completions.create(**request_params)
            
            logger.debug("Successfully received response from LLM")
            return response
            
        except Exception as e:
            logger.error(f"LLM client error: {e}")
            return None
    
    async def simple_completion(self, prompt: str) -> str:
        """Simple completion without tools"""
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages)
        
        if response and response.choices:
            return response.choices[0].message.content
        return "Sorry, I couldn't process that request."
    
    async def test_connection(self) -> bool:
        """Test if connection to Ollama is working"""
        try:
            response = await self.simple_completion("Hello")
            return response is not None and len(response) > 0
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
