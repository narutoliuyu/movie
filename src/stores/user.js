import { defineStore } from 'pinia'
import { ref } from 'vue'
import { CookieUtil } from '../api/config'
import { checkLoginStatus, login as authLogin, logout as authLogout } from '../utils/auth'

export const useUserStore = defineStore('user', () => {
  // 状态
  const isLoggedIn = ref(false)
  const userId = ref(null)
  const username = ref('')

  // 初始化状态 - 从Cookie恢复
  const initializeState = async () => {
    console.log('初始化用户状态...')
    
    // 直接从Cookie中获取基本信息
    const token = CookieUtil.getCookie('token')
    const storedUserId = CookieUtil.getCookie('userId')
    const rememberMeEnabled = CookieUtil.getCookie('rememberMe') === 'true'
    
    console.log('Cookie中的状态:', { token, storedUserId, rememberMeEnabled })
    
    // 如果Cookie中有token和userId，先设置为已登录状态
    if (token && storedUserId && rememberMeEnabled) {
      isLoggedIn.value = true
      userId.value = storedUserId
      console.log('从Cookie恢复登录状态:', { isLoggedIn: isLoggedIn.value, userId: userId.value })
    }
    
    // 无论是否已从Cookie恢复状态，都尝试与后端验证
    if (token) {
      try {
        const result = await checkLoginStatus()
        // 更新状态以匹配后端验证结果
        isLoggedIn.value = result.isLoggedIn
        userId.value = result.userId
        console.log('后端验证登录状态:', { isLoggedIn: isLoggedIn.value, userId: userId.value })
      } catch (error) {
        console.error('验证登录状态出错:', error)
        // 验证失败时，保持从Cookie恢复的状态，而不是直接清除
        if (rememberMeEnabled) {
          console.log('保持从Cookie恢复的状态')
        } else {
          // 如果没有"记住我"，则清除状态
          isLoggedIn.value = false
          userId.value = null
        }
      }
    }
    
    console.log('用户状态初始化完成:', { isLoggedIn: isLoggedIn.value, userId: userId.value })
  }

  // 登录
  const login = async (user, password, rememberMe = false) => {
    const result = await authLogin(user, password, rememberMe)
    if (result.success) {
      isLoggedIn.value = true
      userId.value = result.userId
      console.log('存储中的登录成功:', { isLoggedIn: isLoggedIn.value, userId: userId.value })
    }
    return result
  }

  // 登出
  const logout = () => {
    authLogout()
    isLoggedIn.value = false
    userId.value = null
    username.value = ''
  }

  // 获取访问令牌
  const getToken = () => {
    return CookieUtil.getCookie('token')
  }

  return {
    isLoggedIn,
    userId,
    username,
    initializeState,
    login,
    logout,
    getToken
  }
}) 