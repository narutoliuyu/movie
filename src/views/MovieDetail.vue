<script setup>
import { ref, onMounted, computed, onUnmounted, shallowRef } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import NavBar from '../components/NavBar.vue';
import MovieCard from '../components/MovieCard.vue';
import { getApiUrl, API_PATHS, API_CONFIG, CookieUtil } from '../api/config';
import { useUserStore } from '../stores/user';
import videoUrl from '../assets/video1.mp4';
import backIcon from '../assets/返回.png';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const movie = shallowRef(null); // 使用shallowRef减少深层响应式监听
const loading = ref(true);
const error = ref('');
const showVideo = ref(false);
const isFavorite = ref(false);
const lastWatchProgress = ref(Math.random() * 0.9 + 0.05); // 随机生成5%-95%的进度
const similarMovies = shallowRef([]); // 使用shallowRef减少大数组的响应式开销
let backdropImage = null; // 用于预加载背景图

// 使用节流函数，避免频繁执行
const throttle = (fn, delay = 300) => {
  let lastCall = 0;
  return (...args) => {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      return fn(...args);
    }
  };
};

// 预加载背景图片
const preloadBackdropImage = (url) => {
  if (!url) return;
  
  backdropImage = new Image();
  backdropImage.src = url;
};

// 组件卸载时清理资源
onUnmounted(() => {
  backdropImage = null;
  
  // 清理视频元素
  if (showVideo.value) {
    const videoPlayer = document.querySelector('.video-player');
    if (videoPlayer) {
      videoPlayer.pause();
      videoPlayer.src = '';
      videoPlayer.load();
    }
  }
  
  // 清理内存中的大对象引用
  movie.value = null;
  similarMovies.value = [];
});

// 检查电影是否已收藏 - 使用节流函数优化
const checkIfFavorite = throttle(() => {
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
});

// 获取上次观看进度
const getLastWatchProgress = () => {
  if (!movie.value) return null;
  
  // 直接使用随机生成的观看进度
  return lastWatchProgress.value;
};

// 获取相似电影 - 优化版
const fetchSimilarMovies = async () => {
  if (!movie.value) return;
  
  try {
    // 使用缓存数据避免频繁API调用
    if (sessionStorage.getItem('cachedMovies')) {
      const cachedData = JSON.parse(sessionStorage.getItem('cachedMovies'));
      processMovieData(cachedData);
      return;
    }
    
    // 获取所有电影并过滤
    const response = await axios.get(getApiUrl(API_PATHS.MOVIES.ALL));
    let allMovies = [];
    
    if (response.data && Array.isArray(response.data.data)) {
      allMovies = response.data.data;
    } else if (response.data && Array.isArray(response.data.movies)) {
      allMovies = response.data.movies;
    } else if (Array.isArray(response.data)) {
      allMovies = response.data;
    }
    
    // 缓存电影数据
    sessionStorage.setItem('cachedMovies', JSON.stringify(allMovies));
    processMovieData(allMovies);
    
  } catch (err) {
    console.error('获取相似电影失败:', err);
    // 使用备用数据
    useFallbackMovies();
  }
};

// 处理电影数据 - 优化性能
const processMovieData = (allMovies) => {
  requestAnimationFrame(() => {
    // 过滤条件：不是当前电影且电影类型相同
    const filteredMovies = allMovies.filter(m => 
      m.id !== movie.value.id && 
      m.movie_type === movie.value.movie_type
    );
    
    // 如果没有同类型电影，则显示任意其他电影
    if (filteredMovies.length === 0) {
      similarMovies.value = allMovies
        .filter(m => m.id !== movie.value.id)
        .slice(0, 5);
    } else {
      // 最多取5部相同类型的电影
      similarMovies.value = filteredMovies.slice(0, 5);
    }
  });
};

