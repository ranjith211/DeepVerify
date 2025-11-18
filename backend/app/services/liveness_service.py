import random
import os
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
    def validate_liveness(video_path: str, challenge: Dict, face_count: int = None) -> Tuple[bool, float, Dict]:
        """
        Mock validation of liveness video against challenge with file validation
        Returns: (is_valid, confidence_score, analysis_details)
        
        Args:
            video_path: Path to the video file
            challenge: Challenge dictionary
            face_count: Number of faces detected in the video (None means not checked)
        """
        # KYC Requirement: Exactly 1 face must be detected
        if face_count is not None:
            if face_count == 0:
                return False, 0.0, {
                    "lip_sync_match": False,
                    "lip_sync_confidence": 0.0,
                    "gesture_detected": False,
                    "gesture_confidence": 0.0,
                    "audio_match": False,
                    "audio_confidence": 0.0,
                    "deepfake_probability": 0.98,
                    "video_quality": "failed",
                    "face_count": 0,
                    "analysis_notes": "KYC FAILED: No face detected in video - verification cannot proceed"
                }
            elif face_count > 1:
                return False, 0.0, {
                    "lip_sync_match": False,
                    "lip_sync_confidence": 0.0,
                    "gesture_detected": False,
                    "gesture_confidence": 0.0,
                    "audio_match": False,
                    "audio_confidence": 0.0,
                    "deepfake_probability": 0.95,
                    "video_quality": "failed",
                    "face_count": face_count,
                    "analysis_notes": f"KYC FAILED: Multiple faces detected ({face_count}) - only one person allowed for verification"
                }
        
        # Check if video file exists and has content
        if not os.path.exists(video_path):
            return False, 0.0, {
                "lip_sync_match": False,
                "lip_sync_confidence": 0.0,
                "gesture_detected": False,
                "gesture_confidence": 0.0,
                "audio_match": False,
                "audio_confidence": 0.0,
                "deepfake_probability": 0.95,
                "video_quality": "error",
                "face_count": face_count,
                "analysis_notes": "Video file not found or invalid"
            }
        
        # Check file size (video should be reasonable size)
        file_size = os.path.getsize(video_path)
        
        # Blank screen or very short video (< 10KB)
        if file_size < 10 * 1024:
            return False, 0.15, {
                "lip_sync_match": False,
                "lip_sync_confidence": 0.10,
                "gesture_detected": False,
                "gesture_confidence": 0.05,
                "audio_match": False,
                "audio_confidence": 0.08,
                "deepfake_probability": 0.95,
                "video_quality": "poor",
                "face_count": face_count,
                "analysis_notes": "Video too short or blank screen detected - no person visible"
            }
        
        # Very small video (< 50KB) - likely static or minimal content
        if file_size < 50 * 1024:
            return False, 0.25, {
                "lip_sync_match": False,
                "lip_sync_confidence": 0.20,
                "gesture_detected": False,
                "gesture_confidence": 0.15,
                "audio_match": False,
                "audio_confidence": 0.25,
                "deepfake_probability": 0.85,
                "video_quality": "suspicious",
                "face_count": face_count,
                "analysis_notes": "Minimal video content - possible static image or pre-recorded loop"
            }
        
        # Mock implementation with weighted probability based on file size
        if file_size < 100 * 1024:  # Less than 100KB
            is_valid = random.random() > 0.60  # 40% pass rate
        elif file_size < 500 * 1024:  # Less than 500KB
            is_valid = random.random() > 0.30  # 70% pass rate
        else:
            is_valid = random.random() > 0.15  # 85% pass rate for normal videos
        
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
            "face_count": face_count if face_count is not None else 1,
            "analysis_notes": "Genuine live video" if is_valid else "Potential deepfake or pre-recorded content detected"
        }
        
        return is_valid, confidence, analysis
