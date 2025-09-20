import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
import json
import logging
from config.settings import FEDERAL_REGISTER_BASE_URL

logger = logging.getLogger(__name__)

class FederalRegisterDownloader:
    def __init__(self):
        self.base_url = FEDERAL_REGISTER_BASE_URL
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_documents(self, start_date: str, end_date: str) -> List[Dict]:
        """Download documents from Federal Register API"""
        params = {
            'conditions[publication_date][gte]': start_date,
            'conditions[publication_date][lte]': end_date,
            'per_page': 1000,
            'fields[]': ['document_number', 'title', 'abstract', 
                        'publication_date', 'agencies', 'type']
        }
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        documents = []
        page = 1
        
        try:
            while True:
                params['page'] = page
                logger.info(f"Fetching page {page} for dates {start_date} to {end_date}")
                
                async with self.session.get(self.base_url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"API request failed with status {response.status}")
                        break
                    
                    data = await response.json()
                    
                    if not data.get('results'):
                        logger.info("No more results found")
                        break
                    
                    documents.extend(data['results'])
                    logger.info(f"Retrieved {len(data['results'])} documents from page {page}")
                    
                    if page >= data.get('total_pages', 1):
                        break
                    
                    page += 1
                    await asyncio.sleep(0.5)  # Rate limiting
        
        except Exception as e:
            logger.error(f"Error fetching documents: {e}")
            raise
        
        logger.info(f"Total documents fetched: {len(documents)}")
        return documents
    
    async def fetch_recent_documents(self, days_back: int = 7) -> List[Dict]:
        """Fetch documents from the last N days"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        return await self.fetch_documents(start_date, end_date)
