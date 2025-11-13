import random
from typing import Tuple, Dict
from PIL import Image
import io

class DocumentService:
    """Mock service for document forgery detection"""
    
    @staticmethod
    def analyze_document(image_path: str) -> Tuple[bool, float, Dict]:
        """
        Mock analysis of document for forgery
        Returns: (is_valid, confidence_score, analysis_details)
        """
        # Mock implementation - randomly pass/fail with weighted probability
        is_valid = random.random() > 0.10  # 90% pass rate
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
    def extract_data(image_path: str) -> Dict:
        """
        Mock OCR data extraction from document
        Returns: Extracted data dictionary
        """
        # Mock extracted data
        return {
            "full_name": "John Doe",
            "date_of_birth": "1990-01-15",
            "document_number": "ID123456789",
            "issue_date": "2020-01-01",
            "expiry_date": "2030-01-01",
            "extraction_confidence": random.uniform(0.85, 0.98)
        }
