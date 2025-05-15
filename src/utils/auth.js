import axios from 'axios';
import { getApiUrl, API_PATHS, CookieUtil } from '../api/config';

// 检查用户是否已登录
export const checkLoginStatus = async () => {
  // 从Cookie中获取token
  const token = CookieUtil.getCookie('token');
  const storedUserId = CookieUtil.getCookie('userId');
  
  // 检查是否设置了"记住我"
  const rememberMeEnabled = CookieUtil.getCookie('rememberMe') === 'true';
  
  console.log('登录状态检查：', { token: token ? '存在' : '不存在', userId: storedUserId, rememberMeEnabled });

  // 如果没有token或userId，直接返回未登录
  if (!token || !storedUserId) {
    console.log('无有效登录凭证');
    return { isLoggedIn: false, userId: null };
  }
  
  // 如果只是要检查Cookie中的登录状态而不验证
  if (rememberMeEnabled) {
    console.log('发现"记住我"Cookie，不需验证直接恢复登录状态');
    // 如果设置了"记住我"并且有token和userId，直接认为是登录状态
    return { isLoggedIn: true, userId: storedUserId };
  }
  
  // 尝试向后端验证token
  try {
    const response = await axios.get(getApiUrl(API_PATHS.USER.PROFILE), {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    console.log('自动登录检查响应:', response.data);
    
    if (response.data.status === 'success') {
      const userId = response.data.data.id;
      // 更新Cookie中的userId，以便与后端保持一致
      CookieUtil.setCookie('userId', userId, rememberMeEnabled ? 7 : null);
      console.log('自动登录成功，用户ID:', userId);
      
      return { isLoggedIn: true, userId };
    } else {
      console.log('自动登录失败，清理Cookie');
      // 如果设置了记住我，不要清除Cookie
      if (!rememberMeEnabled) {
        clearLoginState();
      }
      return { isLoggedIn: false, userId: null };
    }
  } catch (error) {
    console.error('自动登录失败:', error);
    // 如果设置了记住我，不要清除Cookie，仍然保持登录状态
    if (rememberMeEnabled) {
      console.log('尽管验证失败，但因启用了"记住我"，保持登录状态');
      return { isLoggedIn: true, userId: storedUserId };
    }
    clearLoginState();
    return { isLoggedIn: false, userId: null };
  }
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
    console.log('登录请求参数:', { username, rememberMe });
    
    const response = await axios.post(getApiUrl(API_PATHS.AUTH.LOGIN), {
      username,
      password
    });

    if (response.data.status === 'success') {
      const { token } = response.data.data;
      const extractedUserId = response.data.data.user_id || response.data.data.id;
      
      console.log('设置Cookie:', { token: '已设置', userId: extractedUserId, rememberMe });
      
      // 设置Cookie
      // 如果记住我，则设置7天过期时间，否则为会话Cookie
      const cookieExpiry = rememberMe ? 7 : null;
      CookieUtil.setCookie('token', token, cookieExpiry);
      CookieUtil.setCookie('userId', extractedUserId, cookieExpiry);
      
      if (rememberMe) {
        CookieUtil.setCookie('rememberMe', 'true', 7);
      } else {
        // 如果没有选择记住我，确保删除rememberMe cookie
        CookieUtil.deleteCookie('rememberMe');
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
    console.error('登录请求失败:', error);
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