import React, { useState, useEffect, useRef } from 'react';
import Webcam from 'react-webcam';
import './App.css';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [showLogin, setShowLogin] = useState(!localStorage.getItem('token'));
  const [userData, setUserData] = useState(null);
  const [sessionExpired, setSessionExpired] = useState(false);
  
  // Auth form states
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authError, setAuthError] = useState('');
  
  // KYC form states
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    fullName: '',
    dob: '',
    phone: ''
  });
  const [documentFile, setDocumentFile] = useState(null);
  const [videoBlob, setVideoBlob] = useState(null);
  const [challenge, setChallenge] = useState(null);
  const [language, setLanguage] = useState('english');
  const [verificationResult, setVerificationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recording, setRecording] = useState(false);
  
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  // Setup axios interceptor for 401 errors
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      response => response,
      error => {
        if (error.response?.status === 401) {
          // Only auto-logout on GET requests (token validation)
          // For POST requests, let the component handle it
          if (error.config?.method?.toLowerCase() === 'get') {
            localStorage.removeItem('token');
            setToken('');
            setIsAuthenticated(false);
            setUserData(null);
            setSessionExpired(true);
          }
        }
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, []);

  useEffect(() => {
    if (token) {
      fetchUserData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const fetchUserData = async (tokenToUse = null) => {
    try {
      const currentToken = tokenToUse || token;
      if (!currentToken) {
        setIsAuthenticated(false);
        return;
      }
      const response = await axios.get(`${API_BASE_URL}/auth/me?token=${currentToken}`);
      setUserData(response.data);
      setIsAuthenticated(true);
    } catch (err) {
      localStorage.removeItem('token');
      setToken('');
      setIsAuthenticated(false);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setAuthError('');
    setLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/signup`, {
        email: authEmail,
        password: authPassword
      });
      
      const newToken = response.data.token;
      setToken(newToken);
      localStorage.setItem('token', newToken);
      setIsAuthenticated(true);
      await fetchUserData(newToken);
    } catch (err) {
      const errorDetail = err.response?.data?.detail;
      if (typeof errorDetail === 'string') {
        setAuthError(errorDetail);
      } else if (Array.isArray(errorDetail)) {
        setAuthError(errorDetail.map(e => e.msg || e).join(', '));
      } else {
        setAuthError('Signup failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError('');
    setLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email: authEmail,
        password: authPassword
      });
      
      const newToken = response.data.token;
      setToken(newToken);
      localStorage.setItem('token', newToken);
      setIsAuthenticated(true);
      await fetchUserData(newToken);
    } catch (err) {
      const errorDetail = err.response?.data?.detail;
      if (typeof errorDetail === 'string') {
        setAuthError(errorDetail);
      } else if (Array.isArray(errorDetail)) {
        setAuthError(errorDetail.map(e => e.msg || e).join(', '));
      } else {
        setAuthError('Login failed. Please check your credentials.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API_BASE_URL}/auth/logout?token=${token}`);
    } catch (err) {
      // Ignore errors
    }
    
    localStorage.removeItem('token');
    setToken('');
    setIsAuthenticated(false);
    setUserData(null);
    setStep(1);
    resetForm();
  };

  const resetForm = () => {
    setFormData({ fullName: '', dob: '', phone: '' });
    setDocumentFile(null);
    setVideoBlob(null);
    setChallenge(null);
    setVerificationResult(null);
    setError(null);
  };

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
      if (!formData.fullName || !formData.dob || !formData.phone) {
        setError('Please fill in all fields');
        return;
      }
      if (!documentFile) {
        setError('Please upload your ID document');
        return;
      }
      setStep(2);
    } else if (step === 2) {
      try {
        setLoading(true);
        const response = await axios.get(`${API_BASE_URL}/challenge/${language}`);
        setChallenge(response.data);
        setStep(3);
      } catch (err) {
        setError('Failed to generate challenge: ' + err.message);
      } finally {
        setLoading(false);
      }
    } else if (step === 3) {
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
    if (!webcamRef.current || !webcamRef.current.stream) {
      setError('Camera not ready. Please allow camera access and try again.');
      return;
    }
    
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
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  };

  const submitVerification = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get fresh token from localStorage
      const currentToken = localStorage.getItem('token') || token;
      
      console.log('Submitting with token:', currentToken ? 'Token exists' : 'No token');
      
      if (!currentToken) {
        setError('Please login again to continue');
        setIsAuthenticated(false);
        return;
      }

      const formDataToSend = new FormData();
      formDataToSend.append('token', currentToken);
      formDataToSend.append('full_name', formData.fullName);
      formDataToSend.append('dob', formData.dob);
      formDataToSend.append('phone', formData.phone);
      formDataToSend.append('document_image', documentFile);
      
      const videoFile = new File([videoBlob], 'liveness_video.webm', { type: 'video/webm' });
      formDataToSend.append('video', videoFile);

      const ingestResponse = await axios.post(`${API_BASE_URL}/ingest`, formDataToSend, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const verificationId = ingestResponse.data.verification_id;

      await new Promise(resolve => setTimeout(resolve, 1000));
      await axios.post(`${API_BASE_URL}/verify/${verificationId}`);

      const statusResponse = await axios.get(`${API_BASE_URL}/status/${verificationId}`);
      setVerificationResult(statusResponse.data);

      // Refresh user data to get updated KYC status
      await fetchUserData();

      setStep(4);
    } catch (err) {
      console.error('Verification error:', err.response?.status, err.response?.data);
      
      // Handle 401 authentication errors
      if (err.response?.status === 401) {
        setError('Session expired. Please click Logout and login again.');
        return;
      }
      setError('Verification failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const getKYCRecommendations = () => {
    if (!userData?.latest_verification) return [];
    
    const recommendations = [];
    const verification = userData.latest_verification;
    
    // Parse rejection_reason which contains structured suggestions for user
    if (verification.rejection_reason) {
      const sections = verification.rejection_reason.split('\n\n');
      sections.forEach(section => {
        const lines = section.split('\n');
        if (lines.length > 0) {
          const title = lines[0];
          const items = lines.slice(1).filter(line => line.trim());
          if (items.length > 0) {
            recommendations.push({ title, items });
          }
        }
      });
    }
    
    // Fallback to basic recommendations if no admin notes
    if (recommendations.length === 0) {
      if (verification.document_status === 'failed') {
        recommendations.push({
          title: '📄 Document Quality',
          items: [
            '• Use a high-resolution camera or scanner',
            '• Ensure good lighting - no shadows or glare',
            '• Keep the document flat and fully visible',
            '• Make sure all text is clear and readable',
            '• Use the original document, not a photocopy'
          ]
        });
      }
      
      if (verification.liveness_status === 'failed') {
        recommendations.push({
          title: '🎥 Liveness Check',
          items: [
            '• Record in a well-lit environment',
            '• Ensure your face is clearly visible',
            '• Speak clearly and match the exact phrase shown',
            '• Perform the exact gesture requested',
            '• Avoid pre-recorded videos or photos'
          ]
        });
      }
    }
    
    return recommendations;
  };

  // Auth Screen
  if (!isAuthenticated) {
    return (
      <div className="auth-container">
        <div className="auth-box">
          <h1>🔐 DeepVerify KYC</h1>
          {sessionExpired && (
            <div className="session-expired-banner">
              ⚠️ Your session has expired. Please login again.
            </div>
          )}
          <div className="auth-tabs">
            <button
              className={showLogin ? 'active' : ''}
              onClick={() => { setShowLogin(true); setAuthError(''); setSessionExpired(false); }}
            >
              Login
            </button>
            <button
              className={!showLogin ? 'active' : ''}
              onClick={() => { setShowLogin(false); setAuthError(''); setSessionExpired(false); }}
            >
              Sign Up
            </button>
          </div>
          
          <form onSubmit={showLogin ? handleLogin : handleSignup}>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={authEmail}
                onChange={(e) => setAuthEmail(e.target.value)}
                placeholder="Enter your email"
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={authPassword}
                onChange={(e) => setAuthPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />
            </div>
            {authError && <div className="error-message">{authError}</div>}
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Please wait...' : (showLogin ? 'Login' : 'Sign Up')}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Dashboard Screen
  if (userData && (userData.kyc_status !== 'not_started' || verificationResult)) {
    const kycStatus = userData.kyc_status;
    const latestVerification = userData.latest_verification;
    const recommendations = getKYCRecommendations();
    
    return (
      <div className="dashboard-container">
        <header className="dashboard-header">
          <h1>Welcome, {userData.full_name || userData.email}</h1>
          <button onClick={handleLogout} className="btn-logout">Logout</button>
        </header>

        <div className="dashboard-content">
          <div className={`kyc-status-card ${kycStatus}`}>
            <h2>KYC Status</h2>
            <div className="status-badge-large">
              {kycStatus === 'approved' && '✅ Approved'}
              {kycStatus === 'pending' && '⏳ Under Review'}
              {kycStatus === 'rejected' && '❌ Rejected'}
              {kycStatus === 'not_started' && '🔄 Not Started'}
            </div>
            
            {kycStatus === 'approved' && (
              <p className="status-message success">
                Your identity has been verified successfully! Your account is ready to use.
              </p>
            )}
            
            {kycStatus === 'pending' && (
              <>
                <p className="status-message pending">
                  Your KYC is under review by our admin team. We'll notify you once it's processed.
                </p>
                {latestVerification && latestVerification.admin_status === 'pending_review' && (
                  <div className="pending-review-info">
                    <div className="info-icon">⏳</div>
                    <div className="info-content">
                      <h3>Awaiting Admin Review</h3>
                      <p>Your submission has been received and is in the queue for manual verification. This typically takes 1-2 business days.</p>
                    </div>
                  </div>
                )}
              </>
            )}
            
            {kycStatus === 'rejected' && (
              <>
                <p className="status-message error">
                  Your KYC submission was rejected. Please review the detailed recommendations below.
                </p>
                <div className="rejection-alert">
                  <div className="alert-icon">⚠️</div>
                  <div className="alert-content">
                    <h3>Action Required</h3>
                    <p>Please carefully read all suggestions below and address each issue before resubmitting your KYC application.</p>
                  </div>
                </div>
              </>
            )}
          </div>

          {latestVerification && (
            <div className="verification-details">
              <h3>Latest Submission Details</h3>
              <div className="detail-grid">
                <div className="detail-item">
                  <span className="label">Submitted:</span>
                  <span>{new Date(latestVerification.created_at).toLocaleString()}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Document Check:</span>
                  <span className={`badge ${latestVerification.document_status}`}>
                    {latestVerification.document_status}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="label">Liveness Check:</span>
                  <span className={`badge ${latestVerification.liveness_status}`}>
                    {latestVerification.liveness_status}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="label">Risk Level:</span>
                  <span className={`badge ${latestVerification.risk_level}`}>
                    {latestVerification.risk_level}
                  </span>
                </div>
              </div>
            </div>
          )}

          {recommendations.length > 0 && (
            <div className="recommendations">
              <h3>📋 Recommendations for Successful Re-submission</h3>
              <div className="recommendations-intro">
                <p>Our AI-powered system has identified the following areas that need your attention. Please address each recommendation carefully to ensure your next submission is successful.</p>
                {latestVerification && (
                  <div className="failure-summary">
                    <strong>Issues Detected:</strong>
                    {latestVerification.document_status === 'failed' && <span className="issue-tag">📄 Document</span>}
                    {latestVerification.liveness_status === 'failed' && <span className="issue-tag">🎥 Liveness</span>}
                    {latestVerification.compliance_status === 'failed' && <span className="issue-tag">⚖️ Compliance</span>}
                  </div>
                )}
              </div>
              {recommendations.map((rec, idx) => (
                <div key={idx} className="recommendation-section">
                  <h4>{rec.title}</h4>
                  <ul>
                    {rec.items.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}

          {(kycStatus === 'rejected' || kycStatus === 'not_started') && (
            <button
              onClick={() => { 
                resetForm(); 
                setStep(1); 
                setVerificationResult(null);
                // Update userData to allow re-entry to KYC form
                setUserData({ ...userData, kyc_status: 'not_started' });
              }}
              className="btn-resubmit"
            >
              {kycStatus === 'rejected' ? '🔄 Resubmit KYC' : '▶️ Start KYC Process'}
            </button>
          )}
        </div>
      </div>
    );
  }

  // KYC Process (existing code - step 1, 2, 3, 4)
  return (
    <div className="verification-container">
      <div className="verification-card">
        <header className="header">
          <h1>DeepVerify</h1>
          <p>Secure Identity Verification</p>
          <button onClick={handleLogout} className="btn-logout-small">Logout</button>
        </header>

        <div className="step-indicator">
          <div className={`step ${step >= 1 ? 'active completed' : ''}`}>
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
          <div className={`step ${step >= 4 ? 'active completed' : ''}`}>
            <div className="step-number">4</div>
            <div className="step-label">Result</div>
          </div>
        </div>

        <div className="form-content">
        {loading && (
          <div className="loading-overlay">
            <div className="spinner"></div>
            <p>Processing...</p>
          </div>
        )}

        {error && (
          <div className="error-box">
            {error}
          </div>
        )}

        {step === 1 && (
          <div>
            <h2>Personal Information</h2>
            <div className="form-group">
              <label>Full Name *</label>
              <input
                type="text"
                name="fullName"
                value={formData.fullName}
                onChange={handleInputChange}
                placeholder="Enter your full name"
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
                placeholder="Enter your phone number"
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
        )}

        {step === 2 && (
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
            </div>
          </div>
        )}

        {step === 3 && (
          <div>
            <h2>Liveness Verification</h2>
            {challenge && (
              <div className="challenge-box">
                <h3>Your Challenge:</h3>
                <div className="challenge-text">{challenge.challenge_text}</div>
              </div>
            )}
            <div className="webcam-container">
              <Webcam
                ref={webcamRef}
                audio={true}
                mirrored={true}
                className="webcam"
              />
            </div>
            <div className="recording-controls">
              {!recording && !videoBlob && (
                <button onClick={startRecording} className="btn-record">
                  🔴 Start Recording
                </button>
              )}
              {recording && (
                <button onClick={stopRecording} className="btn-stop">
                  ⏹️ Stop Recording
                </button>
              )}
              {videoBlob && (
                <div className="recording-complete">
                  ✓ Video recorded successfully
                </div>
              )}
            </div>
          </div>
        )}

        {step === 4 && verificationResult && (
          <div>
            {verificationResult.status === 'approved' && 
             verificationResult.document_status === 'passed' && 
             verificationResult.liveness_status === 'passed' ? (
              <div className="result-box success">
                <h2>✅ Verification Passed Successfully!</h2>
                <p style={{ fontSize: '1.2rem', color: '#28a745', marginTop: '20px' }}>
                  Your identity has been successfully verified!
                </p>
                <p style={{ marginTop: '15px', color: '#666' }}>
                  All checks passed. Your account is ready to use.
                </p>
              </div>
            ) : (
              <div className="result-box warning">
                <h2>👤 Human Check Needed</h2>
                <p style={{ fontSize: '1.2rem', color: '#ff9800', marginTop: '20px' }}>
                  Your submission requires manual review
                </p>
                <p style={{ marginTop: '15px', color: '#666' }}>
                  Our team will review your information and get back to you shortly.
                </p>
              </div>
            )}
            <button onClick={() => window.location.reload()} className="btn-primary" style={{ marginTop: '20px' }}>
              Go to Dashboard
            </button>
          </div>
        )}

        <div className="button-group">
          {step > 1 && step < 4 && (
            <button onClick={handlePrevStep} className="btn-secondary">
              ← Previous
            </button>
          )}
          {step < 3 && (
            <button onClick={handleNextStep} className="btn-primary">
              Next →
            </button>
          )}
          {step === 3 && videoBlob && (
            <button 
              onClick={submitVerification} 
              className="btn-primary"
              disabled={loading}
            >
              {loading ? 'Submitting...' : 'Submit Verification'}
            </button>
          )}
        </div>
      </div>
    </div>
    </div>
  );
}

export default App;
