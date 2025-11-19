import sys
sys.path.insert(0, '.')

from app.services.liveness_service import get_ai_liveness_service
from app.services.document_service import get_ai_document_service

print("Testing AI Services...")
print("="*60)

# Test liveness
liveness = get_ai_liveness_service()
print(f"Liveness Service: MediaPipe={'✓' if liveness.mp_face_mesh else '✗'}")

# Test document  
doc_service = get_ai_document_service()
print(f"Document Service: OCR={'✓' if doc_service else '✗'}")

# Simulate validation
test_challenge = {
    "expected_phrase": "test phrase",
    "expected_gesture": "hold up one finger"
}

print("\nTesting with non-existent video (should fail)...")
try:
    is_valid, conf, analysis = liveness.validate_liveness("fake_video.mp4", test_challenge)
    print(f"Result: Valid={is_valid}, Confidence={conf:.2%}")
    print(f"Analysis: {analysis.get('analysis_notes', 'N/A')}")
except Exception as e:
    print(f"Error: {e}")

print("="*60)
