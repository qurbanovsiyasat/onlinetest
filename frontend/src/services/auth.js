import { apiCall } from './api';

export const authService = {
  // Login user
  login: async (email, password) => {
    const response = await apiCall('/auth/login', {
      method: 'POST',
      data: { email, password }
    });
    return response.data;
  },

  // Register user
  register: async (name, email, password) => {
    const response = await apiCall('/auth/register', {
      method: 'POST',
      data: { name, email, password }
    });
    return response.data;
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await apiCall('/auth/me');
    return response.data;
  },

  // Change password
  changePassword: async (currentPassword, newPassword) => {
    const response = await apiCall('/auth/change-password', {
      method: 'POST',
      data: {
        current_password: currentPassword,
        new_password: newPassword
      }
    });
    return response.data;
  },

  // Logout (client-side)
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};

export default authService;