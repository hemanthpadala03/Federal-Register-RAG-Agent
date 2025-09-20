import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'rag_system')
}

OLLAMA_CONFIG = {
    'base_url': os.getenv('OLLAMA_URL', 'http://localhost:11434/v1'),
    'model': os.getenv('OLLAMA_MODEL', 'llama2')
}

API_CONFIG = {
    'host': os.getenv('API_HOST', '0.0.0.0'),
    'port': int(os.getenv('API_PORT', 8000))
}

# Federal Register API settings
FEDERAL_REGISTER_BASE_URL = "https://www.federalregister.gov/api/v1/documents"