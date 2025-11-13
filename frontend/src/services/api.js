import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Ingest verification with files
export const ingestVerification = async (formData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/ingest`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

// Get liveness challenge
export const getLivenessChallenge = async (language = 'english') => {
  try {
    const response = await api.get(`/challenge/${language}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

// Trigger verification
export const triggerVerification = async (verificationId) => {
  try {
    const response = await api.post(`/verify/${verificationId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

// Get verification status
export const getVerificationStatus = async (verificationId) => {
  try {
    const response = await api.get(`/status/${verificationId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

// Get risk explanation
export const getRiskExplanation = async (verificationId) => {
  try {
    const response = await api.get(`/explain/${verificationId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};
