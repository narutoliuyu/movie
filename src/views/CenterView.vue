<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Profile from '../components/Profile.vue';
import Vip from '../components/Vip.vue';
import History from '../components/History.vue';
import Message from '../components/Message.vue';
import Favorites from '../components/Favorites.vue';
import NavBar from '../components/NavBar.vue';
import backIcon from '../assets/返回.png';

// 导入正确的图标
import userIcon from '../assets/个人中心.png';
import vipIcon from '../assets/vip.png';
import historyIcon from '../assets/历史记录.png';
import messageIcon from '../assets/消息.png';
import favoritesIcon from '../assets/收藏.png';

const route = useRoute();
const router = useRouter();
const currentComponent = ref('profile');

const components = {
  profile: Profile,
  vip: Vip,
  history: History,
  message: Message,
  favorites: Favorites
};

const menuItems = [
  { id: 'profile', name: '个人资料', icon: userIcon },
  { id: 'vip', name: 'VIP会员', icon: vipIcon },
  { id: 'favorites', name: '我的收藏', icon: favoritesIcon },
  { id: 'history', name: '观看历史', icon: historyIcon },
  { id: 'message', name: '消息中心', icon: messageIcon }
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
    <NavBar />
    
    <div class="center-content">
      <div class="back-home" @click="goToHome">
        <img :src="backIcon" alt="返回主页" class="back-icon" />
        <span>返回主页</span>
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
            <img :src="item.icon" alt="图标" class="menu-icon" />
            <span>{{ item.name }}</span>
          </div>
        </div>
        
        <div class="content">
          <component :is="components[currentComponent]" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.center-view {
  min-height: 100vh;
  background: #0f1129;
  color: white;
}

.center-content {
  padding-top: 90px;
  min-height: calc(100vh - 90px);
  display: flex;
  flex-direction: column;
}

.back-home {
  display: flex;
  align-items: center;
  padding: 1rem 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #b9bad3;
  width: fit-content;
}

.back-home:hover {
  color: #e94560;
  transform: translateX(-5px);
}

.back-icon {
  width: 24px;
  height: 24px;
  margin-right: 8px;
}

.main-content {
  display: flex;
  flex: 1;
  padding: 2rem;
  gap: 2rem;
}

.sidebar {
  width: 200px;
  padding: 1.5rem 0;
  height: fit-content;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 0.8rem 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #b9bad3;
  position: relative;
  overflow: hidden;
  gap: 0.8rem;
  margin: 0.3rem 0;
  border-radius: 8px;
}

.menu-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 4px;
  background: linear-gradient(to bottom, #e94560, #c23758);
  transform: scaleY(0);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0;
}

.menu-item:hover {
  background: rgba(233, 69, 96, 0.1);
  color: white;
  transform: translateX(4px);
}

.menu-item:hover::before {
  transform: scaleY(0.7);
  opacity: 1;
}

.menu-item.active {
  background: rgba(233, 69, 96, 0.15);
  color: #e94560;
  transform: translateX(6px);
}

.menu-item.active::before {
  transform: scaleY(1);
  opacity: 1;
}

.menu-icon {
  width: 22px;
  height: 22px;
  transition: all 0.3s ease;
  opacity: 0.9;
}

.menu-item:hover .menu-icon,
.menu-item.active .menu-icon {
  transform: scale(1.15);
  filter: brightness(1.2);
  opacity: 1;
}

.content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  max-height: calc(100vh - 200px);
  border-radius: 12px;
  position: relative;
  background: transparent;
  display: flex;
  justify-content: center;
}

.content > * {
  width: 100%;
  max-width: 800px;
}

@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
    padding: 1rem;
    gap: 1rem;
  }
  
  .sidebar {
    width: 100%;
    padding: 0.5rem 0;
  }
  
  .content {
    padding: 1.5rem;
    max-height: none;
  }
}

::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: rgba(233, 69, 96, 0.5);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(233, 69, 96, 0.7);
}
</style>
