import random
from typing import Tuple, Dict, List

class ComplianceService:
    """Mock service for sanctions and adverse media checks"""
    
    # Mock sanctions list
    SANCTIONS_LIST = [
        {"name": "John Smith", "dob": "1980-05-15", "reason": "Financial fraud"},
        {"name": "Jane Doe", "dob": "1975-03-22", "reason": "Money laundering"},
        {"name": "Bob Johnson", "dob": "1990-11-30", "reason": "Terrorism financing"}
    ]
    
    # Mock adverse media list
    ADVERSE_MEDIA = [
        {"name": "Alice Brown", "source": "News Agency", "issue": "Corporate fraud"},
        {"name": "Charlie Wilson", "source": "Financial Times", "issue": "Insider trading"}
    ]
    
    @staticmethod
    def check_sanctions(full_name: str, dob: str) -> Tuple[bool, List[Dict]]:
        """
        Check if person is on sanctions list
        Returns: (is_sanctioned, matches)
        """
        # Simple name matching (case-insensitive)
        matches = []
        for entry in ComplianceService.SANCTIONS_LIST:
            if entry["name"].lower() in full_name.lower() or full_name.lower() in entry["name"].lower():
                matches.append(entry)
        
        return len(matches) > 0, matches
    
    @staticmethod
    def check_adverse_media(full_name: str) -> Tuple[bool, List[Dict]]:
        """
        Check if person appears in adverse media
        Returns: (has_adverse_media, matches)
        """
        matches = []
        for entry in ComplianceService.ADVERSE_MEDIA:
            if entry["name"].lower() in full_name.lower() or full_name.lower() in entry["name"].lower():
                matches.append(entry)
        
        return len(matches) > 0, matches
    
    @staticmethod
    def perform_compliance_check(full_name: str, dob: str) -> Dict:
        """
        Perform complete compliance check
        Returns: Compliance analysis results
        """
        is_sanctioned, sanction_matches = ComplianceService.check_sanctions(full_name, dob)
        has_adverse, adverse_matches = ComplianceService.check_adverse_media(full_name)
        
        risk_score = 0.0
        if is_sanctioned:
            risk_score += 0.8
        if has_adverse:
            risk_score += 0.5
        
        # Add small random variation for non-matches
        if not is_sanctioned and not has_adverse:
            risk_score = random.uniform(0.01, 0.15)
        
        risk_score = min(risk_score, 1.0)
        
        return {
            "passed": not is_sanctioned and not has_adverse,
            "risk_score": risk_score,
            "sanctions_check": {
                "flagged": is_sanctioned,
                "matches": sanction_matches
            },
            "adverse_media_check": {
                "flagged": has_adverse,
                "matches": adverse_matches
            },
            "recommendation": "Approved" if not is_sanctioned and not has_adverse else "Reject" if is_sanctioned else "Review Required"
        }
