from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
import os

from agent.agent_core import RAGAgent
from database.connection import db
from data_pipeline.scheduler import DataPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Federal Register RAG Agent System",
    description="AI-powered search and analysis of Federal Register documents",
    version="1.0.0"
)

# Mount static files for UI
ui_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui")
if os.path.exists(ui_path):
    app.mount("/static", StaticFiles(directory=ui_path), name="static")

class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

class PipelineRequest(BaseModel):
    days_back: Optional[int] = 1

# Global instances
agent = None
pipeline = None

@app.on_event("startup")
async def startup_event():
    """Initialize database and agent on startup"""
    global agent, pipeline
    
    try:
        logger.info("Starting RAG Agent System...")
        
        # Initialize database
        await db.create_pool()
        logger.info("Database connection pool created")
        
        # Initialize agent
        agent = RAGAgent()
        logger.info("RAG Agent initialized")
        
        # Initialize pipeline
        pipeline = DataPipeline()
        logger.info("Data pipeline initialized")
        
        # Test agent functionality
        test_results = await agent.test_agent()
        logger.info(f"Agent test results: {test_results}")
        
        logger.info("RAG Agent System startup complete!")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        await db.close_pool()
        logger.info("RAG Agent System shutdown complete")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

@app.get("/", response_class=HTMLResponse)
async def get_chat_ui():
    """Serve the chat UI"""
    ui_file = os.path.join(ui_path, "index.html")
    if os.path.exists(ui_file):
        return FileResponse(ui_file)
    else:
        return HTMLResponse("""
        <html>
            <head><title>RAG Agent</title></head>
            <body>
                <h1>Federal Register RAG Agent</h1>
                <p>UI file not found. Please ensure ui/index.html exists.</p>
                <p>API is available at <a href="/docs">/docs</a></p>
            </body>
        </html>
        """)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Handle chat requests"""
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        logger.info(f"Processing chat request: {request.message[:100]}...")
        
        response = await agent.process_query(
            user_query=request.message,
            chat_history=request.chat_history
        )
        
        logger.info("Chat request processed successfully")
        return ChatResponse(response=response)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)[:200]}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        async with db.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1")
                await cursor.fetchone()
        
        # Test agent
        agent_status = "working" if agent else "not_initialized"
        
        return {
            "status": "healthy",
            "message": "RAG Agent System is running",
            "database": "connected",
            "agent": agent_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")

@app.post("/pipeline/run")
async def run_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    """Run data pipeline"""
    try:
        if not pipeline:
            raise HTTPException(status_code=500, detail="Pipeline not initialized")
        
        # Run pipeline in background
        background_tasks.add_task(pipeline.run_daily_update, request.days_back)
        
        return {
            "status": "started",
            "message": f"Pipeline started for last {request.days_back} days",
            "note": "Check logs for progress"
        }
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")

@app.get("/pipeline/status")
async def pipeline_status():
    """Get pipeline status from logs"""
    try:
        async with db.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT run_date, records_processed, status, error_message, created_at
                    FROM pipeline_logs 
                    ORDER BY created_at DESC 
                    LIMIT 10
                """)
                results = await cursor.fetchall()
                
                logs = []
                for row in results:
                    logs.append({
                        "run_date": str(row[0]),
                        "records_processed": row[1],
                        "status": row[2],
                        "error_message": row[3],
                        "created_at": str(row[4])
                    })
                
                return {"pipeline_logs": logs}
                
    except Exception as e:
        logger.error(f"Pipeline status error: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline status error: {e}")

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        # Get document stats through agent
        stats_result = await agent.tool_executor.execute_tool("get_document_stats", {})
        
        return {
            "system": "RAG Agent System",
            "status": "running",
            "document_stats": stats_result
        }
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Stats error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
