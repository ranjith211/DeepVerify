import random
from typing import Dict, Tuple
from app.models.schemas import LivenessChallenge

class LivenessService:
    """Mock service for generating and validating liveness challenges"""
    
    PHRASES = {
        "english": ["blue cat", "red car", "green tree", "yellow sun", "purple moon"],
        "hindi": ["नीली बिल्ली", "लाल गाड़ी", "हरा पेड़", "पीला सूरज", "बैंगनी चाँद"],
        "tamil": ["நீல பூனை", "சிவப்பு கார்", "பச்சை மரம்", "மஞ்சள் சூரியன்", "ஊதா நிலவு"]
    }
    
    GESTURES = [
        "hold up one finger",
        "hold up two fingers", 
        "hold up three fingers",
        "make a thumbs up",
        "wave your hand"
    ]
    
    @staticmethod
    def generate_challenge(language: str = "english") -> LivenessChallenge:
        """Generate a random liveness challenge"""
        if language not in LivenessService.PHRASES:
            language = "english"
        
        phrase = random.choice(LivenessService.PHRASES[language])
        gesture = random.choice(LivenessService.GESTURES)
        
        challenge_text = f"Say '{phrase}' and {gesture}"
        
        return LivenessChallenge(
            challenge_text=challenge_text,
            challenge_language=language,
            expected_gesture=gesture,
            expected_phrase=phrase
        )
    
    @staticmethod
    def validate_liveness(video_path: str, challenge: Dict) -> Tuple[bool, float, Dict]:
        """
        Mock validation of liveness video against challenge
        Returns: (is_valid, confidence_score, analysis_details)
        """
        # Mock implementation - randomly pass/fail with weighted probability
        is_valid = random.random() > 0.15  # 85% pass rate
        confidence = random.uniform(0.75, 0.98) if is_valid else random.uniform(0.20, 0.60)
        
        analysis = {
            "lip_sync_match": is_valid,
            "lip_sync_confidence": confidence,
            "gesture_detected": is_valid,
            "gesture_confidence": confidence if is_valid else confidence * 0.8,
            "audio_match": is_valid,
            "audio_confidence": confidence if is_valid else confidence * 0.9,
            "deepfake_probability": 0.05 if is_valid else random.uniform(0.6, 0.9),
            "video_quality": "good" if is_valid else "suspicious",
            "analysis_notes": "Genuine live video" if is_valid else "Potential deepfake or pre-recorded content detected"
        }
        
        return is_valid, confidence, analysis
