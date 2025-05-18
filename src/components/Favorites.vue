<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/user';
import axios from 'axios';
import { getApiUrl, CookieUtil } from '../api/config';

const router = useRouter();
const userStore = useUserStore();
const favorites = ref([]);
const loading = ref(true);
const error = ref('');

const fetchFavorites = async () => {
  try {
    loading.value = true;
    error.value = '';
    
    // 从本地存储获取收藏数据
    const localFavorites = localStorage.getItem('favorites');
    if (localFavorites) {
      favorites.value = JSON.parse(localFavorites);
    } else {
      favorites.value = [];
    }
    
    // 如果用户已登录，尝试从后端获取数据合并
    if (userStore.isLoggedIn && userStore.userId) {
      try {
        const token = CookieUtil.getCookie('token');
        const response = await axios.get(getApiUrl('/api/user/favorites'), {
          headers: { Authorization: `Bearer ${token}` }
        }).catch(err => {
          console.log('后端API可能不存在，仅使用本地数据', err);
        });
        
        if (response && response.data && response.data.status === 'success') {
          // 合并本地和服务器数据
          const serverFavorites = response.data.data;
          const merged = [...favorites.value];
          
          // 添加服务器上有但本地没有的收藏
          for (const serverFav of serverFavorites) {
            if (!merged.some(item => item.movie_id === serverFav.movie_id)) {
              merged.push(serverFav);
            }
          }
          
          favorites.value = merged;
          // 更新本地存储
          localStorage.setItem('favorites', JSON.stringify(merged));
        }
      } catch (err) {
        console.error('从后端获取收藏失败:', err);
      }
    }
  } catch (err) {
    console.error('获取收藏错误:', err);
    error.value = err.message || '获取收藏失败';
  } finally {
    loading.value = false;
  }
};

// 清空所有收藏
const clearAllFavorites = async () => {
  try {
    // 清空本地收藏
    localStorage.removeItem('favorites');
    favorites.value = [];
    
    // 如果用户已登录，尝试清除后端数据
    if (userStore.isLoggedIn && userStore.userId) {
      try {
        const token = CookieUtil.getCookie('token');
        await axios.delete(getApiUrl('/api/user/favorites/clear'), {
          headers: { Authorization: `Bearer ${token}` },
          params: { user_id: userStore.userId }
        }).catch(err => {
          console.log('后端API可能不存在，只清除本地存储', err);
        });
      } catch (err) {
        console.error('清除后端收藏数据失败:', err);
      }
    }
    
    // 显示成功提示
    alert('收藏已清空');
  } catch (err) {
    console.error('清空收藏失败:', err);
  }
};

const handleMovieClick = (movieId) => {
  // 在进入电影详情页前，保存来源信息
  sessionStorage.setItem('fromCenterComponent', 'favorites');
  router.push(`/movie/${movieId}`);
};

const removeFromFavorites = async (movieId) => {
  try {
    // 从本地移除
    favorites.value = favorites.value.filter(item => item.movie_id !== movieId);
    localStorage.setItem('favorites', JSON.stringify(favorites.value));
    
    // 如果用户已登录，尝试从服务器也移除
    if (userStore.isLoggedIn && userStore.userId) {
      const token = CookieUtil.getCookie('token');
      await axios.delete(getApiUrl(`/api/user/favorites/${movieId}`), {
        headers: { Authorization: `Bearer ${token}` }
      }).catch(err => {
        console.log('后端API可能不存在，仅更新本地数据', err);
      });
    }
  } catch (err) {
    console.error('移除收藏失败:', err);
  }
};

onMounted(() => {
  fetchFavorites();
});
</script>

