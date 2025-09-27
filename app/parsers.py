import os
import logging
from typing import Optional
import pdfplumber
import docx
import openpyxl
# Note: OCR disabled for Vercel deployment (Tesseract not available)
# from PIL import Image
# import pytesseract

logger = logging.getLogger(__name__)

def parse_pdf(file_path: str) -> str:
    """Parse PDF file and extract text, with OCR fallback for scanned PDFs"""
    try:
        # First try with pdfplumber for text-based PDFs
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # If we got meaningful text, return it
        if text.strip():
            logger.info(f"Extracted text from PDF {file_path} using pdfplumber")
            return text
        
        # If pdfplumber didn't extract text, try OCR directly
        logger.info(f"No text found in PDF {file_path} with pdfplumber, trying OCR")
        
        # OCR disabled for Vercel deployment
        logger.warning(f"No text found in PDF {file_path} and OCR not available in serverless environment")
        return ""
        
    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {str(e)}")
        # Try OCR as last resort
        try:
            return parse_image_ocr(file_path)
        except Exception as ocr_e:
            logger.error(f"OCR also failed for {file_path}: {str(ocr_e)}")
            return ""

def parse_docx(file_path: str) -> str:
    """Parse DOCX file and extract text"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    row_text.append(cell.text.strip())
                text += " | ".join(row_text) + "\n"
        
        logger.info(f"Extracted text from DOCX {file_path}")
        return text
        
    except Exception as e:
        logger.error(f"Error parsing DOCX {file_path}: {str(e)}")
        return ""

def parse_xlsx(file_path: str) -> str:
    """Parse XLSX file and extract text"""
    try:
        # Try with openpyxl first
        wb = openpyxl.load_workbook(file_path)
        text = ""
        
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            text += f"Sheet: {sheet_name}\n"
            
            for row in sheet.iter_rows(values_only=True):
                row_data = []
                for cell in row:
                    if cell is not None:
                        row_data.append(str(cell))
                if row_data:  # Only add non-empty rows
                    text += " | ".join(row_data) + "\n"
            text += "\n"
        
        wb.close()
        logger.info(f"Extracted text from XLSX {file_path}")
        return text
        
    except Exception as e:
        logger.error(f"Error with openpyxl for {file_path}: {str(e)}")
        return ""

def parse_image_ocr(file_path: str) -> str:
    """Parse image file using OCR - Disabled for Vercel deployment"""
    logger.warning(f"OCR not available in serverless environment for {file_path}")
    return ""

def parse_attachment(file_path: str) -> str:
    """Main function to parse any attachment based on file extension"""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return ""
    
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    logger.info(f"Parsing attachment: {file_path} (type: {ext})")
    
    if ext == '.pdf':
        return parse_pdf(file_path)
    elif ext == '.docx':
        return parse_docx(file_path)
    elif ext in ['.xlsx', '.xls']:
        return parse_xlsx(file_path)
    elif ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
        logger.warning(f"Image OCR not supported in serverless environment for {file_path}")
        return ""
    else:
        logger.warning(f"Unsupported file type: {ext}")
        return ""