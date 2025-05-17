<script setup>
import { defineProps, ref, onMounted, watch, onBeforeMount } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  movie: {
    type: Object,
    required: true
  }
});

const router = useRouter();
const imageLoaded = ref(false);
const isIntersecting = ref(false);
const cardRef = ref(null);

// 调试用 - 打印电影ID
console.log('MovieCard 创建，ID:', props.movie.id);

const goToMovieDetail = (movieId) => {
  // 不再保存滚动位置，而是直接使用ID定位
  // sessionStorage.setItem('homeScrollPosition', window.scrollY.toString());
  console.log('点击电影卡片，ID:', movieId);
  
  // 显式保存当前浏览的电影ID
  sessionStorage.setItem('lastViewedMovieId', movieId);
  
  router.push({
    name: 'movie-detail',
    params: { id: movieId }
  });
};

const handleImageLoad = () => {
  imageLoaded.value = true;
};

// 使用Intersection Observer实现懒加载
onMounted(() => {
  console.log('MovieCard 挂载，ID:', props.movie.id);
  
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          isIntersecting.value = true;
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );
    
    if (cardRef.value) {
      observer.observe(cardRef.value);
    }
  } else {
    // 如果浏览器不支持IntersectionObserver，默认显示
    isIntersecting.value = true;
  }
});
</script>

<template>
  <div class="movie-card" 
    @click="goToMovieDetail(movie.id)" 
    :data-movie-id="movie.id"
    ref="cardRef">
    <div class="poster">
      <div class="poster-placeholder" v-if="!imageLoaded"></div>
      <img 
        v-if="isIntersecting"
        :src="movie.poster_url || 'https://via.placeholder.com/300x450/1a1a2e/ffffff?text=暂无图片'" 
        :alt="movie.title"
        @load="handleImageLoad"
        :class="{'image-loaded': imageLoaded}"
      />
      <div class="rating" v-if="movie.rating">
        <span class="rating-value">{{ movie.rating }}</span>
      </div>
      <div class="info">
        <h3 class="title">{{ movie.title }}</h3>
        <p class="director">导演：{{ movie.director || '未知' }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.movie-card {
  width: 214px;
  height: 321px;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  position: relative;
  background: #0c0e22;
  margin: 0;
  display: block;
  flex: none;
}

.poster {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: 12px;
}

.poster-placeholder {
  position: absolute;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #13173a 0%, #1c2150 50%, #13173a 100%);
  animation: pulse-bg 2s infinite ease-in-out;
}

@keyframes pulse-bg {
  0% { opacity: 0.6; }
  50% { opacity: 0.8; }
  100% { opacity: 0.6; }
}

.poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.3s ease;
  transform-origin: center;
  opacity: 0;
}

.image-loaded {
  opacity: 1 !important;
}

/* 仅保留图片微微放大效果 */
.movie-card:hover .poster img {
  transform: scale(1.05);
}

.info {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 16px;
  color: white;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8) 0%, rgba(0, 0, 0, 0.6) 40%, rgba(0, 0, 0, 0) 100%); /* 增加渐变背景 */
  z-index: 1;
}

.title {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 1); /* 增强文字阴影 */
}

.rating {
  position: absolute;
  top: 10px;
  left: 10px;
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  padding: 0.25rem 0.6rem;
  border-radius: 20px;
  font-weight: bold;
  font-size: 12px;
  box-shadow: 0 4px 10px rgba(233, 69, 96, 0.5);
  z-index: 2;
}

.director {
  margin: 0;
  font-size: 12px;
  color: #e0e0e0; /* 改为浅灰色 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 1); /* 增强文字阴影 */
}

/* 添加高亮样式 */
.highlight-movie {
  animation: pulse 3s;
  position: relative;
  z-index: 20;
  transform: scale(1.05);
  box-shadow: 0 0 25px rgba(233, 69, 96, 0.8);
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(233, 69, 96, 0.8);
    transform: scale(1);
  }
  
  25% {
    box-shadow: 0 0 20px 5px rgba(233, 69, 96, 0.8);
    transform: scale(1.08);
  }
  
  50% {
    box-shadow: 0 0 10px 0 rgba(233, 69, 96, 0.6);
    transform: scale(1.04);
  }
  
  75% {
    box-shadow: 0 0 15px 2px rgba(233, 69, 96, 0.7);
    transform: scale(1.06);
  }
  
  100% {
    box-shadow: 0 0 0 0 rgba(233, 69, 96, 0);
    transform: scale(1);
  }
}
</style>
