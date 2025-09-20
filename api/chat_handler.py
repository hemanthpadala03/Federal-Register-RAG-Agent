import asyncio
from typing import Dict, List
from agent.agent_core import RAGAgent
import logging
import time

logger = logging.getLogger(__name__)

class ChatHandler:
    def __init__(self):
        self.agent = RAGAgent()
        self.active_sessions = {}
        self.session_timeouts = {}
        self.max_history_length = 20
        self.session_timeout = 3600  # 1 hour
    
    async def handle_message(self, session_id: str, message: str, history: List[Dict] = None) -> str:
        """Handle individual chat message"""
        try:
            start_time = time.time()
            
            # Clean up expired sessions
            await self._cleanup_expired_sessions()
            
            # Use provided history or get from session
            if history is None:
                history = self.get_session_history(session_id)
            
            # Process query through agent
            response = await self.agent.process_query(message, history)
            
            # Store in session history
            self._update_session_history(session_id, message, response)
            
            processing_time = time.time() - start_time
            logger.info(f"Message processed in {processing_time:.2f} seconds for session {session_id}")
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing message: {e}"
            logger.error(error_msg)
            return "I apologize, but I encountered an error processing your request. Please try again or rephrase your question."
    
    def _update_session_history(self, session_id: str, user_message: str, assistant_response: str):
        """Update session history with new exchange"""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = []
        
        # Add new exchange
        self.active_sessions[session_id].extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_response}
        ])
        
        # Trim history if too long
        if len(self.active_sessions[session_id]) > self.max_history_length:
            self.active_sessions[session_id] = self.active_sessions[session_id][-self.max_history_length:]
        
        # Update timeout
        self.session_timeouts[session_id] = time.time()
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get chat history for session"""
        return self.active_sessions.get(session_id, [])
    
    def clear_session(self, session_id: str):
        """Clear session history"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        if session_id in self.session_timeouts:
            del self.session_timeouts[session_id]
        logger.info(f"Cleared session {session_id}")
    
    async def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, last_activity in self.session_timeouts.items():
            if current_time - last_activity > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.clear_session(session_id)
            logger.info(f"Expired session {session_id} cleaned up")
    
    def get_active_sessions_count(self) -> int:
        """Get number of active sessions"""
        return len(self.active_sessions)
    
    async def test_handler(self) -> bool:
        """Test chat handler functionality"""
        try:
            test_session = "test_session"
            response = await self.handle_message(test_session, "Hello, test message")
            self.clear_session(test_session)
            return len(response) > 0
        except Exception as e:
            logger.error(f"Chat handler test failed: {e}")
            return False
