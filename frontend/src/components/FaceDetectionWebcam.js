import React, { useRef, useEffect, useState, forwardRef, useImperativeHandle } from 'react';
import Webcam from 'react-webcam';
import * as faceapi from 'face-api.js';
import { Hands, HAND_CONNECTIONS } from '@mediapipe/hands';

const FaceDetectionWebcam = forwardRef((props, ref) => {
  const { onFaceCountChange, onGestureDetected } = props;
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [faceCount, setFaceCount] = useState(0);
  const [gestureDetected, setGestureDetected] = useState(null);
  const intervalRef = useRef(null);
  const handsRef = useRef(null);

  // Expose webcamRef to parent component
  useImperativeHandle(ref, () => webcamRef.current);

  useEffect(() => {
    // Load face-api models
    const loadModels = async () => {
      const MODEL_URL = process.env.PUBLIC_URL + '/models';
      try {
        await Promise.all([
          faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
          faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
          faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL)
        ]);
        setModelsLoaded(true);
      } catch (error) {
        console.error('Error loading face detection models:', error);
      }
    };

    // Initialize MediaPipe Hands
    const initializeHands = () => {
      const hands = new Hands({
        locateFile: (file) => {
          return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
        }
      });

      hands.setOptions({
        maxNumHands: 2,
        modelComplexity: 1,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
      });

      hands.onResults(onHandsResults);
      handsRef.current = hands;
    };

    loadModels();
    initializeHands();

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (handsRef.current) {
        handsRef.current.close();
      }
    };
  }, []);

  const detectThumbsUp = (landmarks) => {
    if (!landmarks || landmarks.length === 0) return false;

    // Hand landmarks indices (MediaPipe Hands)
    // Thumb: 1-4, Index: 5-8, Middle: 9-12, Ring: 13-16, Pinky: 17-20
    const handLandmarks = landmarks[0];
    
    const thumbTip = handLandmarks.landmark[4];
    const thumbIp = handLandmarks.landmark[3];
    const indexTip = handLandmarks.landmark[8];
    const indexMcp = handLandmarks.landmark[5];
    const middleTip = handLandmarks.landmark[12];
    const ringTip = handLandmarks.landmark[16];
    const pinkyTip = handLandmarks.landmark[20];
    const wrist = handLandmarks.landmark[0];

    // Thumbs up detection logic:
    // 1. Thumb is extended (tip higher than IP joint)
    // 2. Other fingers are curled down
    // 3. Hand orientation is upright

    const thumbExtended = thumbTip.y < thumbIp.y - 0.05;
    const indexCurled = indexTip.y > indexMcp.y;
    const middleCurled = middleTip.y > wrist.y - 0.05;
    const ringCurled = ringTip.y > wrist.y - 0.05;
    const pinkyCurled = pinkyTip.y > wrist.y - 0.05;

    return thumbExtended && indexCurled && middleCurled && ringCurled && pinkyCurled;
  };

  const onHandsResults = (results) => {
    const gesture = detectThumbsUp(results.multiHandLandmarks);
    setGestureDetected(gesture);
    
    if (onGestureDetected) {
      onGestureDetected(gesture);
    }

    // Draw hand landmarks on canvas
    if (results.multiHandLandmarks && canvasRef.current) {
      const ctx = canvasRef.current.getContext('2d');
      
      results.multiHandLandmarks.forEach((landmarks) => {
        // Draw connections
        ctx.strokeStyle = gesture ? '#00ff00' : '#ffff00';
        ctx.lineWidth = 2;
        
        HAND_CONNECTIONS.forEach(([start, end]) => {
          const startPoint = landmarks[start];
          const endPoint = landmarks[end];
          
          ctx.beginPath();
          ctx.moveTo(startPoint.x * canvasRef.current.width, startPoint.y * canvasRef.current.height);
          ctx.lineTo(endPoint.x * canvasRef.current.width, endPoint.y * canvasRef.current.height);
          ctx.stroke();
        });

        // Draw landmarks
        ctx.fillStyle = gesture ? '#00ff00' : '#ffff00';
        landmarks.forEach((landmark) => {
          ctx.beginPath();
          ctx.arc(
            landmark.x * canvasRef.current.width,
            landmark.y * canvasRef.current.height,
            5,
            0,
            2 * Math.PI
          );
          ctx.fill();
        });
      });
    }
  };

  const detectFaces = React.useCallback(async () => {
    if (
      webcamRef.current &&
      webcamRef.current.video &&
      webcamRef.current.video.readyState === 4 &&
      canvasRef.current
    ) {
      const video = webcamRef.current.video;
      const canvas = canvasRef.current;

      // Set canvas dimensions to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Detect faces
      const detections = await faceapi
        .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
        .withFaceLandmarks();

      // Update face count
      const currentFaceCount = detections.length;
      setFaceCount(currentFaceCount);
      
      // Notify parent component of face count change
      if (onFaceCountChange) {
        onFaceCountChange(currentFaceCount);
      }

      // Clear canvas
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Process hand detection
      if (handsRef.current && webcamRef.current && webcamRef.current.video) {
        await handsRef.current.send({ image: webcamRef.current.video });
      }

      if (detections.length > 0) {
        // Draw face boxes and landmarks
        detections.forEach((detection) => {
          const box = detection.detection.box;
          const landmarks = detection.landmarks;

          // Determine color based on number of faces
          const strokeColor = detections.length > 1 ? '#ff0000' : '#00ff00';
          const fillColor = detections.length > 1 ? 'rgba(255, 0, 0, 0.2)' : 'rgba(0, 255, 0, 0.2)';

          // Draw bounding box
          ctx.strokeStyle = strokeColor;
          ctx.lineWidth = 3;
          ctx.strokeRect(box.x, box.y, box.width, box.height);

          // Fill box with semi-transparent color
          ctx.fillStyle = fillColor;
          ctx.fillRect(box.x, box.y, box.width, box.height);

          // Draw face landmarks (68 points)
          const drawLandmarks = landmarks.positions;
          ctx.fillStyle = strokeColor;
          drawLandmarks.forEach((point) => {
            ctx.beginPath();
            ctx.arc(point.x, point.y, 2, 0, 2 * Math.PI);
            ctx.fill();
          });

          // Draw face mesh lines
          ctx.strokeStyle = strokeColor;
          ctx.lineWidth = 1;
          
          // Jaw line
          drawContour(ctx, landmarks.getJawOutline());
          // Left eyebrow
          drawContour(ctx, landmarks.getLeftEyeBrow());
          // Right eyebrow
          drawContour(ctx, landmarks.getRightEyeBrow());
          // Nose
          drawContour(ctx, landmarks.getNose());
          // Left eye
          drawContour(ctx, landmarks.getLeftEye(), true);
          // Right eye
          drawContour(ctx, landmarks.getRightEye(), true);
          // Mouth
          drawContour(ctx, landmarks.getMouth(), true);
        });
      }
    }
  }, []);

  useEffect(() => {
    if (modelsLoaded) {
      // Start face detection loop
      intervalRef.current = setInterval(async () => {
        await detectFaces();
      }, 100); // Run every 100ms for smooth detection
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [modelsLoaded, detectFaces]);

  const drawContour = (ctx, points, closePath = false) => {
    if (points.length < 2) return;
    
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    
    for (let i = 1; i < points.length; i++) {
      ctx.lineTo(points[i].x, points[i].y);
    }
    
    if (closePath) {
      ctx.closePath();
    }
    
    ctx.stroke();
  };

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <Webcam
        ref={webcamRef}
        audio={true}
        muted={true}
        width={640}
        height={480}
        style={{ borderRadius: '8px' }}
      />
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          borderRadius: '8px'
        }}
      />
      <div
        style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          background: faceCount > 1 ? 'rgba(255, 0, 0, 0.8)' : faceCount === 1 ? 'rgba(0, 255, 0, 0.8)' : 'rgba(255, 165, 0, 0.8)',
          color: 'white',
          padding: '8px 16px',
          borderRadius: '4px',
          fontWeight: 'bold',
          fontSize: '14px'
        }}
      >
        {faceCount === 0 && '⚠️ No face detected'}
        {faceCount === 1 && '✓ 1 face detected'}
        {faceCount > 1 && `⚠️ ${faceCount} faces detected - Only 1 allowed!`}
      </div>
      {/* Gesture detection badge */}
      <div
        style={{
          position: 'absolute',
          top: '60px',
          right: '10px',
          background: gestureDetected ? 'rgba(0, 255, 0, 0.8)' : 'rgba(128, 128, 128, 0.8)',
          color: 'white',
          padding: '8px 16px',
          borderRadius: '4px',
          fontWeight: 'bold',
          fontSize: '14px'
        }}
      >
        {gestureDetected ? '👍 Thumbs Up Detected!' : '👍 Show Thumbs Up'}
      </div>
      {!modelsLoaded && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            background: 'rgba(0, 0, 0, 0.7)',
            color: 'white',
            padding: '16px 24px',
            borderRadius: '8px',
            fontWeight: 'bold'
          }}
        >
          Loading face detection...
        </div>
      )}
    </div>
  );
});

export default FaceDetectionWebcam;
