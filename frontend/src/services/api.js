import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 300 seconds (5 min) – CPU-based LLM inference can be slow
});

// Request Interceptor
api.interceptors.request.use(
  (config) => {
    // We can attach tokens or auth headers here later if needed
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response Interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      console.error(`API Error Response [${error.response.status}]:`, error.response.data);
    } else if (error.request) {
      console.error('API Error No Response:', error.request);
    } else {
      console.error('API Error Setup:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;
