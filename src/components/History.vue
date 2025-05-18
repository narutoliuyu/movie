<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { getApiUrl, API_PATHS, CookieUtil } from '../api/config';
import { useUserStore } from '../stores/user';
import backIcon from '../assets/返回.png';

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
        // 尝试多种可能的API路径
        let response;
        let success = false;
        
        // 尝试路径1
        try {
          response = await axios.get(getApiUrl('/api/history'), {
            headers: { Authorization: `Bearer ${token}` },
            params: { user_id: userStore.userId }
          });
          success = true;
        } catch (err1) {
          console.error('第一种API路径尝试失败:', err1);
          
          // 尝试路径2
          try {
            response = await axios.get(getApiUrl(`/api/users/${userStore.userId}/history`), {
              headers: { Authorization: `Bearer ${token}` }
            });
            success = true;
          } catch (err2) {
            console.error('第二种API路径尝试失败:', err2);
            
            // 尝试路径3
            try {
              response = await axios.get(getApiUrl('/api/user/history'), {
                headers: { Authorization: `Bearer ${token}` }
              });
              success = true;
            } catch (err3) {
              console.error('所有API路径尝试失败，尝试从本地存储获取');
            }
          }
        }

        if (success && response.data.status === 'success') {
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
  // 在进入电影详情页前，保存来源信息
  sessionStorage.setItem('fromCenterComponent', 'history');
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

const goToHome = () => {
  router.push('/');
};

onMounted(() => {
  fetchWatchHistory();
});
</script>

<template>
  <div class="history-container history-component">
    <div class="history-header">
      <h2>观看历史</h2>
      <div class="header-actions">
        <button v-if="watchHistory.length > 0" @click="clearHistory" class="clear-btn">
          <img src="../assets/清空.png" alt="清空历史" class="clear-icon">
          清空历史
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchWatchHistory" class="retry-btn">重试</button>
    </div>

    <div v-else-if="watchHistory.length === 0" class="empty-history">
      <div class="empty-icon">📺</div>
      <p>暂无观看记录</p>
      <button @click="goToHome" class="browse-btn">
        去浏览电影
      </button>
    </div>

    <div v-else class="history-grid">
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
          <div class="watch-progress">
            <div class="progress-bar" :style="{width: movie.progress + '%'}"></div>
          </div>
        </div>
        <div class="movie-info">
          <h3>{{ movie.title }}</h3>
          <p class="watch-time">{{ new Date(movie.watch_time).toLocaleString() }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.history-container {
  width: 100%;
  max-width: 1200px;
  color: white;
  padding: 0 1rem;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  width: 100%;
}

.history-header h2 {
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

.loading, .empty-history, .error-message {
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

.history-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.5rem;
  width: 100%;
}

.history-item {
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

.history-item:hover {
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

.history-item:hover .play-overlay {
  opacity: 1;
}

.history-item:hover .play-icon {
  transform: scale(1);
}

.history-item:hover .movie-poster img {
  transform: scale(1.1);
}

.watch-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background-color: rgba(0, 0, 0, 0.5);
}

.progress-bar {
  height: 100%;
  background-color: #e94560;
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

.watch-time {
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
  .history-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 1rem;
  }
  
  .movie-info h3 {
    font-size: 0.9rem;
  }
  
  .watch-time {
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