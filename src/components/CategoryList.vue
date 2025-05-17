<script setup>
import { ref, onMounted, defineEmits, defineProps } from 'vue';
import { axiosInstance, getApiUrl, API_PATHS, API_CONFIG } from '../api/config';

// 导入图标 - 使用中文文件名
import actionIcon from '../assets/动作.png';
import comedyIcon from '../assets/喜剧.png';
import sciFiIcon from '../assets/科幻.png';
import romanceIcon from '../assets/爱情 约会.png';
import animationIcon from '../assets/动漫.png';
import plotIcon from '../assets/画面剧情.png';
import videoIcon from '../assets/视频短视频.png';
import historyIcon from '../assets/历史记录.png';
import messageIcon from '../assets/消息.png';
import homeIcon from '../assets/首页.png';
import errorIcon from '../assets/错误.png';
import vipIcon from '../assets/vip.png';
import allIcon from '../assets/全部.png';
import hotIcon from '../assets/热门.png';

const props = defineProps({
  categories: {
    type: Array,
    required: true
  },
  activeCategory: {
    type: Number,
    default: null
  }
});

const emit = defineEmits(['category-change']);
const loading = ref(true);
const error = ref(null);

// 类别ID到图标的映射（修复映射关系）
const getCategoryIconById = (id) => {
  const idToIcon = {
    1: actionIcon,    // 动作
    2: comedyIcon,    // 喜剧
    3: sciFiIcon,     // 科幻
    4: romanceIcon,   // 爱情
    5: animationIcon, // 动漫
    6: plotIcon,      // 剧情
    7: historyIcon,   // 历史
    8: videoIcon,     // 短视频
    9: vipIcon,       // VIP专区
    10: hotIcon,      // 热门
    11: messageIcon,  // 消息
  };
  
  // 确保ID是数字
  const numId = parseInt(id, 10);
  return idToIcon[numId] || homeIcon; // 如果找不到匹配，返回首页图标作为默认
};

const fetchCategories = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await axiosInstance.get('/api/categories');
    
    // 处理响应数据
    let categoriesData = [];
    if (response.data && response.data.data) {
      categoriesData = Array.isArray(response.data.data) ? response.data.data : [];
    } else if (response.data) {
      categoriesData = Array.isArray(response.data) ? response.data : [];
    } else {
      console.warn('响应数据格式异常:', response.data);
    }
    
    // 直接使用后端数据，添加图标
    const processedCategories = categoriesData.map(category => {
      const categoryWithIcon = {
        id: category.id,
        name: category.name,
        icon: getCategoryIconById(category.id)
      };
      return categoryWithIcon;
    });
    
    // 更新响应式数据
    props.categories = processedCategories;
    
    // 触发分类变更事件
    if (props.categories.length > 0) {
      props.activeCategory = props.categories[0].id;
      emit('category-change', props.activeCategory);
    }
  } catch (err) {
    console.error('获取分类失败:', err);
    error.value = err.response?.data?.message || '获取分类失败';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchCategories();
});

const handleCategoryClick = (categoryId) => {
  emit('category-change', categoryId);
};
</script>

<template>
  <div class="category-sidebar">
    
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>加载分类中...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <img :src="errorIcon" alt="错误" class="error-icon" />
      <p>{{ error }}</p>
      <button @click="fetchCategories" class="retry-button">重试</button>
    </div>
    
    <div class="category-list">
      <div 
        class="category-item" 
        :class="{ active: activeCategory === null }"
        @click="handleCategoryClick(null)"
      >
        <img :src="allIcon" alt="全部" class="category-icon" />
        <span class="category-name">全部电影</span>
      </div>
      <div 
        v-for="category in categories" 
        :key="category.id"
        class="category-item"
        :class="{ active: activeCategory === category.id }"
        @click="handleCategoryClick(category.id)"
      >
        <img :src="getCategoryIconById(category.id)" alt="分类" class="category-icon" />
        <span class="category-name">{{ category.name }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.category-sidebar {
  margin-top: 10px;
  background-color: #0c0e22;
  height: 100%;
  overflow: hidden;
  position: relative;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  height: 100%;
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.category-list::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.category-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.category-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 4px;
  background-color: #e94560;
  transform: scaleY(0);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.category-item:hover {
  transform: translateX(0);
  background-color: rgba(233, 69, 96, 0.05);
}

.category-item:hover::before {
  transform: scaleY(0.6);
}

.category-item.active {
  background-color: rgba(233, 69, 96, 0.1);
}

.category-item.active::before {
  transform: scaleY(1);
}

.category-icon {
  width: 24px;
  height: 24px;
  margin-right: 12px;
  transition: all 0.3s ease;
}

.category-item:hover .category-icon,
.category-item:hover .category-name {
  transform: scale(1.15) translateX(4px);
}

.category-item.active .category-icon {
  transform: scale(1.2) translateX(4px);
  filter: brightness(1.2);
}

.category-name {
  color: #b9bad3;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.category-item:hover .category-name,
.category-item.active .category-name {
  color: #ffffff;
  text-shadow: 0 0 8px rgba(255, 255, 255, 0.4);
}

.category-item.active .category-name {
  transform: scale(1.05) translateX(4px);
}

/* 添加滑动效果 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.category-item {
  animation: slideIn 0.3s ease forwards;
  animation-delay: calc(var(--item-index) * 0.05s);
}

/* 添加点击波纹效果 */
.category-item::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 5px;
  height: 5px;
  background: rgba(233, 69, 96, 0.3);
  opacity: 0;
  border-radius: 100%;
  transform: scale(1, 1) translate(-50%);
  transform-origin: 50% 50%;
}

.category-item:active::after {
  animation: ripple 0.6s ease-out;
}

@keyframes ripple {
  0% {
    transform: scale(0, 0);
    opacity: 0.5;
  }
  100% {
    transform: scale(20, 20);
    opacity: 0;
  }
}

.loading, .error {
  padding: 2rem 1rem;
  text-align: center;
  color: #e0e0e0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(233, 69, 96, 0.2);
  border-radius: 50%;
  border-top-color: #e94560;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error {
  color: #e94560;
}

.error-icon {
  width: 32px;
  height: 32px;
  margin-bottom: 0.5rem;
}

.retry-button {
  margin-top: 1rem;
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 0.5rem 1.5rem;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
}

.retry-button:hover {
  background: linear-gradient(135deg, #e94560, #aa2a49);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(233, 69, 96, 0.5);
}
</style> 