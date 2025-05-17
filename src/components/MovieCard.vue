<script setup>
import { defineProps } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const props = defineProps({
  movie: {
    type: Object,
    required: true
  }
});

const handleClick = () => {
  if (props.movie && props.movie.id) {
    router.push(`/movie/${props.movie.id}`);
  }
};
</script>

<template>
  <div class="movie-card" @click="handleClick">
    <div class="poster">
      <img 
        :src="movie.poster_url || 'https://via.placeholder.com/300x450/1a1a2e/ffffff?text=暂无图片'" 
        :alt="movie.title"
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
  width: 180px;
  border-radius: 20px !important;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  cursor: pointer;
  margin: 8px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
  position: relative;
  height: 250px;
  background: linear-gradient(145deg, #13173a, #0c0e22);
}

.movie-card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.4), 0 0 15px rgba(233, 69, 96, 0.3);
  border-radius: 25px !important;
}

.poster {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: 20px;
}

.poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s cubic-bezier(0.215, 0.61, 0.355, 1);
  display: block;
  border-radius: 20px;
}

.movie-card:hover .poster img {
  transform: scale(1.08);
}

.rating {
  position: absolute;
  top: 10px;
  right: 10px;
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  padding: 0.25rem 0.6rem;
  border-radius: 20px;
  font-weight: bold;
  font-size: 12px;
  backdrop-filter: blur(4px);
  box-shadow: 0 4px 10px rgba(233, 69, 96, 0.5);
  transition: transform 0.3s ease, border-radius 0.3s ease;
  z-index: 2;
}

.movie-card:hover .rating {
  transform: scale(1.1);
  border-radius: 12px;
}

.info {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 50px 16px 16px 16px;
  color: white;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.9) 0%, rgba(0, 0, 0, 0.7) 50%, transparent 100%);
  z-index: 1;
  transition: all 0.4s ease;
  border-top-left-radius: 30px;
  border-top-right-radius: 30px;
  transform: translateY(5px);
}

.movie-card:hover .info {
  padding-bottom: 20px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.95) 0%, rgba(0, 0, 0, 0.8) 60%, transparent 100%);
  transform: translateY(0);
}

.title {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #ffffff;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8);
  transition: transform 0.3s ease;
}

.movie-card:hover .title {
  transform: translateY(-3px);
}

.director {
  margin: 0;
  font-size: 12px;
  color: #e0e0e0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  opacity: 0.8;
  transform: translateY(3px);
  transition: all 0.3s ease;
}

.movie-card:hover .director {
  opacity: 1;
  transform: translateY(0);
}
</style>
