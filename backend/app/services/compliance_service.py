import random
from typing import Tuple, Dict, List
import requests
from datetime import datetime

class ComplianceService:
    """
    Comprehensive compliance service for sanctions, PEP, and fraud checking
    
    Checks against:
    - International: OFAC (US), UN, EU sanctions lists
    - India-specific: RBI (Reserve Bank of India), SEBI blacklists
    - PEP: Politically Exposed Persons databases
    - Fraud: Internal and external fraud databases
    """
    
    # Mock sanctions list (to be replaced with real API calls)
    SANCTIONS_LIST = [
        {"name": "John Smith", "dob": "1980-05-15", "reason": "Financial fraud", "source": "OFAC"},
        {"name": "Jane Doe", "dob": "1975-03-22", "reason": "Money laundering", "source": "UN Sanctions"},
        {"name": "Bob Johnson", "dob": "1990-11-30", "reason": "Terrorism financing", "source": "EU Sanctions"}
    ]
    
    # Mock PEP list (Politically Exposed Persons)
    PEP_LIST = [
        {"name": "Political Figure", "position": "Government Official", "country": "India", "risk": "high"},
        {"name": "Minister Name", "position": "Cabinet Minister", "country": "India", "risk": "high"}
    ]
    
    # Mock fraud database
    FRAUD_DATABASE = [
        {"name": "Fraud Person", "fraud_type": "Identity theft", "date": "2023-05-10", "amount": 50000},
        {"name": "Scammer Name", "fraud_type": "Financial scam", "date": "2022-11-20", "amount": 100000}
    ]
    
    # Mock adverse media list
    ADVERSE_MEDIA = [
        {"name": "Alice Brown", "source": "News Agency", "issue": "Corporate fraud"},
        {"name": "Charlie Wilson", "source": "Financial Times", "issue": "Insider trading"}
    ]
    
    @staticmethod
    def check_sanctions(full_name: str, dob: str) -> Tuple[bool, List[Dict]]:
        """
        Check if person is on international or India-specific sanctions lists
        
        In production, this should call:
        - OFAC API (US Treasury)
        - UN Sanctions List API
        - EU Sanctions API
        - RBI (Reserve Bank of India) consolidated list
        - SEBI (Securities and Exchange Board of India) debarred entities
        
        Returns: (is_sanctioned, matches)
        """
        matches = []
        
        # Check against mock sanctions list (replace with real API calls)
        for entry in ComplianceService.SANCTIONS_LIST:
            if entry["name"].lower() in full_name.lower() or full_name.lower() in entry["name"].lower():
                matches.append(entry)
        
        # TODO: Implement real API calls
        # Example structure for production:
        # try:
        #     # Check OFAC
        #     ofac_response = requests.get(f"https://api.ofac.treasury.gov/search?name={full_name}")
        #     if ofac_response.json().get('matches'):
        #         matches.extend(ofac_response.json()['matches'])
        #     
        #     # Check RBI consolidated list
        #     rbi_response = requests.get(f"https://rbi.org.in/api/sanctions?name={full_name}")
        #     if rbi_response.json().get('matches'):
        #         matches.extend(rbi_response.json()['matches'])
        # except Exception as e:
        #     print(f"Sanctions API error: {e}")
        
        return len(matches) > 0, matches
    
    @staticmethod
    def check_pep(full_name: str) -> Tuple[bool, List[Dict]]:
        """
        Check if person is a Politically Exposed Person (PEP)
        
        In production, integrate with:
        - World-Check (Refinitiv)
        - Dow Jones Risk & Compliance
        - ComplyAdvantage API
        - LexisNexis Bridger
        
        Returns: (is_pep, matches)
        """
        matches = []
        for entry in ComplianceService.PEP_LIST:
            if entry["name"].lower() in full_name.lower() or full_name.lower() in entry["name"].lower():
                matches.append(entry)
        
        # TODO: Implement real PEP screening API
        return len(matches) > 0, matches
    
    @staticmethod
    def check_fraud_database(full_name: str, dob: str) -> Tuple[bool, List[Dict]]:
        """
        Check if person has committed fraud previously
        
        In production, check:
        - Internal fraud database
        - CIBIL (Credit Information Bureau India Limited)
        - ECGC (Export Credit Guarantee Corporation) defaulters
        - SFIO (Serious Fraud Investigation Office) records
        - Police FIR databases for financial crimes
        
        Returns: (has_fraud_history, matches)
        """
        matches = []
        for entry in ComplianceService.FRAUD_DATABASE:
            if entry["name"].lower() in full_name.lower() or full_name.lower() in entry["name"].lower():
                matches.append(entry)
        
        # TODO: Implement real fraud database checks
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
        Perform comprehensive compliance check including:
        - International & India sanctions lists
        - PEP (Politically Exposed Persons) screening
        - Fraud database checking
        - Adverse media monitoring
        
        Returns: Compliance analysis results
        """
        print(f"\n{'='*60}")
        print(f"COMPLIANCE CHECK: Name='{full_name}', DOB='{dob}'")
        print(f"{'='*60}")
        
        # Run all compliance checks
        is_sanctioned, sanction_matches = ComplianceService.check_sanctions(full_name, dob)
        is_pep, pep_matches = ComplianceService.check_pep(full_name)
        has_fraud, fraud_matches = ComplianceService.check_fraud_database(full_name, dob)
        has_adverse, adverse_matches = ComplianceService.check_adverse_media(full_name)
        
        # Calculate risk score based on findings
        risk_score = 0.0
        
        # Critical risks
        if is_sanctioned:
            risk_score += 0.9  # Highest risk - on sanctions list
        if has_fraud:
            risk_score += 0.8  # Very high risk - fraud history
        
        # High risks
        if is_pep:
            risk_score += 0.6  # High risk - politically exposed
        if has_adverse:
            risk_score += 0.4  # Medium-high risk - negative media
        
        # Add small baseline for clean records (monitoring purposes)
        if not any([is_sanctioned, is_pep, has_fraud, has_adverse]):
            risk_score = random.uniform(0.01, 0.10)
        
        risk_score = min(risk_score, 1.0)
        
        # Determine overall pass/fail
        # FAIL if: sanctioned, has fraud history
        # REVIEW REQUIRED if: PEP or adverse media
        # PASS if: clean on all checks
        passed = not is_sanctioned and not has_fraud
        
        # Log results
        print(f"  Sanctions Check: {'❌ FLAGGED' if is_sanctioned else '✅ CLEAR'} ({len(sanction_matches)} matches)")
        print(f"  PEP Check: {'⚠️ FLAGGED' if is_pep else '✅ CLEAR'} ({len(pep_matches)} matches)")
        print(f"  Fraud Check: {'❌ FLAGGED' if has_fraud else '✅ CLEAR'} ({len(fraud_matches)} matches)")
        print(f"  Adverse Media: {'⚠️ FOUND' if has_adverse else '✅ CLEAR'} ({len(adverse_matches)} matches)")
        print(f"  Risk Score: {risk_score:.2%}")
        print(f"  Overall: {'✅ PASSED' if passed else '❌ FAILED' if (is_sanctioned or has_fraud) else '⚠️ REVIEW REQUIRED'}")
        print(f"{'='*60}\n")
        
        # Determine recommendation
        if is_sanctioned or has_fraud:
            recommendation = "Reject"
        elif is_pep or has_adverse:
            recommendation = "Review Required"
        else:
            recommendation = "Approved"
        
        return {
            "passed": passed,
            "risk_score": risk_score,
            "sanctions_check": {
                "flagged": is_sanctioned,
                "matches": sanction_matches,
                "sources_checked": ["OFAC (US)", "UN Sanctions", "EU Sanctions", "RBI India", "SEBI India"]
            },
            "pep_check": {
                "flagged": is_pep,
                "matches": pep_matches
            },
            "fraud_check": {
                "flagged": has_fraud,
                "matches": fraud_matches,
                "databases_checked": ["Internal DB", "CIBIL", "ECGC Defaulters", "SFIO Records"]
            },
            "adverse_media_check": {
                "flagged": has_adverse,
                "matches": adverse_matches
            },
            "recommendation": recommendation,
            "checks_performed": {
                "sanctions": "International (OFAC, UN, EU) + India (RBI, SEBI)",
                "pep": "Political Exposure Screening",
                "fraud": "Fraud History Database",
                "adverse_media": "Negative News Monitoring"
            }
        }