// 使用备用数据
const useFallbackMovies = () => {
  similarMovies.value = [
    {
      id: 101,
      title: '相似电影1',
      poster_url: 'https://via.placeholder.com/300x450/13173a/ffffff?text=相似电影1',
      director: '导演A',
      release_date: '2023',
      movie_type: movie.value?.movie_type || '动作'
    },
    {
      id: 102,
      title: '相似电影2',
      poster_url: 'https://via.placeholder.com/300x450/13173a/ffffff?text=相似电影2',
      director: '导演B',
      release_date: '2022',
      movie_type: movie.value?.movie_type || '动作'
    },
    {
      id: 103,
      title: '相似电影3',
      poster_url: 'https://via.placeholder.com/300x450/13173a/ffffff?text=相似电影3',
      director: '导演C',
      release_date: '2021',
      movie_type: movie.value?.movie_type || '动作'
    },
    {
      id: 104,
      title: '相似电影4',
      poster_url: 'https://via.placeholder.com/300x450/13173a/ffffff?text=相似电影4',
      director: '导演D',
      release_date: '2020',
      movie_type: movie.value?.movie_type || '动作'
    },
    {
      id: 105,
      title: '相似电影5',
      poster_url: 'https://via.placeholder.com/300x450/13173a/ffffff?text=相似电影5',
      director: '导演E',
      release_date: '2019',
      movie_type: movie.value?.movie_type || '动作'
    }
  ];
};

const fetchMovieDetails = async () => {
  try {
    loading.value = true;
    error.value = '';
    
    // 首先检查是否有缓存数据
    const cachedMovies = sessionStorage.getItem('cachedMovies');
    if (cachedMovies) {
      const movies = JSON.parse(cachedMovies);
      const cachedMovie = movies.find(m => m.id == route.params.id);
      
      if (cachedMovie) {
        // 使用requestAnimationFrame分离数据处理和UI渲染
        requestAnimationFrame(() => {
          movie.value = cachedMovie;
          // 预加载背景图片
          preloadBackdropImage(movie.value.poster_url);
          // 检查是否已收藏
          checkIfFavorite();
          // 获取上次观看进度
          getLastWatchProgress();
          // 获取相似电影
          fetchSimilarMovies();
          loading.value = false;
        });
        return;
      }
    }
    
    // 无缓存数据，请求API
    const response = await axios.get(getApiUrl('/api/movies/' + route.params.id));
    
    if (response.data.status === 'success') {
      // 使用requestAnimationFrame分离数据处理和UI渲染
      requestAnimationFrame(() => {
        movie.value = response.data.data;
        // 预加载背景图片
        preloadBackdropImage(movie.value.poster_url);
        // 检查是否已收藏
        checkIfFavorite();
        // 获取上次观看进度
        getLastWatchProgress();
        // 获取相似电影
        setTimeout(() => fetchSimilarMovies(), 100); // 延迟加载相似电影
      });
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
      add_time: new Date().toISOString(),
      // 添加其他可能需要的字段，便于在收藏列表中显示
      rating: movie.value.rating,
      director: movie.value.director,
      release_date: movie.value.release_date,
      movie_type: movie.value.movie_type
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
    
    // 显示操作成功的提示
    const toastText = isFavorite.value ? '已添加到收藏' : '已从收藏中移除';
    showToast(toastText);
    
  } catch (err) {
    console.error('操作收藏失败:', err);
    showToast('操作失败，请重试');
  }
};

// 简单的提示框显示
const showToast = (message) => {
  const toast = document.createElement('div');
  toast.className = 'toast-message';
  toast.textContent = message;
  document.body.appendChild(toast);
  
  // 使用CSS动画显示提示框
  setTimeout(() => {
    toast.classList.add('show');
    
    // 3秒后隐藏并移除提示框
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 300);
    }, 2000);
  }, 10);
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
  // 保存当前电影ID以便返回首页后能找到这个位置
  if (movie.value) {
    sessionStorage.setItem('lastViewedMovieId', movie.value.id);
    // 清除上次保存的滚动位置，确保使用电影ID定位
    sessionStorage.removeItem('homeScrollPosition');
  }
  router.back();
};

