<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Profile from '../components/Profile.vue';
import Vip from '../components/Vip.vue';
import History from '../components/History.vue';
import Message from '../components/Message.vue';

const route = useRoute();
const router = useRouter();
const currentComponent = ref('profile');

const components = {
  profile: Profile,
  vip: Vip,
  history: History,
  message: Message
};

const menuItems = [
  { id: 'profile', name: '个人资料' },
  { id: 'vip', name: 'VIP会员' },
  { id: 'history', name: '观看历史' },
  { id: 'message', name: '消息中心' }
];

// 监听路由查询参数变化
watch(
  () => route.query.component,
  (newComponent) => {
    if (newComponent && components[newComponent]) {
      currentComponent.value = newComponent;
    }
  },
  { immediate: true }
);

const goToHome = () => {
  router.push('/');
};
</script>

<template>
  <div class="center-view">
    <div class="header">
      <button class="back-button" @click="goToHome">
        <i class="back-icon">←</i>
        返回首页
      </button>
      <h1>个人中心</h1>
    </div>
    
    <div class="main-content">
      <div class="sidebar">
        <div 
          v-for="item in menuItems" 
          :key="item.id"
          class="menu-item"
          :class="{ active: currentComponent === item.id }"
          @click="currentComponent = item.id"
        >
          {{ item.name }}
        </div>
      </div>
      
      <div class="content">
        <component :is="components[currentComponent]" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.center-view {
  min-height: 100vh;
  background: #1a1a2e;
  color: white;
  padding-top: 70px;
}

.header {
  background: #16213e;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #e94560;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.back-button:hover {
  background: #d03651;
  transform: translateY(-2px);
}

.back-icon {
  font-size: 1.2rem;
}

.header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: white;
}

.main-content {
  display: flex;
  min-height: calc(100vh - 130px);
  padding: 2rem;
  gap: 2rem;
}

.sidebar {
  width: 200px;
  background: #16213e;
  padding: 1.5rem 0;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  height: fit-content;
}

.menu-item {
  padding: 1rem 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #fff;
  border-left: 4px solid transparent;
}

.menu-item:hover {
  background: rgba(233, 69, 96, 0.1);
  color: #e94560;
  border-left-color: #e94560;
}

.menu-item.active {
  background: rgba(233, 69, 96, 0.2);
  color: #e94560;
  border-left-color: #e94560;
}

.content {
  flex: 1;
  background: #16213e;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
    padding: 1rem;
  }
  
  .sidebar {
    width: 100%;
  }
  
  .content {
    padding: 1rem;
  }
}
</style>
