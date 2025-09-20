import asyncio
import uvicorn
import sys
import logging
from datetime import datetime, timedelta

from data_pipeline.scheduler import DataPipeline
from database.connection import db
from api.main import app

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def run_data_pipeline(days_back=7):
    """Run data pipeline manually"""
    logger.info(f"Starting data pipeline for last {days_back} days")
    
    try:
        await db.create_pool()
        pipeline = DataPipeline()
        await pipeline.run_daily_update(days_back)
        logger.info("Data pipeline completed successfully")
    except Exception as e:
        logger.error(f"Data pipeline failed: {e}")
        return False
    finally:
        await db.close_pool()
    
    return True

async def run_historical_pipeline(start_date, end_date):
    """Run historical data pipeline"""
    logger.info(f"Starting historical pipeline from {start_date} to {end_date}")
    
    try:
        await db.create_pool()
        pipeline = DataPipeline()
        await pipeline.run_historical_update(start_date, end_date)
        logger.info("Historical pipeline completed successfully")
    except Exception as e:
        logger.error(f"Historical pipeline failed: {e}")
        return False
    finally:
        await db.close_pool()
    
    return True

def run_api_server():
    """Run the FastAPI server"""
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        "api.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )

def print_usage():
    """Print usage instructions"""
    print("""
RAG Agent System - Usage Instructions

Commands:
  python run.py                           - Start the API server
  python run.py server                    - Start the API server
  python run.py pipeline                  - Run daily data pipeline (last 1 day)
  python run.py pipeline --days 7         - Run pipeline for last 7 days
  python run.py historical YYYY-MM-DD YYYY-MM-DD - Run historical pipeline
  python run.py help                      - Show this help

Examples:
  python run.py pipeline --days 30        - Get last 30 days of data
  python run.py historical 2025-01-01 2025-01-31 - Get January 2025 data
    """)

if __name__ == "__main__":
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == "server"):
        # Run API server
        run_api_server()
        
    elif sys.argv[1] == "pipeline":
        # Run data pipeline
        days_back = 1
        if len(sys.argv) >= 4 and sys.argv[2] == "--days":
            try:
                days_back = int(sys.argv[3])
            except ValueError:
                print("Error: Invalid number of days")
                sys.exit(1)
        
        success = asyncio.run(run_data_pipeline(days_back))
        sys.exit(0 if success else 1)
        
    elif sys.argv[1] == "historical":
        # Run historical pipeline
        if len(sys.argv) != 4:
            print("Error: Historical pipeline requires start and end dates")
            print("Usage: python run.py historical YYYY-MM-DD YYYY-MM-DD")
            sys.exit(1)
        
        start_date = sys.argv[2]
        end_date = sys.argv[3]
        
        # Validate date format
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
        
        success = asyncio.run(run_historical_pipeline(start_date, end_date))
        sys.exit(0 if success else 1)
        
    elif sys.argv[1] == "help":
        print_usage()
        
    else:
        print(f"Error: Unknown command '{sys.argv[1]}'")
        print_usage()
        sys.exit(1)
