# Deep-Verify Backend

FastAPI-based backend for the Deep-Verify KYC verification engine.

## Features

- Document forgery detection (mock AI analysis)
- Biometric liveness verification with multi-lingual challenges
- Sanctions and adverse media compliance checks
- Explainable AI risk scoring
- Encrypted PII storage
- Complete audit trail in MongoDB

## Prerequisites

- Python 3.8+
- PostgreSQL
- MongoDB
- Redis (optional, for production scaling)

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Copy `env.example` to `.env` and update the values:
```bash
cp env.example .env
```

Edit `.env` with your database credentials.

## Database Setup

### PostgreSQL

Create a database:
```bash
createdb deepverify
```

Or using psql:
```sql
CREATE DATABASE deepverify;
```

### MongoDB

MongoDB will automatically create the database on first connection.
Default database name: `deepverify_logs`

## Running the Application

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## API Endpoints

### Ingestion
- `POST /api/ingest` - Upload document and video for verification
- `GET /api/challenge/{language}` - Get liveness challenge (english/hindi/tamil)

### Verification
- `POST /api/verify/{verification_id}` - Process verification

### Status & Results
- `GET /api/status/{verification_id}` - Get verification status
- `GET /api/explain/{verification_id}` - Get detailed risk explanation

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── ingest.py
│   │   ├── verify.py
│   │   ├── status.py
│   │   └── explain.py
│   ├── models/           # Data models
│   │   ├── database_models.py
│   │   └── schemas.py
│   ├── services/         # Business logic
│   │   ├── document_service.py
│   │   ├── liveness_service.py
│   │   ├── compliance_service.py
│   │   └── xai_service.py
│   ├── utils/            # Utilities
│   │   └── encryption.py
│   ├── database.py       # PostgreSQL config
│   └── mongodb.py        # MongoDB config
├── main.py               # FastAPI app
├── requirements.txt
└── env.example
```

## Security Features

- 256-bit AES encryption for PII (name, DOB, phone)
- Secure file upload handling
- Row-level encryption in PostgreSQL
- Immutable audit logs in MongoDB

## Mock Services (Prototype)

For the hackathon prototype, the following are mocked:
- Document forgery detection (random pass/fail with realistic confidence)
- Liveness verification (random validation)
- Compliance checks (hardcoded sanctions list)

In production, these would be replaced with:
- Real AI/ML models (PyTorch, TensorFlow)
- Actual sanctions API integration
- Real-time video analysis

## Testing

Run a test verification:
```bash
curl -X POST http://localhost:8000/api/challenge/english
```

## License

Proprietary - GHCI 25 Hackathon
