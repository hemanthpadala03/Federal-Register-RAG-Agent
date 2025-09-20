import aiomysql
import contextlib
from config.settings import DATABASE_CONFIG
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.pool = None
    
    async def create_pool(self):
        """Create connection pool"""
        try:
            self.pool = await aiomysql.create_pool(
                host=DATABASE_CONFIG['host'],
                port=DATABASE_CONFIG['port'],
                user=DATABASE_CONFIG['user'],
                password=DATABASE_CONFIG['password'],
                db=DATABASE_CONFIG['database'],
                minsize=5,
                maxsize=20,
                autocommit=False,
                charset='utf8mb4'
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise
    
    @contextlib.asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool as an async context manager"""
        conn = await self.pool.acquire()
        try:
            yield conn
        finally:
            self.pool.release(conn)
    
    async def close_pool(self):
        """Close connection pool"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("Database connection pool closed")

# Global database instance
db = DatabaseConnection()
