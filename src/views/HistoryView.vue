<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { getApiUrl, API_PATHS, CookieUtil } from '../api/config';
import { useUserStore } from '../stores/user';
import NavBar from '../components/NavBar.vue';

const router = useRouter();
const userStore = useUserStore();
const watchHistory = ref([]);
const loading = ref(true);
const error = ref('');

const fetchWatchHistory = async () => {
  try {
    loading.value = true;
    error.value = '';
    
    // 如果用户已登录，尝试从后端获取数据
    if (userStore.isLoggedIn && userStore.userId) {
      try {
        const token = CookieUtil.getCookie('token');
        const response = await axios.get(getApiUrl('/api/history'), {
          headers: { Authorization: `Bearer ${token}` },
          params: { user_id: userStore.userId }
        });

        if (response.data.status === 'success') {
          watchHistory.value = response.data.data;
          loading.value = false;
          return;
        }
      } catch (err) {
        console.error('从后端获取观看历史失败:', err);
        // 后端获取失败，尝试从本地存储获取
      }
    }
    
    // 从本地存储获取观看历史
    console.log('从本地存储获取观看历史');
    const localHistory = localStorage.getItem('watchHistory');
    if (localHistory) {
      try {
        watchHistory.value = JSON.parse(localHistory);
      } catch (e) {
        console.error('解析本地观看历史失败:', e);
        watchHistory.value = [];
        error.value = '解析观看历史数据失败';
      }
    } else {
      watchHistory.value = [];
    }
  } catch (err) {
    console.error('获取观看历史错误:', err);
    error.value = err.message || '获取观看历史失败';
    watchHistory.value = [];
  } finally {
    loading.value = false;
  }
};

const handleMovieClick = (movieId) => {
  router.push(`/movie/${movieId}`);
};

const clearHistory = async () => {
  try {
    // 如果用户已登录，尝试清除后端数据
    if (userStore.isLoggedIn && userStore.userId) {
      try {
        const token = CookieUtil.getCookie('token');
        await axios.delete(getApiUrl('/api/history/clear'), {
          headers: { Authorization: `Bearer ${token}` },
          params: { user_id: userStore.userId }
        }).catch((err) => {
          // 如果后端API不存在，只记录错误但继续执行
          console.log('后端API可能不存在，只清除本地存储', err);
        });
      } catch (err) {
        console.error('清除后端观看历史失败:', err);
        // 即使后端清除失败，仍然清除本地存储
      }
    }

    // 清除本地存储 - 无论用户是否登录
    localStorage.removeItem('watchHistory');
    watchHistory.value = [];
    
    // 显示成功提示
    alert('观看历史已清空');
  } catch (err) {
    console.error('清除观看历史失败:', err);
    error.value = '清除历史记录失败';
  }
};

onMounted(() => {
  fetchWatchHistory();
});
</script>

<template>
  <div class="history-page">
    <NavBar />
    
    <div class="history-container">
      <div class="history-header">
        <div class="header-left">
          <h1>观看历史</h1>
          <button @click="router.push('/')" class="home-btn">
            <i class="home-icon">🏠</i>
            返回首页
          </button>
        </div>
        <button v-if="watchHistory.length > 0" @click="clearHistory" class="clear-btn">
          <i class="clear-icon">🗑️</i>
          清空历史
        </button>
      </div>

      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="error" class="error-message">
        <p>{{ error }}</p>
      </div>

      <div v-else-if="watchHistory.length === 0" class="empty-history">
        <div class="empty-icon">📺</div>
        <p>暂无观看记录</p>
        <button @click="router.push('/')" class="browse-btn">
          去浏览电影
        </button>
      </div>

      <div v-else class="history-list">
        <div 
          v-for="movie in watchHistory" 
          :key="movie.id"
          class="history-item"
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
            <div class="movie-meta">
              <span class="watch-time">
                <i class="time-icon">🕒</i>
                {{ new Date(movie.watch_time).toLocaleString() }}
              </span>
            </div>
            <p class="movie-desc">{{ movie.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.history-page {
  min-height: 100vh;
  background-color: #0f1129;
  color: white;
  padding-top: 90px;
  overflow-y: auto;
  position: relative;
}

.history-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  height: calc(100vh - 90px);
  overflow-y: auto;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 1rem;
  position: sticky;
  top: 0;
  background-color: #0f1129;
  z-index: 10;
  padding-top: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.history-header h1 {
  font-size: 2rem;
  color: #e94560;
  text-shadow: 0 0 10px rgba(233, 69, 96, 0.3);
  margin: 0;
}

.home-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #16213e;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 50px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.home-btn:hover {
  background-color: #1a1a2e;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
}

.clear-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: rgba(233, 69, 96, 0.2);
  color: #e94560;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.clear-btn:hover {
  background-color: rgba(233, 69, 96, 0.3);
  transform: translateY(-2px);
}

.loading, .empty-history, .error-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
  color: #b9bad3;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e94560;
  border-top: 4px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.6;
}

.browse-btn {
  margin-top: 1rem;
  background-color: #e94560;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 8px rgba(233, 69, 96, 0.3);
}

.browse-btn:hover {
  background-color: #d03651;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(233, 69, 96, 0.4);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
}

.history-item {
  display: flex;
  gap: 1.5rem;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.history-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  background-color: rgba(255, 255, 255, 0.1);
}

.movie-poster {
  width: 150px;
  height: 220px;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.play-icon {
  font-size: 2rem;
  color: white;
  background-color: rgba(233, 69, 96, 0.8);
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.history-item:hover .play-overlay {
  opacity: 1;
}

.history-item:hover .movie-poster img {
  transform: scale(1.1);
}

.movie-info {
  padding: 1.2rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.movie-info h3 {
  font-size: 1.5rem;
  margin-bottom: 0.8rem;
  color: white;
  font-weight: 600;
}

.movie-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  color: #b9bad3;
  font-size: 0.875rem;
}

.watch-time {
  background-color: rgba(233, 69, 96, 0.2);
  padding: 0.25rem 0.8rem;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.movie-desc {
  color: #b9bad3;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.6;
  font-size: 0.95rem;
  flex-grow: 1;
}

@media (max-width: 768px) {
  .history-container {
    padding: 1rem;
  }
  
  .history-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-left {
    width: 100%;
    justify-content: space-between;
  }
  
  .clear-btn {
    align-self: flex-end;
  }
  
  .history-item {
    flex-direction: column;
  }
  
  .movie-poster {
    width: 100%;
    height: 200px;
  }
  
  .movie-info {
    padding: 1rem;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .history-container {
    padding: 1.5rem;
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