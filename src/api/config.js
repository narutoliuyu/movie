import axios from 'axios';
// API基础配置
const API_BASE_URL = '';  // 保持为空，由vite代理处理

// API路径
const API_PATHS = {
  CATEGORIES: '/api/categories',  // 确保路径正确
  MOVIES: {
    FEATURED: '/api/movies',      // 添加/api前缀
    ALL: '/api/movies',           // 添加/api前缀
    BY_CATEGORY: (categoryId) => `/api/movies?category_id=${categoryId}`,  // 修改为使用分类ID
    DETAIL: (movieId) => `/api/movie/${movieId}`  // 添加/api前缀
  },
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    PROFILE: '/api/auth/profile'
  }
};

// 获取存储的token
const getToken = () => {
  return localStorage.getItem('token');
};

// 设置token
const setToken = (token) => {
  if (token) {
    localStorage.setItem('token', token);
  } else {
    localStorage.removeItem('token');
  }
};

// API配置
const API_CONFIG = {
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  }
};

// 获取完整的API URL
const getApiUrl = (path) => `${API_BASE_URL}${path}`;

// 处理API错误
const handleApiError = (error) => {
  if (error.response) {
    // 服务器返回错误响应
    console.error('API错误:', error.response.data);
    return error.response.data;
  } else if (error.request) {
    // 请求发送失败
    console.error('请求错误:', error.request);
    return { message: '网络请求失败' };
  } else {
    // 其他错误
    console.error('错误:', error.message);
    return { message: error.message };
  }
};

// 创建axios实例
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 添加请求拦截器
axiosInstance.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 添加响应拦截器
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    handleApiError(error);
    return Promise.reject(error);
  }
);

export {
  API_BASE_URL,
  API_PATHS,
  API_CONFIG,
  getApiUrl,
  handleApiError,
  axiosInstance,
  getToken,
  setToken
}; 