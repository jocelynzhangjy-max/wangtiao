import { create } from 'zustand';
import axios from 'axios';

const useAuthStore = create((set, get) => ({
  isAuthenticated: false,
  user: null,
  token: localStorage.getItem('token'),

  // 检查用户登录状态
  checkAuth: async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      set({ isAuthenticated: false, user: null, token: null });
      return false;
    }

    try {
      // 设置axios默认头部
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      // 检查token是否有效
      const response = await axios.get('/api/users/me');
      set({
        isAuthenticated: true,
        user: response.data,
        token: token
      });
      return true;
    } catch (error) {
      localStorage.removeItem('token');
      set({ isAuthenticated: false, user: null, token: null });
      return false;
    }
  },

  // 登录
  login: async (email, password) => {
    try {
      // 使用表单格式发送数据
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await axios.post('/api/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      // 获取用户信息
      const userResponse = await axios.get('/api/users/me');

      set({
        isAuthenticated: true,
        user: userResponse.data,
        token: access_token
      });

      return true;
    } catch (error) {
      console.error('Login error:', error.response?.data || error.message);
      return false;
    }
  },

  // 注册
  register: async (userData) => {
    try {
      const response = await axios.post('/api/auth/register', userData);
      return true;
    } catch (error) {
      console.error('Register error:', error.response?.data || error.message);
      throw error;
    }
  },

  // 登出
  logout: () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    set({ isAuthenticated: false, user: null, token: null });
  }
}));

export default useAuthStore;
