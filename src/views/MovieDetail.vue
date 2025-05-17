<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import NavBar from '../components/NavBar.vue';
import { getApiUrl, API_PATHS, API_CONFIG, CookieUtil } from '../api/config';
import { useUserStore } from '../stores/user';
import videoUrl from '../assets/video1.mp4';
import backIcon from '../assets/返回.png';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const movie = ref(null);
const loading = ref(true);
const error = ref('');
const showVideo = ref(false);
const isFavorite = ref(false);

// 检查电影是否已收藏
const checkIfFavorite = () => {
  if (!movie.value) return false;
  
  try {
    const favorites = localStorage.getItem('favorites');
    if (favorites) {
      const parsedFavorites = JSON.parse(favorites);
      isFavorite.value = parsedFavorites.some(item => item.movie_id === movie.value.id);
    }
  } catch (err) {
    console.error('检查收藏状态失败:', err);
  }
};

const fetchMovieDetails = async () => {
  try {
    loading.value = true;
    error.value = '';
    const response = await axios.get(getApiUrl('/api/movies/' + route.params.id));
    
    if (response.data.status === 'success') {
      movie.value = response.data.data;
      // 检查是否已收藏
      checkIfFavorite();
    } else {
      throw new Error(response.data.message || '获取电影详情失败');
    }
  } catch (err) {
    console.error('获取电影详情错误:', err);
    if (err.response) {
      if (err.response.status === 404) {
        error.value = '电影不存在或已被删除';
      } else {
        error.value = err.response.data?.message || '获取电影详情失败';
      }
    } else if (err.request) {
      error.value = '无法连接到服务器，请检查网络连接';
    } else {
      error.value = err.message || '获取电影详情失败';
    }
  } finally {
    loading.value = false;
  }
};

// 收藏电影
const toggleFavorite = async () => {
  if (!movie.value) return;
  
  try {
    // 准备电影数据
    const favoriteItem = {
      movie_id: movie.value.id,
      title: movie.value.title,
      poster_url: movie.value.poster_url,
      description: movie.value.description || '',
      add_time: new Date().toISOString()
    };
    
    // 获取当前收藏
    let favorites = [];
    const savedFavorites = localStorage.getItem('favorites');
    if (savedFavorites) {
      favorites = JSON.parse(savedFavorites);
    }
    
    if (isFavorite.value) {
      // 已收藏，移除
      favorites = favorites.filter(item => item.movie_id !== movie.value.id);
    } else {
      // 未收藏，添加
      favorites.push(favoriteItem);
    }
    
    // 保存到本地
    localStorage.setItem('favorites', JSON.stringify(favorites));
    
    // 更新状态
    isFavorite.value = !isFavorite.value;
    
    // 如果用户已登录，同步到服务器
    if (userStore.isLoggedIn && userStore.userId) {
      const token = CookieUtil.getCookie('token');
      if (isFavorite.value) {
        // 添加收藏
        await axios.post(getApiUrl('/api/user/favorites'), favoriteItem, {
          headers: { Authorization: `Bearer ${token}` }
        }).catch(err => {
          console.log('后端API可能不存在，仅使用本地存储', err);
        });
      } else {
        // 移除收藏
        await axios.delete(getApiUrl(`/api/user/favorites/${movie.value.id}`), {
          headers: { Authorization: `Bearer ${token}` }
        }).catch(err => {
          console.log('后端API可能不存在，仅使用本地存储', err);
        });
      }
    }
  } catch (err) {
    console.error('操作收藏失败:', err);
  }
};

// 添加到观看历史
const addToWatchHistory = async () => {
  if (!movie.value) return;
  
  // 准备观看历史数据
  const historyItem = {
    id: Date.now(), // 本地唯一ID
    movie_id: movie.value.id,
    user_id: userStore.userId || 'guest',
    title: movie.value.title,
    poster_url: movie.value.poster_url,
    description: movie.value.description,
    watch_time: new Date().toISOString(),
    progress: 0
  };
  
  // 如果用户已登录，尝试保存到后端
  if (userStore.isLoggedIn && userStore.userId) {
    try {
      const token = CookieUtil.getCookie('token');
      await axios.post(getApiUrl('/api/history'), historyItem, {
        headers: { Authorization: `Bearer ${token}` }
      }).catch(err => {
        console.log('后端API可能不存在，使用本地存储', err);
        saveToLocalStorage(historyItem);
      });
    } catch (err) {
      console.error('保存观看历史失败:', err);
      // 即使后端保存失败，也保存到本地
      saveToLocalStorage(historyItem);
    }
  } else {
    // 未登录用户保存到本地
    saveToLocalStorage(historyItem);
  }
};

