<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import NavBar from '../components/NavBar.vue';
import { getApiUrl, API_PATHS, API_CONFIG } from '../api/config';
import videoUrl from '../assets/video.mp4';

const route = useRoute();
const router = useRouter();
const movie = ref(null);
const loading = ref(true);
const error = ref('');
const showVideo = ref(false);

const fetchMovieDetails = async () => {
  try {
    loading.value = true;
    error.value = '';
    const response = await axios.get(getApiUrl('/api/movies/' + route.params.id));
    
    if (response.data.status === 'success') {
      movie.value = response.data.data;
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

const goBack = () => {
  router.back();
};

const playVideo = () => {
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
    <div class="back-button" @click="goBack">
      <i class="back-icon">←</i>
      返回
    </div>

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

      <div class="movie-info">
        <div class="movie-poster">
          <img :src="movie.poster_url" :alt="movie.title">
          <div class="rating" v-if="movie.rating">
            <span class="rating-value">{{ movie.rating }}</span>
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

          <div class="actions">
            <button class="play-button" @click="playVideo">
              <i class="play-icon">▶</i>
              立即观看
            </button>
            <button class="favorite-button">
              <i class="heart-icon">♥</i>
              收藏
            </button>
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
  background: #1a1a2e;
  color: white;
  position: relative;
  padding-top: 70px;
}

.back-button {
  position: fixed;
  top: 80px;
  left: 20px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(233, 69, 96, 0.9);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.back-button:hover {
  background: #d03651;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.loading, .error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 70px);
  padding: 2rem;
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

.movie-content {
  position: relative;
  min-height: calc(100vh - 70px);
}

.movie-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
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
    rgba(26, 26, 46, 0.7) 0%,
    rgba(26, 26, 46, 0.85) 50%,
    rgba(26, 26, 46, 0.95) 100%
  );
  backdrop-filter: blur(10px);
}

.movie-info {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 3rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 2rem;
}

.movie-poster {
  flex-shrink: 0;
  width: 300px;
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
  transition: transform 0.3s ease;
}

.movie-poster:hover {
  transform: scale(1.02);
}

.movie-poster img {
  width: 100%;
  height: auto;
  display: block;
}

.rating {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(233, 69, 96, 0.9);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: bold;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.movie-details {
  flex: 1;
  padding-top: 1rem;
}

.title {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  background: linear-gradient(45deg, #fff, #e94560);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.meta-info {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  color: #b9bad3;
}

.year, .type {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  backdrop-filter: blur(4px);
}

.director {
  margin-bottom: 1.5rem;
  color: #e0e0e0;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  backdrop-filter: blur(4px);
}

.label {
  color: #b9bad3;
  margin-right: 0.5rem;
}

.description {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  backdrop-filter: blur(4px);
}

.description h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #e94560;
  position: relative;
  display: inline-block;
}

.description h3::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 30px;
  height: 2px;
  background: #e94560;
}

.description p {
  line-height: 1.8;
  color: #e0e0e0;
}

.actions {
  display: flex;
  gap: 1rem;
}

.play-button, .favorite-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.play-button {
  background: #e94560;
  color: white;
  box-shadow: 0 2px 10px rgba(233, 69, 96, 0.3);
}

.play-button:hover {
  background: #d03651;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
}

.favorite-button {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  backdrop-filter: blur(10px);
}

.favorite-button:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .movie-info {
    flex-direction: column;
    padding: 2rem 1rem;
  }

  .movie-poster {
    width: 100%;
    max-width: 300px;
    margin: 0 auto;
  }

  .title {
    font-size: 2rem;
  }

  .meta-info {
    flex-wrap: wrap;
  }

  .actions {
    flex-direction: column;
  }
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
  backdrop-filter: blur(10px);
}

.video-player-container {
  position: relative;
  width: 100%;
  height: 100%;
  max-width: 1920px;
  max-height: 1080px;
}

.video-player {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.close-button {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 1001;
  backdrop-filter: blur(4px);
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

@media (max-width: 768px) {
  .video-player-container {
    padding: 20px;
  }

  .close-button {
    top: 10px;
    right: 10px;
    width: 30px;
    height: 30px;
    font-size: 20px;
  }
}
</style> 