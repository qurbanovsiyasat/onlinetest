import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// API call wrapper
export const apiCall = async (endpoint, options = {}) => {
  try {
    const config = {
      url: `/api${endpoint}`,
      method: options.method || 'GET',
      ...options,
    };

    if (options.data) {
      config.data = options.data;
    }

    const response = await api(config);
    return response;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

export default api;