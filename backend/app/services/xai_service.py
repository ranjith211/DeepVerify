from typing import Dict

class XAIService:
    """Explainability service for generating human-readable risk reports"""
    
    @staticmethod
    def generate_explanation(
        document_analysis: Dict,
        liveness_analysis: Dict,
        compliance_analysis: Dict,
        overall_risk_score: float
    ) -> str:
        """Generate a comprehensive, human-readable explanation"""
        
        explanation_parts = []
        
        # Overall risk assessment
        if overall_risk_score < 0.3:
            risk_level = "LOW"
            intro = "✓ This verification passed all security checks with high confidence."
        elif overall_risk_score < 0.6:
            risk_level = "MEDIUM"
            intro = "⚠ This verification shows some concerning indicators requiring review."
        else:
            risk_level = "HIGH"
            intro = "✗ This verification failed critical security checks."
        
        explanation_parts.append(f"RISK LEVEL: {risk_level} (Score: {overall_risk_score:.2f})\n")
        explanation_parts.append(intro + "\n")
        
        # Document analysis explanation (AI-enhanced)
        explanation_parts.append("\n--- DOCUMENT VERIFICATION (AI-Powered) ---")
        if document_analysis.get("forgery_detected"):
            explanation_parts.append("✗ FAILED: Document appears to be forged or digitally altered")
            explanation_parts.append(f"  • {document_analysis.get('pixel_analysis', {}).get('details', '')}")
            if document_analysis.get('edge_analysis'):
                explanation_parts.append(f"  • {document_analysis.get('edge_analysis', {}).get('details', '')}")
            explanation_parts.append(f"  • {document_analysis.get('metadata_analysis', {}).get('details', '')}")
            if document_analysis.get('quality_analysis'):
                explanation_parts.append(f"  • Image quality: {document_analysis.get('quality_analysis', {}).get('details', '')}")
            if document_analysis.get('ml_score') is not None:
                explanation_parts.append(f"  • AI Detection Score: {document_analysis.get('ml_score', 0):.1%}")
        else:
            explanation_parts.append("✓ PASSED: Document appears authentic")
            explanation_parts.append(f"  • Confidence: {document_analysis.get('confidence', 0):.1%}")
            if document_analysis.get('ml_score') is not None:
                explanation_parts.append(f"  • AI Authenticity Score: {document_analysis.get('ml_score', 0):.1%}")
            if document_analysis.get('quality_analysis'):
                quality = document_analysis.get('quality_analysis', {})
                explanation_parts.append(f"  • Image Quality: {quality.get('score', 0):.1%}")
                explanation_parts.append(f"  • Resolution: {quality.get('resolution', 'N/A')}")
        
        # Liveness analysis explanation (AI-enhanced)
        explanation_parts.append("\n--- LIVENESS VERIFICATION (AI-Powered) ---")
        if liveness_analysis.get("lip_sync_match"):
            explanation_parts.append("✓ PASSED: Live person detected with AI verification")
            explanation_parts.append(f"  • Lip-sync match: {liveness_analysis.get('lip_sync_confidence', 0):.1%}")
            if liveness_analysis.get('transcribed_text'):
                explanation_parts.append(f"  • Speech recognized: '{liveness_analysis.get('transcribed_text')}'")
            explanation_parts.append(f"  • Gesture detected: {liveness_analysis.get('gesture_confidence', 0):.1%}")
            if liveness_analysis.get('detected_gesture'):
                explanation_parts.append(f"  • Gesture type: {liveness_analysis.get('detected_gesture')}")
            if liveness_analysis.get('face_landmarks_detected'):
                explanation_parts.append(f"  • Face landmarks: Detected (468 points)")
            explanation_parts.append(f"  • Deepfake probability: {liveness_analysis.get('deepfake_probability', 0):.1%}")
            explanation_parts.append(f"  • Video quality: {liveness_analysis.get('video_quality', 'good')}")
        else:
            explanation_parts.append("✗ FAILED: Potential deepfake or pre-recorded video detected by AI")
            explanation_parts.append(f"  • {liveness_analysis.get('analysis_notes', '')}")
            explanation_parts.append(f"  • Deepfake probability: {liveness_analysis.get('deepfake_probability', 0):.1%}")
            if liveness_analysis.get('transcribed_text'):
                explanation_parts.append(f"  • Speech mismatch: Expected vs actual")
            if liveness_analysis.get('detected_gesture'):
                explanation_parts.append(f"  • Gesture issue: Expected vs detected")
        
        # Compliance analysis explanation
        explanation_parts.append("\n--- COMPLIANCE CHECK ---")
        sanctions = compliance_analysis.get("sanctions_check", {})
        adverse = compliance_analysis.get("adverse_media_check", {})
        
        if sanctions.get("flagged"):
            explanation_parts.append("✗ FAILED: Individual found on sanctions list")
            for match in sanctions.get("matches", []):
                explanation_parts.append(f"  • Match: {match.get('name')} - Reason: {match.get('reason')}")
        elif adverse.get("flagged"):
            explanation_parts.append("⚠ WARNING: Adverse media found")
            for match in adverse.get("matches", []):
                explanation_parts.append(f"  • Source: {match.get('source')} - Issue: {match.get('issue')}")
        else:
            explanation_parts.append("✓ PASSED: No sanctions or adverse media found")
        
        # Final recommendation
        explanation_parts.append("\n--- RECOMMENDATION ---")
        if overall_risk_score >= 0.7:
            explanation_parts.append("REJECT: High risk - verification failed critical checks")
        elif overall_risk_score >= 0.4:
            explanation_parts.append("HUMAN REVIEW REQUIRED: Medium risk - manual review recommended")
        else:
            explanation_parts.append("APPROVE: Low risk - all checks passed successfully")
        
        return "\n".join(explanation_parts)
    
    @staticmethod
    def calculate_risk_score(
        document_valid: bool,
        document_confidence: float,
        liveness_valid: bool,
        liveness_confidence: float,
        compliance_risk: float
    ) -> float:
        """Calculate overall risk score from component scores"""
        
        risk = 0.0
        
        # Document contributes 35% to risk
        if not document_valid:
            risk += 0.35
        else:
            risk += (1 - document_confidence) * 0.35
        
        # Liveness contributes 35% to risk
        if not liveness_valid:
            risk += 0.35
        else:
            risk += (1 - liveness_confidence) * 0.35
        
        # Compliance contributes 30% to risk
        risk += compliance_risk * 0.30
        
        return min(risk, 1.0)
