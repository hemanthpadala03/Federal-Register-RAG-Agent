import asyncio
from typing import List, Dict
from database.connection import db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
    
    async def process_and_store(self, documents: List[Dict]) -> Dict[str, int]:
        """Process and store documents in MySQL"""
        self.processed_count = 0
        self.error_count = 0
        
        logger.info(f"Starting to process {len(documents)} documents")
        
        async with db.get_connection() as conn:
            async with conn.cursor() as cursor:
                for doc in documents:
                    try:
                        # Extract agency names
                        agencies = doc.get('agencies', [])
                        agency_names = []
                        
                        if isinstance(agencies, list):
                            for agency in agencies:
                                if isinstance(agency, dict):
                                    agency_names.append(agency.get('name', ''))
                                else:
                                    agency_names.append(str(agency))
                        
                        agency_str = ', '.join(filter(None, agency_names)) if agency_names else 'Unknown'
                        
                        # Clean and validate data
                        document_number = doc.get('document_number', '')
                        title = doc.get('title', '')[:1000]  # Limit title length
                        abstract = doc.get('abstract', '')
                        publication_date = doc.get('publication_date')
                        document_type = doc.get('type', '')[:50]  # Limit type length
                        
                        # Skip if missing critical data
                        if not document_number or not title:
                            self.error_count += 1
                            continue
                        
                        # Insert or update document
                        query = """
                        INSERT INTO federal_documents 
                        (document_number, title, abstract, publication_date, agency, document_type)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        title = VALUES(title),
                        abstract = VALUES(abstract),
                        agency = VALUES(agency),
                        document_type = VALUES(document_type),
                        updated_at = CURRENT_TIMESTAMP
                        """
                        
                        await cursor.execute(query, (
                            document_number,
                            title,
                            abstract,
                            publication_date,
                            agency_str[:100],  # Limit agency string length
                            document_type
                        ))
                        
                        self.processed_count += 1
                        
                        # Commit in batches
                        if self.processed_count % 100 == 0:
                            await conn.commit()
                            logger.info(f"Processed {self.processed_count} documents so far")
                        
                    except Exception as e:
                        logger.error(f"Error processing document {doc.get('document_number', 'unknown')}: {e}")
                        self.error_count += 1
                        continue
                
                # Final commit
                await conn.commit()
        
        logger.info(f"Processing complete. Success: {self.processed_count}, Errors: {self.error_count}")
        
        return {
            'processed': self.processed_count,
            'errors': self.error_count,
            'total': len(documents)
        }
