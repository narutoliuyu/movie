import axios from 'axios';
import { getApiUrl, API_PATHS } from '../api/config';

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

// 检查用户是否已登录
export const checkLoginStatus = async () => {
  // 从Cookie中获取token
  const token = CookieUtil.getCookie('token');
  
  // 检查是否设置了"记住我"
  const rememberMeEnabled = CookieUtil.getCookie('rememberMe') === 'true';
  
  console.log('登录状态检查：', { token, rememberMeEnabled });

  if (token) {
    try {
      const response = await axios.get(getApiUrl(API_PATHS.USER.PROFILE), {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('自动登录检查响应:', response.data);
      
      if (response.data.status === 'success') {
        const userId = response.data.data.id;
        CookieUtil.setCookie('userId', userId, rememberMeEnabled ? 7 : null);
        console.log('自动登录成功，用户ID:', userId);
        
        return { isLoggedIn: true, userId };
      } else {
        console.log('自动登录失败，清理Cookie');
        clearLoginState();
        return { isLoggedIn: false, userId: null };
      }
    } catch (error) {
      console.error('自动登录失败:', error);
      clearLoginState();
      return { isLoggedIn: false, userId: null };
    }
  }
  
  // 如果没有token，返回未登录状态
  return { isLoggedIn: false, userId: null };
};

// 清理登录状态
export const clearLoginState = () => {
  CookieUtil.deleteCookie('token');
  CookieUtil.deleteCookie('userId');
  CookieUtil.deleteCookie('rememberMe');
};

// 登录并保存状态
export const login = async (username, password, rememberMe = false) => {
  try {
    const response = await axios.post(getApiUrl(API_PATHS.AUTH.LOGIN), {
      username,
      password
    });

    if (response.data.status === 'success') {
      const { token } = response.data.data;
      const extractedUserId = response.data.data.user_id || response.data.data.id;
      
      // 设置Cookie
      // 如果记住我，则设置7天过期时间，否则为会话Cookie
      CookieUtil.setCookie('token', token, rememberMe ? 7 : null);
      CookieUtil.setCookie('userId', extractedUserId, rememberMe ? 7 : null);
      
      if (rememberMe) {
        CookieUtil.setCookie('rememberMe', 'true', 7);
      }
      
      return { 
        success: true, 
        userId: extractedUserId,
        message: '登录成功'
      };
    } else {
      return { 
        success: false, 
        message: response.data.message || '登录失败'
      };
    }
  } catch (error) {
    return { 
      success: false, 
      message: error.response?.data?.message || '登录失败，请检查用户名和密码'
    };
  }
};

// 登出
export const logout = () => {
  clearLoginState();
}; 