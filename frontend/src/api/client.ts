import axios from 'axios';

// In locale: http://localhost:8000 (default)
// In produzione (GitHub Pages): impostare VITE_API_URL nelle variabili
// del repository GitHub → Settings → Secrets and variables → Actions → Variables
const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

const client = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Interceptor globale per errori API
client.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data?.detail ?? error.message);
    return Promise.reject(error);
  }
);

export default client;
