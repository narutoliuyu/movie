import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import { useUserStore } from './stores/user'
import { CookieUtil } from './api/config'

const app = createApp(App)
const pinia = createPinia()

app.use(router)
app.use(pinia)

// 确保在挂载应用前初始化用户状态
const initApp = async () => {
  try {
    // 先初始化Pinia
    const store = useUserStore(pinia)
    
    // 记录初始Cookie状态，帮助调试
    const initialToken = CookieUtil.getCookie('token')
    const initialUserId = CookieUtil.getCookie('user_id')
    const rememberMe = CookieUtil.getCookie('rememberMe') === 'true'
    
    console.log('应用启动时的Cookie状态:', {
      token: initialToken ? '存在' : '不存在',
      userId: initialUserId || '不存在',
      rememberMe: rememberMe ? '启用' : '未启用'
    })
    
    // 添加全局错误处理
    app.config.errorHandler = (err, vm, info) => {
      console.error('Vue全局错误:', err)
      console.log('错误组件:', vm)
      console.log('错误信息:', info)
    }
    
    // 添加路由守卫，确保在每次路由变化时检查登录状态
    router.beforeEach(async (to, from, next) => {
      // 如果用户已登录状态可疑，这里可以刷新用户状态
      const hasToken = CookieUtil.getCookie('token')
      if (store.isLoggedIn && !hasToken) {
        console.warn('路由守卫检测到登录状态不一致，重置状态')
        store.logout()
      }
      next()
    })
    
    // 挂载应用
    app.mount('#app')
    console.log('应用成功挂载')
  } catch (error) {
    console.error('应用初始化失败:', error)
    // 尝试优雅降级处理
    app.mount('#app')
  }
}

initApp().catch(err => {
  console.error('应用启动过程中出现未捕获的错误:', err)
  // 最后尝试挂载应用，确保用户界面至少能显示
  app.mount('#app')
})
