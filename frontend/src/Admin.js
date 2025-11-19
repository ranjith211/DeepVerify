import React, { useState, useEffect } from 'react';
import './Admin.css';

function Admin() {
  const [authenticated, setAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [adminNotes, setAdminNotes] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    if (username === 'admin' && password === 'admin') {
      setAuthenticated(true);
      setError('');
      fetchSubmissions();
    } else {
      setError('Invalid username or password');
    }
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
        <button onClick={() => setAuthenticated(false)} className="btn-logout">
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
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <h2>Review KYC Submission</h2>
              
              <div className="review-info">
                <h3>{selectedSubmission.full_name}</h3>
                <p><strong>Email:</strong> {selectedSubmission.email}</p>
                <p><strong>Phone:</strong> {selectedSubmission.phone}</p>
                <p><strong>DOB:</strong> {selectedSubmission.dob}</p>
                <p><strong>Risk Score:</strong> {(selectedSubmission.risk_score * 100).toFixed(1)}%</p>
                <p><strong>Risk Level:</strong> 
                  <span style={{ color: getRiskColor(selectedSubmission.risk_level) }}>
                    {selectedSubmission.risk_level?.toUpperCase()}
                  </span>
                </p>
              </div>

              <div className="form-group">
                <label>Admin Notes</label>
                <textarea
                  value={adminNotes}
                  onChange={(e) => setAdminNotes(e.target.value)}
                  placeholder="Enter notes or reason for decision..."
                  rows={4}
                />
              </div>

              <div className="modal-actions">
                <button 
                  onClick={() => handleApprove(selectedSubmission.verification_id)}
                  className="btn-approve"
                >
                  ✓ Approve
                </button>
                <button 
                  onClick={() => handleReject(selectedSubmission.verification_id)}
                  className="btn-reject"
                >
                  ✗ Reject
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
        )}
      </div>
    </div>
  );
}

export default Admin;
