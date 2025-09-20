from database.connection import db
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class SQLTools:
    @staticmethod
    async def search_documents(query: str, limit: int = 10) -> str:
        """Search federal documents by keyword"""
        try:
            async with db.get_connection() as conn:
                async with conn.cursor() as cursor:
                    sql = """
                    SELECT document_number, title, abstract, publication_date, agency, document_type
                    FROM federal_documents 
                    WHERE title LIKE %s OR abstract LIKE %s 
                    ORDER BY publication_date DESC 
                    LIMIT %s
                    """
                    search_term = f"%{query}%"
                    await cursor.execute(sql, (search_term, search_term, limit))
                    results = await cursor.fetchall()
                    
                    documents = []
                    for row in results:
                        documents.append({
                            'document_number': row[0],
                            'title': row[1],
                            'abstract': row[2][:500] + "..." if row[2] and len(row[2]) > 500 else row[2],
                            'publication_date': str(row[3]) if row[3] else None,
                            'agency': row[4],
                            'document_type': row[5]
                        })
                    
                    logger.info(f"Search for '{query}' returned {len(documents)} results")
                    return json.dumps(documents, indent=2) if documents else json.dumps([])
                    
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return f"Error searching documents: {e}"
    
    @staticmethod
    async def get_recent_documents(days: int = 7, limit: int = 20) -> str:
        """Get recent documents from the last N days"""
        try:
            async with db.get_connection() as conn:
                async with conn.cursor() as cursor:
                    sql = """
                    SELECT document_number, title, publication_date, agency, document_type
                    FROM federal_documents 
                    WHERE publication_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                    ORDER BY publication_date DESC 
                    LIMIT %s
                    """
                    await cursor.execute(sql, (days, limit))
                    results = await cursor.fetchall()
                    
                    documents = []
                    for row in results:
                        documents.append({
                            'document_number': row[0],
                            'title': row[1],
                            'publication_date': str(row[2]) if row[2] else None,
                            'agency': row[3],
                            'document_type': row[4]
                        })
                    
                    logger.info(f"Retrieved {len(documents)} recent documents from last {days} days")
                    return json.dumps(documents, indent=2) if documents else json.dumps([])
                    
        except Exception as e:
            logger.error(f"Error getting recent documents: {e}")
            return f"Error getting recent documents: {e}"
    
    @staticmethod
    async def filter_by_agency(agency: str, limit: int = 15) -> str:
        """Filter documents by agency"""
        try:
            async with db.get_connection() as conn:
                async with conn.cursor() as cursor:
                    sql = """
                    SELECT document_number, title, abstract, publication_date, document_type
                    FROM federal_documents 
                    WHERE agency LIKE %s 
                    ORDER BY publication_date DESC 
                    LIMIT %s
                    """
                    agency_term = f"%{agency}%"
                    await cursor.execute(sql, (agency_term, limit))
                    results = await cursor.fetchall()
                    
                    documents = []
                    for row in results:
                        documents.append({
                            'document_number': row[0],
                            'title': row[1],
                            'abstract': row[2][:300] + "..." if row[2] and len(row[2]) > 300 else row[2],
                            'publication_date': str(row[3]) if row[3] else None,
                            'document_type': row[4]
                        })
                    
                    logger.info(f"Filter by agency '{agency}' returned {len(documents)} results")
                    return json.dumps(documents, indent=2) if documents else json.dumps([])
                    
        except Exception as e:
            logger.error(f"Error filtering by agency: {e}")
            return f"Error filtering by agency: {e}"
    
    @staticmethod
    async def get_document_stats() -> str:
        """Get basic statistics about the document database"""
        try:
            async with db.get_connection() as conn:
                async with conn.cursor() as cursor:
                    # Total documents
                    await cursor.execute("SELECT COUNT(*) FROM federal_documents")
                    total_docs = (await cursor.fetchone())[0]
                    
                    # Documents by type
                    await cursor.execute("""
                        SELECT document_type, COUNT(*) as count 
                        FROM federal_documents 
                        GROUP BY document_type 
                        ORDER BY count DESC 
                        LIMIT 5
                    """)
                    doc_types = await cursor.fetchall()
                    
                    # Recent activity
                    await cursor.execute("""
                        SELECT DATE(publication_date) as date, COUNT(*) as count
                        FROM federal_documents 
                        WHERE publication_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                        GROUP BY DATE(publication_date)
                        ORDER BY date DESC
                        LIMIT 10
                    """)
                    recent_activity = await cursor.fetchall()
                    
                    stats = {
                        'total_documents': total_docs,
                        'document_types': [{'type': row[0], 'count': row[1]} for row in doc_types],
                        'recent_activity': [{'date': str(row[0]), 'count': row[1]} for row in recent_activity]
                    }
                    
                    return json.dumps(stats, indent=2)
                    
        except Exception as e:
            logger.error(f"Error getting document stats: {e}")
            return f"Error getting document stats: {e}"
