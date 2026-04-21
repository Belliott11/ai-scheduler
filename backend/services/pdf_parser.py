"""PDF parsing service for extracting syllabus content"""
import pdfplumber
from typing import Optional


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")
    
    return text.strip()


def extract_tables_from_pdf(pdf_path: str) -> list:
    """
    Extract tables from a PDF file (useful for syllabus tables).
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of extracted tables
    """
    tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
    except Exception as e:
        raise ValueError(f"Failed to extract tables from PDF: {str(e)}")
    
    return tables
