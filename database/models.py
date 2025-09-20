"""
Database schema definitions
Run this SQL to set up your MySQL database:

CREATE DATABASE rag_system;
USE rag_system;

CREATE TABLE federal_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_number VARCHAR(50) UNIQUE,
    title TEXT,
    abstract TEXT,
    publication_date DATE,
    agency VARCHAR(100),
    document_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_date (publication_date),
    INDEX idx_agency (agency),
    INDEX idx_type (document_type),
    FULLTEXT(title, abstract)
);

CREATE TABLE pipeline_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    run_date DATE,
    records_processed INT,
    status ENUM('success', 'partial', 'failed'),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# This file contains the SQL schema as documentation
# Execute the above SQL commands in your MySQL database
