# Federal Register RAG Agent

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Available-brightgreen)](https://dcda5298db33.ngrok-free.app)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Ollama](https://img.shields.io/badge/Ollama-Llama2-orange)](https://ollama.ai)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-blue)](https://mysql.com)

An AI-powered Retrieval-Augmented Generation (RAG) chat system for searching and analyzing Federal Register documents using local large language models (LLMs) via Ollama. This system provides intelligent, contextual search capabilities across federal regulations and documents while maintaining complete privacy through local AI processing.

## 🚀 Live Demo

Experience the live system here: **[https://dcda5298db33.ngrok-free.app](https://dcda5298db33.ngrok-free.app)**

## ✨ Features

- 🤖 **Local AI Agent** - Powered by Llama2 via Ollama for private, cost-free operation
- 📊 **Daily Data Updates** - Automated pipeline fetching the latest federal documents
- 🔍 **Smart Search** - Natural language queries across federal regulations and documents
- 🏛️ **Agency Filtering** - Filter documents by specific government agencies
- 📈 **Real-time Stats** - Database statistics and pipeline monitoring
- 💬 **Web Chat Interface** - Clean, responsive chat UI built with modern web technologies
- ⚡ **Async Architecture** - Fast, non-blocking operations for optimal performance
- 🔒 **Privacy-First** - All AI processing happens locally, no data sent to external APIs

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Pipeline │    │  Vector Database │    │   Chat Agent    │
│                 │    │                  │    │                 │
│ • Federal API   │───▶│ • MySQL Storage  │───▶│ • Ollama/Llama2 │
│ • Text Chunking │    │ • Embeddings     │    │ • RAG Pipeline  │
│ • Vectorization │    │ • Metadata       │    │ • Web Interface │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 Project Structure

### `/agent` - AI Agent Core
- **Purpose**: Contains the main RAG agent implementation
- **Key Components**:
  - `chat_agent.py` - Main chat interface and conversation handling
  - `rag_pipeline.py` - Retrieval-augmented generation logic
  - `embedding_service.py` - Text embedding generation
  - `query_processor.py` - Natural language query processing

### `/api` - REST API Layer
- **Purpose**: FastAPI-based REST endpoints for the web interface
- **Key Components**:
  - `main.py` - FastAPI application entry point
  - `chat_routes.py` - Chat API endpoints
  - `document_routes.py` - Document management endpoints
  - `health_routes.py` - System health and monitoring

### `/config` - Configuration Management
- **Purpose**: Centralized configuration for all components
- **Key Components**:
  - `settings.py` - Application settings and environment variables
  - `database_config.py` - MySQL connection configuration
  - `ollama_config.py` - Ollama LLM configuration
  - `logging_config.py` - Logging setup and configuration

### `/data_pipeline` - Data Ingestion Pipeline
- **Purpose**: Automated data fetching and processing from Federal Register API
- **Key Components**:
  - `federal_api_client.py` - Federal Register API integration
  - `document_processor.py` - Text processing and chunking
  - `embedding_pipeline.py` - Document vectorization
  - `daily_update_scheduler.py` - Automated daily updates

### `/database` - Database Layer
- **Purpose**: MySQL database management and vector storage
- **Key Components**:
  - `connection.py` - Database connection management
  - `models.py` - SQLAlchemy database models
  - `vector_store.py` - Vector similarity search implementation
  - `migrations/` - Database schema migrations

### `/rag_env` - Environment Configuration
- **Purpose**: Virtual environment and dependency management
- **Key Components**:
  - Environment-specific configurations
  - Dependency isolation
  - Development vs. production settings

### `/tools` - Utility Tools
- **Purpose**: Helper scripts and utilities
- **Key Components**:
  - `data_validator.py` - Data quality validation
  - `performance_monitor.py` - System performance monitoring
  - `backup_manager.py` - Database backup utilities

### `/ui` - Web User Interface
- **Purpose**: Frontend web application
- **Key Components**:
  - `index.html` - Main chat interface
  - `chat.js` - Real-time chat functionality
  - `styles.css` - UI styling and responsive design
  - `components/` - Reusable UI components

## 🛠️ Installation & Setup

### Prerequisites

Ensure you have the following installed:

1. **Python 3.8+**
2. **MySQL 8.0+** with InnoDB storage engine
3. **Ollama** with Llama2 model
4. **Git** for version control

### Step 1: Clone the Repository

```bash
git clone https://github.com/hemanthpadala03/Federal-Register-RAG-Agent.git
cd Federal-Register-RAG-Agent
```

### Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv rag_env

# Activate virtual environment
# On Windows:
rag_env\Scripts\activate
# On macOS/Linux:
source rag_env/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure MySQL Database

```sql
-- Create database
CREATE DATABASE federal_register_rag;

-- Create user (optional, for security)
CREATE USER 'rag_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON federal_register_rag.* TO 'rag_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 5: Set Up Ollama

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Llama2 model
ollama pull llama2

# Verify installation
ollama list
```

### Step 6: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=federal_register_rag
DB_USER=rag_user
DB_PASSWORD=your_secure_password

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Federal Register API
FEDERAL_REGISTER_API_BASE=https://www.federalregister.gov/api/v1

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
```

### Step 7: Initialize Database

```bash
python -m database.migrations.init_db
```

### Step 8: Run Initial Data Pipeline

```bash
# Fetch initial set of federal documents
python -m data_pipeline.initial_load

# This may take 15-30 minutes depending on your system
```

## 🚀 Running the Application

### Development Mode

```bash
# Start the API server
python -m api.main

# The application will be available at http://localhost:8000
```

### Production Mode

```bash
# Using Gunicorn (recommended for production)
gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker (Alternative)

```bash
# Build the container
docker build -t federal-register-rag .

# Run with Docker Compose
docker-compose up -d
```

## 📋 Usage Examples

### Chat Interface

1. Open your browser to the application URL
2. Type natural language questions about federal regulations
3. Examples:
   - "What are the latest EPA environmental regulations?"
   - "Show me Department of Transportation safety rules from 2024"
   - "Find FDA drug approval guidelines"

### API Usage

```python
import requests

# Send a chat message
response = requests.post('http://localhost:8000/api/chat', json={
    'message': 'What are the latest healthcare regulations?',
    'session_id': 'user123'
})

print(response.json())
```

### Programmatic Query

```python
from agent.rag_pipeline import RAGPipeline

# Initialize the RAG pipeline
rag = RAGPipeline()

# Query the system
result = rag.query("Environmental protection agency water quality standards")
print(result['answer'])
print(result['sources'])
```

## 🔄 Data Pipeline Details

### Daily Update Process

The system automatically fetches new federal documents daily:

1. **API Polling**: Queries Federal Register API for new documents
2. **Text Processing**: Extracts and cleans document content
3. **Chunking**: Breaks large documents into searchable segments
4. **Vectorization**: Generates embeddings using local models
5. **Storage**: Stores in MySQL with vector indexing

### Manual Pipeline Execution

```bash
# Run full pipeline manually
python -m data_pipeline.run_pipeline

# Update specific agency documents
python -m data_pipeline.agency_update --agency="EPA"

# Process documents from specific date range
python -m data_pipeline.date_range_update --start="2024-01-01" --end="2024-12-31"
```

## 🛠️ Configuration

### Ollama Model Configuration

```python
# config/ollama_config.py
OLLAMA_SETTINGS = {
    'base_url': 'http://localhost:11434',
    'model': 'llama2',  # or 'llama2:13b', 'codellama', etc.
    'temperature': 0.7,
    'max_tokens': 2048,
    'timeout': 60
}
```

### Database Optimization

```sql
-- Enable vector search optimization
SET SESSION innodb_lock_wait_timeout = 120;

-- Create indexes for faster retrieval
CREATE INDEX idx_document_embeddings ON documents(embedding_vector);
CREATE INDEX idx_document_agency ON documents(agency_id);
CREATE INDEX idx_document_date ON documents(publication_date);
```

## 🔧 Troubleshooting

### Common Issues

**Ollama Connection Error**
```bash
# Check if Ollama is running
ollama list

# Restart Ollama service
sudo systemctl restart ollama
```

**MySQL Connection Issues**
```bash
# Test database connection
mysql -u rag_user -p federal_register_rag

# Check MySQL service status
sudo systemctl status mysql
```

**Memory Issues**
- Reduce batch size in `data_pipeline/config.py`
- Use smaller Ollama model (e.g., `llama2:7b`)
- Increase system RAM or use swap file

**Slow Performance**
- Enable MySQL query cache
- Add database indexes
- Use SSD storage for better I/O performance

## 📊 Monitoring & Analytics

### System Health Dashboard

Access the monitoring dashboard at `/admin/health` to view:
- Database connection status
- Ollama model availability
- API response times
- Document processing statistics
- Error rates and logs

### Performance Metrics

```bash
# View system statistics
python -m tools.performance_monitor

# Generate usage report
python -m tools.usage_report --days=30
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add unit tests for new features
- Update documentation for API changes
- Test with multiple Ollama models

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Federal Register API** - For providing access to federal document data
- **Ollama Team** - For making local LLM deployment accessible
- **MySQL Team** - For vector search capabilities
- **Open Source Community** - For the amazing tools and libraries used

## 📞 Support

For support and questions:

- 📧 Email: support@federal-register-rag.com
- 💬 Discord: [Join our community](#)
- 🐛 Issues: [GitHub Issues](https://github.com/hemanthpadala03/Federal-Register-RAG-Agent/issues)
- 📖 Documentation: [Full Documentation](#)

---

**Built with ❤️ for transparent government and accessible AI**
