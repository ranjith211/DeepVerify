# Deep-Verify Frontend

React-based frontend for the Deep-Verify KYC verification engine.

## Features

- Multi-step verification wizard
- Document upload interface
- Real-time webcam liveness challenge
- Multi-lingual support (English, Hindi, Tamil)
- Real-time verification results
- Detailed risk explanation display

## Prerequisites

- Node.js 16+
- npm or yarn

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The application will open at: `http://localhost:3000`

## Configuration

The frontend is configured to connect to the backend at `http://localhost:8000`.

To change this, edit `src/services/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

## User Flow

### Step 1: Personal Information
- Enter email, full name, date of birth, phone number
- Upload ID document (image)

### Step 2: Language Selection
- Choose preferred language for liveness challenge
- Supported: English, Hindi, Tamil

### Step 3: Liveness Verification
- System generates a random challenge
- User performs challenge on camera
- Video is recorded and submitted

### Step 4: Results
- View verification status (Approved/Rejected/Review Required)
- See risk score and risk level
- View detailed explanation of each check
- See individual component results:
  - Document verification
  - Liveness verification
  - Compliance check

## Components

- `App.js` - Main application with multi-step wizard
- `services/api.js` - API client for backend communication

## Styling

Custom CSS with:
- Gradient background
- Card-based design
- Responsive layout
- Step indicator
- Color-coded results

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` folder.

## Browser Support

- Chrome (recommended for webcam features)
- Firefox
- Safari
- Edge

## Webcam Permissions

The application requires camera and microphone access for the liveness check.
Make sure to allow permissions when prompted.

## License

Proprietary - GHCI 25 Hackathon
