# Real-Time Face Detection & Tracing

## Overview
The Deep-Verify Engine now includes real-time face detection with visual tracing during the liveness verification step. This enhances security by ensuring only one person is present during verification.

## Features

### 1. **Live Face Detection**
- Uses face-api.js with TinyFaceDetector for real-time detection
- Runs at ~10 FPS for smooth performance
- Detects multiple faces simultaneously

### 2. **Visual Face Tracing**
- **68-point facial landmarks** displayed as dots on detected faces
- **Face mesh overlay** showing:
  - Jaw outline
  - Eyebrows (left & right)
  - Nose bridge
  - Eyes (left & right) - closed contours
  - Mouth - closed contour
- **Bounding box** around each detected face

### 3. **Multi-Face Detection with Red Alert**
- **1 Face Detected (Valid):**
  - Green bounding box
  - Green landmarks
  - Green badge: "✓ 1 face detected"
  - Semi-transparent green overlay
  
- **Multiple Faces Detected (Security Risk):**
  - **RED** bounding boxes (all faces)
  - **RED** landmarks (all faces)
  - **RED** alert badge: "⚠️ X faces detected - Only 1 allowed!"
  - Semi-transparent red overlay
  
- **No Face Detected:**
  - Orange warning badge: "⚠️ No face detected"
  - No overlays

### 4. **Real-Time Face Count**
- Badge in top-right corner of webcam showing:
  - Current number of faces detected
  - Color-coded status (green/red/orange)
  - Clear warning when multiple faces present

## Technical Implementation

### Models Used
- **TinyFaceDetector**: Lightweight CNN for fast face detection (~190KB)
- **FaceLandmark68Net**: 68-point facial landmark detection (~350KB)
- **FaceRecognitionNet**: Face recognition capabilities (~6.5MB total)

All models are pre-loaded in `frontend/public/models/`

### Component Architecture
```
FaceDetectionWebcam (React Component)
├── Face Detection Loop (100ms interval)
├── Canvas Overlay (for drawing)
├── Face Count State (0, 1, 2+)
└── Color Logic (green/red/orange)
```

### Integration Points
- **Step 3** of verification wizard (Liveness Verification)
- Replaces standard Webcam component
- Maintains all recording functionality
- ForwardRef pattern for parent component access

## Security Benefits

1. **Prevents Group Verification**
   - Immediately alerts if multiple people try to verify together
   - Red highlighting makes it visually obvious

2. **Visual Feedback**
   - User knows exactly what the system sees
   - Can adjust positioning if no face detected

3. **Audit Trail**
   - Face count can be logged with verification attempt
   - Suspicious patterns (multiple faces) can trigger additional reviews

4. **Deepfake Prevention Enhancement**
   - Multiple faces in frame = potential screen sharing attack
   - Live detection harder to bypass than static images

## User Experience

### Warning Message
```
⚠️ Make sure only YOUR face is visible. 
Multiple faces will be highlighted in RED.
```

### Visual States
1. **Loading**: "Loading face detection..." overlay
2. **No Face**: Orange badge, no tracing
3. **Valid (1 face)**: Green box + landmarks
4. **Invalid (2+ faces)**: Red boxes + landmarks + warning

## Performance

- **Detection Speed**: ~100ms per frame (10 FPS)
- **Model Load Time**: 2-3 seconds on first load
- **Browser Compatibility**: Chrome, Firefox, Safari, Edge (WebGL required)
- **Mobile Support**: Yes (may be slower on older devices)

## Future Enhancements

1. **Face Quality Checks**
   - Blur detection
   - Lighting quality
   - Face angle/pose validation

2. **Liveness Integration**
   - Verify face movement matches challenge
   - Eye blink detection
   - Smile/expression verification

3. **Age/Gender Detection**
   - Compare with document data
   - Additional verification layer

4. **Recording with Annotations**
   - Save video with face boxes overlaid
   - Include face count in metadata

## Testing

### Test Scenarios
1. ✅ Single face - should show green
2. ✅ Two people in frame - should show red
3. ✅ Photo of a face (on phone/screen) - may detect, but liveness will fail
4. ✅ No face visible - should show orange warning
5. ✅ Face partially visible - may detect if enough landmarks visible

### Demo Flow
1. Navigate to Step 3 (Liveness Verification)
2. Allow camera access
3. Wait for "Loading face detection..." to disappear
4. Position face in frame
5. Observe green box and landmarks
6. Ask someone to join frame
7. Observe both faces turn RED
8. Person leaves frame
9. Face returns to GREEN

## Browser Console Messages

Expected console output:
```
Loading face detection models...
Models loaded successfully
Face detection started (10 FPS)
Detected 1 face(s)
```

No errors should appear unless:
- Camera access denied
- WebGL not supported
- Model files not found (check `/models` directory)

## Known Limitations

1. **Glasses/Masks**: May reduce landmark accuracy
2. **Low Light**: Face detection may fail
3. **Side Profile**: Works best with frontal faces (±45°)
4. **Distance**: Face should be at least 100px wide
5. **Source Maps**: 175 warnings from face-api.js (cosmetic, not functional)

## Files Modified

- `frontend/package.json` - Added face-api.js dependency
- `frontend/src/App.js` - Integrated FaceDetectionWebcam
- `frontend/src/components/FaceDetectionWebcam.js` - New component
- `frontend/public/models/` - 7 model weight files

## Dependencies

```json
"face-api.js": "^0.22.2"
```

Total size: ~7MB (models)
Runtime memory: ~50MB

---

**Status**: ✅ Fully Implemented and Tested
**Date**: November 18, 2025
**Version**: 1.0.0
