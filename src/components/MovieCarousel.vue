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
let autoSlideEnabled = true;

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
    if (autoSlideEnabled) {
      nextSlide();
    }
  }, 5000);
};

const pauseAutoSlide = () => {
  autoSlideEnabled = false;
};

const resumeAutoSlide = () => {
  autoSlideEnabled = true;
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
  <!-- 轮播图 -->
  <div 
    class="carousel-container" 
    @mouseenter="showControls = true; pauseAutoSlide()" 
    @mouseleave="showControls = false; resumeAutoSlide()"
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
        </div>
      </div>
      
      <div class="movie-info-container">
        <h2 class="movie-title">{{ slides[currentSlide].title }}</h2>
        <p class="movie-desc">{{ slides[currentSlide].description }}</p>
      </div>
      
      <button 
        v-show="showControls && slides.length > 1" 
        class="carousel-control prev" 
        @click.stop="prevSlide"
      >
        <img src="/src/assets/左.png" alt="上一个" class="control-icon" />
      </button>
      <button 
        v-show="showControls && slides.length > 1" 
        class="carousel-control next" 
        @click.stop="nextSlide"
      >
        <img src="/src/assets/右.png" alt="下一个" class="control-icon" />
      </button>
      
      <div v-if="slides.length > 1" class="carousel-indicators" :class="{ 'show-indicators': showControls }">
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
  position: relative;
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
  height: 100%; /* 让图片占满整个容器 */
  transition: transform 0.5s ease;
}

.slide {
  flex: 0 0 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  position: relative;
  cursor: pointer;
  transition: transform 0.7s ease; /* 放慢放大效果的过渡速度 */
}

.slide:hover {
  transform: scale(1.05); /* 鼠标悬停时图片微微放大 */
}

.slide::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.1) 0%,
    rgba(0, 0, 0, 0.2) 70%,
    rgba(0, 0, 0, 0.5) 100%
  );
}

.movie-info-container {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 2rem 3rem;
  z-index: 2;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.7) 0%,
    rgba(0, 0, 0, 0.4) 80%,
    transparent 100%
  );
}

.movie-title {
  font-size: 2.5rem;
  margin-bottom: 0.8rem;
  font-weight: 700;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
  color: #ffffff;
  text-align: left;
}

.movie-desc {
  font-size: 1rem;
  line-height: 1.5;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
  color: rgba(255, 255, 255, 0.9);
  text-align: left;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.carousel-control {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background-color: rgba(0, 0, 0, 0.5); /* 添加半透明背景 */
  border: none;
  cursor: pointer;
  z-index: 2;
  opacity: 0;
  width: 40px;
  height: 40px;
  padding: 0;
  transition: opacity 0.3s ease, background-color 0.3s ease;
  border-radius: 50%; /* 添加圆形边框 */
  display: flex;
  align-items: center;
  justify-content: center;
  outline: none; /* 去除点击时的边框 */
}

.carousel-container:hover .carousel-control {
  opacity: 1;
}

.carousel-control:hover {
  background-color: rgba(0, 0, 0, 0.7); /* 悬停时加深背景色 */
}

.carousel-control:focus {
  outline: none; /* 去除焦点时的边框 */
}

.control-icon {
  width: 60%;
  height: 60%;
}

.prev {
  left: 30px;
}

.next {
  right: 30px;
}

.carousel-indicators {
  position: absolute;
  bottom: 25px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 12px;
  z-index: 3;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.carousel-indicators.show-indicators {
  opacity: 1;
}

.indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.5);
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
}

.indicator:hover {
  background-color: rgba(255, 255, 255, 0.8);
  transform: scale(1.3);
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