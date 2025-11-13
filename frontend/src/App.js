import React, { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import './App.css';
import {
  ingestVerification,
  getLivenessChallenge,
  triggerVerification,
  getVerificationStatus,
  getRiskExplanation
} from './services/api';

function App() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    email: '',
    fullName: '',
    dob: '',
    phone: ''
  });
  const [documentFile, setDocumentFile] = useState(null);
  const [videoBlob, setVideoBlob] = useState(null);
  const [challenge, setChallenge] = useState(null);
  const [language, setLanguage] = useState('english');
  const [verificationId, setVerificationId] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recording, setRecording] = useState(false);
  
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleDocumentUpload = (e) => {
    if (e.target.files && e.target.files[0]) {
      setDocumentFile(e.target.files[0]);
    }
  };

  const handleNextStep = async () => {
    setError(null);
    
    if (step === 1) {
      // Validate form
      if (!formData.email || !formData.fullName || !formData.dob || !formData.phone) {
        setError('Please fill in all fields');
        return;
      }
      if (!documentFile) {
        setError('Please upload your ID document');
        return;
      }
      setStep(2);
    } else if (step === 2) {
      // Generate challenge
      try {
        setLoading(true);
        const challengeData = await getLivenessChallenge(language);
        setChallenge(challengeData);
        setStep(3);
      } catch (err) {
        setError('Failed to generate challenge: ' + err);
      } finally {
        setLoading(false);
      }
    } else if (step === 3) {
      // Submit verification
      if (!videoBlob) {
        setError('Please record your video response');
        return;
      }
      await submitVerification();
    }
  };

  const handlePrevStep = () => {
    setError(null);
    setStep(step - 1);
  };

  const startRecording = () => {
    setRecording(true);
    chunksRef.current = [];
    
    const stream = webcamRef.current.stream;
    mediaRecorderRef.current = new MediaRecorder(stream, {
      mimeType: 'video/webm'
    });
    
    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        chunksRef.current.push(event.data);
      }
    };
    
    mediaRecorderRef.current.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'video/webm' });
      setVideoBlob(blob);
    };
    
    mediaRecorderRef.current.start();
  };

  const stopRecording = () => {
    setRecording(false);
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
  };

  const submitVerification = async () => {
    try {
      setLoading(true);
      setError(null);

      // Create form data
      const formDataToSend = new FormData();
      formDataToSend.append('email', formData.email);
      formDataToSend.append('full_name', formData.fullName);
      formDataToSend.append('dob', formData.dob);
      formDataToSend.append('phone', formData.phone);
      formDataToSend.append('document_image', documentFile);
      
      // Convert video blob to file
      const videoFile = new File([videoBlob], 'liveness_video.webm', { type: 'video/webm' });
      formDataToSend.append('video', videoFile);

      // Step 1: Ingest
      const ingestResponse = await ingestVerification(formDataToSend);
      setVerificationId(ingestResponse.verification_id);

      // Step 2: Trigger verification
      await new Promise(resolve => setTimeout(resolve, 1000)); // Small delay
      await triggerVerification(ingestResponse.verification_id);

      // Step 3: Get status
      const statusResponse = await getVerificationStatus(ingestResponse.verification_id);
      setVerificationResult(statusResponse);

      // Step 4: Get explanation
      const explanationResponse = await getRiskExplanation(ingestResponse.verification_id);
      setExplanation(explanationResponse);

      setStep(4);
    } catch (err) {
      setError('Verification failed: ' + (err.detail || err.toString()));
    } finally {
      setLoading(false);
    }
  };

  const renderStep1 = () => (
    <div>
      <h2>Personal Information</h2>
      <div className="form-group">
        <label>Email *</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleInputChange}
          placeholder="your.email@example.com"
        />
      </div>
      <div className="form-group">
        <label>Full Name *</label>
        <input
          type="text"
          name="fullName"
          value={formData.fullName}
          onChange={handleInputChange}
          placeholder="John Doe"
        />
      </div>
      <div className="form-group">
        <label>Date of Birth *</label>
        <input
          type="date"
          name="dob"
          value={formData.dob}
          onChange={handleInputChange}
        />
      </div>
      <div className="form-group">
        <label>Phone Number *</label>
        <input
          type="tel"
          name="phone"
          value={formData.phone}
          onChange={handleInputChange}
          placeholder="+1 234 567 8900"
        />
      </div>
      <div className="form-group">
        <label>Upload ID Document *</label>
        <div className="file-input-wrapper">
          <input
            type="file"
            id="document"
            accept="image/*"
            onChange={handleDocumentUpload}
          />
          <label htmlFor="document" className="file-input-label">
            {documentFile ? '✓ Document uploaded' : '📄 Click to upload ID document'}
          </label>
        </div>
        {documentFile && (
          <div className="file-preview">
            {documentFile.name}
          </div>
        )}
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div>
      <h2>Language Selection</h2>
      <p>Choose your preferred language for the liveness challenge:</p>
      <div className="form-group">
        <label>Select Language</label>
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="english">English</option>
          <option value="hindi">Hindi (हिंदी)</option>
          <option value="tamil">Tamil (தமிழ்)</option>
        </select>
      </div>
      <div className="challenge-box">
        <h3>📹 Next Step: Video Liveness Check</h3>
        <p>You will be asked to perform a simple challenge on camera to verify you are a real person.</p>
        <p>This helps prevent deepfakes and pre-recorded videos.</p>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div>
      <h2>Liveness Verification</h2>
      {challenge && (
        <div className="challenge-box">
          <h3>Your Challenge:</h3>
          <div className="challenge-text">{challenge.challenge_text}</div>
          <p>Please perform this action clearly on camera</p>
        </div>
      )}
      <div className="webcam-container">
        <Webcam
          ref={webcamRef}
          audio={true}
          muted={true}
          width={640}
          height={480}
        />
      </div>
      <div style={{ textAlign: 'center', marginTop: '20px' }}>
        {!recording && !videoBlob && (
          <button className="btn btn-primary" onClick={startRecording}>
            🎥 Start Recording
          </button>
        )}
        {recording && (
          <button className="btn btn-secondary" onClick={stopRecording}>
            ⏹ Stop Recording
          </button>
        )}
        {videoBlob && !recording && (
          <div>
            <p style={{ color: '#4caf50', fontWeight: 'bold' }}>✓ Video recorded successfully!</p>
          </div>
        )}
      </div>
    </div>
  );

  const renderStep4 = () => {
    if (!verificationResult || !explanation) return null;

    const getResultClass = () => {
      if (verificationResult.status === 'approved') return 'success';
      if (verificationResult.status === 'rejected') return 'error';
      return 'warning';
    };

    const getResultIcon = () => {
      if (verificationResult.status === 'approved') return '✓';
      if (verificationResult.status === 'rejected') return '✗';
      return '⚠';
    };

    const getResultTitle = () => {
      if (verificationResult.status === 'approved') return 'Verification Approved';
      if (verificationResult.status === 'rejected') return 'Verification Rejected';
      return 'Manual Review Required';
    };

    return (
      <div>
        <div className={`result-box ${getResultClass()}`}>
          <h2>{getResultIcon()} {getResultTitle()}</h2>
          <div className="risk-score">
            Risk Score: {(verificationResult.risk_score * 100).toFixed(1)}%
          </div>
          <p style={{ textAlign: 'center', fontSize: '1.2rem' }}>
            Risk Level: <strong>{verificationResult.risk_level?.toUpperCase()}</strong>
          </p>
        </div>

        <div className="status-grid">
          <div className="status-item">
            <h4>Document</h4>
            <span className={`status-badge ${verificationResult.document_status === 'passed' ? 'passed' : 'failed'}`}>
              {verificationResult.document_status}
            </span>
          </div>
          <div className="status-item">
            <h4>Liveness</h4>
            <span className={`status-badge ${verificationResult.liveness_status === 'passed' ? 'passed' : 'failed'}`}>
              {verificationResult.liveness_status}
            </span>
          </div>
          <div className="status-item">
            <h4>Compliance</h4>
            <span className={`status-badge ${verificationResult.compliance_status === 'passed' ? 'passed' : 'failed'}`}>
              {verificationResult.compliance_status}
            </span>
          </div>
        </div>

        <h3 style={{ marginTop: '30px' }}>Detailed Explanation:</h3>
        <div className="explanation">
          {explanation.explanation}
        </div>

        <p style={{ marginTop: '20px', color: '#666', fontSize: '0.9rem' }}>
          Verification ID: {verificationId}
        </p>
      </div>
    );
  };

  return (
    <div className="verification-container">
      <div className="verification-card">
        <div className="header">
          <h1>🔐 Deep-Verify Engine</h1>
          <p>AI-Powered KYC Verification in 60 Seconds</p>
        </div>

        <div className="step-indicator">
          <div className={`step ${step >= 1 ? 'active' : ''} ${step > 1 ? 'completed' : ''}`}>
            <div className="step-number">1</div>
            <div className="step-label">Information</div>
          </div>
          <div className={`step ${step >= 2 ? 'active' : ''} ${step > 2 ? 'completed' : ''}`}>
            <div className="step-number">2</div>
            <div className="step-label">Language</div>
          </div>
          <div className={`step ${step >= 3 ? 'active' : ''} ${step > 3 ? 'completed' : ''}`}>
            <div className="step-number">3</div>
            <div className="step-label">Liveness</div>
          </div>
          <div className={`step ${step >= 4 ? 'active' : ''}`}>
            <div className="step-number">4</div>
            <div className="step-label">Result</div>
          </div>
        </div>

        {error && (
          <div className="error-message">
            ⚠ {error}
          </div>
        )}

        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Processing your verification...</p>
          </div>
        ) : (
          <>
            {step === 1 && renderStep1()}
            {step === 2 && renderStep2()}
            {step === 3 && renderStep3()}
            {step === 4 && renderStep4()}
          </>
        )}

        {!loading && step < 4 && (
          <div className="button-group">
            {step > 1 && (
              <button className="btn btn-secondary" onClick={handlePrevStep}>
                ← Previous
              </button>
            )}
            <button 
              className="btn btn-primary" 
              onClick={handleNextStep}
              disabled={step === 3 && !videoBlob}
            >
              {step === 3 ? 'Submit Verification' : 'Next →'}
            </button>
          </div>
        )}

        {step === 4 && (
          <div className="button-group">
            <button className="btn btn-primary" onClick={() => window.location.reload()}>
              Start New Verification
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
