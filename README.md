# Deep-Verify Engine

A unified, multi-modal GenAI system for modern KYC verification that defeats sophisticated, AI-driven fraud with a secure, seamless 60-second verification process.

## Overview

Deep-Verify addresses two primary fraud vectors:
- **Document Fraud**: Using GenAI vision to forensically detect Photoshopped or digitally-forged IDs
- **Biometric Fraud**: Using a dynamic, multi-lingual, GenAI-powered challenge to defeat deepfakes and pre-recorded video attacks

## Technology Stack

### Frontend
- React
- Axios for API communication
- Material-UI/TailwindCSS for styling

### Backend
- Python (FastAPI)
- PostgreSQL (relational data - user information)
- MongoDB (unstructured AI logs)
- Redis (session management)

### AI/ML
- PyTorch
- TensorFlow
- Hugging Face Transformers
- OpenCV for image processing

## System Architecture

The system follows a microservices architecture with the following components:

1. **Ingestion Service**: Secure endpoint to receive document images and video
2. **Deep-Verify Document Service**: GenAI vision model for forgery detection
3. **Real-Time Liveness Service**: Multi-modal GenAI for biometric verification
4. **Compliance Service**: NLP module for sanctions and adverse media checks
5. **XAI Service**: Explainability engine for risk reports

## Project Structure

```
DeepVerify/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── models/   # Database models
│   │   ├── services/ # Business logic
│   │   └── utils/    # Utilities
│   ├── requirements.txt
│   └── main.py
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.js
│   └── package.json
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (create `.env` file):
   ```
   DATABASE_URL=postgresql://user:password@localhost/deepverify
   MONGODB_URL=mongodb://localhost:27017/
   REDIS_URL=redis://localhost:6379
   SECRET_KEY=your-secret-key
   ENCRYPTION_KEY=your-encryption-key
   ```

5. Run the backend:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## API Endpoints

- `POST /api/ingest` - Accept document images and video
- `POST /api/verify` - Perform verification
- `GET /api/status/{verification_id}` - Check verification status
- `GET /api/explain/{verification_id}` - Get risk explanation

## Security Features

- 256-bit AES encryption for PII
- Row-level encryption in PostgreSQL
- HTTPS/TLS for data in transit
- Secure session management with Redis
- Immutable audit logs

## Compliance

- Sanctions list checking (AML/CTF)
- Adverse media screening
- Explainable AI risk scores
- Complete audit trail

## Human-in-the-Loop

High-risk or ambiguous cases (<5%) are automatically escalated to human review with complete explainable risk score packages.

## License

Proprietary - GHCI 25 Hackathon Submission

## Team

Submitted for GHCI 25 Hackathon Round 2
