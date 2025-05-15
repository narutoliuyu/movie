import axios from 'axios';
// API基础配置
const API_BASE_URL = '';  // 保持为空，由vite代理处理

// Cookie工具函数
const CookieUtil = {
  // 设置Cookie
  setCookie(name, value, days) {
    let expires = '';
    if (days) {
      const date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = '; expires=' + date.toUTCString();
    }
    document.cookie = name + '=' + encodeURIComponent(value) + expires + '; path=/';
  },

  // 获取Cookie
  getCookie(name) {
    const nameEQ = name + '=';
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
    }
    return null;
  },

  // 删除Cookie
  deleteCookie(name) {
    this.setCookie(name, '', -1);
  }
};

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
  },
  SEARCH: {
    HISTORY: '/api/search/history',
    RANKINGS: '/api/search/rankings'
  },
  USER: {
    PROFILE: '/api/user/profile'
  }
};

// 获取存储的token
const getToken = () => {
  return CookieUtil.getCookie('token');
};

// 设置token
const setToken = (token, rememberMe = false) => {
  if (token) {
    CookieUtil.setCookie('token', token, rememberMe ? 7 : null);
  } else {
    CookieUtil.deleteCookie('token');
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
  setToken,
  CookieUtil
}; 