const goToHome = () => {
  // 保存当前电影ID以便返回首页后能找到这个位置
  if (movie.value) {
    sessionStorage.setItem('lastViewedMovieId', movie.value.id);
    // 清除上次保存的滚动位置，确保使用电影ID定位
    sessionStorage.removeItem('homeScrollPosition');
  }
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
  <div class="movie-detail-page">
    <div class="movie-detail">
      <NavBar />

      <button class="back-button" @click="goBack">
        <img class="back-icon" :src="backIcon" alt="返回" />
        返回
      </button>

      <div v-if="loading" class="loading">
        <div class="skeleton-movie-detail">
          <div class="skeleton-movie-info">
            <div class="skeleton-poster"></div>
            <div class="skeleton-info-content">
              <div class="skeleton-title"></div>
              <div class="skeleton-subtitle"></div>
              <div class="skeleton-info-grid">
                <div class="skeleton-info-item" v-for="n in 6" :key="n"></div>
              </div>
              <div class="skeleton-synopsis"></div>
              <div class="skeleton-buttons">
                <div class="skeleton-button"></div>
                <div class="skeleton-button"></div>
              </div>
            </div>
          </div>
          <div class="skeleton-similar-movies">
            <div class="skeleton-section-title"></div>
            <div class="skeleton-movies-grid">
              <div class="skeleton-movie-card" v-for="n in 5" :key="n"></div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button class="retry-button" @click="fetchMovieDetails">
          重试
        </button>
      </div>

      <div v-else-if="movie" class="movie-content">
        <!-- 背景图 -->
        <div 
          class="movie-backdrop animation-gpu" 
          :style="{ backgroundImage: `url(${movie.backdrop_url || movie.poster_url})` }"
        >
          <div class="backdrop-overlay"></div>
        </div>
        
        <div class="movie-info">
          <!-- 左侧海报 -->
          <div class="movie-poster-container animation-gpu">
            <div class="movie-poster">
              <img 
                :src="movie.poster_url || 'https://via.placeholder.com/300x450/1a1a2e/ffffff?text=暂无图片'" 
                :alt="movie.title"
                loading="eager"
              />
              
              <!-- 评分（常驻显示） -->
              <div class="rating" v-if="movie.rating">
                <span class="rating-value">{{ movie.rating }}</span>
              </div>
              
              <!-- 收藏按钮 -->
              <button 
                class="favorite-btn" 
                :class="{'active': isFavorite}"
                @click.stop="toggleFavorite"
              >
                <span class="heart-icon">❤</span>
              </button>
              
              <!-- 悬停时显示的海报覆盖层 -->
              <div class="poster-overlay">
                <div class="overlay-actions">
                  <!-- 播放按钮 -->
                  <button class="play-btn" @click.stop="playVideo">
                    <span class="play-icon">▶</span>
                  </button>
                </div>
              </div>
              
              <!-- 观看进度 -->
              <div class="watch-progress-container" v-if="getLastWatchProgress()">
                <div class="progress-text">已观看 {{ Math.round(getLastWatchProgress() * 100) }}%</div>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{width: (getLastWatchProgress() * 100) + '%'}"></div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 右侧详细信息 -->
          <div class="movie-details content-visibility-auto">
            <h1 class="title">{{ movie.title }}</h1>
            <div class="tagline" v-if="movie.tagline">{{ movie.tagline }}</div>
            
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">上映日期</span>
                <span class="info-value">{{ movie.release_date }}</span>
              </div>
              
              <div class="info-item">
                <span class="info-label">类型</span>
                <span class="info-value">{{ movie.movie_type }}</span>
              </div>
              
              <div class="info-item">
                <span class="info-label">导演</span>
                <span class="info-value">{{ movie.director }}</span>
              </div>
              
              <div class="info-item full-width">
                <span class="info-label">剧情简介</span>
                <p class="info-value description-text">{{ movie.description }}</p>
              </div>
            </div>

            <div class="movie-tags">
              <span class="tag">动作</span>
              <span class="tag">冒险</span>
              <span class="tag">科幻</span>
              <span class="tag">剧情</span>
            </div>
          </div>
        </div>
        
        <!-- 相似电影推荐 -->
        <div class="similar-movies-section content-visibility-auto" v-if="similarMovies.length > 0">
          <h2 class="section-title">相似电影推荐</h2>
          <div class="similar-movies-container">
            <div class="similar-movies-grid">
              <MovieCard
                v-for="movie in similarMovies"
                :key="movie.id"
                :movie="movie"
                class="animation-gpu"
              />
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
            preload="auto"
          ></video>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
/* 全局样式修复 */
html, body {
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: auto !important;
  overscroll-behavior: none; /* 防止页面触底反弹 */
}
</style>

<style scoped>
/* 外层容器 */
.movie-detail-page {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  position: relative;
  will-change: transform; /* 提示浏览器这个元素会变化，优化性能 */
  contain: content; /* 告诉浏览器该元素和它的内容尽可能独立于DOM的其他部分 */
}

/* 修复滚动问题 */
.movie-detail {
  min-height: 100vh;
  background: #0f1129;
  color: white;
  position: relative;
  overflow-y: auto !important;
  padding-bottom: 50px;
  height: auto;
  width: 100%;
  display: flex;
  flex-direction: column;
  contain: content; /* 性能优化 */
}

body {
  overflow-y: auto !important;
  height: auto !important;
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
  width: 100%;
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

/* 骨架屏效果 */
.skeleton-movie-detail {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.skeleton-movie-info {
  display: flex;
  gap: 3rem;
  margin-bottom: 40px;
}

.skeleton-poster {
  width: 300px;
  height: 450px;
  border-radius: 16px;
  background: linear-gradient(110deg, #13173a 25%, #1c2150 37%, #13173a 63%);
  background-size: 200% 100%;
  animation: loading-shine 1.5s infinite;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
}

.skeleton-info-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.skeleton-title {
  height: 40px;
  width: 70%;
  background: linear-gradient(110deg, #333755 25%, #444a7a 37%, #333755 63%);
  background-size: 200% 100%;
  animation: loading-shine 1.5s infinite;
  border-radius: 8px;
}

.skeleton-subtitle {
  height: 24px;
  width: 50%;
  margin-top: 12px;
  background: linear-gradient(110deg, #333755 25%, #444a7a 37%, #333755 63%);
  background-size: 200% 100%;
  animation: loading-shine 1.5s infinite;
  border-radius: 6px;
}

.skeleton-info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 20px;
}

.skeleton-info-item {
  height: 70px;
  background: linear-gradient(110deg, #1a1f45 25%, #252b5c 37%, #1a1f45 63%);
  background-size: 200% 100%;
  animation: loading-shine 1.5s infinite;
  border-radius: 8px;
}

.skeleton-synopsis {
  height: 120px;
  margin-top: 20px;
  background: linear-gradient(110deg, #1a1f45 25%, #252b5c 37%, #1a1f45 63%);
  background-size: 200% 100%;
  animation: loading-shine 1.5s infinite;
  border-radius: 8px;
}

.skeleton-buttons {
  display: flex;
  gap: 16px;
  margin-top: 20px;
}

.skeleton-button {
  height: 50px;
  width: 150px;
  background: linear-gradient(110deg, #e9455f33 25%, #e9455f66 37%, #e9455f33 63%);
  background-size: 200% 100%;
  animation: loading-shine 1.5s infinite;
  border-radius: 50px;
}

.skeleton-similar-movies {
  margin-top: 60px;
}

.skeleton-section-title {
  height: 30px;
  width: 200px;
  margin-bottom: 24px;
  background: linear-gradient(110deg, #333755 25%, #444a7a 37%, #333755 63%);
  background-size: 200% 100%;
  animation: loading-shine 1.5s infinite;
  border-radius: 6px;
}

.skeleton-movies-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
}

.skeleton-movie-card {
  aspect-ratio: 2/3;
  background: linear-gradient(110deg, #13173a 25%, #1c2150 37%, #13173a 63%);
  background-size: 200% 100%;
  animation: loading-shine 1.5s infinite;
  border-radius: 12px;
}

@keyframes loading-shine {
  0% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0 50%;
  }
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
  padding-bottom: 50px;
  overflow: visible;
  display: flex;
  flex-direction: column;
  contain: content; /* 内容隔离，优化渲染 */
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
  will-change: transform; /* 性能优化 */
  contain: paint; /* 性能优化 */
  transform: translateZ(0); /* 触发硬件加速 */
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
  flex: 0 0 auto;
  width: 300px;
  height: 450px;
  margin-right: 3rem;
  position: relative;
}

.movie-poster {
  width: 100%;
  height: 100%;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  transition: transform 0.3s ease;
}

.movie-poster:hover {
  transform: scale(1.02);
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* 评分组件 - 常驻显示 */
.rating {
  position: absolute;
  top: 15px;
  left: 15px;
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  padding: 0.25rem 0.7rem;
  border-radius: 20px;
  font-weight: bold;
  font-size: 14px;
  box-shadow: 0 4px 10px rgba(233, 69, 96, 0.5);
  z-index: 3;
  transition: all 0.3s ease;
}

/* 收藏按钮 */
.favorite-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(15, 17, 41, 0.7);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}

.movie-poster:hover .favorite-btn {
  opacity: 1;
  transform: translateY(0);
}

.heart-icon {
  font-size: 20px;
  color: #8f8f9f;
  transition: all 0.3s ease;
}

.favorite-btn.active .heart-icon {
  color: #e94560;
  text-shadow: 0 0 10px rgba(233, 69, 96, 0.7);
}

.favorite-btn:hover .heart-icon {
  transform: scale(1.2);
}

/* 海报覆盖层（悬停时显示） */
.poster-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to top, rgba(12, 14, 34, 0.9) 0%, rgba(12, 14, 34, 0.4) 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 2;
}

.movie-poster:hover .poster-overlay {
  opacity: 1;
}

/* 覆盖层内的操作按钮 */
.overlay-actions {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 播放按钮 */
.play-btn {
  width: 65px;
  height: 65px;
  border-radius: 50%;
  background: rgba(233, 69, 96, 0.85);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.3s ease;
  box-shadow: 0 0 20px rgba(233, 69, 96, 0.5);
  transform: scale(0.9);
}

.play-btn:hover {
  transform: scale(1);
  background: #e94560;
  box-shadow: 0 0 30px rgba(233, 69, 96, 0.7);
}

.play-icon {
  font-size: 30px;
  margin-left: 5px;
}

/* 观看进度 */
.watch-progress-container {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 12px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
  z-index: 3;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s ease;
}

.movie-poster:hover .watch-progress-container {
  opacity: 1;
  transform: translateY(0);
}

.progress-text {
  font-size: 12px;
  color: #ffffff;
  margin-bottom: 5px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(to right, #e94560, #c23758);
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

/* 新的信息网格布局 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 25px;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.03);
  padding: 25px;
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.info-item {
  display: flex;
  flex-direction: column;
  position: relative;
}

.info-item::after {
  content: '';
  position: absolute;
  bottom: -12px;
  left: 0;
  width: 30px;
  height: 2px;
  background: linear-gradient(90deg, #e94560, transparent);
  border-radius: 1px;
}

.full-width {
  grid-column: 1 / -1;
  margin-top: 15px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.info-label {
  font-size: 13px;
  color: #b9bad3;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.info-value {
  font-size: 16px;
  color: #ffffff;
}

.description-text {
  line-height: 1.8;
  margin-top: 10px;
  color: #e0e0e0;
  text-align: justify;
  font-size: 15px;
}

.movie-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 25px 0;
}

.tag {
  background: rgba(233, 69, 96, 0.1);
  padding: 6px 16px;
  border-radius: 50px;
  font-size: 13px;
  color: #e0e0e0;
  border: 1px solid rgba(233, 69, 96, 0.2);
  transition: all 0.3s ease;
}

.tag:hover {
  background: rgba(233, 69, 96, 0.2);
  transform: translateY(-2px);
}

/* 相似电影推荐区域 */
.similar-movies-section {
  margin-top: 50px;
  padding: 20px 0;
}

.section-title {
  font-size: 1.8rem;
  margin-bottom: 30px;
  font-weight: 600;
  background: linear-gradient(45deg, #ffffff, #e94560);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
  padding-left: 15px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 30px;
  background: linear-gradient(to bottom, #e94560, #aa2a49);
  border-radius: 2px;
}

.similar-movies-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.similar-movies-grid {
  display: grid;
  grid-template-columns: repeat(5, 214px);
  gap: 20px;
  padding: 10px 0;
  justify-content: center;
}

/* 响应式布局 */
@media (max-width: 1190px) {
  .similar-movies-grid {
    grid-template-columns: repeat(4, 214px);
  }
}

@media (max-width: 956px) {
  .similar-movies-grid {
    grid-template-columns: repeat(3, 214px);
  }
}

@media (max-width: 722px) {
  .similar-movies-grid {
    grid-template-columns: repeat(2, 214px);
  }
}

@media (max-width: 500px) {
  .similar-movies-grid {
    grid-template-columns: repeat(1, 214px);
  }
}

/* 视频播放器样式 */
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

/* Toast提示样式 */
.toast-message {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%) translateY(100px);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 14px;
  z-index: 10000;
  opacity: 0;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(233, 69, 96, 0.3);
}

.toast-message.show {
  transform: translateX(-50%) translateY(0);
  opacity: 1;
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

  .info-grid {
    grid-template-columns: 1fr 1fr;
    justify-content: center;
  }
  
  .back-button {
    top: 80px;
    left: 50%;
    transform: translateX(-50%);
  }
  
  .back-button:hover {
    transform: translateX(-50%) translateY(-3px);
  }
  
  .action-buttons {
    flex-direction: column;
    width: 100%;
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

  .similar-movies-grid {
    justify-content: space-between;
  }
  
  .similar-movies-grid :deep(.movie-card) {
    width: calc(50% - 8px);
  }
  
  .section-title {
    font-size: 1.3rem;
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
  
  .info-grid {
    gap: 15px;
  }

  .similar-movies-grid :deep(.movie-card) {
    width: calc(33.33% - 10px);
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