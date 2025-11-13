# Quick Start Guide - Deep-Verify Engine

## ✅ Application is Running Successfully!

The Deep-Verify Engine is now running locally with both backend and frontend services.

### Current Status

- ✅ **Backend (FastAPI)**: Running on http://localhost:8000
- ✅ **Frontend (React)**: Running on http://localhost:3000
- ✅ **Database**: SQLite (auto-created, no setup needed)
- ✅ **Mock Services**: All AI services working with mock data

## Access the Application

1. **Frontend UI**: Open http://localhost:3000 in your browser
2. **Backend API Docs**: http://localhost:8000/docs
3. **Backend Health**: http://localhost:8000/health

## What You Can Do Now

### Test the Full Verification Flow

1. Open http://localhost:3000
2. Fill in personal information:
   - Email: test@example.com
   - Full Name: John Doe
   - Date of Birth: 1990-01-15
   - Phone: +1234567890
3. Upload any image as an ID document
4. Select language (English/Hindi/Tamil)
5. Record a video performing the challenge
6. View verification results with risk scores

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get liveness challenge
curl http://localhost:8000/api/challenge/english
curl http://localhost:8000/api/challenge/hindi
curl http://localhost:8000/api/challenge/tamil

# View API documentation
open http://localhost:8000/docs
```

## Features Working

✅ **Multi-step Form**
- Personal information input
- Document upload
- Language selection
- Video recording

✅ **Mock AI Services**
- Document forgery detection (90% pass rate)
- Liveness verification (85% pass rate)
- Compliance checking with mock sanctions list
- Explainable AI risk scoring

✅ **Security**
- PII encryption
- Secure file handling
- Audit logging

✅ **Results Display**
- Risk score calculation
- Component-wise status (Document/Liveness/Compliance)
- Detailed explanations
- Human review flagging

## Stopping the Services

### Stop Backend
In the terminal running the backend, press `Ctrl+C`

### Stop Frontend
In the terminal running the frontend, press `Ctrl+C`

## Restarting the Services

### Backend
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm start
```

## Project Structure

```
DeepVerify/
├── backend/              # FastAPI backend (Python)
│   ├── deepverify.db    # SQLite database (auto-created)
│   ├── uploads/         # Uploaded files directory
│   └── venv/            # Python virtual environment
├── frontend/            # React frontend
│   └── node_modules/    # npm packages
└── ...
```

## Mock Data Details

### Document Analysis
- **Pass Rate**: 90% (random)
- **Checks**: Pixel analysis, font matching, metadata, edge detection

### Liveness Verification
- **Pass Rate**: 85% (random)
- **Challenges**: Random multi-lingual phrases + gestures
- **Checks**: Lip-sync, gesture detection, deepfake probability

### Compliance Check
- **Hardcoded Sanctions List**:
  - John Smith (1980-05-15) - Financial fraud
  - Jane Doe (1975-03-22) - Money laundering
  - Bob Johnson (1990-11-30) - Terrorism financing
- **Adverse Media**: Alice Brown, Charlie Wilson

### Risk Scoring
- **Low Risk** (< 30%): Approved
- **Medium Risk** (30-60%): Human review required
- **High Risk** (> 60%): Rejected

## Troubleshooting

### Backend won't start
```bash
# Kill any process on port 8000
lsof -ti:8000 | xargs kill -9

# Restart backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend won't start
```bash
# Kill any process on port 3000
lsof -ti:3000 | xargs kill -9

# Clear cache and restart
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Webcam not working
- Allow camera permissions in your browser
- Use Chrome or Firefox (recommended)
- Check if camera is not in use by another app

### Database issues
```bash
# Reset database (if needed)
cd backend
rm deepverify.db
# Database will be recreated on next startup
```

## Next Steps for Hackathon Submission

1. ✅ **Code is working locally**
2. ⏭️ **Record demo video** (Use DEMO_SCRIPT.md)
3. ⏭️ **Create PDF documentation** (Cover all technical aspects)
4. ⏭️ **Push to GitHub** 
5. ⏭️ **Submit before November 19, 2025**

## Technical Stack Running

- **Frontend**: React 18.2.0
- **Backend**: FastAPI 0.115.0
- **Database**: SQLite (local file)
- **Mock Storage**: In-memory Python dictionaries
- **Encryption**: Fernet (AES-256)
- **No External Dependencies**: PostgreSQL, MongoDB, Redis not required

## Performance

- **Verification Time**: ~2-3 seconds (mock processing)
- **API Response Time**: < 100ms
- **Database**: SQLite (sufficient for demo)

---

**Status**: ✅ Application fully functional for demo and testing!

**Issues**: None - all systems operational

**Ready for**: Demo video recording and hackathon submission
