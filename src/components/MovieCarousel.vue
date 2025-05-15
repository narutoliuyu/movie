<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { getApiUrl, API_PATHS, API_CONFIG, handleApiError } from '../api/config';

const router = useRouter();
const slides = ref([]);
const currentSlide = ref(0);
const loading = ref(true);
const error = ref(null);
const showControls = ref(false);
const retryCount = ref(0);
const maxRetries = 3;
let timer = null;

const fetchFeaturedMovies = async () => {
  try {
    loading.value = true;
    error.value = null;
    const response = await axios.get('/api/movies');
    
    // 处理响应数据
    let movies = [];
    if (response.data && Array.isArray(response.data)) {
      movies = response.data;
    } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
      movies = response.data.data;
    }
    
    // 只取前5部电影
    slides.value = movies.slice(0, 5).map(movie => ({
      id: movie.id,
      title: movie.title,
      poster_url: movie.poster_url,
      description: movie.description,
      director: movie.director,
      rating: movie.rating,
      movie_type: movie.movie_type
    }));
    
    loading.value = false;
  } catch (err) {
    console.error('获取轮播图电影错误:', err);
    error.value = err.response?.data?.message || '获取电影数据失败';
    loading.value = false;
  }
};

// 移除重试逻辑，简化错误处理
const startDataRefresh = () => {
  setInterval(() => {
    fetchFeaturedMovies();
  }, 5 * 60 * 1000);
};

onMounted(() => {
  fetchFeaturedMovies();
  startAutoSlide();
  startDataRefresh();
});

// 当slides变化时重置当前幻灯片位置
watch(slides, () => {
  if (slides.value.length > 0 && currentSlide.value >= slides.value.length) {
    currentSlide.value = 0;
  }
});

const nextSlide = () => {
  if (slides.value.length > 0) {
    currentSlide.value = (currentSlide.value + 1) % slides.value.length;
  }
};

const prevSlide = () => {
  if (slides.value.length > 0) {
    currentSlide.value = (currentSlide.value - 1 + slides.value.length) % slides.value.length;
  }
};

const setSlide = (index) => {
  currentSlide.value = index;
};

const startAutoSlide = () => {
  if (timer) {
    clearInterval(timer);
  }
  timer = setInterval(() => {
    nextSlide();
  }, 5000);
};

const goToMovieDetail = (movieId) => {
  router.push({
    name: 'movie-detail',
    params: { id: movieId }
  });
};

onBeforeUnmount(() => {
  if (timer) {
    clearInterval(timer);
  }
});
</script>

<template>
  <div 
    class="carousel-container" 
    @mouseenter="showControls = true" 
    @mouseleave="showControls = false"
  >
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="slides.length === 0" class="empty-container">
      <p>暂无轮播数据</p>
    </div>
    <div v-else class="carousel">
      <div class="slides" :style="{ transform: `translateX(-${currentSlide * 100}%)` }">
        <div 
          v-for="slide in slides" 
          :key="slide.id" 
          class="slide"
          :style="{ backgroundImage: `url(${slide.poster_url})` }"
          @click="goToMovieDetail(slide.id)"
        >
          <div class="slide-content">
            <div class="info-container">
              <h2 class="movie-title">{{ slide.title }}</h2>
              <div class="movie-meta">
                <span class="rating">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
                  </svg>
                  {{ slide.rating }}
                </span>
              </div>
              <p class="movie-desc">{{ slide.description }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <button 
        v-show="showControls && slides.length > 1" 
        class="carousel-control prev" 
        @click.stop="prevSlide"
      >&#10094;</button>
      <button 
        v-show="showControls && slides.length > 1" 
        class="carousel-control next" 
        @click.stop="nextSlide"
      >&#10095;</button>
      
      <div v-if="slides.length > 1" class="carousel-indicators">
        <button 
          v-for="(slide, index) in slides" 
          :key="slide.id"
          class="indicator"
          :class="{ active: index === currentSlide }"
          @click.stop="setSlide(index)"
        ></button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.carousel-container {
  width: 100%;
  height: 615px;
  overflow: hidden;
  border-radius: 12px;
  background-color: #0f1129;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.25);
}

.carousel {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  border-radius: 12px;
}

.slides {
  display: flex;
  height: 100%;
  transition: transform 0.5s ease;
}

.slide {
  flex: 0 0 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  position: relative;
  cursor: pointer;
}

.slide::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(rgba(0, 0, 0, 0.1), rgba(15, 17, 41, 0.9));
}

.slide-content {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 3rem;
  color: white;
  z-index: 1;
}

.info-container {
  max-width: 70%;
}

.movie-title {
  font-size: 3rem;
  margin-bottom: 1rem;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
  letter-spacing: 0.5px;
  color: #ffffff;
}

.movie-meta {
  display: flex;
  align-items: center;
  margin-bottom: 1.2rem;
}

.movie-desc {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  line-height: 1.7;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.6);
  opacity: 0.95;
  max-width: 100%;
}

.director {
  margin-left: 1.5rem;
  font-size: 0.95rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.6);
}

.rating {
  display: inline-flex;
  align-items: center;
  background-color: #e94560;
  color: white;
  padding: 5px 10px;
  border-radius: 20px;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(233, 69, 96, 0.5);
  font-size: 0.95rem;
}

.rating svg {
  margin-right: 5px;
}

.carousel-control {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background-color: rgba(0, 0, 0, 0.4);
  color: white;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.6rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 2;
  opacity: 0.7;
}

.carousel-control:hover {
  background-color: rgba(0, 0, 0, 0.7);
  opacity: 1;
}

.prev {
  left: 20px;
}

.next {
  right: 20px;
}

.carousel-indicators {
  position: absolute;
  bottom: 25px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 12px;
  z-index: 2;
}

.indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.5);
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
}

.indicator.active {
  background-color: white;
  transform: scale(1.2);
}

.loading-container, .error-container, .empty-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  background-color: #0f1129;
  border-radius: 10px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #e94560;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-container {
  color: #e94560;
}
</style> 