<template>
  <div class="favorites-container favorites-component">
    <div class="favorites-header">
      <h2>我的收藏</h2>
      <div class="header-actions">
        <button v-if="favorites.length > 0" @click="clearAllFavorites" class="clear-btn">
          <!-- 清空图标占位，需要替换为实际图标 -->
          <img src="../assets/清空.png" alt="清空收藏" class="clear-icon">
          清空收藏
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchFavorites" class="retry-btn">重试</button>
    </div>

    <div v-else-if="favorites.length === 0" class="empty-favorites">
      <div class="empty-icon">♡</div>
      <p>暂无收藏电影</p>
      <button @click="router.push('/')" class="browse-btn">
        去浏览电影
      </button>
    </div>

    <div v-else class="favorites-grid">
      <div 
        v-for="movie in favorites" 
        :key="movie.movie_id"
        class="favorite-item"
        @click="handleMovieClick(movie.movie_id)"
      >
        <div class="movie-poster">
          <img :src="movie.poster_url" :alt="movie.title">
          <div class="play-overlay">
            <span class="play-icon">▶</span>
          </div>
        </div>
        <div class="movie-info">
          <h3>{{ movie.title }}</h3>
          <p class="add-time">{{ new Date(movie.add_time || Date.now()).toLocaleString() }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.favorites-container {
  width: 100%;
  max-width: 1200px;
  color: white;
  padding: 0 1rem;
}

.favorites-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  width: 100%;
}

.favorites-header h2 {
  font-size: 1.8rem;
  font-weight: 600;
  color: white;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.clear-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, rgba(233, 69, 96, 0.1), rgba(233, 69, 96, 0.2));
  color: #e94560;
  border: none;
  padding: 0.7rem 1.2rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
  border: 1px solid rgba(233, 69, 96, 0.3);
}

.clear-btn:hover {
  background: linear-gradient(135deg, rgba(233, 69, 96, 0.2), rgba(233, 69, 96, 0.3));
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.2);
}

.clear-icon {
  width: 18px;
  height: 18px;
  object-fit: contain;
  opacity: 0.9;
  transition: transform 0.3s ease;
}

.clear-btn:hover .clear-icon {
  transform: rotate(10deg);
  opacity: 1;
}

.loading, .empty-favorites, .error-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
  color: #b9bad3;
  margin-top: 2rem;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(233, 69, 96, 0.3);
  border-top: 4px solid #e94560;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 4.5rem;
  margin-bottom: 1.5rem;
  opacity: 0.6;
}

.browse-btn, .retry-btn {
  margin-top: 1.5rem;
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  border: none;
  padding: 0.8rem 1.8rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
  font-weight: 500;
}

.browse-btn:hover, .retry-btn:hover {
  background: linear-gradient(135deg, #e94560, #a92e48);
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(233, 69, 96, 0.4);
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.5rem;
  width: 100%;
}

.favorite-item {
  display: flex;
  flex-direction: column;
  background: linear-gradient(145deg, rgba(19, 23, 58, 0.7), rgba(23, 28, 73, 0.7));
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.05);
  height: 100%;
}

.favorite-item:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.3);
}

.movie-poster {
  position: relative;
  aspect-ratio: 2/3;
  overflow: hidden;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8) 0%, rgba(0, 0, 0, 0) 60%);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.4s ease;
}

.play-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #e94560, #c23758);
  border-radius: 50%;
  color: white;
  box-shadow: 0 4px 15px rgba(233, 69, 96, 0.5);
  transform: scale(0.8);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.favorite-item:hover .play-overlay {
  opacity: 1;
}

.favorite-item:hover .play-icon {
  transform: scale(1);
}

.favorite-item:hover .movie-poster img {
  transform: scale(1.1);
}

.movie-info {
  padding: 1rem;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.movie-info h3 {
  font-size: 1rem;
  margin-bottom: 0.5rem;
  color: white;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.add-time {
  color: #b9bad3;
  font-size: 0.8rem;
  margin: 0;
}

.error-message p {
  color: #e94560;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .favorites-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 1rem;
  }
  
  .movie-info h3 {
    font-size: 0.9rem;
  }
  
  .add-time {
    font-size: 0.75rem;
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