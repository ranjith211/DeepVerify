import React, { useState, useEffect } from 'react';
import './Admin.css';
import './Modern.css';

function Admin() {
  const [authenticated, setAuthenticated] = useState(localStorage.getItem('adminAuthenticated') === 'true');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [adminNotes, setAdminNotes] = useState('');

  // Load submissions on mount if already authenticated
  useEffect(() => {
    if (authenticated) {
      fetchSubmissions();
    }
  }, []);

  const handleLogin = (e) => {
    e.preventDefault();
    if (username === 'admin' && password === 'admin') {
      localStorage.setItem('adminAuthenticated', 'true');
      setAuthenticated(true);
      setError('');
      fetchSubmissions();
    } else {
      setError('Invalid username or password');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('adminAuthenticated');
    setAuthenticated(false);
    setSubmissions([]);
    setSelectedSubmission(null);
  };

  const fetchSubmissions = async () => {
    setLoading(true);
    try {
      const auth = btoa('admin:admin'); // Base64 encode credentials
      const response = await fetch('http://localhost:8000/api/admin/kyc-submissions', {
        headers: {
          'Authorization': `Basic ${auth}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch submissions');
      
      const data = await response.json();
      setSubmissions(data.submissions);
    } catch (err) {
      setError('Failed to load submissions: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (verificationId) => {
    try {
      const auth = btoa('admin:admin');
      const response = await fetch(`http://localhost:8000/api/admin/kyc-submissions/${verificationId}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${auth}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ notes: adminNotes })
      });
      
      if (!response.ok) throw new Error('Failed to approve');
      
      alert('KYC Approved Successfully!');
      setAdminNotes('');
      setSelectedSubmission(null);
      fetchSubmissions();
    } catch (err) {
      alert('Error approving: ' + err.message);
    }
  };

  const handleReject = async (verificationId) => {
    if (!adminNotes.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }
    
    try {
      const auth = btoa('admin:admin');
      const response = await fetch(`http://localhost:8000/api/admin/kyc-submissions/${verificationId}/reject`, {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${auth}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ notes: adminNotes })
      });
      
      if (!response.ok) throw new Error('Failed to reject');
      
      alert('KYC Rejected');
      setAdminNotes('');
      setSelectedSubmission(null);
      fetchSubmissions();
    } catch (err) {
      alert('Error rejecting: ' + err.message);
    }
  };

  const getStatusColor = (status) => {
    if (status === 'passed' || status === 'approved') return '#28a745';
    if (status === 'failed' || status === 'rejected') return '#dc3545';
    return '#ffc107';
  };

  const getRiskColor = (riskLevel) => {
    if (riskLevel === 'low') return '#28a745';
    if (riskLevel === 'medium') return '#ffc107';
    if (riskLevel === 'high') return '#dc3545';
    return '#6c757d';
  };

  if (!authenticated) {
    return (
      <div className="admin-login-container">
        <div className="admin-login-box">
          <h1>🔐 Admin Login</h1>
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username"
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                required
              />
            </div>
            {error && <div className="error-message">{error}</div>}
            <button type="submit" className="btn-primary">Login</button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <h1>📊 KYC Admin Dashboard</h1>
        <button onClick={handleLogout} className="btn-logout">
          Logout
        </button>
      </header>

      <div className="admin-content">
        <div className="dashboard-stats">
          <div className="stat-card">
            <h3>Total Submissions</h3>
            <div className="stat-number">{submissions.length}</div>
          </div>
          <div className="stat-card">
            <h3>Pending Review</h3>
            <div className="stat-number">
              {submissions.filter(s => !s.admin_status || s.admin_status === 'pending_review').length}
            </div>
          </div>
          <div className="stat-card">
            <h3>Approved</h3>
            <div className="stat-number" style={{ color: '#28a745' }}>
              {submissions.filter(s => s.admin_status === 'approved').length}
            </div>
          </div>
          <div className="stat-card">
            <h3>Rejected</h3>
            <div className="stat-number" style={{ color: '#dc3545' }}>
              {submissions.filter(s => s.admin_status === 'rejected').length}
            </div>
          </div>
        </div>

        {loading ? (
          <div className="loading">Loading submissions...</div>
        ) : (
          <div className="submissions-grid">
            {submissions.map((submission) => (
              <div key={submission.verification_id} className="submission-card">
                <div className="submission-header">
                  <h3>{submission.full_name}</h3>
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(submission.admin_status || 'pending') }}
                  >
                    {submission.admin_status || 'Pending Review'}
                  </span>
                </div>

                <div className="submission-details">
                  <p><strong>Email:</strong> {submission.email}</p>
                  <p><strong>Phone:</strong> {submission.phone}</p>
                  <p><strong>DOB:</strong> {submission.dob}</p>
                  <p><strong>Risk Level:</strong> 
                    <span style={{ 
                      color: getRiskColor(submission.risk_level),
                      fontWeight: 'bold',
                      marginLeft: '5px'
                    }}>
                      {submission.risk_level?.toUpperCase()}
                    </span>
                  </p>
                  <p><strong>Risk Score:</strong> {(submission.risk_score * 100).toFixed(1)}%</p>
                </div>

                <div className="verification-checks">
                  <div className="check-item">
                    <span>Document:</span>
                    <span style={{ color: getStatusColor(submission.document_status) }}>
                      {submission.document_status}
                    </span>
                  </div>
                  <div className="check-item">
                    <span>Liveness:</span>
                    <span style={{ color: getStatusColor(submission.liveness_status) }}>
                      {submission.liveness_status}
                    </span>
                  </div>
                  <div className="check-item">
                    <span>Compliance:</span>
                    <span style={{ color: getStatusColor(submission.compliance_status) }}>
                      {submission.compliance_status}
                    </span>
                  </div>
                </div>

                <div className="submission-meta">
                  <small>Created: {new Date(submission.created_at).toLocaleString()}</small>
                  <small>ID: {submission.verification_id.substring(0, 8)}...</small>
                </div>

                {submission.admin_notes && (
                  <div className="admin-notes">
                    <strong>Notes:</strong> {submission.admin_notes}
                  </div>
                )}

                {(!submission.admin_status || submission.admin_status === 'pending_review') && (
                  <div className="action-buttons">
                    <button 
                      onClick={() => setSelectedSubmission(submission)}
                      className="btn-review"
                    >
                      Review
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {selectedSubmission && (
          <div className="modal-overlay" onClick={() => setSelectedSubmission(null)}>
            <div className="modal-content detailed-review" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>📋 Detailed KYC Review</h2>
                <button className="close-btn" onClick={() => setSelectedSubmission(null)}>✕</button>
              </div>
              
              <div className="review-sections">
                {/* User Information */}
                <div className="review-section">
                  <h3>👤 User Information</h3>
                  <div className="info-grid">
                    <div><strong>Name:</strong> {selectedSubmission.full_name}</div>
                    <div><strong>Email:</strong> {selectedSubmission.email}</div>
                    <div><strong>Phone:</strong> {selectedSubmission.phone}</div>
                    <div><strong>DOB:</strong> {selectedSubmission.dob}</div>
                    <div><strong>Risk Score:</strong> <span style={{color: getRiskColor(selectedSubmission.risk_level), fontWeight: 'bold'}}>{(selectedSubmission.risk_score * 100).toFixed(1)}%</span></div>
                    <div><strong>Risk Level:</strong> <span style={{color: getRiskColor(selectedSubmission.risk_level), fontWeight: 'bold'}}>{selectedSubmission.risk_level?.toUpperCase()}</span></div>
                  </div>
                </div>

                {/* Document Analysis */}
                {selectedSubmission.document_analysis && (
                  <div className="review-section">
                    <h3>📄 Document Verification Analysis</h3>
                    <div className="analysis-details">
                      <div className="detail-row">
                        <span className="label">Document Status:</span>
                        <span className={`value ${selectedSubmission.document_analysis.forgery_detected ? 'fail' : 'pass'}`}>
                          {selectedSubmission.document_analysis.forgery_detected ? '❌ Forgery Detected' : '✅ Authentic'}
                        </span>
                      </div>
                      <div className="detail-row">
                        <span className="label">Confidence Score:</span>
                        <span className="value">{(selectedSubmission.document_analysis.confidence * 100).toFixed(1)}%</span>
                      </div>
                      <div className="detail-row">
                        <span className="label">ML Forgery Score:</span>
                        <span className="value">{(selectedSubmission.document_analysis.ml_score * 100).toFixed(1)}%</span>
                      </div>
                      
                      <div className="subsection">
                        <h4>🔍 Identity Verification</h4>
                        <div className="detail-row">
                          <span className="label">Name Match:</span>
                          <span className={`value ${selectedSubmission.document_analysis.name_match ? 'pass' : 'fail'}`}>
                            {selectedSubmission.document_analysis.name_match ? '✅ Matched' : '❌ Failed'} 
                            ({(selectedSubmission.document_analysis.name_match_score * 100).toFixed(0)}%)
                          </span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Expected Name:</span>
                          <span className="value">{selectedSubmission.full_name}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Extracted Name:</span>
                          <span className="value">{selectedSubmission.document_analysis.extracted_name}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">DOB Match:</span>
                          <span className={`value ${selectedSubmission.document_analysis.dob_match ? 'pass' : 'fail'}`}>
                            {selectedSubmission.document_analysis.dob_match ? '✅ Matched' : '❌ Failed'}
                            ({(selectedSubmission.document_analysis.dob_match_score * 100).toFixed(0)}%)
                          </span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Expected DOB:</span>
                          <span className="value">{selectedSubmission.dob}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Extracted DOB:</span>
                          <span className="value">{selectedSubmission.document_analysis.extracted_dob}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">OCR Available:</span>
                          <span className={`value ${selectedSubmission.document_analysis.ocr_available ? 'pass' : 'fail'}`}>
                            {selectedSubmission.document_analysis.ocr_available ? '✅ Yes' : '❌ No'}
                          </span>
                        </div>
                      </div>

                      {selectedSubmission.document_analysis.quality_analysis && (
                        <div className="subsection">
                          <h4>📊 Image Quality Analysis</h4>
                          <div className="detail-row">
                            <span className="label">Quality Score:</span>
                            <span className="value">{(selectedSubmission.document_analysis.quality_analysis.score * 100).toFixed(1)}%</span>
                          </div>
                          <div className="detail-row">
                            <span className="label">Resolution:</span>
                            <span className="value">{selectedSubmission.document_analysis.quality_analysis.resolution}</span>
                          </div>
                          <div className="detail-row">
                            <span className="label">Blur Score:</span>
                            <span className="value">{(selectedSubmission.document_analysis.quality_analysis.blur_score * 100).toFixed(1)}%</span>
                          </div>
                          <div className="detail-row">
                            <span className="label">Details:</span>
                            <span className="value">{selectedSubmission.document_analysis.quality_analysis.details}</span>
                          </div>
                        </div>
                      )}

                      {selectedSubmission.document_analysis.edge_analysis && (
                        <div className="subsection">
                          <h4>🔎 Edge Artifact Detection</h4>
                          <div className="detail-row">
                            <span className="label">Suspicious Edges:</span>
                            <span className={`value ${selectedSubmission.document_analysis.edge_analysis.suspicious_edges ? 'fail' : 'pass'}`}>
                              {selectedSubmission.document_analysis.edge_analysis.suspicious_edges ? '⚠️ Yes' : '✅ No'}
                            </span>
                          </div>
                          <div className="detail-row">
                            <span className="label">Edge Ratio:</span>
                            <span className="value">{(selectedSubmission.document_analysis.edge_analysis.edge_ratio * 100).toFixed(2)}%</span>
                          </div>
                          <div className="detail-row">
                            <span className="label">Sharpness:</span>
                            <span className="value">{selectedSubmission.document_analysis.edge_analysis.sharpness?.toFixed(2)}</span>
                          </div>
                        </div>
                      )}

                      {selectedSubmission.document_analysis.pixel_analysis && (
                        <div className="subsection">
                          <h4>🖼️ Pixel Anomaly Detection</h4>
                          <div className="detail-row">
                            <span className="label">Anomalies Found:</span>
                            <span className={`value ${selectedSubmission.document_analysis.pixel_analysis.anomalies_found ? 'fail' : 'pass'}`}>
                              {selectedSubmission.document_analysis.pixel_analysis.anomalies_found ? '⚠️ Yes' : '✅ No'}
                            </span>
                          </div>
                          <div className="detail-row">
                            <span className="label">Anomaly Count:</span>
                            <span className="value">{selectedSubmission.document_analysis.pixel_analysis.anomaly_count}</span>
                          </div>
                          <div className="detail-row">
                            <span className="label">Variance Inconsistency:</span>
                            <span className="value">{selectedSubmission.document_analysis.pixel_analysis.variance_inconsistency?.toFixed(2)}</span>
                          </div>
                        </div>
                      )}

                      <div className="detail-row overall">
                        <span className="label">Overall Assessment:</span>
                        <span className="value">{selectedSubmission.document_analysis.overall_assessment}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Liveness Analysis */}
                {selectedSubmission.liveness_analysis && (
                  <div className="review-section">
                    <h3>🎥 Liveness Detection Analysis</h3>
                    <div className="analysis-details">
                      <div className="detail-row">
                        <span className="label">Liveness Status:</span>
                        <span className={`value ${selectedSubmission.liveness_analysis.is_live ? 'pass' : 'fail'}`}>
                          {selectedSubmission.liveness_analysis.is_live ? '✅ Live Person Detected' : '❌ Failed'}
                        </span>
                      </div>
                      <div className="detail-row">
                        <span className="label">Confidence Score:</span>
                        <span className="value">{(selectedSubmission.liveness_analysis.confidence * 100).toFixed(1)}%</span>
                      </div>

                      <div className="subsection">
                        <h4>🎤 Audio Analysis</h4>
                        <div className="detail-row">
                          <span className="label">Audio Available:</span>
                          <span className={`value ${selectedSubmission.liveness_analysis.audio_available ? 'pass' : 'fail'}`}>
                            {selectedSubmission.liveness_analysis.audio_available ? '✅ Yes' : '❌ No'}
                          </span>
                        </div>
                        {selectedSubmission.liveness_analysis.audio_match !== undefined && (
                          <>
                            <div className="detail-row">
                              <span className="label">Audio Match:</span>
                              <span className={`value ${selectedSubmission.liveness_analysis.audio_match ? 'pass' : 'fail'}`}>
                                {selectedSubmission.liveness_analysis.audio_match ? '✅ Matched' : '❌ Failed'}
                              </span>
                            </div>
                            <div className="detail-row">
                              <span className="label">Audio Match Score:</span>
                              <span className="value">{(selectedSubmission.liveness_analysis.audio_match_score * 100).toFixed(1)}%</span>
                            </div>
                            <div className="detail-row">
                              <span className="label">Expected Phrase:</span>
                              <span className="value">{selectedSubmission.liveness_analysis.expected_phrase}</span>
                            </div>
                            <div className="detail-row">
                              <span className="label">Transcribed Text:</span>
                              <span className="value">{selectedSubmission.liveness_analysis.transcribed_text || 'N/A'}</span>
                            </div>
                          </>
                        )}
                      </div>

                      <div className="subsection">
                        <h4>👋 Gesture Recognition</h4>
                        <div className="detail-row">
                          <span className="label">Face Detected:</span>
                          <span className={`value ${selectedSubmission.liveness_analysis.face_detected ? 'pass' : 'fail'}`}>
                            {selectedSubmission.liveness_analysis.face_detected ? '✅ Yes' : '❌ No'}
                          </span>
                        </div>
                        {selectedSubmission.liveness_analysis.gesture_match !== undefined && (
                          <>
                            <div className="detail-row">
                              <span className="label">Gesture Match:</span>
                              <span className={`value ${selectedSubmission.liveness_analysis.gesture_match ? 'pass' : 'fail'}`}>
                                {selectedSubmission.liveness_analysis.gesture_match ? '✅ Matched' : '❌ Failed'}
                              </span>
                            </div>
                            <div className="detail-row">
                              <span className="label">Gesture Match Score:</span>
                              <span className="value">{(selectedSubmission.liveness_analysis.gesture_match_score * 100).toFixed(1)}%</span>
                            </div>
                            <div className="detail-row">
                              <span className="label">Expected Gesture:</span>
                              <span className="value">{selectedSubmission.liveness_analysis.expected_gesture}</span>
                            </div>
                            <div className="detail-row">
                              <span className="label">Detected Gesture:</span>
                              <span className="value">{selectedSubmission.liveness_analysis.detected_gesture || 'N/A'}</span>
                            </div>
                          </>
                        )}
                      </div>

                      <div className="subsection">
                        <h4>🛡️ Anti-Spoofing Detection</h4>
                        <div className="detail-row">
                          <span className="label">Spoof Score:</span>
                          <span className={`value ${selectedSubmission.liveness_analysis.spoof_score < 0.3 ? 'pass' : 'fail'}`}>
                            {(selectedSubmission.liveness_analysis.spoof_score * 100).toFixed(1)}% {selectedSubmission.liveness_analysis.spoof_score < 0.3 ? '✅' : '⚠️'}
                          </span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Motion Detected:</span>
                          <span className={`value ${selectedSubmission.liveness_analysis.motion_detected ? 'pass' : 'fail'}`}>
                            {selectedSubmission.liveness_analysis.motion_detected ? '✅ Yes' : '❌ No'}
                          </span>
                        </div>
                        {selectedSubmission.liveness_analysis.avg_motion_score !== undefined && (
                          <div className="detail-row">
                            <span className="label">Average Motion Score:</span>
                            <span className="value">{(selectedSubmission.liveness_analysis.avg_motion_score * 100).toFixed(1)}%</span>
                          </div>
                        )}
                      </div>

                      {selectedSubmission.liveness_analysis.issues && selectedSubmission.liveness_analysis.issues.length > 0 && (
                        <div className="subsection issues">
                          <h4>⚠️ Issues Identified</h4>
                          <ul>
                            {selectedSubmission.liveness_analysis.issues.map((issue, idx) => (
                              <li key={idx} className="issue-item">{issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      <div className="detail-row overall">
                        <span className="label">Overall Details:</span>
                        <span className="value">{selectedSubmission.liveness_analysis.details || 'All checks passed'}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Compliance Analysis */}
                {selectedSubmission.compliance_analysis && (
                  <div className="review-section">
                    <h3>⚖️ Compliance Check Results</h3>
                    <div className="analysis-details">
                      <div className="detail-row">
                        <span className="label">Compliance Status:</span>
                        <span className={`value ${selectedSubmission.compliance_analysis.passed ? 'pass' : 'fail'}`}>
                          {selectedSubmission.compliance_analysis.passed ? '✅ Passed' : '❌ Failed'}
                        </span>
                      </div>
                      <div className="detail-row">
                        <span className="label">Risk Score:</span>
                        <span className={`value ${selectedSubmission.compliance_analysis.risk_score > 0.6 ? 'fail' : selectedSubmission.compliance_analysis.risk_score > 0.3 ? 'warning' : 'pass'}`}>
                          {(selectedSubmission.compliance_analysis.risk_score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="detail-row">
                        <span className="label">Recommendation:</span>
                        <span className={`value ${selectedSubmission.compliance_analysis.recommendation === 'Approved' ? 'pass' : selectedSubmission.compliance_analysis.recommendation === 'Reject' ? 'fail' : 'warning'}`}>
                          {selectedSubmission.compliance_analysis.recommendation}
                        </span>
                      </div>

                      <div className="subsection">
                        <h4>🚫 Sanctions Screening</h4>
                        <div className="detail-row">
                          <span className="label">Status:</span>
                          <span className={`value ${selectedSubmission.compliance_analysis.sanctions_check?.flagged ? 'fail' : 'pass'}`}>
                            {selectedSubmission.compliance_analysis.sanctions_check?.flagged ? '❌ Flagged' : '✅ Clear'}
                          </span>
                        </div>
                        {selectedSubmission.compliance_analysis.sanctions_check?.sources_checked && (
                          <div className="detail-row">
                            <span className="label">Sources Checked:</span>
                            <span className="value">{selectedSubmission.compliance_analysis.sanctions_check.sources_checked.join(', ')}</span>
                          </div>
                        )}
                        {selectedSubmission.compliance_analysis.sanctions_check?.matches && selectedSubmission.compliance_analysis.sanctions_check.matches.length > 0 && (
                          <div className="subsection issues">
                            <h4>⚠️ Sanctions Matches Found</h4>
                            <ul>
                              {selectedSubmission.compliance_analysis.sanctions_check.matches.map((match, idx) => (
                                <li key={idx} className="issue-item">
                                  <strong>{match.name}</strong> - {match.reason} (Source: {match.source})
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>

                      <div className="subsection">
                        <h4>👔 PEP Screening (Politically Exposed Persons)</h4>
                        <div className="detail-row">
                          <span className="label">Status:</span>
                          <span className={`value ${selectedSubmission.compliance_analysis.pep_check?.flagged ? 'warning' : 'pass'}`}>
                            {selectedSubmission.compliance_analysis.pep_check?.flagged ? '⚠️ Flagged' : '✅ Clear'}
                          </span>
                        </div>
                        {selectedSubmission.compliance_analysis.pep_check?.matches && selectedSubmission.compliance_analysis.pep_check.matches.length > 0 && (
                          <div className="subsection issues">
                            <h4>⚠️ PEP Matches Found</h4>
                            <ul>
                              {selectedSubmission.compliance_analysis.pep_check.matches.map((match, idx) => (
                                <li key={idx} className="issue-item">
                                  <strong>{match.name}</strong> - {match.position} ({match.country}) - Risk: {match.risk}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>

                      <div className="subsection">
                        <h4>🔍 Fraud History Check</h4>
                        <div className="detail-row">
                          <span className="label">Status:</span>
                          <span className={`value ${selectedSubmission.compliance_analysis.fraud_check?.flagged ? 'fail' : 'pass'}`}>
                            {selectedSubmission.compliance_analysis.fraud_check?.flagged ? '❌ Fraud Found' : '✅ No Fraud'}
                          </span>
                        </div>
                        {selectedSubmission.compliance_analysis.fraud_check?.databases_checked && (
                          <div className="detail-row">
                            <span className="label">Databases Checked:</span>
                            <span className="value">{selectedSubmission.compliance_analysis.fraud_check.databases_checked.join(', ')}</span>
                          </div>
                        )}
                        {selectedSubmission.compliance_analysis.fraud_check?.matches && selectedSubmission.compliance_analysis.fraud_check.matches.length > 0 && (
                          <div className="subsection issues">
                            <h4>❌ Fraud Records Found</h4>
                            <ul>
                              {selectedSubmission.compliance_analysis.fraud_check.matches.map((match, idx) => (
                                <li key={idx} className="issue-item">
                                  <strong>{match.name}</strong> - {match.fraud_type} (Date: {match.date}, Amount: ₹{match.amount})
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>

                      <div className="subsection">
                        <h4>📰 Adverse Media Check</h4>
                        <div className="detail-row">
                          <span className="label">Status:</span>
                          <span className={`value ${selectedSubmission.compliance_analysis.adverse_media_check?.flagged ? 'warning' : 'pass'}`}>
                            {selectedSubmission.compliance_analysis.adverse_media_check?.flagged ? '⚠️ Found' : '✅ Clear'}
                          </span>
                        </div>
                        {selectedSubmission.compliance_analysis.adverse_media_check?.matches && selectedSubmission.compliance_analysis.adverse_media_check.matches.length > 0 && (
                          <div className="subsection issues">
                            <h4>⚠️ Adverse Media Found</h4>
                            <ul>
                              {selectedSubmission.compliance_analysis.adverse_media_check.matches.map((match, idx) => (
                                <li key={idx} className="issue-item">
                                  <strong>{match.name}</strong> - {match.issue} (Source: {match.source})
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>

                      {selectedSubmission.compliance_analysis.checks_performed && (
                        <div className="detail-row overall">
                          <span className="label">Checks Performed:</span>
                          <div className="value">
                            <ul style={{ margin: 0, paddingLeft: '20px' }}>
                              <li>Sanctions: {selectedSubmission.compliance_analysis.checks_performed.sanctions}</li>
                              <li>PEP: {selectedSubmission.compliance_analysis.checks_performed.pep}</li>
                              <li>Fraud: {selectedSubmission.compliance_analysis.checks_performed.fraud}</li>
                              <li>Adverse Media: {selectedSubmission.compliance_analysis.checks_performed.adverse_media}</li>
                            </ul>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* AI Explanation */}
                {selectedSubmission.explanation && (
                  <div className="review-section">
                    <h3>🤖 AI Explanation</h3>
                    <div className="explanation-text">
                      {selectedSubmission.explanation}
                    </div>
                  </div>
                )}

                {/* Admin Action Section */}
                <div className="review-section admin-action">
                  <h3>✍️ Admin Decision</h3>
                  <div className="form-group">
                    <label>Admin Notes (required for rejection)</label>
                    <textarea
                      value={adminNotes}
                      onChange={(e) => setAdminNotes(e.target.value)}
                      placeholder="Enter your decision notes or reason for rejection..."
                      rows={4}
                    />
                  </div>

                  <div className="modal-actions">
                    <button 
                      onClick={() => handleApprove(selectedSubmission.verification_id)}
                      className="btn-approve"
                    >
                      ✓ Approve KYC
                    </button>
                    <button 
                      onClick={() => handleReject(selectedSubmission.verification_id)}
                      className="btn-reject"
                    >
                      ✗ Reject KYC
                    </button>
                    <button 
                      onClick={() => {
                        setSelectedSubmission(null);
                        setAdminNotes('');
                      }}
                      className="btn-cancel"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Admin;
