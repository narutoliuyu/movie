import { defineStore } from 'pinia'
import { ref } from 'vue'
import { CookieUtil, axiosInstance, getApiUrl, API_PATHS } from '../api/config'
import { checkLoginStatus, login as authLogin, logout as authLogout } from '../utils/auth'

export const useUserStore = defineStore('user', () => {
  // 状态
  const isLoggedIn = ref(false)
  const userId = ref(null)
  const username = ref('')
  const token = ref(null)

  // 初始化状态 - 从Cookie恢复
  const initializeState = async () => {
    console.log('初始化用户状态...')
    
    // 从Cookie中获取基本信息
    const storedToken = CookieUtil.getCookie('token')
    const storedUserId = CookieUtil.getCookie('user_id')
    const storedUsername = CookieUtil.getCookie('username')
    const rememberMeEnabled = CookieUtil.getCookie('rememberMe') === 'true'
    
    console.log('Cookie状态:', { 
      token: storedToken ? '存在' : '不存在', 
      userId: storedUserId, 
      username: storedUsername, 
      rememberMe: rememberMeEnabled 
    })
    
    // 如果Cookie中有token和userId，设置为已登录状态
    if (storedToken && storedUserId) {
      isLoggedIn.value = true
      userId.value = storedUserId
      username.value = storedUsername || '用户'
      token.value = storedToken
      
      // 确保Axios请求头也包含token
      axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
      
      console.log('已恢复登录状态:', isLoggedIn.value)
    } else {
      // 清除登录状态
      isLoggedIn.value = false
      userId.value = null
      username.value = ''
      token.value = null
      console.log('无登录状态')
    }
  }

  // 登录
  const login = async (user, password, rememberMe = false) => {
    try {
      // 清除可能存在的旧Cookie
      CookieUtil.deleteCookie('token')
      CookieUtil.deleteCookie('user_id')
      CookieUtil.deleteCookie('username')
      CookieUtil.deleteCookie('rememberMe')
      
      console.log('准备发送登录请求:', {url: getApiUrl(API_PATHS.AUTH.LOGIN), user})
      
      const response = await axiosInstance.post(getApiUrl(API_PATHS.AUTH.LOGIN), {
        username: user,
        password
      })
      
      console.log('登录请求响应:', response.data)
      
      if (response.data.status === 'success') {
        const { token: newToken, user_id } = response.data
        
        console.log('登录成功, 提取token和user_id:', {
          token: newToken ? '已获取' : '未获取',
          user_id: user_id
        })
        
        // 存储登录状态
        isLoggedIn.value = true
        userId.value = user_id
        username.value = user
        token.value = newToken
        
        // 使用Cookie存储token
        const expiryDays = rememberMe ? 7 : 1
        console.log('设置Cookie，过期天数:', expiryDays, '记住我:', rememberMe)
        
        CookieUtil.setCookie('token', newToken, expiryDays)
        CookieUtil.setCookie('user_id', user_id, expiryDays)
        CookieUtil.setCookie('username', user, expiryDays)
        CookieUtil.setCookie('rememberMe', rememberMe ? 'true' : 'false', expiryDays)
        
        // 配置axios默认请求头
        axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
        
        // 打印当前Cookie状态以便调试
        setTimeout(() => {
          console.log('登录后Cookie状态:',{
            token: CookieUtil.getCookie('token') ? '已设置' : '未设置',
            userId: CookieUtil.getCookie('user_id'),
            rememberMe: CookieUtil.getCookie('rememberMe')
          })
        }, 100)
        
        return { success: true, userId: user_id }
      } else {
        throw new Error(response.data.message || '登录失败')
      }
    } catch (error) {
      console.error('登录失败:', error)
      
      // 添加更详细的错误信息
      if (error.response) {
        console.error('服务器响应:', error.response.data)
        console.error('状态码:', error.response.status)
      }
      
      return { 
        success: false, 
        message: error.response?.data?.message || error.message || '登录失败，请稍后重试'
      }
    }
  }

  // 登出
  const logout = () => {
    // 清除Cookie
    CookieUtil.deleteCookie('token')
    CookieUtil.deleteCookie('user_id')
    CookieUtil.deleteCookie('username')
    CookieUtil.deleteCookie('rememberMe')
    
    // 清除状态
    isLoggedIn.value = false
    userId.value = null
    username.value = ''
    token.value = null
    
    // 移除axios默认请求头中的token
    delete axiosInstance.defaults.headers.common['Authorization']
    
    console.log('用户已登出')
  }

  // 获取访问令牌
  const getToken = () => {
    return CookieUtil.getCookie('token')
  }

  return {
    isLoggedIn,
    userId,
    username,
    token,
    initializeState,
    login,
    logout,
    getToken
  }
}) 