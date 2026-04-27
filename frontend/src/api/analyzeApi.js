// src/api/analyzeApi.js
import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const api = axios.create({ baseURL: BASE_URL });

// Analyze text only
export const analyzeText = async (text) => {
  const res = await api.post('/analyze/text', { text });
  return res.data;
};

// Analyze image only
export const analyzeImage = async (imageFile) => {
  const formData = new FormData();
  formData.append('file', imageFile);
  const res = await api.post('/analyze/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
};

// Analyze URL only
export const analyzeUrl = async (url) => {
  const res = await api.post('/analyze/url', { url });
  return res.data;
};

// Full analysis (all at once)
export const analyzeAll = async ({ text, url, imageFile }) => {
  const formData = new FormData();
  if (text) formData.append('text', text);
  if (url) formData.append('url', url);
  if (imageFile) formData.append('file', imageFile);
  const res = await api.post('/analyze/full', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
};
