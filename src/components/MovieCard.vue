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
    </div>
    <div class="info">
      <h3 class="title">{{ movie.title }}</h3>
      <p class="director">导演：{{ movie.director }}</p>
    </div>
  </div>
</template>

<style scoped>
.movie-card {
  width: 200px;
  background: linear-gradient(145deg, #1a1a2e, #16213e);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  cursor: pointer;
  margin: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
}

.movie-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.4), 0 0 10px rgba(233, 69, 96, 0.2);
}

.poster {
  position: relative;
  width: 100%;
  height: 300px;
  padding-top: 150%;
  overflow: hidden;
}

.poster img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s cubic-bezier(0.215, 0.61, 0.355, 1);
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
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 10px rgba(233, 69, 96, 0.5);
  transition: transform 0.3s ease;
}

.movie-card:hover .rating {
  transform: scale(1.1);
}

.info {
  padding: 16px;
  color: white;
  background: linear-gradient(to top, #0e1123, #16213e);
}

.title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #ffffff;
}

.director {
  margin: 0;
  font-size: 14px;
  color: #c4c5e3;
}
</style>
