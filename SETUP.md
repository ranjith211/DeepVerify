# Deep-Verify Engine - Setup Guide

Complete setup guide for running the Deep-Verify prototype locally.

## Quick Start (Development Mode)

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- MongoDB 4.4+

### 1. Clone the Repository
```bash
git clone https://github.com/ranjith211/DeepVerify.git
cd DeepVerify
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL database
createdb deepverify

# Copy environment file
cp env.example .env

# Edit .env with your database credentials
# (You can use default values for local testing)

# Run the backend
uvicorn main:app --reload
```

Backend will run at: `http://localhost:8000`

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

Frontend will open at: `http://localhost:3000`

## Simplified Setup (Without External Databases)

For quick testing without setting up PostgreSQL and MongoDB:

### Option 1: Use SQLite (Backend Modification)

Edit `backend/app/database.py` to use SQLite:
```python
DATABASE_URL = "sqlite:///./deepverify.db"
```

### Option 2: Skip Database Setup

The application will show errors but you can still test the UI flow.

## Testing the Application

1. Open `http://localhost:3000` in your browser
2. Fill in the form with sample data:
   - Email: test@example.com
   - Full Name: John Doe
   - DOB: 1990-01-15
   - Phone: +1234567890
3. Upload any image as ID document
4. Select language (English/Hindi/Tamil)
5. Record a video (perform the challenge shown)
6. View verification results

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/deepverify
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DB=deepverify_logs
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-change-this
ENCRYPTION_KEY=your-encryption-key-change-this
DEBUG=True
UPLOAD_DIR=./uploads
MODEL_PATH=./models
```

## Default Ports
- Backend API: `8000`
- Frontend: `3000`
- PostgreSQL: `5432`
- MongoDB: `27017`
- Redis: `6379` (optional)

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running: `pg_isready`
- Check MongoDB is running: `mongosh` or `mongo`
- Verify Python dependencies: `pip list`

### Frontend won't start
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (should be 16+)

### CORS errors
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`

### Webcam not working
- Allow camera/microphone permissions in browser
- Use Chrome or Firefox (recommended)
- Check if camera is in use by another application

### Database connection errors
- For PostgreSQL: Check credentials in `.env`
- For MongoDB: Ensure MongoDB service is running
- For quick testing: Use SQLite instead (see above)

## File Structure

```
DeepVerify/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic (mock AI)
│   │   └── utils/        # Utilities
│   ├── uploads/          # Uploaded files (created automatically)
│   ├── main.py           # FastAPI app
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── services/     # API client
│   │   ├── App.js        # Main component
│   │   └── App.css       # Styles
│   ├── package.json
│   └── README.md
├── .gitignore
└── README.md
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Mock Data

The prototype uses mock/simulated AI services:
- **Document Analysis**: 90% pass rate (random)
- **Liveness Check**: 85% pass rate (random)
- **Compliance**: Hardcoded sanctions list

## Production Deployment Notes

For production deployment, you would need to:
1. Replace mock services with real AI models
2. Set up proper database clustering
3. Implement Redis for session management
4. Add proper authentication/authorization
5. Use HTTPS/TLS everywhere
6. Implement rate limiting
7. Add monitoring and logging
8. Use Docker/Kubernetes for deployment

## Support

For issues or questions about this prototype:
- Check the README files in backend/ and frontend/
- Review API documentation at /docs
- Contact the development team

## License

Proprietary - GHCI 25 Hackathon Round 2 Submission
