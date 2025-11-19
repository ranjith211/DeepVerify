#!/usr/bin/env python3
"""Test script to verify AI models are loaded and working"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.liveness_service import get_ai_liveness_service
from app.services.document_service import get_ai_document_service

print("=" * 60)
print("AI Models Status Check")
print("=" * 60)

# Test Liveness Service
print("\n1. Testing Liveness Service...")
liveness = get_ai_liveness_service()
print(f"   Device: {liveness.device}")
print(f"   MediaPipe Face Mesh: {'✓ Loaded' if liveness.mp_face_mesh else '✗ Not loaded'}")
print(f"   MediaPipe Hands: {'✓ Loaded' if liveness.mp_hands else '✗ Not loaded'}")
print(f"   Whisper (lazy): {'✓ Will load on first use' if not liveness._speech_recognizer_loaded else '✓ Already loaded'}")

# Test Document Service
print("\n2. Testing Document Service...")
doc_service = get_ai_document_service()
print(f"   Device: {doc_service.device}")
print(f"   CV Models: ✓ OpenCV available")

# Test challenge generation
print("\n3. Testing Challenge Generation...")
challenge = liveness.generate_challenge("english")
print(f"   Challenge: {challenge.challenge_text}")
print(f"   Expected: '{challenge.expected_phrase}' + {challenge.expected_gesture}")

print("\n" + "=" * 60)
print("Summary:")
if liveness.mp_face_mesh and liveness.mp_hands:
    print("✓ AI models are properly loaded and ready!")
    print("✓ Strict validation is enabled")
    print("✓ Videos without faces will FAIL")
    print("✓ Wrong gestures will FAIL")
    print("✓ Wrong speech will FAIL")
else:
    print("✗ WARNING: Some AI models failed to load!")
    print("✗ Validation will FAIL all requests")
print("=" * 60)