// 保存到本地存储
const saveToLocalStorage = (historyItem) => {
  try {
    // 获取现有历史
    let history = [];
    const savedHistory = localStorage.getItem('watchHistory');
    if (savedHistory) {
      history = JSON.parse(savedHistory);
    }
    
    // 检查是否已存在相同电影，如果存在则更新时间
    const index = history.findIndex(item => item.movie_id === historyItem.movie_id);
    if (index !== -1) {
      history[index] = historyItem;
    } else {
      history.unshift(historyItem); // 新的历史记录放在最前面
    }
    
    // 限制历史记录数量为50条
    if (history.length > 50) {
      history = history.slice(0, 50);
    }
    
    // 保存到本地存储
    localStorage.setItem('watchHistory', JSON.stringify(history));
    console.log('已保存到本地观看历史');
  } catch (err) {
    console.error('保存到本地存储失败:', err);
  }
};

const goBack = () => {
  router.back();
};

const goToHome = () => {
  router.push('/');
};

const playVideo = async () => {
  // 先保存到观看历史
  await addToWatchHistory();
  // 然后显示视频播放器
  showVideo.value = true;
};

const closeVideo = () => {
  showVideo.value = false;
};

onMounted(() => {
  fetchMovieDetails();
});
</script>

<template>
  <div class="movie-detail">
    <NavBar />

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button class="retry-button" @click="fetchMovieDetails">
        重试
      </button>
    </div>

    <div v-else-if="movie" class="movie-content">
      <div class="movie-backdrop" :style="{ backgroundImage: 'url(' + movie.poster_url + ')' }">
        <div class="backdrop-overlay"></div>
      </div>

      <button class="back-button" @click="goToHome">
        <img :src="backIcon" alt="返回" class="back-icon" />
        <span>返回首页</span>
      </button>

      <div class="movie-info">
        <div class="movie-poster-container">
          <div class="movie-poster">
            <img :src="movie.poster_url" :alt="movie.title">
            <div class="rating" v-if="movie.rating">
              <span class="rating-value">{{ movie.rating }}</span>
            </div>
            
            <div class="poster-overlay">
              <div class="overlay-actions">
                <button class="overlay-btn play-btn" @click="playVideo">
                  <i class="play-icon">▶</i>
                  <span>播放</span>
                </button>
                <button class="overlay-btn favorite-btn" @click="toggleFavorite" :class="{ active: isFavorite }">
                  <i class="heart-icon">{{ isFavorite ? '♥' : '♡' }}</i>
                  <span>{{ isFavorite ? '已收藏' : '收藏' }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="movie-details">
          <h1 class="title">{{ movie.title }}</h1>
          
          <div class="meta-info">
            <span class="year">{{ movie.release_date }}</span>
            <span class="type">{{ movie.movie_type }}</span>
          </div>

          <div class="director">
            <span class="label">导演：</span>
            <span class="value">{{ movie.director }}</span>
          </div>

          <div class="description">
            <h3>剧情简介</h3>
            <p>{{ movie.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 视频播放器 -->
    <div v-if="showVideo" class="video-player-overlay" @click="closeVideo">
      <div class="video-player-container" @click.stop>
        <button class="close-button" @click="closeVideo">×</button>
        <video 
          class="video-player" 
          :src="videoUrl" 
          controls 
          autoplay
          ref="videoPlayer"
        ></video>
      </div>
    </div>
  </div>
</template>

<style scoped>
.movie-detail {
  min-height: 100vh;
  background: #0f1129;
  color: white;
  position: relative;
}

.back-button {
  position: absolute;
  top: 100px;
  left: 20px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  background: linear-gradient(135deg, rgba(233, 69, 96, 0.8), rgba(194, 55, 88, 0.8));
  color: white;
  border: none;
  padding: 0.7rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
}

.back-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(233, 69, 96, 0.4);
  background: linear-gradient(135deg, #e94560, #a92e48);
}

.back-icon {
  width: 22px;
  height: 22px;
}

.loading, .error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding-top: 90px;
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

.error p {
  color: #e94560;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.retry-button {
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  border: none;
  padding: 0.8rem 1.8rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
}

.retry-button:hover {
  background: linear-gradient(135deg, #e94560, #a92e48);
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(233, 69, 96, 0.4);
}

.movie-content {
  position: relative;
  min-height: 100vh;
  padding-top: 90px;
}

.movie-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  z-index: 0;
}

.backdrop-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, 
    rgba(15, 17, 41, 0.7) 0%,
    rgba(15, 17, 41, 0.85) 50%,
    rgba(15, 17, 41, 0.95) 100%
  );
  backdrop-filter: blur(20px);
}

.movie-info {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 3rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 8rem 2rem 3rem;
}

.movie-poster-container {
  flex-shrink: 0;
}

.movie-poster {
  width: 300px;
  height: 450px;
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 16px 30px rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.5s ease;
}

.movie-poster:hover img {
  transform: scale(1.05);
}

/* 海报覆盖层 */
.poster-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to top, 
    rgba(0, 0, 0, 0.9) 0%,
    rgba(0, 0, 0, 0.7) 20%,
    rgba(0, 0, 0, 0.4) 40%,
    rgba(0, 0, 0, 0.1) 100%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 1.5rem;
}

