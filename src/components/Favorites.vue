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

const handleMovieClick = (movieId) => {
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
  <div class="favorites-container">
    <div class="favorites-header">
      <h2>我的收藏</h2>
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
      >
        <div class="movie-poster" @click="handleMovieClick(movie.movie_id)">
          <img :src="movie.poster_url" :alt="movie.title">
          <div class="play-overlay">
            <span class="play-icon">▶</span>
          </div>
        </div>
        <div class="movie-info">
          <h3>{{ movie.title }}</h3>
          <div class="actions">
            <button class="watch-btn" @click="handleMovieClick(movie.movie_id)">
              观看
            </button>
            <button class="remove-btn" @click="removeFromFavorites(movie.movie_id)">
              移除
            </button>
          </div>
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

.loading, .empty-favorites, .error-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
  color: #b9bad3;
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
  font-size: 4rem;
  color: rgba(233, 69, 96, 0.3);
  margin-bottom: 1rem;
}

.empty-favorites p {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.browse-btn, .retry-btn {
  background: linear-gradient(135deg, rgba(233, 69, 96, 0.8), rgba(194, 55, 88, 0.8));
  color: white;
  border: none;
  padding: 0.8rem 1.8rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  font-weight: 500;
}

.browse-btn:hover, .retry-btn:hover {
  background: linear-gradient(135deg, #e94560, #c23758);
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(233, 69, 96, 0.4);
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
  margin-top: 1rem;
}

.favorite-item {
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.favorite-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: rgba(233, 69, 96, 0.3);
}

.movie-poster {
  position: relative;
  aspect-ratio: 2/3;
  overflow: hidden;
  cursor: pointer;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.movie-poster:hover img {
  transform: scale(1.08);
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.movie-poster:hover .play-overlay {
  opacity: 1;
}

.play-icon {
  font-size: 2.5rem;
  color: white;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}

.movie-info {
  padding: 1rem;
}

.movie-info h3 {
  margin: 0 0 1rem;
  font-size: 1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.watch-btn, .remove-btn {
  padding: 0.5rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.8rem;
  flex: 1;
  transition: all 0.3s ease;
}

.watch-btn {
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
}

.watch-btn:hover {
  background: linear-gradient(135deg, #e94560, #a92e48);
  transform: translateY(-2px);
}

.remove-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #e0e0e0;
}

.remove-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .favorites-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 1rem;
  }
  
  .movie-info h3 {
    font-size: 0.9rem;
  }
  
  .actions {
    flex-direction: column;
  }
}
</style> 