import axios from 'axios';
// API基础配置
const API_BASE_URL = '';  // 保持为空，由vite代理处理

// Cookie工具
export const CookieUtil = {
  getCookie(name) {
    const matches = document.cookie.match(new RegExp(
      "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : '';
  },
  
  setCookie(name, value, days) {
    let expires = '';
    if (days) {
      const date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = '; expires=' + date.toUTCString();
    }
    // 简单设置Cookie
    document.cookie = name + '=' + encodeURIComponent(value) + expires + '; path=/';
    console.log(`Cookie已设置: ${name}, 过期天数: ${days || '会话'}`);
  },
  
  deleteCookie(name) {
    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
    console.log(`Cookie已删除: ${name}`);
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
    MAIN: '/api/search',  // 添加主搜索路径
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
    CookieUtil.setCookie('token', token, rememberMe ? 7 : 1);
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
    // 处理API错误
    handleApiError(error);
    
    // 在开发环境中模拟接口返回数据
    if (import.meta.env.DEV) {
      console.warn('开发环境：API请求失败，返回模拟数据', error.config.url);
      
      // 根据请求URL返回不同的模拟数据
      const url = error.config.url;
      
      // 处理用户资料请求
      if (url.includes('/api/user/profile') || url.includes('/api/users')) {
        console.log('返回模拟用户数据');
        return Promise.resolve({
          data: {
            status: 'success',
            data: {
              id: 1,
              username: '测试用户',
              email: 'test@example.com',
              created_at: new Date().toISOString(),
              avatar: localStorage.getItem('userAvatar') || ''
            }
          }
        });
      }
      
      // 处理历史记录请求
      if (url.includes('/api/history')) {
        console.log('返回模拟历史数据');
        return Promise.resolve({
          data: {
            status: 'success',
            data: []
          }
        });
      }
      
      // 处理登录请求
      if (url.includes('/api/auth/login')) {
        console.log('返回模拟登录数据');
        return Promise.resolve({
          data: {
            status: 'success',
            token: 'test_token_12345',
            user_id: 1,
            username: error.config.data ? JSON.parse(error.config.data).username : '测试用户'
          }
        });
      }
      
      // 处理搜索请求
      if (url.includes('/api/search') && !url.includes('/history') && !url.includes('/rankings')) {
        console.log('返回模拟搜索结果数据');
        // 尝试从URL中提取搜索查询
        const searchParams = new URLSearchParams(url.split('?')[1] || '');
        const query = searchParams.get('query') || '未知搜索';
        
        // 生成随机数量的搜索结果（3-8个）
        const resultCount = Math.floor(Math.random() * 6) + 3;
        
        // 电影类型列表
        const movieTypes = [
          '动作/冒险', '剧情/科幻', '喜剧/爱情', '恐怖/惊悚', '动画/家庭',
          '犯罪/悬疑', '历史/传记', '奇幻/冒险', '战争/历史', '音乐/歌舞'
        ];
        
        // 生成随机年份
        const generateYear = () => (Math.floor(Math.random() * 30) + 1990).toString();
        
        // 生成随机评分
        const generateRating = () => (Math.floor(Math.random() * 30) + 60) / 10;
        
        // 生成搜索结果
        const movies = Array.from({ length: resultCount }, (_, i) => ({
          id: 100 + i,
          title: `${query} ${['相关影片', '系列电影', '同类作品', '推荐观看'][Math.floor(Math.random() * 4)]} ${i + 1}`,
          poster_url: `https://via.placeholder.com/300x450/1a1a2e/ffffff?text=${query}${i+1}`,
          release_date: generateYear(),
          movie_type: movieTypes[Math.floor(Math.random() * movieTypes.length)],
          rating: generateRating().toFixed(1)
        }));
        
        return Promise.resolve({
          data: {
            status: 'success',
            data: {
              total: resultCount,
              movies: movies
            }
          }
        });
      }
    }
    
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