import React, { useRef, useEffect, useState, forwardRef, useImperativeHandle } from 'react';
import Webcam from 'react-webcam';
import * as faceapi from 'face-api.js';

const FaceDetectionWebcam = forwardRef((props, ref) => {
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [faceCount, setFaceCount] = useState(0);
  const intervalRef = useRef(null);

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

    loadModels();

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

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
      setFaceCount(detections.length);

      // Clear canvas
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);

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
