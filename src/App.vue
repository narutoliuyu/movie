<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useUserStore } from './stores/user'

const userStore = useUserStore()

// 在页面可见性变化时检查登录状态
const handleVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    console.log('页面变为可见，重新检查登录状态')
    try {
      userStore.initializeState()
      console.log('页面可见性变化后，用户状态初始化成功')
    } catch (error) {
      console.error('页面可见性变化后初始化用户状态失败:', error)
    }
  }
}

// 组件挂载时初始化用户状态
onMounted(async () => {
  try {
    // 初始化用户状态
    await userStore.initializeState()
    console.log('App mounted, user state initialized')
  } catch (error) {
    console.error('App挂载时初始化用户状态失败:', error)
  }
  
  // 添加页面可见性变化事件监听器
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

// 清理事件监听器
onUnmounted(() => {
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>

<template>
  <router-view />
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
  background-color: #0f1129;
}

#app {
  width: 100%;
  height: 100%;
  font-family: 'Arial', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
