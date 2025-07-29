import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth functions
export const auth = {
  login: async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await apiClient.post('/api/v1/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    const { access_token } = response.data;
    localStorage.setItem('access_token', access_token);
    return response.data;
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
};

// Users API
export const users = {
  getAll: async () => {
    const response = await apiClient.get('/api/v1/users');
    return response.data;
  }
};

// Dashboard API
export const dashboard = {
  getTaskOverview: async () => {
    const response = await apiClient.get('/api/v1/dashboard/tasks/overview');
    return response.data;
  },
  
  getProductionEfficiency: async () => {
    const response = await apiClient.get('/api/v1/dashboard/production/efficiency');
    return response.data;
  },
  
  getActiveOrders: async () => {
    const response = await apiClient.get('/api/v1/dashboard/orders/active');
    return response.data;
  }
};

// Request interceptor for adding auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });
        
        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (err) {
        // Refresh token expired, redirect to login
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(err);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