.movie-poster:hover .poster-overlay {
  opacity: 1;
}

.overlay-actions {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.overlay-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  border: none;
  border-radius: 8px;
  padding: 0.7rem 0;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: transform 0.2s ease, background-color 0.2s ease;
  opacity: 0;
  transform: translateY(20px);
}

.movie-poster:hover .overlay-btn {
  opacity: 1;
  transform: translateY(0);
}

.play-btn {
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  transition-delay: 0.1s;
}

.play-btn:hover {
  background: linear-gradient(135deg, #e94560, #a92e48);
  transform: translateY(-2px);
}

.favorite-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  transition-delay: 0.2s;
}

.favorite-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.favorite-btn.active {
  color: #e94560;
}

.play-icon, .heart-icon {
  font-size: 1.2rem;
}

.heart-icon {
  color: white;
  transition: color 0.3s ease;
}

.favorite-btn.active .heart-icon {
  color: #e94560;
}

.rating {
  position: absolute;
  top: 12px;
  right: 12px;
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  padding: 0.4rem 0.7rem;
  border-radius: 10px;
  font-weight: bold;
  font-size: 0.95rem;
  box-shadow: 0 4px 10px rgba(233, 69, 96, 0.5);
  z-index: 2;
}

.movie-details {
  flex: 1;
  padding-top: 1rem;
}

.title {
  font-size: 3rem;
  margin-bottom: 1.5rem;
  font-weight: bold;
  text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.4);
  background: linear-gradient(45deg, #ffffff, #e94560);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 1px;
}

.meta-info {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.8rem;
}

.year, .type {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 30px;
  backdrop-filter: blur(8px);
  font-size: 0.95rem;
  color: #e0e0e0;
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.year:hover, .type:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.director {
  margin-bottom: 2rem;
  color: #e0e0e0;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.director:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.label {
  color: #b9bad3;
  margin-right: 0.5rem;
  font-weight: 500;
}

.description {
  margin-bottom: 2.5rem;
  padding: 1.8rem;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.description:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.description h3 {
  font-size: 1.5rem;
  margin-bottom: 1.2rem;
  color: #e94560;
  position: relative;
  display: inline-block;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.description h3::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, #e94560, transparent);
  border-radius: 3px;
}

.description p {
  line-height: 1.8;
  color: #e0e0e0;
  font-size: 1.05rem;
}

.video-player-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.9);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(15px);
}

.video-player-container {
  position: relative;
  width: 90%;
  height: 80%;
  max-width: 1280px;
  max-height: 720px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
}

.video-player {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #000;
  border-radius: 16px;
}

.close-button {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(233, 69, 96, 0.8);
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 1001;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.close-button:hover {
  background: #e94560;
  transform: scale(1.1) rotate(90deg);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
}

@media (max-width: 768px) {
  .movie-info {
    flex-direction: column;
    padding: 6rem 1.5rem 2rem;
    align-items: center;
  }

  .movie-poster {
    width: 220px;
    height: 330px;
    margin-bottom: 2rem;
  }

  .title {
    font-size: 2rem;
    text-align: center;
  }

  .meta-info {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .back-button {
    top: 80px;
    left: 50%;
    transform: translateX(-50%);
  }
  
  .back-button:hover {
    transform: translateX(-50%) translateY(-3px);
  }

  .video-player-container {
    width: 95%;
    height: 50%;
  }

  .close-button {
    top: 10px;
    right: 10px;
    width: 30px;
    height: 30px;
    font-size: 20px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .movie-info {
    padding: 7rem 1.5rem 2rem;
  }
  
  .movie-poster {
    width: 250px;
    height: 375px;
  }
  
  .title {
    font-size: 2.5rem;
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