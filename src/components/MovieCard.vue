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
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s ease;
  cursor: pointer;
  margin: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
}

.poster {
  position: relative;
  width: 100%;
  height: 300px;
  padding-top: 150%;
}

.poster img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.movie-card:hover .poster img {
  transform: scale(1.05);
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
}

.info {
  padding: 12px;
  color: white;
  background: linear-gradient(to top, #16213e, rgba(22, 33, 62, 0.9));
}

.title {
  margin: 0 0 8px 0;
  font-size: 16px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.director {
  margin: 0;
  font-size: 14px;
  color: #b9bad3;
}
</style>
