import random
import os
from typing import Tuple, Dict

class DocumentService:
    """Mock service for document forgery detection"""
    
    @staticmethod
    def analyze_document(image_path: str) -> Tuple[bool, float, Dict]:
        """
        Mock analysis of document for forgery with basic file validation
        Returns: (is_valid, confidence_score, analysis_details)
        """
        # Check if file exists and has content
        if not os.path.exists(image_path):
            return False, 0.0, {
                "forgery_detected": True,
                "confidence": 0.0,
                "error": "Document file not found"
            }
        
        # Check file size (should be > 1KB for a real image)
        file_size = os.path.getsize(image_path)
        if file_size < 1024:  # Less than 1KB
            return False, 0.20, {
                "forgery_detected": True,
                "confidence": 0.20,
                "pixel_analysis": {
                    "anomalies_found": True,
                    "anomaly_count": 999,
                    "details": "File too small - likely blank or invalid image"
                },
                "font_analysis": {
                    "consistent": False,
                    "mismatches": 10,
                    "details": "No readable text detected"
                },
                "metadata_analysis": {
                    "suspicious": True,
                    "details": "Invalid or missing image metadata"
                },
                "edge_detection": {
                    "authentic_edges": False,
                    "details": "No document edges detected"
                },
                "overall_assessment": "Invalid document - blank or corrupted file"
            }
        
        # Check if file is too large (> 10MB might be suspicious)
        if file_size > 10 * 1024 * 1024:
            return False, 0.35, {
                "forgery_detected": True,
                "confidence": 0.35,
                "overall_assessment": "Suspicious file size - possible manipulation"
            }
        
        # Mock implementation - weighted probability based on file characteristics
        # Smaller files (blank screens) have higher failure rate
        if file_size < 10 * 1024:  # Less than 10KB
            is_valid = random.random() > 0.70  # 30% pass rate for small files
        elif file_size < 50 * 1024:  # Less than 50KB  
            is_valid = random.random() > 0.40  # 60% pass rate
        else:
            is_valid = random.random() > 0.10  # 90% pass rate for normal sized files
        
        confidence = random.uniform(0.80, 0.99) if is_valid else random.uniform(0.30, 0.65)
        
        analysis = {
            "forgery_detected": not is_valid,
            "confidence": confidence,
            "pixel_analysis": {
                "anomalies_found": not is_valid,
                "anomaly_count": 0 if is_valid else random.randint(3, 15),
                "details": "No pixel-level anomalies detected" if is_valid else "Multiple pixel inconsistencies detected"
            },
            "font_analysis": {
                "consistent": is_valid,
                "mismatches": 0 if is_valid else random.randint(1, 5),
                "details": "Font patterns consistent with authentic documents" if is_valid else "Font mismatches detected"
            },
            "metadata_analysis": {
                "suspicious": not is_valid,
                "details": "Metadata appears authentic" if is_valid else "Metadata shows signs of digital manipulation"
            },
            "edge_detection": {
                "authentic_edges": is_valid,
                "details": "Natural edge patterns" if is_valid else "Artificial edge artifacts detected"
            },
            "overall_assessment": "Authentic document" if is_valid else "Likely forged or digitally altered"
        }
        
        return is_valid, confidence, analysis
    
    @staticmethod
    def extract_data(image_path: str, expected_name: str = None) -> Dict:
        """
        Mock OCR data extraction from document
        Returns: Extracted data dictionary
        """
        # Check file size for basic validation
        file_size = os.path.getsize(image_path) if os.path.exists(image_path) else 0
        
        if file_size < 1024:
            # Blank or invalid file - return poor extraction
            return {
                "full_name": "",
                "date_of_birth": "",
                "document_number": "",
                "issue_date": "",
                "expiry_date": "",
                "extraction_confidence": 0.05,
                "error": "Unable to extract text from document"
            }
        
        # For realistic testing, use the expected name if provided
        # In production, this would be actual OCR extraction
        extracted_name = expected_name if expected_name else "John Doe"
        
        # Mock extracted data with some variation
        return {
            "full_name": extracted_name,
            "date_of_birth": "1990-01-15",
            "document_number": f"ID{random.randint(100000000, 999999999)}",
            "issue_date": "2020-01-01",
            "expiry_date": "2030-01-01",
            "extraction_confidence": random.uniform(0.85, 0.98) if file_size > 50*1024 else random.uniform(0.20, 0.50)
        }
