import axios from 'axios';
import { getApiUrl, API_PATHS, CookieUtil } from '../api/config';

// 检查用户是否已登录
export const checkLoginStatus = async () => {
  // 从Cookie中获取token
  const token = CookieUtil.getCookie('token');
  const storedUserId = CookieUtil.getCookie('user_id');
  const storedUsername = CookieUtil.getCookie('username');
  
  // 检查是否设置了"记住我"
  const rememberMeEnabled = CookieUtil.getCookie('rememberMe') === 'true';
  
  console.log('登录状态检查：', { 
    token: token ? '存在' : '不存在', 
    userId: storedUserId, 
    username: storedUsername,
    rememberMe: rememberMeEnabled
  });

  // 如果没有token或userId，直接返回未登录
  if (!token || !storedUserId) {
    console.log('无有效登录凭证');
    return { isLoggedIn: false, userId: null, username: null };
  }
  
  // 设置axios的全局Authorization头
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  
  // 如果Cookie中有token，就认为是登录状态
  return { isLoggedIn: true, userId: storedUserId, username: storedUsername };
};

// 清理登录状态
export const clearLoginState = () => {
  CookieUtil.deleteCookie('token');
  CookieUtil.deleteCookie('user_id');
  CookieUtil.deleteCookie('username');
  CookieUtil.deleteCookie('rememberMe');
};

// 登录并保存状态
export const login = async (username, password, rememberMe = false) => {
  try {
    console.log('登录请求参数:', { username, rememberMe: !!rememberMe });
    
    // 先清除可能的旧状态
    clearLoginState();
    
    const response = await axios.post(getApiUrl(API_PATHS.AUTH.LOGIN), {
      username, 
      password
    });
    
    if (response.data && response.data.status === 'success') {
      // 获取token和user_id
      const token = response.data.data?.token || response.data.token;
      const user_id = response.data.data?.user_id || response.data.data?.id || response.data.user_id;
      
      if (!token || !user_id) {
        console.error('登录响应缺少必要字段:', response.data);
        return { 
          success: false, 
          message: '服务器响应格式错误'
        };
      }
      
      console.log('登录成功，设置Cookie:', { 
        token: token ? '已获取' : '未获取', 
        userId: user_id, 
        rememberMe: !!rememberMe 
      });
      
      // 存储用户信息到Cookie
      const expiryDays = rememberMe ? 7 : 1; // 根据rememberMe设置过期时间
      CookieUtil.setCookie('token', token, expiryDays);
      CookieUtil.setCookie('user_id', user_id, expiryDays);
      CookieUtil.setCookie('username', username, expiryDays);
      CookieUtil.setCookie('rememberMe', rememberMe ? 'true' : 'false', expiryDays);
      
      // 设置Authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      return { success: true, userId: user_id };
    } else {
      console.error('登录失败, 服务器响应:', response.data);
      return { 
        success: false, 
        message: response.data?.message || '登录失败'
      };
    }
  } catch (error) {
    console.error('登录请求失败:', error);
    return { 
      success: false, 
      message: error.response?.data?.message || '登录失败，请稍后重试'
    };
  }
};

// 登出
export const logout = () => {
  // 清除Cookie
  CookieUtil.deleteCookie('token');
  CookieUtil.deleteCookie('user_id');
  CookieUtil.deleteCookie('username');
  CookieUtil.deleteCookie('rememberMe');
  
  // 移除axios默认请求头中的token
  delete axios.defaults.headers.common['Authorization'];
  
  console.log('用户已登出');
}; 