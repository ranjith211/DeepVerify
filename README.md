# 🔐 DeepVerify - AI-Powered KYC Verification System

A unified, multi-modal GenAI system for modern KYC verification that defeats sophisticated, AI-driven fraud with a secure, seamless 60-second verification process.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2.0-61dafb)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Features in Detail](#features-in-detail)
- [Security & Compliance](#security--compliance)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

DeepVerify is an enterprise-grade KYC (Know Your Customer) verification system that leverages cutting-edge AI/ML technologies to combat sophisticated fraud attempts. The system addresses two primary fraud vectors:

### 🆔 Document Fraud Detection
- **GenAI Vision Analysis**: Forensically detects Photoshopped or digitally-forged IDs
- **Deep Learning Models**: Multi-layered detection using PyTorch and TensorFlow
- **OCR & Validation**: Extracts and validates document information using Tesseract OCR
- **Tampering Detection**: Identifies inconsistencies in document authenticity

### 👤 Biometric Liveness Verification
- **Multi-Modal AI Challenge**: Dynamic, real-time challenges to defeat deepfakes
- **8 Language Support**: English, Hindi, Tamil, Marathi, Telugu, Kannada, Malayalam, Bengali
- **Audio & Video Analysis**: Simultaneous speech recognition and gesture detection
- **Anti-Spoofing**: MediaPipe-based face mesh analysis and motion detection
- **Lip Sync Analysis**: Validates audio-visual synchronization

## ✨ Key Features

### 🚀 User Experience
- **60-Second Verification**: Complete KYC process in under a minute
- **Multi-Language Support**: 8 Indian languages with native script support
- **Real-Time Feedback**: Progressive step indicator with instant validation
- **Responsive Design**: Apple-inspired glossy UI with smooth animations
- **Admin Dashboard**: Comprehensive management interface for verification oversight

### 🤖 AI/ML Capabilities
- **Document Analysis**: Advanced forgery detection using computer vision
- **Speech Recognition**: Whisper model for multi-lingual audio processing
- **Gesture Recognition**: MediaPipe Hands for real-time gesture validation
- **Face Detection**: MediaPipe Face Mesh for anti-spoofing
- **Deepfake Detection**: Multi-modal analysis for synthetic media detection

### 🔒 Security Features
- **256-bit AES Encryption**: All PII data encrypted at rest
- **Row-Level Encryption**: PostgreSQL database with encryption
- **HTTPS/TLS**: Secure data transmission
- **Session Management**: Redis-based secure sessions
- **Immutable Audit Logs**: Complete verification trail

### 📊 Compliance & Reporting
- **Sanctions Screening**: AML/CTF compliance checks
- **Adverse Media Screening**: NLP-based risk assessment
- **Explainable AI**: XAI service provides transparent risk scores
- **Human-in-the-Loop**: Automatic escalation for ambiguous cases (<5%)

## 🛠 Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.2.0 | UI framework |
| React Webcam | 7.2.0 | Camera integration |
| TensorFlow.js | 4.22.0 | Client-side face detection |
| Axios | 1.6.2 | HTTP client |
| CSS3 | - | Modern styling with animations |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Core language |
| FastAPI | 0.115.0 | Web framework |
| Uvicorn | 0.32.1 | ASGI server |
| SQLAlchemy | 2.0.36 | ORM for SQL database |
| Pydantic | 2.10.3 | Data validation |

### AI/ML Stack
| Technology | Version | Purpose |
|------------|---------|---------|
| PyTorch | 2.0.0+ | Deep learning framework |
| Transformers | 4.35.0+ | Whisper speech recognition |
| MediaPipe | 0.10.0+ | Face & hand detection |
| OpenCV | 4.8.0+ | Computer vision |
| Librosa | 0.10.0+ | Audio processing |
| MoviePy | 1.0.3+ | Video processing |

### Databases & Storage
| Technology | Purpose |
|------------|---------|
| SQLite | Relational data (development) |
| MongoDB | Unstructured AI logs & analysis |
| Redis | Session management & caching |

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Document │  │ Liveness │  │  Admin   │  │  Status  │     │
│  │ Capture  │  │ Challenge│  │Dashboard │  │  Check   │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓ HTTPS/TLS
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Ingest  │  │  Verify  │  │  Status  │  │ Explain  │     │
│  │   API    │  │   API    │  │   API    │  │   API    │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Document   │  │   Liveness   │  │  Compliance  │       │
│  │   Service    │  │   Service    │  │   Service    │       │
│  │ (Forgery Det)│  │ (Multi-Modal)│  │ (AML/Adverse)│       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │     XAI      │  │  Encryption  │                         │
│  │   Service    │  │    Utils     │                         │
│  │ (Explainbil) │  │ (256-bit AES)│                         │ 
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │  SQLite  │  │ MongoDB  │  │  Redis   │                   │
│  │(User Data)│ │(AI Logs) │  │(Sessions)│                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
DeepVerify/
├── backend/                          # FastAPI Backend Server
│   ├── app/
│   │   ├── api/                     # REST API Endpoints
│   │   │   ├── ingest.py           # Document & video ingestion
│   │   │   ├── verify.py           # Verification processing
│   │   │   ├── status.py           # Status checking
│   │   │   ├── explain.py          # XAI explanations
│   │   │   ├── admin.py            # Admin operations
│   │   │   └── auth.py             # Authentication
│   │   ├── models/                  # Data Models
│   │   │   ├── database_models.py  # SQLAlchemy models
│   │   │   └── schemas.py          # Pydantic schemas
│   │   ├── services/                # Business Logic
│   │   │   ├── document_service.py # Document analysis
│   │   │   ├── liveness_service.py # Liveness detection
│   │   │   ├── compliance_service.py # Compliance checks
│   │   │   └── xai_service.py      # Explainability
│   │   ├── utils/                   # Utilities
│   │   │   └── encryption.py       # AES encryption
│   │   ├── database.py              # SQL database setup
│   │   └── mongodb.py               # MongoDB setup
│   ├── uploads/                     # Uploaded files storage
│   ├── models/                      # ML model weights
│   ├── main.py                      # FastAPI application
│   ├── requirements.txt             # Python dependencies
│   └── env.example                  # Environment template
│
├── frontend/                         # React Frontend Application
│   ├── public/
│   │   └── index.html              # HTML template
│   ├── src/
│   │   ├── services/
│   │   │   └── api.js              # API client
│   │   ├── App.js                  # Main application
│   │   ├── Admin.js                # Admin dashboard
│   │   ├── App.css                 # Main styles
│   │   ├── Admin.css               # Admin styles
│   │   ├── Modern.css              # Modern UI components
│   │   ├── index.css               # Global styles
│   │   └── index.js                # Entry point
│   ├── package.json                # Node dependencies
│   └── README.md                   # Frontend docs
│
└── README.md                        # This file
```

## 🚀 Setup Instructions

### Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.8+** (with pip)
- **Node.js 16+** (with npm)
- **FFmpeg** (for video processing)
- **Git** (for cloning the repository)

Optional:
- **MongoDB** (for AI logs - can use cloud MongoDB)
- **Redis** (for session management - optional in development)

### Quick Start (Development Mode)

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/ranjith211/DeepVerify.git
cd DeepVerify
```

#### 2️⃣ Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env

# Edit .env file with your configurations
# Minimal configuration for development:
# DATABASE_URL=sqlite:///./deepverify.db
# SECRET_KEY=your-secret-key-here
# ENCRYPTION_KEY=your-encryption-key-here

# Run database migrations (automatic on first run)
# The app will create SQLite database automatically

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

#### 3️⃣ Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at: `http://localhost:3000`

### 📝 Environment Configuration

#### Backend `.env` File

```bash
# Database Configuration
DATABASE_URL=sqlite:///./deepverify.db
MONGODB_URL=mongodb://localhost:27017/  # Optional
MONGODB_DB=deepverify_logs
REDIS_URL=redis://localhost:6379        # Optional

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-this-in-production
ENCRYPTION_KEY=your-encryption-key-change-this-in-production

# Application Settings
DEBUG=True
UPLOAD_DIR=./uploads

# AI/ML Configuration
AI_DEVICE=cpu                           # Use 'cuda' if GPU available
WHISPER_MODEL=openai/whisper-base      # Speech recognition model
MAX_VIDEO_FRAMES=100
PROCESS_EVERY_N_FRAMES=5
MODEL_PATH=./models
```

#### Production Environment

For production deployment:

1. **Change Database to PostgreSQL:**
   ```bash
   DATABASE_URL=postgresql://username:your-password@host:5432/deepverify
   ```

2. **Set up MongoDB:**
   ```bash
   MONGODB_URL=mongodb+srv://username:your-password@cluster.mongodb.net/
   ```

3. **Configure Redis:**
   ```bash
   REDIS_URL=redis://redis-host:6379
   ```

4. **Update Security Keys:**
   ```bash
   # Generate secure random keys
   SECRET_KEY=$(openssl rand -hex 32)
   ENCRYPTION_KEY=$(openssl rand -base64 32)
   ```

5. **Disable Debug Mode:**
   ```bash
   DEBUG=False
   ```

### 🐳 Docker Deployment (Optional)

```bash
# Coming soon - Docker compose configuration
docker-compose up -d
```

## 📚 API Documentation

### Base URL
- **Development:** `http://localhost:8000`
- **Production:** `https://your-domain.com`

### Core Endpoints

#### 1. Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy"
}
```

#### 2. Ingest Document & Video
```http
POST /api/ingest
Content-Type: multipart/form-data
```
**Request Body:**
- `document_image`: File (JPEG/PNG)
- `liveness_video`: File (WEBM/MP4)
- `name`: String
- `email`: String
- `phone`: String

**Response:**
```json
{
  "verification_id": "uuid-string",
  "status": "pending",
  "message": "Verification initiated"
}
```

#### 3. Get Liveness Challenge
```http
GET /api/challenge/{language}
```
**Parameters:**
- `language`: english | hindi | tamil | marathi | telugu | kannada | malayalam | bengali

**Response:**
```json
{
  "challenge_text": "Say 'blue cat' and hold up two fingers",
  "challenge_language": "english",
  "expected_gesture": "hold up two fingers",
  "expected_phrase": "blue cat"
}
```

#### 4. Check Verification Status
```http
GET /api/status/{verification_id}
```
**Response:**
```json
{
  "verification_id": "uuid",
  "status": "approved|rejected|pending",
  "document_score": 0.95,
  "liveness_score": 0.92,
  "overall_score": 0.935,
  "created_at": "2025-11-22T10:30:00Z"
}
```

#### 5. Get XAI Explanation
```http
GET /api/explain/{verification_id}
```
**Response:**
```json
{
  "verification_id": "uuid",
  "risk_score": 0.15,
  "risk_level": "low",
  "factors": [
    {
      "category": "document",
      "confidence": 0.95,
      "explanation": "Document shows authentic patterns"
    }
  ],
  "recommendation": "Approved for onboarding"
}
```

#### 6. Admin Login
```http
POST /api/admin/login
Content-Type: application/json
```
**Request Body:**
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

#### 7. Admin Dashboard
```http
GET /api/admin/verifications?status={status}&limit={limit}&offset={offset}
```
**Parameters:**
- `status`: all | pending | approved | rejected
- `limit`: integer (default 20)
- `offset`: integer (default 0)

#### 8. Admin Action
```http
POST /api/admin/verify/{verification_id}
Content-Type: application/json
```
**Request Body:**
```json
{
  "action": "approve|reject",
  "notes": "Manual review notes"
}
```

### Authentication

Admin endpoints require JWT token:
```http
Authorization: Bearer <token>
```

## 🎨 Features in Detail

### Document Verification

The document service performs comprehensive analysis:

1. **Image Quality Check**
   - Resolution validation
   - Blur detection
   - Lighting analysis

2. **Forgery Detection**
   - Edge analysis for cut-and-paste detection
   - Compression artifact analysis
   - Font consistency checking
   - Shadow and reflection validation

3. **OCR & Data Extraction**
   - Tesseract OCR for text extraction
   - Field validation (name, DOB, ID number)
   - Format consistency checking

4. **Deep Learning Analysis**
   - CNN-based authenticity scoring
   - Pattern recognition for known forgery types
   - Anomaly detection

### Liveness Detection

Multi-modal liveness verification includes:

1. **Dynamic Challenge Generation**
   - Random phrase selection (8 languages)
   - Random gesture requirement
   - Prevents replay attacks

2. **Audio Analysis**
   - Whisper model for speech recognition
   - Voice quality analysis
   - Background noise detection

3. **Video Analysis**
   - MediaPipe Face Mesh (468 landmarks)
   - Blink detection
   - Head pose estimation
   - Micro-expression analysis

4. **Gesture Recognition**
   - MediaPipe Hands tracking
   - Real-time gesture validation
   - Motion pattern analysis

5. **Lip Sync Validation**
   - Audio-visual synchronization check
   - Natural speech pattern detection
   - Deepfake detection

### Multi-Language Support

Supported languages with native script:
- 🇬🇧 English
- 🇮🇳 Hindi (हिंदी)
- 🇮🇳 Tamil (தமிழ்)
- 🇮🇳 Marathi (मराठी)
- 🇮🇳 Telugu (తెలుగు)
- 🇮🇳 Kannada (ಕನ್ನಡ)
- 🇮🇳 Malayalam (മലയാളം)
- 🇮🇳 Bengali (বাংলা)

### Admin Dashboard

Comprehensive management interface:
- **Real-time Statistics**: Live verification metrics
- **Verification Queue**: Pending cases requiring review
- **Search & Filter**: Find verifications by status, date, user
- **Detailed View**: Complete verification data including media
- **Manual Override**: Approve/reject with notes
- **Audit Trail**: Complete history of all actions

## 🔒 Security & Compliance

### Data Security

1. **Encryption at Rest**
   - 256-bit AES encryption for PII
   - Encrypted database fields
   - Secure key management

2. **Encryption in Transit**
   - HTTPS/TLS 1.3
   - Secure WebSocket connections
   - Certificate pinning

3. **Access Control**
   - JWT-based authentication
   - Role-based access control (RBAC)
   - Session timeout management

4. **Data Privacy**
   - GDPR compliant
   - Right to deletion
   - Data minimization
   - Purpose limitation

### Compliance Features

1. **AML/CTF Compliance**
   - Sanctions list screening
   - PEP (Politically Exposed Persons) checks
   - Transaction monitoring

2. **Adverse Media Screening**
   - NLP-based news analysis
   - Risk classification
   - Automated alerts

3. **Audit Trail**
   - Immutable logs in MongoDB
   - Complete verification history
   - Admin action logging
   - Compliance reporting

4. **Explainable AI (XAI)**
   - Transparent risk scoring
   - Factor-based explanations
   - Model interpretability
   - Regulatory compliance

### Human-in-the-Loop

- **Automatic Escalation**: Cases with score 0.7-0.8
- **Expert Review**: High-risk cases reviewed by humans
- **Quality Assurance**: Random sampling for accuracy
- **Continuous Learning**: Feedback loop for model improvement

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
source venv/bin/activate
pytest
```

### Test AI Models
```bash
python test_ai.py
```

### Test Validation
```bash
python test_validation.py
```

## 🐛 Troubleshooting

### Common Issues

**1. Backend won't start**
- Check Python version: `python --version` (need 3.8+)
- Verify virtual environment is activated
- Install missing dependencies: `pip install -r requirements.txt`

**2. Frontend won't start**
- Check Node version: `node --version` (need 16+)
- Clear node_modules: `rm -rf node_modules && npm install`
- Check port 3000 is free: `lsof -ti:3000`

**3. Video processing fails**
- Install FFmpeg: `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Linux)
- Check FFmpeg: `ffmpeg -version`

**4. Database errors**
- SQLite: Check file permissions in backend directory
- Ensure DATABASE_URL is correct in .env

**5. Camera not working**
- Use HTTPS or localhost (browsers require secure context)
- Check browser permissions for camera/microphone
- Try different browser (Chrome recommended)

## 🤝 Contributing

This is a hackathon submission project. For contributions:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

**Made with ❤️ for GHCI 25 Hackathon**
