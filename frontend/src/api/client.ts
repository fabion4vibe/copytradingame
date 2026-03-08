import axios from 'axios';

const client = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
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
