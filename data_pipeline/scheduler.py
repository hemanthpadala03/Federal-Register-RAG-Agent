import asyncio
from datetime import datetime, timedelta
from .downloader import FederalRegisterDownloader
from .processor import DataProcessor
from database.connection import db
import logging

logger = logging.getLogger(__name__)

class DataPipeline:
    def __init__(self):
        self.processor = DataProcessor()
    
    async def run_daily_update(self, days_back: int = 1):
        """Run daily data update"""
        run_start = datetime.now()
        logger.info(f"Starting data pipeline run at {run_start}")
        
        try:
            # Initialize database connection
            await db.create_pool()
            
            # Download documents
            async with FederalRegisterDownloader() as downloader:
                documents = await downloader.fetch_recent_documents(days_back)
            
            if not documents:
                logger.warning("No documents downloaded")
                await self._log_pipeline_run(0, 'partial', 'No documents found')
                return
            
            # Process documents
            logger.info(f"Processing {len(documents)} documents")
            results = await self.processor.process_and_store(documents)
            
            # Log results
            if results['errors'] == 0:
                status = 'success'
                error_msg = None
            elif results['processed'] > 0:
                status = 'partial'
                error_msg = f"Processed {results['processed']}, Failed {results['errors']}"
            else:
                status = 'failed'
                error_msg = f"All {results['errors']} documents failed to process"
            
            await self._log_pipeline_run(results['processed'], status, error_msg)
            
            run_end = datetime.now()
            duration = run_end - run_start
            logger.info(f"Pipeline completed in {duration}. Status: {status}")
            
        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}")
            await self._log_pipeline_run(0, 'failed', str(e))
            raise
    
    async def run_historical_update(self, start_date: str, end_date: str):
        """Run historical data update for a date range"""
        logger.info(f"Starting historical update from {start_date} to {end_date}")
        
        try:
            await db.create_pool()
            
            async with FederalRegisterDownloader() as downloader:
                documents = await downloader.fetch_documents(start_date, end_date)
            
            if documents:
                results = await self.processor.process_and_store(documents)
                logger.info(f"Historical update complete: {results}")
            else:
                logger.warning("No historical documents found")
                
        except Exception as e:
            logger.error(f"Historical update failed: {e}")
            raise
    
    async def _log_pipeline_run(self, records_processed: int, status: str, error_message: str = None):
        """Log pipeline run to database"""
        try:
            async with db.get_connection() as conn:
                async with conn.cursor() as cursor:
                    query = """
                    INSERT INTO pipeline_logs (run_date, records_processed, status, error_message)
                    VALUES (%s, %s, %s, %s)
                    """
                    await cursor.execute(query, (
                        datetime.now().date(),
                        records_processed,
                        status,
                        error_message
                    ))
                    await conn.commit()
        except Exception as e:
            logger.error(f"Failed to log pipeline run: {e}")
